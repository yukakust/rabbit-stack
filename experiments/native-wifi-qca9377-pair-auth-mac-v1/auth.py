"""Public challenge builder ONLY: no signer, owner key, password or BLE.
Physical caller supplies actual parent target/epoch/sealed code set and full
Dell SPKI hash confirmed by the human. No approval Boolean is serialized.
"""
import hashlib,hmac,struct
from cryptography.hazmat.primitives import serialization

def _hash(value):return isinstance(value,bytes) and len(value)==32 and any(value)
def body(template,target,epoch,code_set,confirmed_dell_spki,own_der_spki):
    if not isinstance(template,bytes) or len(template)!=200 or template[:8]!=b'RABPAIR1' or struct.unpack_from('<II',template,8)!=(1,0):raise ValueError('challenge header')
    if not all(_hash(h) for h in [target,code_set,confirmed_dell_spki]) or not isinstance(epoch,int) or not 0<epoch<2**64:raise ValueError('trusted binding')
    if not hmac.compare_digest(template[16:48],target) or struct.unpack_from('<Q',template,48)[0]!=epoch or not hmac.compare_digest(template[56:88],code_set) or not hmac.compare_digest(template[88:120],confirmed_dell_spki):raise ValueError('challenge binding')
    if template[120:152]!=bytes(32) or not any(template[152:184]):raise ValueError('challenge nonce/placeholder')
    issued,expires=struct.unpack_from('<QQ',template,184)
    if not 0<issued<expires<2**64 or expires-issued>60000000:raise ValueError('challenge lifetime')
    if not isinstance(own_der_spki,bytes) or not 0<len(own_der_spki)<=128:raise ValueError('client SPKI bound')
    key=serialization.load_der_public_key(own_der_spki)
    from cryptography.hazmat.primitives.asymmetric import ec
    if not isinstance(key,ec.EllipticCurvePublicKey) or not isinstance(key.curve,ec.SECP256R1):raise ValueError('client P256')
    canonical=key.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
    if canonical!=own_der_spki:raise ValueError('canonical client SPKI')
    return template[:120]+hashlib.sha256(canonical).digest()+template[152:]

def packet(public_body,signature):
    if not isinstance(public_body,bytes) or len(public_body)!=200 or public_body[:8]!=b'RABPAIR1' or not any(public_body[120:152]) or not isinstance(signature,bytes) or len(signature)!=64:raise ValueError('signed packet bounds')
    # Actual owner's public-key verification is required by admitted Dell.
    return public_body+signature
