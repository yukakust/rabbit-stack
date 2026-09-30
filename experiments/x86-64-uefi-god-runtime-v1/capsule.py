#!/usr/bin/env python3
"""Compile and inspect the fixed-width Rabbit God Runtime capsule."""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


MAGIC = b"RGC1"
VERSION = 1
BODY_SIZE = 128
SIGNATURE_SIZE = 64
CAPSULE_SIZE = BODY_SIZE + SIGNATURE_SIZE
CAT_CREATION_SHA256 = "c6e1def6497769bbaa3917a8dacba099b01676af459358d7e6551fb6fa82eab8"
COMPONENT_SET_SHA256 = "4d82c213d799bad7122574bd7f1373b25b00bd3b2f5a603fcc89afbe6ef8d5bf"
TOON_CREATION_SHA256 = "52c76a8592f5929e31af97e020325afa53f93a63c94bce06a1ba6159b6875609"
TOON_COMPONENT_SET_SHA256 = "b14c75fce56d318512a6ef0f8db416829bdfa4a76a82b86f5feac8b4e70b224f"
SCENES = {"cat-ball": 0, "toon-cat-mouse": 1}


class CapsuleError(ValueError):
    pass


@dataclass(frozen=True)
class SceneConfig:
    counter: int
    inventory_package_sha256: str
    cat_x: int = 12
    cat_y: int = 58
    ball_x: int = 116
    ball_y: int = 34
    ball_vx: int = 2
    ball_vy: int = 1
    health_fault: bool = False
    scene: str = "cat-ball"


def _digest(value: str, label: str) -> bytes:
    try:
        result = bytes.fromhex(value)
    except ValueError as error:
        raise CapsuleError(f"{label} must be lowercase SHA-256") from error
    if len(result) != 32 or value != value.lower():
        raise CapsuleError(f"{label} must be lowercase SHA-256")
    return result


def body(config: SceneConfig) -> bytes:
    if isinstance(config.counter, bool) or not 1 <= config.counter <= 0xFFFFFFFF:
        raise CapsuleError("counter must fit nonzero uint32")
    coordinates = (config.cat_x, config.cat_y, config.ball_x, config.ball_y)
    if any(isinstance(value, bool) or not 0 <= value <= 152 for value in coordinates):
        raise CapsuleError("scene coordinates exceed the reviewed 160x90 surface")
    if any(isinstance(value, bool) or not -3 <= value <= 3 or value == 0 for value in (config.ball_vx, config.ball_vy)):
        raise CapsuleError("moving target velocity must be nonzero and between -3 and 3")
    if config.scene not in SCENES:
        raise CapsuleError("scene is not trusted by this Runtime")
    scene_kind = SCENES[config.scene]
    creation = CAT_CREATION_SHA256 if scene_kind == 0 else TOON_CREATION_SHA256
    components = COMPONENT_SET_SHA256 if scene_kind == 0 else TOON_COMPONENT_SET_SHA256
    value = bytearray(BODY_SIZE)
    value[0:4] = MAGIC
    value[4:8] = bytes((VERSION, 1, 30, (scene_kind << 1) | int(config.health_fault)))
    struct.pack_into("<I", value, 8, config.counter)
    value[12:44] = _digest(config.inventory_package_sha256, "Inventory package digest")
    value[44:76] = bytes.fromhex(creation)
    value[76:84] = bytes((*coordinates, config.ball_vx & 0xFF, config.ball_vy & 0xFF, 3, 2))
    struct.pack_into("<HHHH", value, 84, 2, 160, 90, 600)
    value[92:124] = bytes.fromhex(components)
    struct.pack_into("<I", value, 124, 3)  # display.draw | time.read
    return bytes(value)


def encode(config: SceneConfig, private_key: Ed25519PrivateKey) -> bytes:
    payload = body(config)
    encoded = payload + private_key.sign(payload)
    if len(encoded) != CAPSULE_SIZE:
        raise AssertionError("capsule size changed")
    return encoded


def decode(encoded: bytes, public_key: bytes, last_counter: int = 0) -> dict[str, object]:
    if len(encoded) != CAPSULE_SIZE:
        raise CapsuleError("capsule length differs from 192 bytes")
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(encoded[BODY_SIZE:], encoded[:BODY_SIZE])
    except Exception as error:
        raise CapsuleError("capsule signature is invalid") from error
    payload = encoded[:BODY_SIZE]
    if payload[:4] != MAGIC or payload[4:7] != bytes((VERSION, 1, 30)):
        raise CapsuleError("capsule identity is unsupported")
    counter = struct.unpack_from("<I", payload, 8)[0]
    if counter <= last_counter:
        raise CapsuleError("capsule counter is stale")
    flags = payload[7]
    if flags & 0xFC:
        raise CapsuleError("capsule scene flags are unsupported")
    scene_kind = flags >> 1
    creation = CAT_CREATION_SHA256 if scene_kind == 0 else TOON_CREATION_SHA256
    components = COMPONENT_SET_SHA256 if scene_kind == 0 else TOON_COMPONENT_SET_SHA256
    if payload[44:76].hex() != creation:
        raise CapsuleError("capsule Creation is not trusted")
    if payload[83] != 2 or struct.unpack_from("<HHHH", payload, 84) != (2, 160, 90, 600):
        raise CapsuleError("capsule budgets differ from Scene/Anima v2")
    if payload[92:124].hex() != components or struct.unpack_from("<I", payload, 124)[0] != 3:
        raise CapsuleError("capsule components or authority differ from the reviewed world")
    return {
        "counter": counter,
        "inventory_package_sha256": payload[12:44].hex(),
        "creation_sha256": payload[44:76].hex(),
        "scene": "cat-ball" if scene_kind == 0 else "toon-cat-mouse",
        "cat": [payload[76], payload[77]],
        "target": [payload[78], payload[79]],
        "target_velocity": [struct.unpack("b", payload[80:81])[0], struct.unpack("b", payload[81:82])[0]],
        "health_fault": bool(flags & 1),
        "capsule_sha256": hashlib.sha256(encoded).hexdigest(),
    }


class TransactionModel:
    """Target-independent mirror of the UEFI active/provisional/rollback state."""

    def __init__(self, public_key: bytes):
        self.public_key = public_key
        self.last_counter = 0
        self.active: dict[str, object] = {"world": "embedded-cat-bootstrap", "counter": 0}
        self.state = "active"

    def apply(self, encoded: bytes) -> dict[str, object]:
        candidate = decode(encoded, self.public_key, self.last_counter)
        previous = self.active
        self.state = "provisional"
        self.active = candidate
        if candidate["health_fault"]:
            self.active = previous
            self.state = "rolled-back"
            return {"status": "ROLLED-BACK", "active": self.active}
        self.last_counter = int(candidate["counter"])
        self.state = "committed"
        return {"status": "COMMITTED", "active": self.active}
