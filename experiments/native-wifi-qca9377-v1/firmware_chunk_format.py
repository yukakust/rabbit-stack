"""Owner-signed RAM assets. No chip writes or compatibility inference.

The eventual owner route must check the exact physical BMI identity and reviewed
firmware hashes before supplying a private signing object to this pure encoder.
"""
import hashlib,struct
CHUNK=65536
MAX=32*CHUNK
def packets(data,private,*,target,generation,target_type,target_version,kind):
    if not 0<len(data)<=MAX or len(target)!=32 or not any(target):
        raise ValueError('bounded asset and reviewed target required')
    if kind not in (1,2) or not 0<generation<2**64 or not 0<target_type<2**32-1 or not 0<target_version<2**32-1:
        raise ValueError('reviewed generation, kind and physical BMI identity required')
    whole=hashlib.sha256(data).digest()
    result=[]
    for offset in range(0,len(data),CHUNK):
        body=data[offset:offset+CHUNK]
        header=(b'RABFW001'+target+whole+hashlib.sha256(body).digest()
                +struct.pack('<IIIIQIII',len(data),offset,len(body),CHUNK,generation,target_type,target_version,kind)+bytes(20))
        assert len(header)==160
        packet=header+private.sign(header)+body
        assert len(packet)<=65760
        result.append(packet)
    return result
