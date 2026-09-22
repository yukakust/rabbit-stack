#!/usr/bin/env python3
"""Verify the bounded x86-64 UEFI Bluetooth local-capability artifact."""

from __future__ import annotations

import copy
import hashlib
import struct
import tempfile
from collections.abc import Callable
from pathlib import Path

from rabbit_hci_capabilities import (
    BuildError, IMAGE_SIZE, PARTITION_LBA, PROGRAM_SHA256, PROGRAM_SIZE, PROBE_PATH, ROOT,
    SECTOR_SIZE, SOURCE_PATH, TARGET_PATH, build, load_json, load_program,
    parse_command_complete, validate_probe, validate_target,
)


EXPECTED_PROBE_SHA256 = "00e209f0b457b5f52b8b076f806d4dd8636bf854765b4556903f2245d3c35d76"
EXPECTED_TARGET_SHA256 = "92706f0913e5807c2639331f3d2f58cfaded58e195a9c3111da59d97b24eb9af"
EXPECTED_SOURCE_SHA256 = "e26575c8d816b66f955c04cbf76e7eb3f2f3d87e63d28ffd643269d4e9e9a1c1"
EXPECTED_EFI_SHA256 = "23ffeb7474d03cec04d139fa18be5e91737c40d254e6411ac8f93a54a45e6b5e"
EXPECTED_IMAGE_SHA256 = "006ed8b12843b7d91712764cc4b42462c1e192924d8a1ddb6ae05fa3232336ea"
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
    require(raw_size == 0xC00 and raw_offset == 0x200, "program section layout changed")
    require(efi[raw_offset:raw_offset + len(program)] == program, "machine bytes changed")


def inspect_program(program: bytes) -> None:
    require(len(program) == PROGRAM_SIZE, "program size changed")
    require(hashlib.sha256(program).hexdigest() == PROGRAM_SHA256, "program identity changed")
    require(program.count(USB_IO_GUID) == 1, "UEFI USB I/O GUID changed")
    require(program.count(bytes.fromhex("48 8b 46 30 ff d0")) == 1, "device descriptor call changed")
    require(program.count(bytes.fromhex("48 8b 46 40 ff d0")) == 1, "interface descriptor call changed")
    require(program.count(bytes.fromhex("48 8b 46 48 ff d0")) == 1, "endpoint descriptor call changed")
    require(program.count(bytes.fromhex("49 8b 45 00 ff d0")) == 3, "control-transfer call count changed")
    require(program.count(bytes.fromhex("49 8b 45 18 ff d0")) == 3, "interrupt-transfer call count changed")
    require(b"0CF3:E009" in program, "exact target marker changed")
    require(b"SUPPORTED COMMANDS (64B)=" in program, "supported-command marker changed")
    require(b"BR/EDR FEATURES (8B)=" in program, "BR/EDR feature marker changed")
    require(b"LE FEATURES (8B)=" in program, "LE feature marker changed")
    require(b"LOCAL CAPABILITY QUERIES: 3/3 OK" in program, "success marker changed")
    require(b"NO SCAN; NO ADVERTISE; NO PAIR; NO RADIO DATA" in program, "safety banner changed")
    require(program.count(bytes.fromhex("48 83 ec 28 ff d0 48 83 c4 28 c3")) == 1, "nested output call ABI changed")


def duplicate_json_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="rabbit-hci-capabilities-json-") as temp_dir:
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
        require(report_a["allowed_hci_opcodes"] == ["0x1002", "0x1003", "0x2003"], "opcode authority changed")
        require(report_a["max_hci_commands"] == 3, "command budget changed")
        require(report_a["max_hci_events_per_command"] == 8, "event budget changed")
        require(report_a["max_event_bytes"] == 80, "event-size budget changed")
        require(report_a["radio_packets_authorized"] == 0 and report_a["pairing_authorized"] is False, "radio authority changed")
        require(report_a["writes_performed"] == [], "builder claims physical writes")
        program = load_program()
        inspect_program(program)
        inspect_efi(inspect_image(image_a), program)
        source = SOURCE_PATH.read_text(encoding="ascii")
        require("UsbControlTransfer" in source and "UsbSyncInterruptTransfer" in source, "reviewed HCI transport path changed")
        for forbidden in ("UsbBulkTransfer", "UsbPortReset", "Reset command", "Set Scan", "Set Advertising"):
            require(forbidden not in source, f"forbidden source path appears: {forbidden}")
        print("PASS: deterministic UEFI image binds three local HCI queries to exact USB 0CF3:E009")
        print("PASS: code has three bounded control-OUT/event-IN exchanges and no reset/bulk/radio path")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")

        commands = bytes(range(64))
        commands_event = bytes((0x0E, 68, 1, 0x02, 0x10, 0)) + commands
        require(parse_command_complete(commands_event, 0x1002, 64) == commands, "supported-command parser changed")
        features = bytes.fromhex("01 02 03 04 05 06 07 08")
        features_event = bytes((0x0E, 12, 1, 0x03, 0x20, 0)) + features
        require(parse_command_complete(features_event, 0x2003, 8) == features, "feature parser changed")
        rejected("a short HCI event", lambda: parse_command_complete(features_event[:10], 0x2003, 8))
        rejected("an event for another opcode", lambda: parse_command_complete(features_event, 0x1003, 8))
        rejected("a controller error status", lambda: parse_command_complete(features_event[:5] + b"\x01" + features_event[6:], 0x2003, 8))
        print("PASS: parsers enforce exact opcode, status, 64-byte command map, and 8-byte feature maps")

        qemu = load_json(ROOT / "evidence" / "qemu-macos-arm64-observed.json")
        require(qemu["status"] == "OBSERVED-MANUAL-QEMU-LOCAL-CAPABILITIES-FAIL-CLOSED", "QEMU evidence status changed")
        for field in ("probe_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(qemu["bindings"][field] == report_a[field], f"QEMU {field} binding changed")
        require(qemu["observation"]["visible_version"] == "v0.1", "QEMU version marker changed")
        require(qemu["observation"]["visible_stage"] == "STAGE 1: FIND 0CF3:E009 INTERFACE 00", "QEMU stage changed")
        require(qemu["observation"]["result"] == "TARGET NOT FOUND; NO HCI COMMAND SENT", "QEMU fail-closed result changed")
        require(qemu["observation"]["target_found"] is False, "QEMU claims exact target")
        require(qemu["observation"]["hci_commands_sent"] == 0, "QEMU claims HCI commands")
        require(qemu["observation"]["radio_operations_requested"] == 0, "QEMU claims radio activity")
        require(qemu["execution"]["physical_execution_verified"] is False, "QEMU evidence claims physical execution")
        print("PASS: exact QEMU evidence proves all three local queries fail closed without 0CF3:E009")

        physical = load_json(ROOT / "evidence" / "dell-optiplex-3060-physical-observed.json")
        require(physical["status"] == "OBSERVED-PHYSICAL-DELL-HCI-LOCAL-CAPABILITIES", "physical evidence status changed")
        for field in ("probe_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(physical["bindings"][field] == report_a[field], f"physical {field} binding changed")
        observation = physical["observation"]
        commands = bytes.fromhex(observation["supported_commands_64b"])
        bredr = bytes.fromhex(observation["bredr_features_8b"])
        le = bytes.fromhex(observation["le_features_8b"])
        require(len(commands) == 64 and len(bredr) == 8 and len(le) == 8, "physical capability-map length changed")
        require(observation["queries_completed"] == observation["queries_expected"] == 3, "physical query count changed")
        for octet, bit, label in (
            (25, 5, "LE Set Advertising Parameters"),
            (25, 7, "LE Set Advertising Data"),
            (26, 1, "LE Set Advertising Enable"),
            (26, 2, "LE Set Scan Parameters"),
            (26, 3, "LE Set Scan Enable"),
            (26, 4, "LE Create Connection"),
        ):
            require(commands[octet] & (1 << bit), f"physical controller lacks {label}")
        require(le[0] == 0x1F and le[1:] == bytes(7), "physical LE feature map changed")
        require(physical["safety"]["radio_data_packets_sent"] == 0, "physical evidence claims radio data")
        require(physical["safety"]["scan_requested"] is False, "physical evidence claims scanning")
        require(
            physical["next_boundary"] == "bounded-receive-only-le-scan-for-one-rabbit-beacon",
            "physical evidence opens an unexpected next boundary",
        )
        print("PASS: physical evidence proves legacy BLE advertising, scanning, and connection commands are supported")

        over_budget = copy.deepcopy(probe)
        over_budget["limits"]["max_hci_commands"] = 4
        rejected("four HCI commands", lambda: validate_probe(over_budget))
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
    print("PASS: physical-Dell-observed three-command Bluetooth local-capability contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
