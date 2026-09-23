#!/usr/bin/env python3
"""Build the bounded UEFI BLE BLUE/YELLOW framebuffer-command runtime."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from typing import Any

from fetch_firmware import FirmwareError, fetch_all, load_manifest

ROOT = Path(__file__).resolve().parent
PROBE_PATH, TARGET_PATH = ROOT / "probe.json", ROOT / "target.json"
PROGRAM_PATH, SOURCE_PATH = ROOT / "program.hex", ROOT / "program.S"
MEDIA_BUILDER_PATH = ROOT.parent / "x86-64-uefi-v0" / "build_image.py"
PROGRAM_TEMPLATE_SIZE = 77920
PROGRAM_TEMPLATE_SHA256 = "b91501714714cb487d081cbbd56f87244493cd46a12fe6bfc42b391df244ab81"
PROGRAM_SHA256 = "6611f5bbeb494d0a0738444150aab7928bb1f5eeee952fedc3f8a6fdd372e595"
RAMPATCH_MARKER, NVM_MARKER = b"RABBIT_RAMPATCH!", b"RABBIT_NVM_BLOB!"


def _load_media_builder():
    spec = importlib.util.spec_from_file_location("rabbit_combined_media", MEDIA_BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load reviewed UEFI media builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


media = _load_media_builder()
IMAGE_SIZE, PARTITION_LBA, SECTOR_SIZE = media.IMAGE_SIZE, media.PARTITION_LBA, media.SECTOR_SIZE


class BuildError(ValueError):
    pass


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def _unique_pairs(pairs):
    result = {}
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


EXPECTED_PROBE, EXPECTED_TARGET = load_json(PROBE_PATH), load_json(TARGET_PATH)


def validate_probe(probe: dict[str, Any]) -> None:
    if probe != EXPECTED_PROBE:
        raise BuildError("probe differs from reviewed BLE color-command contract")


def validate_target(target: dict[str, Any]) -> None:
    if target != EXPECTED_TARGET:
        raise BuildError("target differs from reviewed Dell BLE color-command Target Pack")
    authority = target["authority"]
    if authority["vendor_out_requests"] != ["0x01:28", "0x01:4"]:
        raise BuildError("QCA RAM header authority changed")
    if authority["bulk_out_endpoint"] != "0x02" or authority["bulk_out_max_transfers"] != 18:
        raise BuildError("QCA RAM bulk authority changed")
    if authority["allowed_hci_command_sequence"] != ["0x0C03-reset", "0x0C01", "0x2001", "0x200B", "0x200C-enable", "0x200C-disable"]:
        raise BuildError("passive receive command sequence changed")
    if authority["controller_reset"] is not True or authority["post_load_reset_count"] != 1 or authority["post_load_reset_wait_ms"] != 100:
        raise BuildError("bounded post-load reset authority changed")
    if authority["accepted_commands"] != ["blue", "yellow"]:
        raise BuildError("exact accepted command set changed")
    if authority["gop_framebuffer_write"] != "centered-128x128-square-only":
        raise BuildError("framebuffer authority changed")
    for field in ("controller_flash_write", "active_scan", "radio_transmit", "advertise", "pair", "connect", "internal_storage_writes", "firmware_writes"):
        if authority[field]:
            raise BuildError(f"target permits forbidden authority: {field}")


def load_template() -> bytes:
    try:
        code = bytes.fromhex(PROGRAM_PATH.read_text(encoding="ascii"))
    except (OSError, ValueError) as error:
        raise BuildError(f"could not decode reviewed combined template: {error}") from error
    if len(code) != PROGRAM_TEMPLATE_SIZE or sha256(code) != PROGRAM_TEMPLATE_SHA256:
        raise BuildError("reviewed combined template bytes changed")
    return code


def load_program(payloads: dict[str, bytes]) -> bytes:
    code = bytearray(load_template())
    for marker, name, size in (
        (RAMPATCH_MARKER, "rampatch_usb_00000302.bin", 68644),
        (NVM_MARKER, "nvm_usb_00000302.bin", 1998),
    ):
        if code.count(marker) != 1:
            raise BuildError(f"loader marker changed: {marker!r}")
        offset = code.index(marker) + len(marker)
        if code[offset:offset + size] != bytes(size):
            raise BuildError(f"loader placeholder changed for {name}")
        data = payloads.get(name)
        if data is None or len(data) != size:
            raise BuildError(f"missing exact firmware payload: {name}")
        code[offset:offset + size] = data
    result = bytes(code)
    if sha256(result) != PROGRAM_SHA256:
        raise BuildError("combined program plus firmware byte identity changed")
    return result


def build_efi(code: bytes) -> bytes:
    raw_size = (len(code) + SECTOR_SIZE - 1) // SECTOR_SIZE * SECTOR_SIZE
    if raw_size != 0x13200:
        raise BuildError("unexpected combined code size")
    dos = bytearray(0x80); dos[0:2] = b"MZ"; struct.pack_into("<I", dos, 0x3C, 0x80)
    coff = struct.pack("<HHIIIHH", 0x8664, 2, 0, 0, 0, 0xF0, 0x0022)
    optional = bytearray()
    optional += struct.pack("<HBBIIIII", 0x20B, 1, 0, raw_size, 0x200, 0, 0x1000, 0x1000)
    optional += struct.pack("<QII", 0, 0x1000, 0x200)
    optional += struct.pack("<HHHHHH", 0, 0, 0, 0, 2, 0)
    image_size = 0x1000 + ((len(code) + 0xFFF) // 0x1000) * 0x1000 + 0x1000
    reloc_rva = image_size - 0x1000
    optional += struct.pack("<IIII", 0, image_size, 0x200, 0)
    optional += struct.pack("<HH", 10, 0x0100)
    optional += struct.pack("<QQQQII", 0x100000, 0x1000, 0x100000, 0x1000, 0, 16)
    directories = [(0, 0)] * 16; directories[5] = (reloc_rva, 8)
    optional += b"".join(struct.pack("<II", *entry) for entry in directories)
    text = struct.pack("<8sIIIIIIHHI", b".text\0\0\0", len(code), 0x1000, raw_size, 0x200, 0, 0, 0, 0, 0x60000020)
    reloc = struct.pack("<8sIIIIIIHHI", b".reloc\0\0", 8, reloc_rva, 0x200, 0x200 + raw_size, 0, 0, 0, 0, 0x42000040)
    headers = (bytes(dos) + b"PE\0\0" + coff + bytes(optional) + text + reloc).ljust(0x200, b"\0")
    return headers + code.ljust(raw_size, b"\0") + struct.pack("<II", 0x1000, 8).ljust(0x200, b"\0")


def build_fetched() -> tuple[bytes, dict[str, Any]]:
    probe, target, manifest = load_json(PROBE_PATH), load_json(TARGET_PATH), load_manifest()
    validate_probe(probe); validate_target(target)
    try:
        payloads = fetch_all()
    except FirmwareError as error:
        raise BuildError(str(error)) from error
    code = load_program(payloads); efi = build_efi(code); image = media.build_image(efi)
    report = {
        "schema_version": 1, "status": "BUILT-NOT-INSTALLED",
        "probe_sha256": sha256(canonical_bytes(probe)), "target_sha256": sha256(canonical_bytes(target)),
        "firmware_manifest_sha256": sha256(canonical_bytes(manifest)), "source_sha256": sha256(SOURCE_PATH.read_bytes()),
        "program_template_sha256": PROGRAM_TEMPLATE_SHA256, "program_sha256": sha256(code),
        "efi_sha256": sha256(efi), "image_sha256": sha256(image), "image_size_bytes": len(image),
        "boot_path": "EFI/BOOT/BOOTX64.EFI", "target_usb_id": "0CF3:E009",
        "required_rom_version": "0x00000302",
        "command_service_uuids": {
            "blue": "52414242-4954-4C45-8000-000000000002",
            "yellow": "52414242-4954-4C45-8000-000000000003",
        },
        "transient_controller_ram_write_authorized": True, "passive_radio_receive_authorized": True,
        "gop_framebuffer_write_authorized": "centered-128x128-square-only",
        "post_load_hci_reset_authorized": 1, "post_load_reset_wait_ms": 100,
        "active_scan_authorized": False, "radio_transmit_authorized": False,
        "pairing_authorized": False, "connection_authorized": False,
        "persistent_writes_authorized": 0, "physical_execution_verified": False, "writes_performed": [],
    }
    return image, report
