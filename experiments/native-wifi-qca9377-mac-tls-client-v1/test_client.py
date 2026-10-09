"""Synthetic identities only: genuine OpenSSL two-endpoint TLS, no BLE/keyfile."""
import datetime,hashlib,ssl,tempfile
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import ec
from client import Client,Closed,context
checks=0
def check(v):
 global checks;checks+=1;assert v

def identity(folder,name):
 key=ec.generate_private_key(ec.SECP256R1());subject=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,name)])
 cert=x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(datetime.datetime(2020,1,1)).not_valid_after(datetime.datetime(2099,1,1)).add_extension(x509.BasicConstraints(ca=True,path_length=0),True).sign(key,hashes.SHA256())
 c=folder/(name+'.crt');k=folder/(name+'.key');c.write_bytes(cert.public_bytes(serialization.Encoding.PEM));k.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));k.chmod(0o600)
 pin=hashlib.sha256(key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)).digest()
 return c,k,pin

def rejected(fn):
 try:fn()
 except (Closed,ValueError):return True
 return False
with tempfile.TemporaryDirectory(prefix='rabbit-public-synthetic-tls-') as tmp:
 folder=Path(tmp);sc,sk,pin=identity(folder,'synthetic-server');cc,ck,_=identity(folder,'synthetic-client');ctx=context(cc,ck)
 check(rejected(lambda:Client(ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT),pin,7,1)))
 check(rejected(lambda:Client(ctx,bytes(32),7,1)));check(rejected(lambda:Client(ctx,pin,0,1)))
 c=Client(ctx,pin,7,1);check(rejected(lambda:c.write(7,1,b'synthetic-test')));check(c.closed and not c.ready)
 c=Client(ctx,pin,7,1);check(rejected(lambda:c.poll(8,1)))
 c=Client(ctx,pin,7,2);check(rejected(lambda:c.poll(7,1)))
 c=Client(ctx,pin,7,1);check(rejected(lambda:c.poll(7,60000001)))
 c=Client(ctx,pin,7,1);check(rejected(lambda:c.feed(7,1,b'x'*241)))
 c=Client(ctx,pin,7,1)
 for _ in range(34):c.feed(7,1,b'x'*240)
 check(rejected(lambda:c.feed(7,1,b'x'*240)))
 for mode in range(4):
  serverctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);serverctx.minimum_version=serverctx.maximum_version=ssl.TLSVersion.TLSv1_3;serverctx.options|=ssl.OP_NO_TICKET;serverctx.num_tickets=0;serverctx.load_cert_chain(sc,sk);serverctx.verify_mode=ssl.CERT_REQUIRED;serverctx.load_verify_locations(cafile=cc)
  si=ssl.MemoryBIO();so=ssl.MemoryBIO();server=serverctx.wrap_bio(si,so,server_side=True)
  p=pin if mode!=1 else pin[:-1]+bytes([pin[-1]^1]);c=Client(ctx,p,7,1);serverready=False;failed=False;largest=0
  for step in range(1000):
   try:c.poll(7,2+step)
   except Closed:failed=True;break
   while c.output.pending:
    fragment=c.drain(7,2+step);largest=max(largest,len(fragment));si.write(fragment)
   try:server.do_handshake();serverready=True
   except (ssl.SSLWantReadError,ssl.SSLWantWriteError):pass
   while so.pending:c.feed(7,2+step,so.read(min(240,so.pending)))
   if c.ready and serverready:break
  if mode==1:check(failed and not c.ready);continue
  check(c.ready and serverready and 0<largest<=240);check(server.getpeercert(binary_form=True) is not None);check(not server.session_reused)
  if mode==2:check(rejected(lambda:c.write(7,2000,b'x'*2049)));continue
  if mode==3:check(rejected(lambda:c.poll(7,60000001)));continue
  data=b'public synthetic encrypted application';check(c.write(7,2000,data)==len(data))
  while c.output.pending:si.write(c.drain(7,2000))
  check(server.read(2048)==data);server.write(b'public synthetic reply')
  while so.pending:c.feed(7,2001,so.read(min(240,so.pending)))
  check(c.read(7,2001)==b'public synthetic reply');c.close();check(rejected(lambda:c.poll(7,2002)))
print('MAC-MEMORYBIO-TLS13',checks,'genuine fixture/mutual certificate/fullSPKI/bounded negative checks; physical=0')
