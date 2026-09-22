#!/usr/bin/env python3
"""Build the bounded receive-only x86-64 UEFI Rabbit BLE beacon probe."""

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
PROGRAM_SIZE = 3432
PROGRAM_SHA256 = "0aa77e83498e57bb3dc6554e9e5750ec9a12b42f5fa0a4d76f6c9c86ccf0465f"
RABBIT_UUID = bytes.fromhex("52 41 42 42 49 54 4C 45 80 00 00 00 00 00 00 01")
RABBIT_UUID_LE = RABBIT_UUID[::-1]


def _load_media_builder():
    spec = importlib.util.spec_from_file_location("rabbit_uefi_media_hci_identity", MEDIA_BUILDER_PATH)
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
        raise BuildError("probe differs from the reviewed bounded passive-scan contract")
    if probe["target_usb_id"] != "0CF3:E009":
        raise BuildError("probe target USB identity changed")
    if probe["rabbit_service_uuid"] != "52414242-4954-4C45-8000-000000000001":
        raise BuildError("Rabbit service UUID changed")
    if probe["limits"] != {
        "max_usb_interfaces": 64,
        "max_endpoints_per_interface": 8,
        "max_hci_commands": 5,
        "max_command_events": 8,
        "max_scan_events": 100,
        "event_timeout_ms": 200,
        "max_scan_duration_ms": 20000,
        "max_event_bytes": 80,
    }:
        raise BuildError("passive-scan budget changed")


def validate_target(target: dict[str, Any]) -> None:
    if target != EXPECTED_TARGET:
        raise BuildError("target differs from the reviewed Dell QCA Rome passive-scan Target Pack")
    authority = target["authority"]
    if authority["allowed_hci_command_sequence"] != ["0x0C01", "0x2001", "0x200B", "0x200C-enable", "0x200C-disable"]:
        raise BuildError("target permits an unreviewed HCI command sequence")
    if authority["passive_scan"] is not True or authority["radio_receive"] is not True:
        raise BuildError("target omits the reviewed receive-only authority")
    for forbidden in (
        "active_scan", "radio_transmit", "advertise", "pair", "connect",
        "controller_reset", "firmware_download", "internal_storage_writes", "firmware_writes",
    ):
        if authority[forbidden]:
            raise BuildError(f"target permits forbidden authority: {forbidden}")


def parse_command_complete(event: bytes, opcode: int) -> None:
    if len(event) < 6:
        raise BuildError("HCI event is shorter than Command Complete")
    if event[0] != 0x0E or event[1] < 4:
        raise BuildError("not a complete HCI Command Complete event")
    if event[3:5] != opcode.to_bytes(2, "little"):
        raise BuildError("HCI event belongs to a different opcode")
    if event[5] != 0:
        raise BuildError(f"controller returned HCI status 0x{event[5]:02X}")


def contains_rabbit_uuid(event: bytes) -> bool:
    if len(event) < 4 or event[0] != 0x3E or event[2] != 0x02:
        return False
    bounded = event[:80]
    return RABBIT_UUID in bounded or RABBIT_UUID_LE in bounded


def load_program() -> bytes:
    try:
        code = bytes.fromhex(PROGRAM_PATH.read_text(encoding="ascii"))
    except (OSError, ValueError) as error:
        raise BuildError(f"could not decode reviewed beacon-receiver bytes: {error}") from error
    if len(code) != PROGRAM_SIZE or sha256(code) != PROGRAM_SHA256:
        raise BuildError("reviewed beacon-receiver machine bytes changed")
    return code


def build_efi(code: bytes) -> bytes:
    raw_size = (len(code) + SECTOR_SIZE - 1) // SECTOR_SIZE * SECTOR_SIZE
    if raw_size != 0xE00:
        raise BuildError("unexpected beacon-receiver code size")
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
        "target_usb_id": "0CF3:E009",
        "rabbit_service_uuid": "52414242-4954-4C45-8000-000000000001",
        "allowed_hci_command_sequence": ["0x0C01", "0x2001", "0x200B", "0x200C-enable", "0x200C-disable"],
        "max_hci_commands": 5,
        "max_command_events": 8,
        "max_scan_events": 100,
        "max_scan_duration_ms": 20000,
        "max_event_bytes": 80,
        "radio_receive_authorized": True,
        "radio_transmit_authorized": False,
        "pairing_authorized": False,
        "connection_authorized": False,
        "physical_execution_verified": False,
        "writes_performed": [],
    }
    return image, report
