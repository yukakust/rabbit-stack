"""Bounded Mac TLS1.3 ciphertext endpoint; no BLE, password or owner-key access.
Caller must first prove physical full Dell SPKI + current parent epoch/code-set
and owner-authorize this client's exact public SPKI. This class grants neither.
"""
import hashlib,hmac,ssl
from cryptography import x509
from cryptography.hazmat.primitives import serialization
class Closed(Exception): pass
class Client:
    def __init__(self,context,pin,epoch,now):
        if not isinstance(context,ssl.SSLContext) or context.minimum_version!=ssl.TLSVersion.TLSv1_3 or context.maximum_version!=ssl.TLSVersion.TLSv1_3 or not context.options&ssl.OP_NO_TICKET:
            raise ValueError('TLS1.3/no-ticket context required')
        if not isinstance(pin,bytes) or len(pin)!=32 or not any(pin) or not isinstance(epoch,int) or not 0<epoch<2**64 or not isinstance(now,int) or not 0<now<2**64-60000000:
            raise ValueError('binding required')
        self.input=ssl.MemoryBIO();self.output=ssl.MemoryBIO()
        self.tls=context.wrap_bio(self.input,self.output,server_side=False,server_hostname=None)
        self.pin=pin;self.epoch=epoch;self.last=now;self.deadline=now+60000000
        self.ready=False;self.closed=False;self.sent=0;self.received=0
    def _tick(self,epoch,now):
        if self.closed:raise Closed('closed')
        if epoch!=self.epoch or not isinstance(now,int) or now<self.last or now>=self.deadline:
            self.close();raise Closed('binding expired')
        self.last=now
    def feed(self,epoch,now,data):
        self._tick(epoch,now)
        if not isinstance(data,bytes) or not 0<len(data)<=240 or self.input.pending+len(data)>8192:
            self.close();raise Closed('ciphertext bounds')
        self.input.write(data)
    def poll(self,epoch,now):
        self._tick(epoch,now)
        if self.ready:return True
        try:
            self.tls.do_handshake()
            cert=self.tls.getpeercert(binary_form=True)
            if not cert or len(cert)>4096 or self.tls.version()!='TLSv1.3' or self.tls.session_reused:
                raise ValueError('full TLS1.3 required')
            spki=x509.load_der_x509_certificate(cert).public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
            if not hmac.compare_digest(hashlib.sha256(spki).digest(),self.pin):raise ValueError('SPKI mismatch')
            self.ready=True
        except (ssl.SSLWantReadError,ssl.SSLWantWriteError):pass
        except (ssl.SSLError,ValueError):
            self.close();raise Closed('handshake rejected') from None
        if self.output.pending>8192:self.close();raise Closed('ciphertext overflow')
        return self.ready
    def drain(self,epoch,now):
        self._tick(epoch,now)
        return self.output.read(min(240,self.output.pending))
    def write(self,epoch,now,data):
        self._tick(epoch,now)
        if not self.ready or not isinstance(data,bytes) or not 0<len(data)<=2048 or self.sent+len(data)>4096 or self.output.pending>4096:
            self.close();raise Closed('application gate')
        try:n=self.tls.write(data)
        except (ssl.SSLError,ValueError):self.close();raise Closed('application write') from None
        if n!=len(data):self.close();raise Closed('partial application write')
        self.sent+=n
        return n
    def read(self,epoch,now):
        self._tick(epoch,now)
        if not self.ready:self.close();raise Closed('application gate')
        try:data=self.tls.read(2048)
        except (ssl.SSLWantReadError,ssl.SSLWantWriteError):return b''
        except (ssl.SSLError,ValueError):self.close();raise Closed('application read') from None
        self.received+=len(data)
        if not data or self.received>4096:self.close();raise Closed('application bounds')
        return data
    def close(self):
        self.ready=False;self.closed=True;self.tls=None
        # Drop owned TLS/BIO references. Python/OpenSSL internal secret memory
        # is managed by the runtime; this is not a claim of explicit zeroization.
        self.input=None;self.output=None;self.pin=b''
def context(certificate_file,key_file):
    c=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT);c.check_hostname=False;c.verify_mode=ssl.CERT_NONE
    c.minimum_version=c.maximum_version=ssl.TLSVersion.TLSv1_3;c.options|=ssl.OP_NO_TICKET
    c.load_cert_chain(certificate_file,key_file)
    # No session object/caching/early-data interface. Certificate chain is
    # intentionally replaced ONLY by exact out-of-band full-SPKI pin validation.
    return c
