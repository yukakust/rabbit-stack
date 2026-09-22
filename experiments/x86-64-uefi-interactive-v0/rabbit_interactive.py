#!/usr/bin/env python3
"""Lower a movable rectangle world to reviewed x86-64 UEFI machine bytes."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
WORLD_PATH = ROOT / "world.json"
TARGET_PATH = ROOT / "target.json"
FRAMEBUFFER_BUILDER_PATH = ROOT.parent / "x86-64-uefi-framebuffer-v0" / "rabbit_framebuffer.py"


def _load_framebuffer_builder():
    spec = importlib.util.spec_from_file_location("rabbit_framebuffer_v0", FRAMEBUFFER_BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load reviewed framebuffer builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


framebuffer = _load_framebuffer_builder()
media = framebuffer.media
Code = framebuffer.Code
GOP_GUID = framebuffer.GOP_GUID
IMAGE_SIZE = framebuffer.IMAGE_SIZE
PARTITION_LBA = framebuffer.PARTITION_LBA
SECTOR_SIZE = framebuffer.SECTOR_SIZE


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


def validate_world(world: dict[str, Any]) -> dict[str, int]:
    if world != EXPECTED_WORLD:
        raise BuildError("world differs from the reviewed first-interactive-object contract")
    obj = world["objects"][0]
    return {
        "x": obj["x"],
        "y": obj["y"],
        "width": obj["width"],
        "height": obj["height"],
        "step": world["contract"]["movement_step_pixels"],
        "red": 0xFF,
        "green": 0x80,
        "blue": 0x00,
    }


def validate_target(target: dict[str, Any]) -> None:
    if target != EXPECTED_TARGET:
        raise BuildError("target differs from the reviewed x86-64 UEFI interactive contract")


def simulate_key(position: tuple[int, int], scan_code: int, screen: tuple[int, int]) -> tuple[int, int]:
    x, y = position
    width, height = screen
    step, size = 16, 128
    if scan_code == 1:
        y = max(0, y - step)
    elif scan_code == 2:
        y = min(height - size, y + step)
    elif scan_code == 3:
        x = min(width - size, x + step)
    elif scan_code == 4:
        x = max(0, x - step)
    return x, y


def machine_code(spec: dict[str, int]) -> bytes:
    if spec != validate_world(EXPECTED_WORLD):
        raise BuildError("interactive object differs from the reviewed world")
    rgb_word = spec["red"] | (spec["green"] << 8) | (spec["blue"] << 16)
    bgr_word = spec["blue"] | (spec["green"] << 8) | (spec["red"] << 16)
    code = Code()
    code.emit("53 56 57 41 54 41 55 41 56 41 57 48 83 ec 30")
    code.emit("48 8b 72 30 48 8b 5a 60")
    code.emit("48 8d 0d"); code.rel32("gop_guid")
    code.emit("31 d2 4c 8d 44 24 28 48 8b 83 40 01 00 00 ff d0")
    code.emit("48 85 c0 0f 85"); code.rel32("cleanup")
    code.emit("48 8b 44 24 28 48 8b 40 18")
    code.emit("48 8b 58 18")              # RBX = FrameBufferBase
    code.emit("48 8b 50 08")              # RDX = Mode->Info
    code.emit("44 8b 72 04 44 8b 7a 08")  # R14D/R15D = visible width/height
    code.emit("8b 7a 20")                 # EDI = PixelsPerScanLine
    code.emit("41 81 fe e4 00 00 00 0f 82"); code.rel32("unsupported")
    code.emit("41 81 ff e4 00 00 00 0f 82"); code.rel32("unsupported")
    code.emit("83 7a 0c 00 0f 84"); code.rel32("rgb")
    code.emit("83 7a 0c 01 0f 84"); code.rel32("bgr")
    code.emit("e9"); code.rel32("unsupported")
    code.label("rgb")
    code.emit("c7 44 24 20"); code.raw(struct.pack("<I", rgb_word)); code.emit("e9"); code.rel32("color_ready")
    code.label("bgr")
    code.emit("c7 44 24 20"); code.raw(struct.pack("<I", bgr_word))
    code.label("color_ready")
    code.emit("41 bc"); code.raw(struct.pack("<I", spec["x"]))
    code.emit("41 bd"); code.raw(struct.pack("<I", spec["y"]))
    code.emit("48 89 f8 49 0f af c7 48 89 d9 31 d2")
    code.label("clear_pixel")
    code.emit("89 11 48 83 c1 04 48 ff c8 0f 85"); code.rel32("clear_pixel")
    code.emit("8b 44 24 20 e8"); code.rel32("draw")
    code.label("read_key")
    code.emit("48 89 f1 48 8d 54 24 28 48 8b 41 08 ff d0 48 85 c0 0f 85")
    code.rel32("read_key")
    code.emit("0f b7 44 24 28 83 f8 17 0f 84"); code.rel32("success")
    code.emit("83 f8 01 0f 82"); code.rel32("read_key")
    code.emit("83 f8 04 0f 87"); code.rel32("read_key")
    code.emit("89 44 24 24 31 c0 e8"); code.rel32("draw")
    code.emit("8b 44 24 24 83 f8 01 0f 84"); code.rel32("move_up")
    code.emit("83 f8 02 0f 84"); code.rel32("move_down")
    code.emit("83 f8 03 0f 84"); code.rel32("move_right")
    code.emit("e9"); code.rel32("move_left")
    code.label("move_up")
    code.emit("41 83 fd 10 0f 82"); code.rel32("up_zero")
    code.emit("41 83 ed 10 e9"); code.rel32("redraw")
    code.label("up_zero")
    code.emit("45 31 ed e9"); code.rel32("redraw")
    code.label("move_down")
    code.emit("44 89 f9 81 e9 80 00 00 00 44 89 ea 83 c2 10 39 ca 0f 47 d1 41 89 d5 e9")
    code.rel32("redraw")
    code.label("move_right")
    code.emit("44 89 f1 81 e9 80 00 00 00 44 89 e2 83 c2 10 39 ca 0f 47 d1 41 89 d4 e9")
    code.rel32("redraw")
    code.label("move_left")
    code.emit("41 83 fc 10 0f 82"); code.rel32("left_zero")
    code.emit("41 83 ec 10 e9"); code.rel32("redraw")
    code.label("left_zero")
    code.emit("45 31 e4")
    code.label("redraw")
    code.emit("8b 44 24 20 e8"); code.rel32("draw")
    code.emit("e9"); code.rel32("read_key")
    code.label("success")
    code.emit("31 c0 e9"); code.rel32("cleanup")
    code.label("unsupported")
    code.emit("48 b8 03 00 00 00 00 00 00 80")
    code.label("cleanup")
    code.emit("48 83 c4 30 41 5f 41 5e 41 5d 41 5c 5f 5e 5b c3")
    code.label("draw")
    code.emit("41 89 c2 44 89 e8 48 0f af c7 44 89 e1 48 01 c8 48 c1 e0 02 48 8d 14 03")
    code.emit("41 b8"); code.raw(struct.pack("<I", spec["height"]))
    code.label("draw_row")
    code.emit("48 89 d1 41 b9"); code.raw(struct.pack("<I", spec["width"]))
    code.label("draw_pixel")
    code.emit("44 89 11 48 83 c1 04 41 ff c9 0f 85"); code.rel32("draw_pixel")
    code.emit("48 8d 14 ba 41 ff c8 0f 85"); code.rel32("draw_row")
    code.emit("c3")
    code.label("gop_guid")
    code.raw(GOP_GUID)
    return code.finish()


def build_efi(spec: dict[str, int]) -> bytes:
    code = machine_code(spec)
    if len(code) > 2 * SECTOR_SIZE:
        raise BuildError("interactive UEFI code exceeds two file sectors")
    dos = bytearray(0x80)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x80)
    coff = struct.pack("<HHIIIHH", 0x8664, 2, 0, 0, 0, 0xF0, 0x0022)
    optional = bytearray()
    optional += struct.pack("<HBBIIIII", 0x20B, 1, 0, 0x400, 0x200, 0, 0x1000, 0x1000)
    optional += struct.pack("<QII", 0, 0x1000, 0x200)
    optional += struct.pack("<HHHHHH", 0, 0, 0, 0, 2, 0)
    optional += struct.pack("<IIII", 0, 0x3000, 0x200, 0)
    optional += struct.pack("<HH", 10, 0x0100)
    optional += struct.pack("<QQQQII", 0x100000, 0x1000, 0x100000, 0x1000, 0, 16)
    directories = [(0, 0)] * 16
    directories[5] = (0x2000, 8)
    optional += b"".join(struct.pack("<II", *entry) for entry in directories)
    text_section = struct.pack(
        "<8sIIIIIIHHI", b".text\0\0\0", len(code), 0x1000, 0x400, 0x200,
        0, 0, 0, 0, 0x60000020,
    )
    reloc_section = struct.pack(
        "<8sIIIIIIHHI", b".reloc\0\0", 8, 0x2000, 0x200, 0x600,
        0, 0, 0, 0, 0x42000040,
    )
    headers = (bytes(dos) + b"PE\0\0" + coff + bytes(optional) + text_section + reloc_section).ljust(0x200, b"\0")
    return headers + code.ljust(0x400, b"\0") + struct.pack("<II", 0x1000, 8).ljust(0x200, b"\0")


def build(world: dict[str, Any], target: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    spec = validate_world(world)
    validate_target(target)
    efi = build_efi(spec)
    image = media.build_image(efi)
    report = {
        "schema_version": 1,
        "status": "BUILT-NOT-INSTALLED",
        "world_sha256": sha256(canonical_bytes(world)),
        "target_sha256": sha256(canonical_bytes(target)),
        "efi_sha256": sha256(efi),
        "image_sha256": sha256(image),
        "image_size_bytes": len(image),
        "boot_path": "EFI/BOOT/BOOTX64.EFI",
        "expected_interaction": {
            "initial_position": [spec["x"], spec["y"]],
            "step_pixels": spec["step"],
            "arrow_keys_move": True,
            "escape_exits": True,
        },
        "physical_execution_verified": False,
        "writes_performed": [],
    }
    return image, report
