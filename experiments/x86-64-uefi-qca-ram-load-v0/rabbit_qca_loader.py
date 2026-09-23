#!/usr/bin/env python3
"""Build the exact QCA Rome 3.2 transient-RAM initialization artifact."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from typing import Any

from fetch_firmware import MANIFEST_PATH, FirmwareError, fetch_all, load_manifest

ROOT = Path(__file__).resolve().parent
PROBE_PATH, TARGET_PATH = ROOT / "probe.json", ROOT / "target.json"
PROGRAM_PATH, SOURCE_PATH = ROOT / "program.hex", ROOT / "program.S"
MEDIA_BUILDER_PATH = ROOT.parent / "x86-64-uefi-v0" / "build_image.py"
PROGRAM_TEMPLATE_SIZE = 73138
PROGRAM_TEMPLATE_SHA256 = "7d5da33ee1fb62b6cd77495e0b886fc6620c43330d85d7e3d23bad3a3dfc1e59"
PROGRAM_SHA256 = "6cada945ae22c1e1a7494ad437fb93dbd6c9fd552b816eb36105ce43569250f4"
RAMPATCH_MARKER, NVM_MARKER = b"RABBIT_RAMPATCH!", b"RABBIT_NVM_BLOB!"


def _load_media_builder():
    spec = importlib.util.spec_from_file_location("rabbit_uefi_media_qca_loader", MEDIA_BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load reviewed UEFI media builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


media = _load_media_builder()
IMAGE_SIZE, PARTITION_LBA, SECTOR_SIZE = media.IMAGE_SIZE, media.PARTITION_LBA, media.SECTOR_SIZE


class BuildError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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


EXPECTED_PROBE, EXPECTED_TARGET, EXPECTED_FIRMWARE = load_json(PROBE_PATH), load_json(TARGET_PATH), load_json(MANIFEST_PATH)


def validate_probe(probe):
    if probe != EXPECTED_PROBE:
        raise BuildError("probe differs from reviewed transient QCA RAM-load contract")


def validate_target(target):
    if target != EXPECTED_TARGET:
        raise BuildError("target differs from reviewed transient QCA RAM-load Target Pack")
    authority = target["authority"]
    if authority["vendor_out_requests"] != ["0x01:28", "0x01:4"]:
        raise BuildError("vendor-OUT header authority changed")
    if authority["bulk_out_endpoint"] != "0x02" or authority["bulk_out_max_transfers"] != 18 or authority["bulk_out_max_bytes"] != 70610:
        raise BuildError("bounded bulk-OUT authority changed")
    if authority["transient_controller_ram_write"] is not True:
        raise BuildError("transient controller RAM authority is missing")
    for field in ("controller_flash_write", "controller_reset", "radio_receive", "radio_transmit", "internal_storage_writes", "firmware_writes"):
        if authority[field]:
            raise BuildError(f"target permits forbidden authority: {field}")
    if authority["hci_commands"] != 0:
        raise BuildError("target permits HCI commands")


def validate_firmware_manifest(manifest):
    if manifest != EXPECTED_FIRMWARE:
        raise BuildError("firmware manifest differs from reviewed pinned upstream inputs")


def load_template() -> bytes:
    try:
        code = bytes.fromhex(PROGRAM_PATH.read_text(encoding="ascii"))
    except (OSError, ValueError) as error:
        raise BuildError(f"could not decode reviewed loader template: {error}") from error
    if len(code) != PROGRAM_TEMPLATE_SIZE or sha256(code) != PROGRAM_TEMPLATE_SHA256:
        raise BuildError("reviewed loader template bytes changed")
    return code


def load_program(payloads: dict[str, bytes]) -> bytes:
    code = bytearray(load_template())
    replacements = (
        (RAMPATCH_MARKER, "rampatch_usb_00000302.bin", 68644),
        (NVM_MARKER, "nvm_usb_00000302.bin", 1998),
    )
    for marker, name, size in replacements:
        if code.count(marker) != 1:
            raise BuildError(f"loader marker changed: {marker!r}")
        offset = code.index(marker) + len(marker)
        if code[offset:offset + size] != bytes(size):
            raise BuildError(f"loader placeholder changed for {name}")
        data = payloads.get(name)
        if data is None or len(data) != size:
            raise BuildError(f"missing exact firmware payload: {name}")
        expected = next(item for item in EXPECTED_FIRMWARE["files"] if item["name"] == name)
        if sha256(data) != expected["sha256"]:
            raise BuildError(f"firmware payload SHA-256 mismatch: {name}")
        code[offset:offset + size] = data
    result = bytes(code)
    if sha256(result) != PROGRAM_SHA256:
        raise BuildError("final loader plus firmware byte identity changed")
    return result


def build_efi(code: bytes) -> bytes:
    raw_size = (len(code) + SECTOR_SIZE - 1) // SECTOR_SIZE * SECTOR_SIZE
    if raw_size != 0x11E00:
        raise BuildError("unexpected QCA loader code size")
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


def build(probe, target, manifest, payloads):
    validate_probe(probe); validate_target(target); validate_firmware_manifest(manifest)
    code = load_program(payloads); efi = build_efi(code); image = media.build_image(efi)
    report = {
        "schema_version": 1, "status": "BUILT-NOT-INSTALLED",
        "probe_sha256": sha256(canonical_bytes(probe)), "target_sha256": sha256(canonical_bytes(target)),
        "firmware_manifest_sha256": sha256(canonical_bytes(manifest)), "source_sha256": sha256(SOURCE_PATH.read_bytes()),
        "program_template_sha256": PROGRAM_TEMPLATE_SHA256, "program_sha256": sha256(code),
        "efi_sha256": sha256(efi), "image_sha256": sha256(image), "image_size_bytes": len(image),
        "boot_path": "EFI/BOOT/BOOTX64.EFI", "target_usb_id": "0CF3:E009", "required_rom_version": "0x00000302",
        "firmware_files": [{"name": item["name"], "size": item["size"], "sha256": item["sha256"]} for item in manifest["files"]],
        "transient_controller_ram_write_authorized": True, "controller_reset_authorized": False,
        "hci_commands_authorized": 0, "radio_operations_authorized": 0,
        "persistent_writes_authorized": 0, "physical_execution_verified": False, "writes_performed": [],
    }
    return image, report


def build_fetched():
    try:
        payloads = fetch_all()
    except FirmwareError as error:
        raise BuildError(str(error)) from error
    return build(load_json(PROBE_PATH), load_json(TARGET_PATH), load_manifest(), payloads)
