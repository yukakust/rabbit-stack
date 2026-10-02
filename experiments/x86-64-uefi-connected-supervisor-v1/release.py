"""RRT3: owner-authenticated combined Scene/radio ABI3, local RSS2 live state."""
import sys
from pathlib import Path
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime-update-contract-v1'))
from update import HEADER,MAX_BYTES,Policy,UpdateError,Candidate,digest,_hash,_uint
DOMAIN=b'Rabbit trusted runtime update v3\0'
def pack(payload,*,private,target,base_runtime,world,counter):
    if type(payload) is not bytes or not payload or len(payload)+256>MAX_BYTES or type(world) is not bytes:
        raise UpdateError('invalid bounded payload/world')
    public=private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    policy=Policy(target,public,3,2)
    # Receipt counter uses uint32 on this connected protocol; no truncation.
    c=_uint(counter,0xffffffff)
    if not c:raise UpdateError('positive native counter required')
    body=HEADER.pack(b'RRT3',3,1,len(payload)+256,len(payload),3,2,c,
        policy.target,_hash(base_runtime),digest(payload),digest(world),public)+payload
    return body+private.sign(DOMAIN+body)
def verify(data,*,target,owner,base_runtime,world,counter):
    policy=Policy(target,owner,3,2)
    if type(data) is not bytes or not 257<=len(data)<=MAX_BYTES:raise UpdateError('invalid envelope size')
    fields=HEADER.unpack_from(data)
    if fields[:7]!=(b'RRT3',3,1,len(data),len(data)-256,3,2):raise UpdateError('wrong ABI/domain profile')
    if not counter<fields[7]<=0xffffffff or fields[8]!=policy.target or fields[9]!=_hash(base_runtime) or fields[11]!=digest(world) or fields[12]!=policy.owner_public:
        raise UpdateError('wrong target/base/world/owner/counter')
    payload=data[192:-64]
    if fields[10]!=digest(payload):raise UpdateError('payload hash mismatch')
    try:Ed25519PublicKey.from_public_bytes(owner).verify(data[-64:],DOMAIN+data[:-64])
    except InvalidSignature as e:raise UpdateError('owner signature rejected') from e
    return Candidate(digest(data),payload,fields[7],fields[9],fields[11])
