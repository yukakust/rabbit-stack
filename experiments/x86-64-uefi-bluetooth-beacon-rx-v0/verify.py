#!/usr/bin/env python3
"""Verify the bounded receive-only x86-64 UEFI Rabbit BLE beacon artifact."""

from __future__ import annotations

import copy
import hashlib
import struct
import tempfile
from collections.abc import Callable
from pathlib import Path

from rabbit_beacon_rx import (
    BuildError, IMAGE_SIZE, PARTITION_LBA, PROGRAM_SHA256, PROGRAM_SIZE, PROBE_PATH,
    RABBIT_UUID, RABBIT_UUID_LE, SECTOR_SIZE, SOURCE_PATH, TARGET_PATH, build,
    contains_rabbit_uuid, load_json, load_program, parse_command_complete,
    validate_probe, validate_target,
)


ROOT = Path(__file__).resolve().parent
EXPECTED_PROBE_SHA256 = "5af8faf2d75190d264a213235fce17a0e20c1674965ff00f1a2eb6ff86cce3e8"
EXPECTED_TARGET_SHA256 = "e122e120d12783ebec3dc5f9496576c04b333040db5694008d2956b86df6d937"
EXPECTED_SOURCE_SHA256 = "f712de757b8fd76d0955da9a6ca3fe32feca3c58a245adfb1cd12c376321e743"
EXPECTED_EFI_SHA256 = "8b9df03b61e21319c1d0329d185b080d17962a1b3763424ddb0d6ddc98c62840"
EXPECTED_IMAGE_SHA256 = "0fa4c4ce888d9a2ba916898f1ab43f579b92b52553d7f6a96b44fabddc2dd50c"
EXPECTED_MAC_SOURCE_SHA256 = "f72103e7234b291c6c1733ad7cd64800a44834122d200571e2d3c26ea97e2c76"
EXPECTED_PLIST_SHA256 = "1312d38dbb8a06a36e97f01b9fea7558a709a6ad5a81d8a741798fcc0ef1f121"
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
    require(raw_size == 0xE00 and raw_offset == 0x200, "program section layout changed")
    require(efi[raw_offset:raw_offset + len(program)] == program, "machine bytes changed")


def inspect_program(program: bytes) -> None:
    require(len(program) == PROGRAM_SIZE, "program size changed")
    require(hashlib.sha256(program).hexdigest() == PROGRAM_SHA256, "program identity changed")
    require(program.count(USB_IO_GUID) == 1, "UEFI USB I/O GUID changed")
    require(program.count(bytes.fromhex("48 8b 46 30 ff d0")) == 1, "device descriptor call changed")
    require(program.count(bytes.fromhex("48 8b 46 40 ff d0")) == 1, "interface descriptor call changed")
    require(program.count(bytes.fromhex("48 8b 46 48 ff d0")) == 1, "endpoint descriptor call changed")
    require(program.count(bytes.fromhex("49 8b 45 00 ff d0")) == 5, "control-transfer call count changed")
    require(program.count(bytes.fromhex("49 8b 45 18 ff d0")) == 6, "interrupt-transfer call count changed")
    require(program.count(RABBIT_UUID) == 1 and program.count(RABBIT_UUID_LE) == 1, "Rabbit UUID markers changed")
    require(bytes.fromhex("0b 20 07 00 10 00 10 00 00 00") in program, "passive scan parameters changed")
    require(bytes.fromhex("0c 20 02 01 00") in program, "scan-enable packet changed")
    require(bytes.fromhex("0c 20 02 00 00") in program, "scan-disable packet changed")
    require(b"PASSIVE RECEIVE ONLY; NO PAIR OR CONNECT" in program, "receive-only banner changed")
    require(b"RABBIT BEACON RECEIVED" in program, "success marker changed")
    require(b"NO PAIR; NO CONNECT; NO RADIO TRANSMIT" in program, "safety marker changed")
    require(program.count(bytes.fromhex("48 83 ec 28 ff d0 48 83 c4 28 c3")) == 1, "nested output call ABI changed")


def advertising_event(uuid: bytes) -> bytes:
    ad = bytes((17, 0x07)) + uuid
    parameters = bytes((0x02, 1, 0, 0)) + bytes.fromhex("01 02 03 04 05 06") + bytes((len(ad),)) + ad + bytes((0xC0,))
    return bytes((0x3E, len(parameters))) + parameters


def duplicate_json_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="rabbit-beacon-rx-json-") as temp_dir:
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
        require(report_a["max_hci_commands"] == 5 and report_a["max_scan_events"] == 100, "runtime budget changed")
        require(report_a["max_scan_duration_ms"] == 20000 and report_a["max_event_bytes"] == 80, "scan bound changed")
        require(report_a["radio_receive_authorized"] is True, "radio receive is not explicit")
        require(report_a["radio_transmit_authorized"] is False, "radio transmit authority changed")
        require(report_a["pairing_authorized"] is False and report_a["connection_authorized"] is False, "pair/connect authority changed")
        require(report_a["writes_performed"] == [], "builder claims physical writes")
        program = load_program()
        inspect_program(program)
        inspect_efi(inspect_image(image_a), program)
        print("PASS: deterministic image binds one exact Rabbit UUID to a 20-second passive scan")
        print("PASS: exact packets enable receive-only scanning and always include scan disable")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")

        complete = bytes.fromhex("0e 04 01 0c 20 00")
        require(parse_command_complete(complete, 0x200C) is None, "Command Complete parser changed")
        rejected("a short Command Complete", lambda: parse_command_complete(complete[:5], 0x200C))
        rejected("a Command Complete for another opcode", lambda: parse_command_complete(complete, 0x200B))
        rejected("a controller error status", lambda: parse_command_complete(complete[:5] + b"\x01", 0x200C))
        require(contains_rabbit_uuid(advertising_event(RABBIT_UUID_LE)), "little-endian Rabbit UUID was not accepted")
        require(contains_rabbit_uuid(advertising_event(RABBIT_UUID)), "canonical Rabbit UUID was not accepted")
        require(not contains_rabbit_uuid(advertising_event(bytes(16))), "foreign UUID was accepted")
        require(not contains_rabbit_uuid(b"\x0e\x04\x01\x0c\x20\x00" + RABBIT_UUID), "non-advertising event was accepted")
        print("PASS: event parser accepts only the Rabbit UUID inside an LE Advertising Report")

        mac_source = ROOT / "mac_beacon.swift"
        plist = ROOT / "RabbitBeacon-Info.plist"
        require(hashlib.sha256(mac_source.read_bytes()).hexdigest() == EXPECTED_MAC_SOURCE_SHA256, "Mac beacon source changed")
        require(hashlib.sha256(plist.read_bytes()).hexdigest() == EXPECTED_PLIST_SHA256, "Mac beacon permission manifest changed")
        require("52414242-4954-4C45-8000-000000000001" in mac_source.read_text(), "Mac Rabbit UUID changed")
        require("CBAdvertisementDataServiceUUIDsKey" in mac_source.read_text(), "Mac beacon no longer advertises a service UUID")
        print("PASS: reviewed Mac CoreBluetooth sender advertises the exact same Rabbit UUID")

        qemu = load_json(ROOT / "evidence" / "qemu-macos-arm64-observed.json")
        require(qemu["status"] == "OBSERVED-MANUAL-QEMU-BEACON-RX-FAIL-CLOSED", "QEMU evidence status changed")
        for field in ("probe_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(qemu["bindings"][field] == report_a[field], f"QEMU {field} binding changed")
        require(qemu["observation"]["visible_version"] == "v0.1", "QEMU version marker changed")
        require(qemu["observation"]["visible_mode"] == "PASSIVE RECEIVE ONLY; NO PAIR OR CONNECT", "QEMU mode marker changed")
        require(qemu["observation"]["visible_stage"] == "STAGE 1: FIND 0CF3:E009 INTERFACE 00", "QEMU stage changed")
        require(qemu["observation"]["result"] == "TARGET NOT FOUND; NO HCI COMMAND SENT", "QEMU fail-closed result changed")
        require(qemu["observation"]["hci_commands_sent"] == 0, "QEMU claims HCI commands")
        require(qemu["observation"]["passive_scan_started"] is False, "QEMU claims passive scanning")
        require(qemu["observation"]["radio_operations_requested"] == 0, "QEMU claims radio activity")
        require(qemu["execution"]["physical_execution_verified"] is False, "QEMU evidence claims physical execution")
        print("PASS: exact QEMU evidence proves the receiver fails closed before HCI and radio")

        over_budget = copy.deepcopy(probe)
        over_budget["limits"]["max_scan_events"] = 101
        rejected("an unbounded scan extension", lambda: validate_probe(over_budget))
        wrong_uuid = copy.deepcopy(probe)
        wrong_uuid["rabbit_service_uuid"] = "00000000-0000-0000-0000-000000000000"
        rejected("a substituted beacon UUID", lambda: validate_probe(wrong_uuid))
        active = copy.deepcopy(target)
        active["authority"]["active_scan"] = True
        rejected("active scanning", lambda: validate_target(active))
        for field in ("radio_transmit", "advertise", "pair", "connect", "controller_reset", "firmware_download", "internal_storage_writes", "firmware_writes"):
            unsafe = copy.deepcopy(target)
            unsafe["authority"][field] = True
            rejected(f"target permitting {field}", lambda unsafe=unsafe: validate_target(unsafe))
        missing_disable = copy.deepcopy(target)
        missing_disable["authority"]["allowed_hci_command_sequence"].pop()
        rejected("a command sequence without scan disable", lambda: validate_target(missing_disable))
        tampered = bytearray(inspect_image(image_a))
        tampered[0x200] ^= 1
        rejected("tampered machine instructions", lambda: inspect_efi(bytes(tampered), program))
        rejected("duplicate JSON fields", duplicate_json_is_rejected)
        print("PASS: active scan, transmit, pairing, connection, missing cleanup, tamper, and ambiguity are rejected")
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: QEMU-observed receive-only Rabbit BLE beacon contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
