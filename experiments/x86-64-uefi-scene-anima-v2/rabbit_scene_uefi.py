#!/usr/bin/env python3
"""Lower the exact Scene/Anima v2 reference trace to a bounded Dell UEFI player."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
TARGET_PATH = ROOT / "target.json"
PROGRAM_PATH = ROOT / "program.hex"
REFERENCE_ROOT = ROOT.parent / "scene-anima-v2-runner"
MEDIA_BUILDER_PATH = ROOT.parent / "x86-64-uefi-v0" / "build_image.py"
PROGRAM_SIZE = 2093
PROGRAM_SHA256 = "1f33053936965726b66c92bf18fe929f6ea0244fbbf812faa6f51a3daecd40fe"
GOP_GUID = bytes.fromhex("de a9 42 90 dc 23 38 4a 96 fb 7a de d0 80 51 6a")


def _load_media_builder():
    spec = importlib.util.spec_from_file_location("rabbit_uefi_media_scene_v2", MEDIA_BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load reviewed UEFI media builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


media = _load_media_builder()
IMAGE_SIZE = media.IMAGE_SIZE
PARTITION_LBA = media.PARTITION_LBA
SECTOR_SIZE = media.SECTOR_SIZE


class BuildError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BuildError(f"duplicate JSON field: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"could not load {path}: {error}") from error
    if not isinstance(value, dict):
        raise BuildError(f"{path.name} must contain one object")
    return value


EXPECTED_TARGET = load_json(TARGET_PATH)


def reference_execution() -> dict[str, Any]:
    reference = str(REFERENCE_ROOT)
    if reference not in sys.path:
        sys.path.insert(0, reference)
    from rabbit_scene import execute  # type: ignore

    return execute(240)


def trace_bytes(result: dict[str, Any]) -> bytes:
    encoded = bytearray()
    for state in result["trace"]:
        values = (
            state["cat"]["x"], state["cat"]["y"],
            state["ball"]["x"], state["ball"]["y"], state["cat_frame"],
        )
        if any(isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 255 for value in values):
            raise BuildError("reference trace cannot be represented by the bounded player")
        encoded.extend(values)
    if len(encoded) != 241 * 5:
        raise BuildError("reference trace length differs from the reviewed lowering")
    return bytes(encoded)


def sprite_indices(result: dict[str, Any], component_id: str, frame: int) -> bytes:
    implementation = result["components"][component_id]["implementation"]
    symbol_map = {".": 0, "O": 1, "K": 2, "W": 3, "B": 4}
    try:
        encoded = bytes(symbol_map[symbol] for row in implementation["frames"][frame] for symbol in row)
    except (KeyError, IndexError, TypeError) as error:
        raise BuildError("sprite cannot be represented by the reviewed Dell palette") from error
    if len(encoded) != 64:
        raise BuildError("sprite dimensions differ from eight-by-eight")
    return encoded


def validate_target(target: dict[str, Any], result: dict[str, Any]) -> None:
    if target != EXPECTED_TARGET:
        raise BuildError("target differs from the reviewed Dell Scene/Anima v2 Target Pack")
    accepted = target["accepted_creation"]
    if accepted != {
        "creation_id": result["contract"]["accepted_creation_id"],
        "creation_sha256": result["contract"]["accepted_creation_sha256"],
        "runner_contract_sha256": sha256(canonical_bytes(result["contract"])),
        "trace_sha256": result["trace_sha256"],
    }:
        raise BuildError("Target Pack is stale for the exact Creation and runner")


def load_program(result: dict[str, Any]) -> bytes:
    try:
        program = bytes.fromhex(PROGRAM_PATH.read_text(encoding="ascii"))
    except (OSError, ValueError) as error:
        raise BuildError(f"could not decode reviewed physical program: {error}") from error
    validate_program(program, result)
    return program


def validate_program(program: bytes, result: dict[str, Any]) -> None:
    if len(program) != PROGRAM_SIZE or sha256(program) != PROGRAM_SHA256:
        raise BuildError("reviewed physical machine bytes changed")
    expected_trace = trace_bytes(result)
    if not program.endswith(expected_trace) or program.count(expected_trace) != 1:
        raise BuildError("physical program is not bound to the exact canonical trace")
    assets = (
        sprite_indices(result, "rabbit.asset.cat-pixel", 0),
        sprite_indices(result, "rabbit.asset.cat-pixel", 1),
        sprite_indices(result, "rabbit.asset.ball-pixel", 0),
    )
    if any(program.count(asset) != 1 for asset in assets):
        raise BuildError("physical program is not bound to the exact catalog sprites")
    if program.count(GOP_GUID) != 1:
        raise BuildError("physical program GOP binding changed")


def align(value: int, boundary: int) -> int:
    return (value + boundary - 1) // boundary * boundary


def build_efi(program: bytes) -> bytes:
    raw_size = align(len(program), SECTOR_SIZE)
    reloc_rva = 0x1000 + align(len(program), 0x1000)
    dos = bytearray(0x80)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x80)
    coff = struct.pack("<HHIIIHH", 0x8664, 2, 0, 0, 0, 0xF0, 0x0022)
    optional = bytearray()
    optional += struct.pack("<HBBIIIII", 0x20B, 1, 0, raw_size, 0x200, 0, 0x1000, 0x1000)
    optional += struct.pack("<QII", 0, 0x1000, 0x200)
    optional += struct.pack("<HHHHHH", 0, 0, 0, 0, 2, 0)
    optional += struct.pack("<IIII", 0, reloc_rva + 0x1000, 0x200, 0)
    optional += struct.pack("<HH", 10, 0x0100)
    optional += struct.pack("<QQQQII", 0x100000, 0x1000, 0x100000, 0x1000, 0, 16)
    directories = [(0, 0)] * 16
    directories[5] = (reloc_rva, 8)
    optional += b"".join(struct.pack("<II", *entry) for entry in directories)
    text = struct.pack(
        "<8sIIIIIIHHI", b".text\0\0\0", len(program), 0x1000, raw_size, 0x200,
        0, 0, 0, 0, 0x60000020,
    )
    reloc = struct.pack(
        "<8sIIIIIIHHI", b".reloc\0\0", 8, reloc_rva, 0x200, 0x200 + raw_size,
        0, 0, 0, 0, 0x42000040,
    )
    headers = (bytes(dos) + b"PE\0\0" + coff + bytes(optional) + text + reloc).ljust(0x200, b"\0")
    return headers + program.ljust(raw_size, b"\0") + struct.pack("<II", reloc_rva, 8).ljust(0x200, b"\0")


def build(target: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    result = reference_execution()
    validate_target(target, result)
    program = load_program(result)
    efi = build_efi(program)
    image = media.build_image(efi)
    report = {
        "schema_version": 1,
        "status": "PHYSICAL-CANDIDATE-BUILT-NOT-INSTALLED",
        "creation_sha256": result["contract"]["accepted_creation_sha256"],
        "runner_contract_sha256": sha256(canonical_bytes(result["contract"])),
        "trace_sha256": result["trace_sha256"],
        "target_sha256": sha256(canonical_bytes(target)),
        "program_sha256": sha256(program),
        "efi_sha256": sha256(efi),
        "image_sha256": sha256(image),
        "image_size_bytes": len(image),
        "boot_path": "EFI/BOOT/BOOTX64.EFI",
        "expected_observation": "looping pixel cat chases and bats one bouncing blue ball; Escape exits",
        "physical_execution_verified": False,
        "writes_performed": [],
    }
    return image, report
