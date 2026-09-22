#!/usr/bin/env python3
"""Build and model the reviewed jump-and-stone UEFI world."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
WORLD_PATH = ROOT / "world.json"
TARGET_PATH = ROOT / "target.json"
PROGRAM_PATH = ROOT / "program.hex"
MEDIA_BUILDER_PATH = ROOT.parent / "x86-64-uefi-v0" / "build_image.py"
PROGRAM_SHA256 = "4c22fa9be1fd0a6495b909ac35765914cea95bc4d91dafd4f17144ecedf53331"


def _load_media_builder():
    spec = importlib.util.spec_from_file_location("rabbit_uefi_media_jump_stone", MEDIA_BUILDER_PATH)
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
        raise BuildError(f"{path.name} must contain an object")
    return value


EXPECTED_WORLD = load_json(WORLD_PATH)
EXPECTED_TARGET = load_json(TARGET_PATH)


def validate_world(world: dict[str, Any]) -> None:
    if world != EXPECTED_WORLD:
        raise BuildError("world differs from the reviewed jump-and-stone contract")


def validate_target(target: dict[str, Any]) -> None:
    if target != EXPECTED_TARGET:
        raise BuildError("target differs from the reviewed jump-and-stone Target Pack")


def load_program() -> bytes:
    try:
        code = bytes.fromhex(PROGRAM_PATH.read_text(encoding="ascii"))
    except (OSError, ValueError) as error:
        raise BuildError(f"could not decode reviewed program bytes: {error}") from error
    if len(code) != 1064 or sha256(code) != PROGRAM_SHA256:
        raise BuildError("reviewed jump-and-stone machine bytes changed")
    return code


def build_efi(code: bytes) -> bytes:
    raw_size = (len(code) + SECTOR_SIZE - 1) // SECTOR_SIZE * SECTOR_SIZE
    if raw_size != 0x600:
        raise BuildError("unexpected jump-and-stone code size")
    dos = bytearray(0x80)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x80)
    coff = struct.pack("<HHIIIHH", 0x8664, 2, 0, 0, 0, 0xF0, 0x0022)
    optional = bytearray()
    optional += struct.pack("<HBBIIIII", 0x20B, 1, 0, raw_size, 0x200, 0, 0x1000, 0x1000)
    optional += struct.pack("<QII", 0, 0x1000, 0x200)
    optional += struct.pack("<HHHHHH", 0, 0, 0, 0, 2, 0)
    optional += struct.pack("<IIII", 0, 0x3000, 0x200, 0)
    optional += struct.pack("<HH", 10, 0x0100)
    optional += struct.pack("<QQQQII", 0x100000, 0x1000, 0x100000, 0x1000, 0, 16)
    directories = [(0, 0)] * 16
    directories[5] = (0x2000, 8)
    optional += b"".join(struct.pack("<II", *entry) for entry in directories)
    text = struct.pack(
        "<8sIIIIIIHHI", b".text\0\0\0", len(code), 0x1000, raw_size, 0x200,
        0, 0, 0, 0, 0x60000020,
    )
    reloc = struct.pack(
        "<8sIIIIIIHHI", b".reloc\0\0", 8, 0x2000, 0x200, 0x200 + raw_size,
        0, 0, 0, 0, 0x42000040,
    )
    headers = (bytes(dos) + b"PE\0\0" + coff + bytes(optional) + text + reloc).ljust(0x200, b"\0")
    return headers + code.ljust(raw_size, b"\0") + struct.pack("<II", 0x1000, 8).ljust(0x200, b"\0")


def build(world: dict[str, Any], target: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    validate_world(world)
    validate_target(target)
    code = load_program()
    efi = build_efi(code)
    image = media.build_image(efi)
    report = {
        "schema_version": 1,
        "status": "BUILT-NOT-INSTALLED",
        "world_sha256": sha256(canonical_bytes(world)),
        "target_sha256": sha256(canonical_bytes(target)),
        "program_sha256": sha256(code),
        "efi_sha256": sha256(efi),
        "image_sha256": sha256(image),
        "image_size_bytes": len(image),
        "boot_path": "EFI/BOOT/BOOTX64.EFI",
        "physical_execution_verified": False,
        "writes_performed": [],
    }
    return image, report


@dataclass(frozen=True)
class State:
    x: int = 100
    y: int = 100
    direction: str = "right"
    stone: tuple[int, int] | None = None


def overlaps_stone(x: int, y: int, stone: tuple[int, int] | None) -> bool:
    if stone is None:
        return False
    sx, sy = stone
    return x + 64 > sx and sx + 16 > x and y + 64 > sy and sy + 16 > y


def move(state: State, direction: str, screen: tuple[int, int] = (640, 480)) -> State:
    dx, dy = {"up": (0, -16), "down": (0, 16), "right": (16, 0), "left": (-16, 0)}[direction]
    x = min(max(0, state.x + dx), screen[0] - 64)
    y = min(max(0, state.y + dy), screen[1] - 64)
    if overlaps_stone(x, y, state.stone):
        x, y = state.x, state.y
    return State(x, y, direction, state.stone)


def leave_stone(state: State, screen: tuple[int, int] = (640, 480)) -> State:
    moved = move(State(state.x, state.y, state.direction, None), state.direction, screen)
    if (moved.x, moved.y) == (state.x, state.y):
        return state
    if state.direction == "right":
        stone = (state.x, state.y + 24)
    elif state.direction == "left":
        stone = (state.x + 48, state.y + 24)
    elif state.direction == "up":
        stone = (state.x + 24, state.y + 48)
    else:
        stone = (state.x + 24, state.y)
    return State(moved.x, moved.y, state.direction, stone)
