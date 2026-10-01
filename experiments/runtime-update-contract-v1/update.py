"""Signed runtime-update envelope and NON-EXECUTING supervisor reference model.

Not a Dell updater. Native execution, watchdog recovery and BLE I/O are not
implemented here. This model cannot certify that signed machine code is safe.
"""
from dataclasses import dataclass
from hashlib import sha256
import struct

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

MAX_BYTES = 262144
HEADER = struct.Struct("<4sHHIIIIQ32s32s32s32s32s")
SIGNATURE_BYTES = 64
DOMAIN = b"Rabbit trusted runtime update v1\0"
WORLD_DEVELOPMENT_PUBLIC = Ed25519PrivateKey.from_private_bytes(bytes(range(32))).public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)


class UpdateError(ValueError):
    pass


def digest(data):
    return sha256(data).digest()


def _hash(value):
    if type(value) is not bytes or len(value) != 32:
        raise UpdateError("identity must be an exact 32-byte SHA-256")
    return value


def _uint(value, maximum):
    if type(value) is not int or not 1 <= value <= maximum:
        raise UpdateError("counter/ABI must be a positive bounded integer")
    return value


@dataclass(frozen=True)
class Policy:
    target: bytes
    owner_public: bytes
    supervisor_abi: int = 1
    state_abi: int = 1

    def __post_init__(self):
        _hash(self.target)
        _hash(self.owner_public)
        _uint(self.supervisor_abi, 0xffffffff)
        _uint(self.state_abi, 0xffffffff)
        if self.owner_public == WORLD_DEVELOPMENT_PUBLIC:
            raise UpdateError("the public development world key cannot authorize native runtime updates")


@dataclass(frozen=True)
class Candidate:
    identity: bytes
    payload: bytes
    counter: int
    base_runtime: bytes
    state_identity: bytes


def pack(payload, *, private, target, base_runtime, state, counter,
         supervisor_abi=1, state_abi=1):
    """Serialize reviewed opaque runtime bytes; do not execute or certify them."""
    if type(payload) is not bytes or not payload or len(payload) + HEADER.size + SIGNATURE_BYTES > MAX_BYTES:
        raise UpdateError("runtime payload exceeds the bounded RAM envelope")
    if type(state) is not bytes:
        raise UpdateError("state snapshot must be immutable bytes")
    public = private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    policy = Policy(target, public, supervisor_abi, state_abi)
    body = HEADER.pack(b"RRT1", 1, 1, HEADER.size + len(payload) + 64,
                       len(payload), policy.supervisor_abi, policy.state_abi,
                       _uint(counter, 0xffffffffffffffff), policy.target,
                       _hash(base_runtime), digest(payload), digest(state), public) + payload
    return body + private.sign(DOMAIN + body)


def verify(data, policy, *, base_runtime, state, minimum_counter):
    if type(data) is not bytes or not HEADER.size + 65 <= len(data) <= MAX_BYTES:
        raise UpdateError("truncated or oversized runtime envelope")
    if type(state) is not bytes or type(minimum_counter) is not int or not 0 <= minimum_counter <= 0xffffffffffffffff:
        raise UpdateError("invalid trusted state/counter")
    (magic, version, flags, total, length, abi, state_abi, counter,
     target, base, payload_hash, state_hash, public) = HEADER.unpack_from(data)
    if (magic, version, flags, total, length) != (b"RRT1", 1, 1, len(data), len(data)-HEADER.size-64):
        raise UpdateError("noncanonical runtime envelope")
    if (abi, state_abi, target, public) != (policy.supervisor_abi, policy.state_abi, policy.target, policy.owner_public):
        raise UpdateError("wrong target, owner or unsupported supervisor/state ABI")
    if not counter or counter <= minimum_counter:
        raise UpdateError("stale in-boot runtime counter")
    if base != _hash(base_runtime) or state_hash != digest(state):
        raise UpdateError("runtime base/state snapshot differs; migration is unsupported")
    payload = data[HEADER.size:-64]
    if digest(payload) != payload_hash:
        raise UpdateError("runtime SHA-256 mismatch")
    try:
        Ed25519PublicKey.from_public_bytes(policy.owner_public).verify(data[-64:], DOMAIN + data[:-64])
    except InvalidSignature as error:
        raise UpdateError("invalid owner runtime signature") from error
    return Candidate(digest(data), payload, counter, base, state_hash)


@dataclass(frozen=True)
class Receipt:
    update_identity: bytes
    runtime_identity: bytes
    status: str
    counter: int
    authenticated: bool = False


class SupervisorModel:
    """Only model transitions; health must come from a future trusted backend.

    Keeping old bytes is NOT crash isolation. No candidate code runs in this model.
    Receipt correlation is not Dell attestation. All state is intentionally volatile.
    """
    def __init__(self, policy, fallback_runtime, state):
        if type(fallback_runtime) is not bytes or not fallback_runtime or type(state) is not bytes:
            raise UpdateError("invalid fallback/state")
        self.policy = policy
        self.fallback = fallback_runtime
        self.fallback_state = state
        self.active = fallback_runtime
        self.state = state
        self.minimum_counter = 0
        self.pending = None
        self.receipt = None

    def stage(self, data, *, reviewed_payload_sha256):
        if self.pending is not None:
            raise UpdateError("one trial at a time")
        # Exact completed retry repeats the receipt, never a trial or activation.
        if self.receipt is not None and digest(data) == self.receipt.update_identity:
            return self.receipt
        candidate = verify(data, self.policy, base_runtime=digest(self.active),
                           state=self.state, minimum_counter=self.minimum_counter)
        if digest(candidate.payload) != _hash(reviewed_payload_sha256):
            raise UpdateError("native payload lacks an exact separately reviewed identity")
        self.pending = candidate
        # Failed authorized trials consume their counter too, preventing auto retry.
        self.minimum_counter = candidate.counter
        return candidate

    def resolve(self, *, candidate_identity, healthy):
        if self.pending is None or candidate_identity != self.pending.identity or type(healthy) is not bool:
            raise UpdateError("missing, mismatched or malformed trusted health result")
        candidate = self.pending
        if healthy:
            self.active = candidate.payload
        self.receipt = Receipt(candidate.identity, digest(self.active),
                               "COMMITTED" if healthy else "RETAINED-OLD", candidate.counter)
        self.pending = None
        return self.receipt

    def reboot(self):
        # Represents owner reset/power cycle, not automatic watchdog recovery.
        self.active = self.fallback
        self.pending = None
        self.minimum_counter = 0
        self.receipt = None
        self.state = self.fallback_state  # Only the immutable bootstrap survives.
