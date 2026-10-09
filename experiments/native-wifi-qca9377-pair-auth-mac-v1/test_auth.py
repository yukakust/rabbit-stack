import struct,hashlib
from cryptography.hazmat.primitives.asymmetric import ec,ed25519
from cryptography.hazmat.primitives import serialization
from auth import body,packet
# Generated synthetic fixture owner/client; no runtime key or physical authority.
owner=ed25519.Ed25519PrivateKey.generate();client=ec.generate_private_key(ec.SECP256R1());der=client.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
target=bytes(range(32));codeset=bytes(range(1,33));dell=bytes(range(2,34));nonce=bytes(range(3,35));t=b'RABPAIR1'+struct.pack('<II',1,0)+target+struct.pack('<Q',66)+codeset+dell+bytes(32)+nonce+struct.pack('<QQ',10,60000010)
b=body(t,target,66,codeset,dell,der);assert len(b)==200 and b[:120]==t[:120] and b[152:]==t[152:] and b[120:152]==hashlib.sha256(der).digest();p=packet(b,owner.sign(b));owner.public_key().verify(p[200:],p[:200]);checks=2
for offset in [0,8,12,16,48,56,88,120]:
 bad=bytearray(t);bad[offset]^=1
 try:body(bytes(bad),target,66,codeset,dell,der)
 except ValueError:checks+=1
 else:raise AssertionError(offset)
for bad in [t[:-1],t+b'x',t[:152]+bytes(32)+t[184:],t[:184]+struct.pack('<QQ',0,1),t[:184]+struct.pack('<QQ',10,10),t[:184]+struct.pack('<QQ',10,60000011)]:
 try:body(bad,target,66,codeset,dell,der)
 except ValueError:checks+=1
 else:raise AssertionError('bad bounds')
for badder in [der+b'x',b'',der[:20],der*2]:
 try:body(t,target,66,codeset,dell,badder)
 except ValueError:checks+=1
 else:raise AssertionError('bad der')
for offset in [16,48,56,88,120,152,184,192,200,263]:
 bad=bytearray(p);bad[offset]^=1
 try:owner.public_key().verify(bytes(bad[200:]),bytes(bad[:200]))
 except Exception:checks+=1
 else:raise AssertionError('bad signature')
print('MAC-PUBLIC-PAIR-AUTH',checks,'canonical binding/DER/genuine fixture signature negatives; physical=0')
