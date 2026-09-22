#!/usr/bin/env python3
"""Compile a semantic Rabbit world into a target-independent binary package."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
WORLD_PATH = ROOT.parent / "x86-64-uefi-jump-stone-v0" / "world.json"
INTERPRETATION_PATH = ROOT / "interpretation.json"
MAGIC = b"RBTW"
VERSION = 1
HEADER = struct.Struct("<4sHHII32s")
MAX_MANIFEST_SIZE = 64 * 1024
MAX_CODE_SIZE = 4 * 1024


class PackageError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PackageError(f"duplicate JSON field: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
    except (OSError, json.JSONDecodeError) as error:
        raise PackageError(f"could not load {path}: {error}") from error
    if not isinstance(result, dict):
        raise PackageError(f"{path.name} must contain an object")
    return result


EXPECTED_WORLD = load_json(WORLD_PATH)
EXPECTED_INTERPRETATION = load_json(INTERPRETATION_PATH)


def validate(world: dict[str, Any], interpretation: dict[str, Any]) -> None:
    if world != EXPECTED_WORLD:
        raise PackageError("world differs from the owner-observed semantic revision")
    if interpretation != EXPECTED_INTERPRETATION:
        raise PackageError("interpretation differs from the reviewed intent decisions")
    encoded = canonical_bytes(world)
    forbidden = (b"uefi", b"x86", b"qemu", b"framebuffer", b"firmware", b"usb")
    if any(word in encoded.lower() for word in forbidden):
        raise PackageError("portable world contains target-specific vocabulary")


def compile_bytecode(world: dict[str, Any]) -> bytes:
    player = world["player"]
    actions = world["actions"]
    stone = world["stone"]
    code = bytearray()
    code += b"\x01" + struct.pack("<HHBB3B", player["x"], player["y"], player["size"], player["movement_step"], 255, 212, 0)
    code += b"\x02" + struct.pack("<BB3B", actions["z"]["stone_size"], stone["maximum_count"], 255, 212, 0)
    code += b"\x10" + struct.pack("<B", player["movement_step"])
    code += b"\x11" + struct.pack("<BBI", 32, actions["space"]["height"], actions["space"]["hold_microseconds"])
    code += b"\x12" + struct.pack("<BBB", 90, 122, 1)
    code += b"\x20\x21"
    code += b"\xfe" + struct.pack("<BB", 23, world["contract"]["exit_status"])
    code += b"\xff"
    return bytes(code)


def build_package(world: dict[str, Any], interpretation: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    validate(world, interpretation)
    world_identity = sha256(canonical_bytes(world))
    interpretation_identity = sha256(canonical_bytes(interpretation))
    manifest_value = {
        "schema_version": 1,
        "world": world,
        "interpretation_sha256": interpretation_identity,
    }
    manifest = canonical_bytes(manifest_value)
    bytecode = compile_bytecode(world)
    identity = hashlib.sha256(manifest).digest()
    header = HEADER.pack(MAGIC, VERSION, 0, len(manifest), len(bytecode), identity)
    package = header + manifest + bytecode
    report = {
        "schema_version": 1,
        "status": "PACKAGE-BUILT-NOT-DEPLOYED",
        "world_sha256": world_identity,
        "interpretation_sha256": interpretation_identity,
        "manifest_sha256": identity.hex(),
        "bytecode_sha256": sha256(bytecode),
        "package_sha256": sha256(package),
        "package_size_bytes": len(package),
        "target_specific_fields": [],
        "deployments_performed": [],
    }
    return package, report


def decode_package(package: bytes) -> tuple[dict[str, Any], bytes]:
    if len(package) < HEADER.size:
        raise PackageError("package is truncated")
    magic, version, flags, manifest_size, code_size, identity = HEADER.unpack_from(package)
    if magic != MAGIC or version != VERSION or flags != 0:
        raise PackageError("package header is unsupported")
    if not 0 < manifest_size <= MAX_MANIFEST_SIZE or not 0 < code_size <= MAX_CODE_SIZE:
        raise PackageError("package payload sizes are outside reviewed limits")
    if len(package) != HEADER.size + manifest_size + code_size:
        raise PackageError("package lengths do not match payload")
    manifest_bytes = package[HEADER.size:HEADER.size + manifest_size]
    if hashlib.sha256(manifest_bytes).digest() != identity:
        raise PackageError("manifest identity mismatch")
    try:
        manifest = json.loads(manifest_bytes.decode("ascii"), object_pairs_hook=unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PackageError(f"manifest is invalid: {error}") from error
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema_version", "world", "interpretation_sha256"
    }:
        raise PackageError("manifest fields differ from the reviewed package schema")
    if manifest["schema_version"] != 1:
        raise PackageError("manifest schema version is unsupported")
    world = manifest["world"]
    if not isinstance(world, dict):
        raise PackageError("manifest world must be an object")
    expected_interpretation = sha256(canonical_bytes(EXPECTED_INTERPRETATION))
    if manifest["interpretation_sha256"] != expected_interpretation:
        raise PackageError("interpretation identity is not approved")
    validate(world, EXPECTED_INTERPRETATION)
    bytecode = package[HEADER.size + manifest_size:]
    if bytecode != compile_bytecode(world):
        raise PackageError("bytecode does not match semantic manifest")
    return world, bytecode
