"""RRT2: native Scene ABI 2, signed immutable world revision, local live snapshot.

Deliberately distinct from RRT1's externally signed full mutable-state snapshot.
This signature is owner release authorization, not code isolation or attestation.
"""
from pathlib import Path
import sys
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
CONTRACT = Path(__file__).resolve().parents[1] / 'runtime-update-contract-v1'
sys.path.insert(0, str(CONTRACT))
from update import HEADER, MAX_BYTES, Policy, Candidate, UpdateError, digest, _hash, _uint
DOMAIN = b'Rabbit trusted runtime update v2\0'

def pack(payload, *, private, target, base_runtime, world, counter):
    if type(payload) is not bytes or not payload or len(payload)+256 > MAX_BYTES or type(world) is not bytes:
        raise UpdateError('invalid bounded native payload/world')
    public = private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    policy = Policy(target, public, 2, 2)
    body = HEADER.pack(b'RRT2', 2, 1, len(payload)+256, len(payload), 2, 2,
                       _uint(counter, 0xffffffffffffffff), policy.target,
                       _hash(base_runtime), digest(payload), digest(world), public) + payload
    return body + private.sign(DOMAIN+body)

def verify(data, *, target, owner, base_runtime, world, counter):
    policy = Policy(target, owner, 2, 2)
    if type(data) is not bytes or not 257 <= len(data) <= MAX_BYTES:
        raise UpdateError('invalid envelope size')
    if type(world) is not bytes or type(counter) is not int or not 0 <= counter <= 0xffffffffffffffff:
        raise UpdateError('invalid world/counter policy')
    fields = HEADER.unpack_from(data)
    if fields[:7] != (b'RRT2', 2, 1, len(data), len(data)-256, 2, 2):
        raise UpdateError('unsupported RRT2 Scene profile')
    if fields[7] <= counter or fields[8] != policy.target or fields[9] != _hash(base_runtime) or fields[11] != digest(world) or fields[12] != policy.owner_public:
        raise UpdateError('wrong target/base/world/owner or stale runtime counter')
    payload = data[192:-64]
    if fields[10] != digest(payload): raise UpdateError('payload SHA mismatch')
    try: Ed25519PublicKey.from_public_bytes(owner).verify(data[-64:], DOMAIN+data[:-64])
    except InvalidSignature as error: raise UpdateError('owner signature rejected') from error
    return Candidate(digest(data), payload, fields[7], fields[9], fields[11])
