#!/usr/bin/env python3
"""Verify the exact, transient QCA Rome 3.2 RAM-load artifact."""

from __future__ import annotations

import copy
import hashlib
import struct
import tempfile
from collections.abc import Callable
from pathlib import Path

from fetch_firmware import fetch_all, load_manifest
from rabbit_qca_loader import (
    BuildError, IMAGE_SIZE, NVM_MARKER, PARTITION_LBA, PROGRAM_SHA256,
    PROGRAM_TEMPLATE_SHA256, PROGRAM_TEMPLATE_SIZE, PROBE_PATH, RAMPATCH_MARKER,
    SECTOR_SIZE, SOURCE_PATH, TARGET_PATH, build, load_json, load_program,
    load_template, validate_firmware_manifest, validate_probe, validate_target,
)

EXPECTED_PROBE_SHA256 = "3e27abe33295b0c3be75d0d807122cc2fb9062ae305255546326077dc655a41a"
EXPECTED_TARGET_SHA256 = "57f57633569c28b637f5413758cf7db721d5faac0a2a9cab0b20e5124caff4aa"
EXPECTED_FIRMWARE_MANIFEST_SHA256 = "cabf8be8ee76815a03d1407fd635c983563303a9661f9419d82e9dbcb3e81dfc"
EXPECTED_SOURCE_SHA256 = "357da707d63c942f7096fe826201f979ffd934ca5da47eec3551fe30f816e85d"
EXPECTED_EFI_SHA256 = "3fa8eacf475d4c711d365f1712e8494dd2c18666de2e2d124f42c20daa101bb5"
EXPECTED_IMAGE_SHA256 = "2b4894f77181626cafd7369fd80f60ae3451e9d93ca8ee4ebf7f6cc696eccadd"
USB_IO_GUID = bytes.fromhex("d6 68 2f 2b d2 0c cf 44 8e 8b bb a2 0b 1b 5b 75")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejected(label: str, action: Callable[[], object]) -> None:
    try:
        action()
    except (BuildError, RuntimeError) as error:
        print(f"PASS: rejected {label}: {error}")
        return
    raise RuntimeError(f"invalid case accepted: {label}")


def short_entry(directory: bytes, name: bytes) -> tuple[int, int]:
    for offset in range(0, len(directory), 32):
        entry = directory[offset:offset + 32]
        if entry[:11] == name:
            cluster = struct.unpack_from("<H", entry, 20)[0] << 16
            cluster |= struct.unpack_from("<H", entry, 26)[0]
            return cluster, struct.unpack_from("<I", entry, 28)[0]
    raise RuntimeError(f"missing FAT entry {name!r}")


def inspect_image(image: bytes) -> bytes:
    require(len(image) == IMAGE_SIZE and image[510:512] == b"\x55\xaa", "disk envelope changed")
    partition = image[446:462]
    start, count = struct.unpack_from("<II", partition, 8)
    require(partition[4] == 0x0C and start == PARTITION_LBA, "partition contract changed")
    require(count == len(image) // SECTOR_SIZE - start, "partition length changed")
    boot = image[start * SECTOR_SIZE:(start + 1) * SECTOR_SIZE]
    reserved, fat_sectors = struct.unpack_from("<H", boot, 14)[0], struct.unpack_from("<I", boot, 36)[0]
    data_lba = start + reserved + 2 * fat_sectors

    def cluster(number: int) -> bytes:
        offset = (data_lba + number - 2) * SECTOR_SIZE
        return image[offset:offset + SECTOR_SIZE]

    efi_dir, _ = short_entry(cluster(2), b"EFI        ")
    boot_dir, _ = short_entry(cluster(efi_dir), b"BOOT       ")
    current, size = short_entry(cluster(boot_dir), b"BOOTX64 EFI")
    fat_offset = (start + reserved) * SECTOR_SIZE
    result = bytearray()
    while current < 0x0FFFFFF8:
        result += cluster(current)
        current = struct.unpack_from("<I", image, fat_offset + current * 4)[0] & 0x0FFFFFFF
    return bytes(result[:size])


def inspect_efi(efi: bytes, program: bytes) -> None:
    require(efi[:2] == b"MZ", "missing DOS signature")
    pe = struct.unpack_from("<I", efi, 0x3C)[0]
    require(efi[pe:pe + 4] == b"PE\0\0", "missing PE signature")
    coff, optional = pe + 4, pe + 24
    require(struct.unpack_from("<HH", efi, coff) == (0x8664, 2), "not reviewed x86-64 PE")
    require(struct.unpack_from("<H", efi, optional)[0] == 0x20B, "not PE32+")
    require(struct.unpack_from("<H", efi, optional + 68)[0] == 10, "not EFI application")
    section = optional + 0xF0
    raw_size, raw_offset = struct.unpack_from("<II", efi, section + 16)
    require(raw_size == 0x11E00 and raw_offset == 0x200, "program section layout changed")
    require(efi[raw_offset:raw_offset + len(program)] == program, "machine bytes changed")


def inspect_program(template: bytes, program: bytes, payloads: dict[str, bytes]) -> None:
    require(len(template) == PROGRAM_TEMPLATE_SIZE, "template size changed")
    require(hashlib.sha256(template).hexdigest() == PROGRAM_TEMPLATE_SHA256, "template identity changed")
    require(hashlib.sha256(program).hexdigest() == PROGRAM_SHA256, "final program identity changed")
    prefix = template[:template.index(RAMPATCH_MARKER)]
    require(prefix.count(USB_IO_GUID) == 1, "UEFI USB I/O GUID changed")
    require(prefix.count(bytes.fromhex("48 8b 46 30 ff d0")) == 1, "device descriptor call changed")
    require(prefix.count(bytes.fromhex("48 8b 46 40 ff d0")) == 1, "interface descriptor call changed")
    require(prefix.count(bytes.fromhex("49 8b 04 24 ff d0")) == 1, "vendor-OUT control helper changed")
    require(prefix.count(bytes.fromhex("49 8b 44 24 08 ff d0")) == 1, "bulk-OUT helper changed")
    require(bytes.fromhex("49 8b 45 18 ff d0") not in prefix, "interrupt/HCI path appeared")
    for marker in (
        b"TRANSIENT CONTROLLER RAM ONLY; RADIO OFF", b"REQUIRE ROM=00000302",
        b"LOAD HASH-PINNED RAMPATCH TO RAM", b"LOAD HASH-PINNED NVM TO RAM",
        b"PATCH_UPDATED=YES; SYSCFG_UPDATED=YES",
        b"NO RESET; NO HCI; NO SCAN; NO RADIO; POWER-OFF ROLLBACK",
        b"ROM MISMATCH; NO DEVICE WRITE SENT",
    ):
        require(marker in prefix, f"required safety marker changed: {marker!r}")
    for marker, name, size in ((RAMPATCH_MARKER, "rampatch_usb_00000302.bin", 68644), (NVM_MARKER, "nvm_usb_00000302.bin", 1998)):
        offset = template.index(marker) + len(marker)
        require(template[offset:offset + size] == bytes(size), f"template placeholder changed: {name}")
        require(program[offset:offset + size] == payloads[name], f"embedded bytes changed: {name}")


def duplicate_json_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="rabbit-qca-loader-json-") as temp_dir:
        path = Path(temp_dir) / "duplicate.json"
        path.write_text('{"schema_version":1,"schema_version":1}\n', encoding="utf-8")
        load_json(path)


def main() -> int:
    try:
        probe, target, manifest = load_json(PROBE_PATH), load_json(TARGET_PATH), load_manifest()
        payloads = fetch_all()
        image_a, report_a = build(probe, target, manifest, payloads)
        image_b, report_b = build(copy.deepcopy(probe), copy.deepcopy(target), copy.deepcopy(manifest), dict(payloads))
        require(image_a == image_b and report_a == report_b, "repeated builds differ")
        for field, expected in (
            ("probe_sha256", EXPECTED_PROBE_SHA256), ("target_sha256", EXPECTED_TARGET_SHA256),
            ("firmware_manifest_sha256", EXPECTED_FIRMWARE_MANIFEST_SHA256), ("source_sha256", EXPECTED_SOURCE_SHA256),
            ("program_template_sha256", PROGRAM_TEMPLATE_SHA256), ("program_sha256", PROGRAM_SHA256),
            ("efi_sha256", EXPECTED_EFI_SHA256), ("image_sha256", EXPECTED_IMAGE_SHA256),
        ):
            require(report_a[field] == expected, f"{field} changed")
        require(report_a["transient_controller_ram_write_authorized"] is True, "RAM-load authority missing")
        require(report_a["controller_reset_authorized"] is False, "controller reset became authorized")
        require(report_a["hci_commands_authorized"] == report_a["radio_operations_authorized"] == 0, "HCI or radio authority appeared")
        require(report_a["persistent_writes_authorized"] == 0 and report_a["writes_performed"] == [], "persistent write appeared")
        template, program = load_template(), load_program(payloads)
        inspect_program(template, program, payloads)
        inspect_efi(inspect_image(image_a), program)
        print("PASS: exact upstream rampatch and NVM are pinned by immutable commit, size, and SHA-256")
        print("PASS: deterministic UEFI artifact embeds unmodified payloads for exact USB 0CF3:E009 and ROM 00000302")
        print("PASS: machine path is bounded to two vendor-OUT headers and 18 endpoint-02 bulk chunks")
        print("PASS: controller reset, HCI, scan, advertising, radio, flash, and persistent storage remain absent")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")

        qemu = load_json(Path(__file__).resolve().parent / "evidence" / "qemu-macos-arm64-observed.json")
        require(qemu["status"] == "OBSERVED-MANUAL-QEMU-QCA-RAM-LOAD-FAIL-CLOSED", "QEMU evidence status changed")
        for field in ("probe_sha256", "target_sha256", "firmware_manifest_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(qemu["bindings"][field] == report_a[field], f"QEMU {field} binding changed")
        observation = qemu["observation"]
        require(observation["visible_version"] == "v0.1", "QEMU version marker changed")
        require(observation["result"] == "TARGET NOT FOUND; NO DEVICE WRITE SENT", "QEMU fail-closed result changed")
        require(observation["target_found"] is False and observation["controller_ram_writes"] == 0, "QEMU evidence claims a device write")
        require(observation["controller_reset_performed"] is False, "QEMU evidence claims controller reset")
        require(observation["hci_commands_sent"] == observation["radio_operations_requested"] == 0, "QEMU evidence claims HCI/radio activity")
        require(qemu["execution"]["physical_execution_verified"] is False, "QEMU evidence claims physical execution")
        print("PASS: exact QEMU evidence proves RAM loading fails closed before device writes on a mismatch")

        wrong_rom = copy.deepcopy(probe); wrong_rom["required_rom_version"] = "0x00000300"
        rejected("a substituted ROM version", lambda: validate_probe(wrong_rom))
        extra_bulk = copy.deepcopy(target); extra_bulk["authority"]["bulk_out_max_transfers"] = 19
        rejected("a nineteenth bulk transfer", lambda: validate_target(extra_bulk))
        wrong_endpoint = copy.deepcopy(target); wrong_endpoint["authority"]["bulk_out_endpoint"] = "0x03"
        rejected("a substituted bulk endpoint", lambda: validate_target(wrong_endpoint))
        for field in ("controller_flash_write", "controller_reset", "radio_receive", "radio_transmit", "internal_storage_writes", "firmware_writes"):
            unsafe = copy.deepcopy(target); unsafe["authority"][field] = True
            rejected(f"target permitting {field}", lambda unsafe=unsafe: validate_target(unsafe))
        hci = copy.deepcopy(target); hci["authority"]["hci_commands"] = 1
        rejected("an HCI command", lambda: validate_target(hci))
        altered_manifest = copy.deepcopy(manifest); altered_manifest["source"]["commit"] = "0" * 40
        rejected("an unpinned firmware revision", lambda: validate_firmware_manifest(altered_manifest))
        altered_payloads = dict(payloads); altered_payloads["nvm_usb_00000302.bin"] = payloads["nvm_usb_00000302.bin"][:-1] + b"\0"
        rejected("a modified NVM payload", lambda: load_program(altered_payloads))
        tampered = bytearray(inspect_image(image_a)); tampered[0x200] ^= 1
        rejected("tampered machine instructions", lambda: inspect_efi(bytes(tampered), program))
        rejected("duplicate JSON fields", duplicate_json_is_rejected)
        print("PASS: ROM/device substitution, authority escalation, payload mutation, tamper, and ambiguity are rejected")
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: QEMU-observed exact QCA Rome 3.2 transient-RAM initialization contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
