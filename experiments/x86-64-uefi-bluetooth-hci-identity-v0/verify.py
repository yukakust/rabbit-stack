#!/usr/bin/env python3
"""Verify the bounded x86-64 UEFI Bluetooth HCI identity artifact."""

from __future__ import annotations

import copy
import hashlib
import struct
import tempfile
from collections.abc import Callable
from pathlib import Path

from rabbit_hci_identity import (
    BuildError, IMAGE_SIZE, PARTITION_LBA, PROGRAM_SHA256, PROGRAM_SIZE, PROBE_PATH, ROOT,
    SECTOR_SIZE, SOURCE_PATH, TARGET_PATH, build, load_json, load_program,
    parse_read_local_version_event, validate_probe, validate_target,
)


EXPECTED_PROBE_SHA256 = "d8f28775ef6a025935e177f06ff59628b7dce8deed329d27f74b6bccf455de91"
EXPECTED_TARGET_SHA256 = "a682160b86c4d46895280e359748d811885fe1f28af5cac26b4cab17b205c97e"
EXPECTED_SOURCE_SHA256 = "7eae9a8883e495d3fd94a30c87ab95385dcd61f19ed7eff4a2a2fd784b998f32"
EXPECTED_EFI_SHA256 = "b7da72b8fa450e047c9f6d69c0879c394aa7274ba28b8643813885186d9485fe"
EXPECTED_IMAGE_SHA256 = "c5658d3edf41028089f72d2be324c12dddbaad1b3f0c037930a1d81bd91ec8de"
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
        if entry[0:11] == name:
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
    reserved = struct.unpack_from("<H", boot, 14)[0]
    fat_sectors = struct.unpack_from("<I", boot, 36)[0]
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
    require(efi[0:2] == b"MZ", "missing DOS signature")
    pe = struct.unpack_from("<I", efi, 0x3C)[0]
    require(efi[pe:pe + 4] == b"PE\0\0", "missing PE signature")
    coff = pe + 4
    require(struct.unpack_from("<HH", efi, coff) == (0x8664, 2), "not reviewed x86-64 PE")
    optional = coff + 20
    require(struct.unpack_from("<H", efi, optional)[0] == 0x20B, "not PE32+")
    require(struct.unpack_from("<H", efi, optional + 68)[0] == 10, "not EFI application")
    section = optional + 0xF0
    raw_size, raw_offset = struct.unpack_from("<II", efi, section + 16)
    require(raw_size == 0x800 and raw_offset == 0x200, "program section layout changed")
    require(efi[raw_offset:raw_offset + len(program)] == program, "machine bytes changed")


def inspect_program(program: bytes) -> None:
    require(len(program) == PROGRAM_SIZE, "program size changed")
    require(hashlib.sha256(program).hexdigest() == PROGRAM_SHA256, "program identity changed")
    require(program.count(USB_IO_GUID) == 1, "UEFI USB I/O GUID changed")
    require(program.count(bytes.fromhex("48 8b 46 30 ff d0")) == 1, "device descriptor call changed")
    require(program.count(bytes.fromhex("48 8b 46 40 ff d0")) == 1, "interface descriptor call changed")
    require(program.count(bytes.fromhex("48 8b 46 48 ff d0")) == 1, "endpoint descriptor call changed")
    require(program.count(bytes.fromhex("49 8b 45 00 ff d0")) == 1, "control-transfer call changed")
    require(program.count(bytes.fromhex("49 8b 45 18 ff d0")) == 1, "interrupt-transfer call changed")
    require(b"0CF3:E009" in program, "exact target marker changed")
    require(b"HCI READ LOCAL VERSION SENT (0x1001)" in program, "single HCI opcode marker changed")
    require(b"NO SCAN; NO ADVERTISE; NO PAIR; NO RADIO DATA" in program, "safety banner changed")
    require(program.count(bytes.fromhex("48 83 ec 28 ff d0 48 83 c4 28 c3")) == 1, "nested output call ABI changed")


def duplicate_json_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="rabbit-hci-json-") as temp_dir:
        path = Path(temp_dir) / "duplicate.json"
        path.write_text('{"schema_version":1,"schema_version":1}\n', encoding="utf-8")
        load_json(path)


def main() -> int:
    try:
        probe, target = load_json(PROBE_PATH), load_json(TARGET_PATH)
        image_a, report_a = build(probe, target)
        image_b, report_b = build(copy.deepcopy(probe), copy.deepcopy(target))
        require(image_a == image_b and report_a == report_b, "repeated builds differ")
        require(report_a["probe_sha256"] == EXPECTED_PROBE_SHA256, "probe identity changed")
        require(report_a["target_sha256"] == EXPECTED_TARGET_SHA256, "target identity changed")
        require(report_a["source_sha256"] == EXPECTED_SOURCE_SHA256, "source identity changed")
        require(report_a["program_sha256"] == PROGRAM_SHA256, "program identity report changed")
        require(report_a["efi_sha256"] == EXPECTED_EFI_SHA256, "EFI identity changed")
        require(report_a["image_sha256"] == EXPECTED_IMAGE_SHA256, "image identity changed")
        require(report_a["allowed_hci_opcodes"] == ["0x1001"], "opcode authority changed")
        require(report_a["max_hci_commands"] == 1 and report_a["max_hci_events"] == 8, "runtime budget changed")
        require(report_a["radio_packets_authorized"] == 0 and report_a["pairing_authorized"] is False, "radio authority changed")
        require(report_a["writes_performed"] == [], "builder claims physical writes")
        program = load_program()
        inspect_program(program)
        inspect_efi(inspect_image(image_a), program)
        source = SOURCE_PATH.read_text(encoding="ascii")
        require("UsbControlTransfer" in source and "UsbSyncInterruptTransfer" in source, "reviewed HCI transport path changed")
        for forbidden in ("UsbBulkTransfer", "UsbPortReset", "Reset command", "Set Scan", "Set Advertising"):
            require(forbidden not in source, f"forbidden source path appears: {forbidden}")
        print("PASS: deterministic UEFI image binds one HCI identity command to exact USB 0CF3:E009")
        print("PASS: code has one control-OUT path, one interrupt-IN path, and no reset/bulk/radio path")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")

        sample = bytes.fromhex("0e 0c 01 01 10 00 08 34 12 08 0d 00 78 56")
        require(
            parse_read_local_version_event(sample)
            == {"hci_version": 8, "hci_revision": 0x1234, "lmp_version": 8, "manufacturer": 0x000D, "lmp_subversion": 0x5678},
            "HCI Command Complete parser changed",
        )
        rejected("a short HCI event", lambda: parse_read_local_version_event(sample[:10]))
        rejected("an event for another opcode", lambda: parse_read_local_version_event(sample[:3] + b"\x02" + sample[4:]))
        rejected("a controller error status", lambda: parse_read_local_version_event(sample[:5] + b"\x01" + sample[6:]))
        print("PASS: HCI response parser accepts the exact Command Complete shape and rejects ambiguity")

        qemu = load_json(ROOT / "evidence" / "qemu-macos-arm64-observed.json")
        require(qemu["status"] == "OBSERVED-MANUAL-QEMU-HCI-IDENTITY-FAIL-CLOSED", "QEMU evidence status changed")
        for field in ("probe_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(qemu["bindings"][field] == report_a[field], f"QEMU {field} binding changed")
        require(qemu["observation"]["visible_version"] == "v0.1", "QEMU version marker changed")
        require(qemu["observation"]["visible_stage"] == "STAGE 1: FIND 0CF3:E009 INTERFACE 00", "QEMU stage changed")
        require(qemu["observation"]["result"] == "TARGET NOT FOUND; NO HCI COMMAND SENT", "QEMU fail-closed result changed")
        require(qemu["observation"]["target_found"] is False, "QEMU claims exact target")
        require(qemu["observation"]["hci_commands_sent"] == 0, "QEMU claims an HCI command")
        require(qemu["observation"]["radio_operations_requested"] == 0, "QEMU claims radio activity")
        require(qemu["physical_dell_status"] == "NOT-OBSERVED-WITH-HCI-IDENTITY-V0.1", "QEMU evidence overclaims physical Dell")
        require(qemu["execution"]["physical_execution_verified"] is False, "QEMU evidence claims physical execution")
        print("PASS: exact QEMU evidence proves the artifact fails closed without 0CF3:E009")

        physical = load_json(ROOT / "evidence" / "dell-optiplex-3060-physical-observed.json")
        require(physical["status"] == "OBSERVED-PHYSICAL-DELL-HCI-LOCAL-VERSION", "physical evidence status changed")
        for field in ("probe_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(physical["bindings"][field] == report_a[field], f"physical {field} binding changed")
        require(
            physical["observation"] == {
                "method": "owner-reviewed-photograph",
                "visible_version": "v0.1",
                "target_usb_id": "0CF3:E009",
                "interface_number": "00",
                "event_endpoint": "81",
                "command_opcode": "0x1001",
                "command_complete_status": "00",
                "hci_version": "07",
                "hci_revision": "0000",
                "lmp_version": "07",
                "manufacturer": "001D",
                "lmp_subversion": "025A",
            },
            "physical HCI observation changed",
        )
        require(
            physical["interpretation"] == {
                "hci_core_version": "Bluetooth Core Specification 4.1",
                "manufacturer_name": "Qualcomm",
                "controller_transport": "internal-usb-hci",
            },
            "physical controller interpretation changed",
        )
        require(
            physical["safety"] == {
                "hci_commands_sent": 1,
                "allowed_hci_opcodes": ["0x1001"],
                "scan_requested": False,
                "advertising_requested": False,
                "pairing_attempts": 0,
                "connection_attempts": 0,
                "radio_data_packets_sent": 0,
                "controller_resets": 0,
                "firmware_downloads": 0,
                "persistent_machine_changes": False,
            },
            "physical safety observation changed",
        )
        require(
            physical["next_boundary"] == "bounded-local-capability-query-before-any-radio-operation",
            "physical evidence opens an unexpected next boundary",
        )
        print("PASS: exact physical evidence records Qualcomm Bluetooth 4.1 identity over endpoint 81")

        over_budget = copy.deepcopy(probe)
        over_budget["limits"]["max_hci_commands"] = 2
        rejected("two HCI commands", lambda: validate_probe(over_budget))
        wrong_device = copy.deepcopy(probe)
        wrong_device["target_usb_id"] = "FFFF:FFFF"
        rejected("a substituted USB device", lambda: validate_probe(wrong_device))
        extra_opcode = copy.deepcopy(target)
        extra_opcode["authority"]["allowed_hci_opcodes"].append("0x200C")
        rejected("LE scan-enable authority", lambda: validate_target(extra_opcode))
        for field in ("controller_reset", "firmware_download", "scan", "advertise", "pair", "connect", "radio_data", "internal_storage_writes", "firmware_writes"):
            unsafe = copy.deepcopy(target)
            unsafe["authority"][field] = True
            rejected(f"target permitting {field}", lambda unsafe=unsafe: validate_target(unsafe))
        tampered = bytearray(inspect_image(image_a))
        tampered[0x200] ^= 1
        rejected("tampered machine instructions", lambda: inspect_efi(bytes(tampered), program))
        rejected("duplicate JSON fields", duplicate_json_is_rejected)
        print("PASS: device substitution, authority escalation, tamper, and ambiguous JSON are rejected")
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: physical-Dell-observed single-command Bluetooth HCI identity contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
