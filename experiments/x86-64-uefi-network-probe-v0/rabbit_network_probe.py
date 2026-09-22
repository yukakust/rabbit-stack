#!/usr/bin/env python3
"""Build the reviewed read-only x86-64 UEFI network inventory probe."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PROBE_PATH = ROOT / "probe.json"
TARGET_PATH = ROOT / "target.json"
PROGRAM_PATH = ROOT / "program.hex"
SOURCE_PATH = ROOT / "program.S"
MEDIA_BUILDER_PATH = ROOT.parent / "x86-64-uefi-v0" / "build_image.py"
PROGRAM_SIZE = 1120
PROGRAM_SHA256 = "da81a6f725fcc259403e3658c6c4d1f6b5b7b6fecceebf6d88711cbad2add831"


def _load_media_builder():
    spec = importlib.util.spec_from_file_location("rabbit_uefi_media_network_probe", MEDIA_BUILDER_PATH)
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


EXPECTED_PROBE = load_json(PROBE_PATH)
EXPECTED_TARGET = load_json(TARGET_PATH)


def validate_probe(probe: dict[str, Any]) -> None:
    if probe != EXPECTED_PROBE:
        raise BuildError("probe differs from the reviewed read-only network inventory contract")
    if probe["mutations"] != []:
        raise BuildError("network discovery must declare no mutations")


def validate_target(target: dict[str, Any]) -> None:
    if target != EXPECTED_TARGET:
        raise BuildError("target differs from the reviewed UEFI network-probe Target Pack")
    policy = target["probe_policy"]
    if policy["configuration_data_writes"] or policy["network_transmit"] or policy["network_receive"]:
        raise BuildError("probe policy permits a network or PCI configuration effect")
    installation = target["installation_policy"]
    if installation["internal_storage_writes"] or installation["firmware_writes"]:
        raise BuildError("probe target permits persistent machine writes")


def load_program() -> bytes:
    try:
        code = bytes.fromhex(PROGRAM_PATH.read_text(encoding="ascii"))
    except (OSError, ValueError) as error:
        raise BuildError(f"could not decode reviewed network-probe bytes: {error}") from error
    if len(code) != PROGRAM_SIZE or sha256(code) != PROGRAM_SHA256:
        raise BuildError("reviewed network-probe machine bytes changed")
    return code


def build_efi(code: bytes) -> bytes:
    raw_size = (len(code) + SECTOR_SIZE - 1) // SECTOR_SIZE * SECTOR_SIZE
    if raw_size != 0x600:
        raise BuildError("unexpected network-probe code size")
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


def build(probe: dict[str, Any], target: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    validate_probe(probe)
    validate_target(target)
    code = load_program()
    efi = build_efi(code)
    image = media.build_image(efi)
    report = {
        "schema_version": 1,
        "status": "BUILT-NOT-INSTALLED",
        "probe_sha256": sha256(canonical_bytes(probe)),
        "target_sha256": sha256(canonical_bytes(target)),
        "source_sha256": sha256(SOURCE_PATH.read_bytes()),
        "program_sha256": sha256(code),
        "efi_sha256": sha256(efi),
        "image_sha256": sha256(image),
        "image_size_bytes": len(image),
        "boot_path": "EFI/BOOT/BOOTX64.EFI",
        "expected_observation": "firmware protocol availability and PCI network identities",
        "network_packets_sent": 0,
        "configuration_data_writes": 0,
        "physical_execution_verified": False,
        "writes_performed": [],
    }
    return image, report
