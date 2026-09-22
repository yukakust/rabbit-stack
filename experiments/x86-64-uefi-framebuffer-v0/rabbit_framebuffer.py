#!/usr/bin/env python3
"""Lower one semantic color rectangle to reviewed x86-64 UEFI machine bytes."""

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
LEGACY_BUILDER_PATH = ROOT.parent / "x86-64-uefi-v0" / "build_image.py"


def _load_legacy_builder():
    spec = importlib.util.spec_from_file_location("rabbit_uefi_media_v0", LEGACY_BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load reviewed UEFI media builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


media = _load_legacy_builder()
IMAGE_SIZE = media.IMAGE_SIZE
PARTITION_LBA = media.PARTITION_LBA
SECTOR_SIZE = media.SECTOR_SIZE
GOP_GUID = bytes.fromhex("de a9 42 90 dc 23 38 4a 96 fb 7a de d0 80 51 6a")


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
        raise BuildError("world differs from the reviewed first-color-object contract")
    obj = world["objects"][0]
    return {
        "x": obj["x"],
        "y": obj["y"],
        "width": obj["width"],
        "height": obj["height"],
        "red": 0xFF,
        "green": 0x80,
        "blue": 0x00,
    }


def validate_target(target: dict[str, Any]) -> None:
    if target != EXPECTED_TARGET:
        raise BuildError("target differs from the reviewed x86-64 UEFI framebuffer contract")


class Code:
    def __init__(self) -> None:
        self.data = bytearray()
        self.labels: dict[str, int] = {}
        self.patches: list[tuple[int, str, int]] = []

    def emit(self, value: str) -> None:
        self.data += bytes.fromhex(value)

    def raw(self, value: bytes) -> None:
        self.data += value

    def label(self, name: str) -> None:
        if name in self.labels:
            raise AssertionError(f"duplicate label {name}")
        self.labels[name] = len(self.data)

    def rel32(self, label: str) -> None:
        offset = len(self.data)
        self.data += b"\0" * 4
        self.patches.append((offset, label, 4))

    def finish(self) -> bytes:
        for offset, label, size in self.patches:
            if label not in self.labels:
                raise AssertionError(f"missing label {label}")
            displacement = self.labels[label] - (offset + size)
            struct.pack_into("<i", self.data, offset, displacement)
        return bytes(self.data)


def machine_code(rect: dict[str, int]) -> bytes:
    if rect != validate_world(EXPECTED_WORLD):
        raise BuildError("rectangle differs from the reviewed world")
    rgb_word = rect["red"] | (rect["green"] << 8) | (rect["blue"] << 16)
    bgr_word = rect["blue"] | (rect["green"] << 8) | (rect["red"] << 16)
    code = Code()
    code.emit("53 56 57 48 83 ec 30")       # preserve RBX/RSI/RDI; aligned call frame
    code.emit("48 8b 72 30")                # RSI = SystemTable->ConIn
    code.emit("48 8b 5a 60")                # RBX = SystemTable->BootServices
    code.emit("48 8d 0d"); code.rel32("gop_guid")
    code.emit("31 d2")                      # Registration = NULL
    code.emit("4c 8d 44 24 28")             # Interface = &stack_slot
    code.emit("48 8b 83 40 01 00 00 ff d0") # BootServices->LocateProtocol(...)
    code.emit("48 85 c0 0f 85"); code.rel32("cleanup")
    code.emit("48 8b 5c 24 28")             # RBX = GOP
    code.emit("48 8b 43 18")                # RAX = GOP->Mode
    code.emit("48 8b 78 18")                # RDI = FrameBufferBase
    code.emit("48 8b 50 08")                # RDX = Mode->Info
    code.emit("81 7a 04 64 01 00 00 0f 82"); code.rel32("unsupported")
    code.emit("81 7a 08 64 01 00 00 0f 82"); code.rel32("unsupported")
    code.emit("83 7a 0c 00 0f 84"); code.rel32("rgb")
    code.emit("83 7a 0c 01 0f 84"); code.rel32("bgr")
    code.emit("e9"); code.rel32("unsupported")
    code.label("rgb")
    code.emit("41 ba"); code.raw(struct.pack("<I", rgb_word)); code.emit("e9"); code.rel32("color_ready")
    code.label("bgr")
    code.emit("41 ba"); code.raw(struct.pack("<I", bgr_word))
    code.label("color_ready")
    code.emit("8b 42 20")                    # EAX = PixelsPerScanLine
    code.emit("48 6b c0 64 48 83 c0 64")    # offset = 100 * stride + 100
    code.emit("48 c1 e0 02 48 01 c7")        # byte offset; RDI = first pixel
    code.emit("41 b8"); code.raw(struct.pack("<I", rect["height"]))
    code.label("row")
    code.emit("48 89 f9 41 b9"); code.raw(struct.pack("<I", rect["width"]))
    code.label("pixel")
    code.emit("44 89 11 48 83 c1 04 41 ff c9 0f 85"); code.rel32("pixel")
    code.emit("8b 42 20 48 c1 e0 02 48 01 c7 41 ff c8 0f 85"); code.rel32("row")
    code.label("wait_key")
    code.emit("48 89 f1 48 8d 54 24 28 48 8b 41 08 ff d0 48 85 c0 0f 85")
    code.rel32("wait_key")
    code.emit("31 c0 e9"); code.rel32("cleanup")
    code.label("unsupported")
    code.emit("48 b8 03 00 00 00 00 00 00 80") # EFI_UNSUPPORTED
    code.label("cleanup")
    code.emit("48 83 c4 30 5f 5e 5b c3")
    code.label("gop_guid")
    code.raw(GOP_GUID)
    return code.finish()


def build_efi(rect: dict[str, int]) -> bytes:
    code = machine_code(rect)
    if len(code) > SECTOR_SIZE:
        raise BuildError("UEFI framebuffer code exceeds one file sector")
    dos = bytearray(0x80)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x80)
    coff = struct.pack("<HHIIIHH", 0x8664, 2, 0, 0, 0, 0xF0, 0x0022)
    optional = bytearray()
    optional += struct.pack("<HBBIIIII", 0x20B, 1, 0, 0x200, 0x200, 0, 0x1000, 0x1000)
    optional += struct.pack("<QII", 0, 0x1000, 0x200)
    optional += struct.pack("<HHHHHH", 0, 0, 0, 0, 2, 0)
    optional += struct.pack("<IIII", 0, 0x3000, 0x200, 0)
    optional += struct.pack("<HH", 10, 0x0100)
    optional += struct.pack("<QQQQII", 0x100000, 0x1000, 0x100000, 0x1000, 0, 16)
    directories = [(0, 0)] * 16
    directories[5] = (0x2000, 8)
    optional += b"".join(struct.pack("<II", *entry) for entry in directories)
    text_section = struct.pack(
        "<8sIIIIIIHHI", b".text\0\0\0", len(code), 0x1000, 0x200, 0x200,
        0, 0, 0, 0, 0x60000020,
    )
    reloc_section = struct.pack(
        "<8sIIIIIIHHI", b".reloc\0\0", 8, 0x2000, 0x200, 0x400,
        0, 0, 0, 0, 0x42000040,
    )
    headers = (bytes(dos) + b"PE\0\0" + coff + bytes(optional) + text_section + reloc_section).ljust(0x200, b"\0")
    return headers + code.ljust(0x200, b"\0") + struct.pack("<II", 0x1000, 8).ljust(0x200, b"\0")


def build(world: dict[str, Any], target: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    rect = validate_world(world)
    validate_target(target)
    efi = build_efi(rect)
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
        "expected_visual": world["objects"][0],
        "physical_execution_verified": False,
        "writes_performed": [],
    }
    return image, report
