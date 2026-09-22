#!/usr/bin/env python3
"""Verify the read-only x86-64 UEFI USB/Bluetooth discovery artifact."""

from __future__ import annotations

import copy
import hashlib
import json
import struct
import tempfile
from collections.abc import Callable
from pathlib import Path

from rabbit_bluetooth_probe import (
    BuildError, IMAGE_SIZE, PARTITION_LBA, PROGRAM_SHA256, PROGRAM_SIZE, PROBE_PATH, ROOT,
    SECTOR_SIZE, SOURCE_PATH, TARGET_PATH, build, load_json, load_program,
    validate_probe, validate_target,
)


EXPECTED_PROBE_SHA256 = "69741ff58157e88b4f8b59a01cbd1e57979d7ae34ecee65385ca817cb7ab0e96"
EXPECTED_TARGET_SHA256 = "af9b486ceca68af2fe65b808aaa37bcdce10aed7f292948b06eb851b1c7b6b64"
EXPECTED_SOURCE_SHA256 = "041ae6a93a269b9e118bd38671fb394ecc758f19e23e80992f79897cc24d6003"
EXPECTED_EFI_SHA256 = "9c143212037c6368187f4daecf09b360a8f6d1689146a1e2c7ef7ae9706c1c34"
EXPECTED_IMAGE_SHA256 = "15bc2c6e19236bbb0a1f2823eda0ab89f55a93b51b682d81e53e85db8e5d69a2"
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
    require(raw_size == 0x600 and raw_offset == 0x200, "program section layout changed")
    require(efi[raw_offset:raw_offset + len(program)] == program, "machine bytes changed")


def inspect_program(program: bytes) -> None:
    require(len(program) == PROGRAM_SIZE, "program size changed")
    require(hashlib.sha256(program).hexdigest() == PROGRAM_SHA256, "program identity changed")
    require(program.count(USB_IO_GUID) == 1, "UEFI USB I/O GUID changed")
    require(bytes.fromhex("48 8b 87 38 01 00 00 ff d0") in program, "LocateHandleBuffer path changed")
    require(bytes.fromhex("48 8b 87 98 00 00 00 ff d0") in program, "HandleProtocol path changed")
    require(program.count(bytes.fromhex("48 8b 46 30 ff d0")) == 1, "device descriptor call changed")
    require(program.count(bytes.fromhex("48 8b 46 40 ff d0")) == 1, "interface descriptor call changed")
    require(bytes.fromhex("48 8b 47 48 ff d0") in program, "temporary handle-buffer cleanup changed")
    require(
        program.count(bytes.fromhex("48 83 ec 28 ff d0 48 83 c4 28 c3")) == 1,
        "nested firmware call lacks reviewed shadow space and alignment",
    )
    require(b"READ-ONLY DESCRIPTORS; RADIO OFF" in program, "safety banner changed")
    require(b"BLUETOOTH CANDIDATES:" in program, "Bluetooth result format changed")
    require(b"PHOTOGRAPH THIS SCREEN" in program, "observation instruction changed")


def is_bluetooth(device: tuple[int, int, int], interface: tuple[int, int, int]) -> bool:
    return device == (0xE0, 0x01, 0x01) or interface == (0xE0, 0x01, 0x01)


def duplicate_json_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="rabbit-bt-json-") as temp_dir:
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
        require(report_a["source_sha256"] == EXPECTED_SOURCE_SHA256, "review source changed")
        require(report_a["program_sha256"] == PROGRAM_SHA256, "program report changed")
        require(report_a["efi_sha256"] == EXPECTED_EFI_SHA256, "EFI identity changed")
        require(report_a["image_sha256"] == EXPECTED_IMAGE_SHA256, "image identity changed")
        require(report_a["usb_descriptor_reads_authorized"] is True, "descriptor reads are not explicit")
        require(report_a["usb_data_transfers"] == 0, "probe claims USB data transfer")
        require(report_a["bluetooth_hci_commands"] == 0, "probe claims Bluetooth HCI commands")
        require(report_a["radio_packets_sent"] == 0, "probe claims radio transmission")
        require(report_a["configuration_data_writes"] == 0, "probe claims configuration writes")
        require(report_a["writes_performed"] == [], "builder claims physical writes")
        program = load_program()
        inspect_program(program)
        inspect_efi(inspect_image(image_a), program)
        source = SOURCE_PATH.read_text(encoding="ascii")
        require("UsbGetDeviceDescriptor" in source and "UsbGetInterfaceDescriptor" in source, "descriptor source path changed")
        for forbidden in ("UsbControlTransfer", "UsbBulkTransfer", "UsbPortReset", "HCI command", "radio transmit"):
            require(forbidden not in source, f"forbidden source path appears: {forbidden}")
        print("PASS: deterministic UEFI image reads only USB device and interface descriptors")
        print("PASS: machine bytes contain no reviewed path for USB data, reset, HCI, pairing, or radio transmit")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")

        require(is_bluetooth((0xE0, 0x01, 0x01), (0, 0, 0)), "device-level Bluetooth triple missed")
        require(is_bluetooth((0, 0, 0), (0xE0, 0x01, 0x01)), "interface-level Bluetooth triple missed")
        require(not is_bluetooth((0, 0, 0), (0x03, 0x01, 0x01)), "USB keyboard misclassified as Bluetooth")
        require(not is_bluetooth((0, 0, 0), (0x08, 0x06, 0x50)), "USB storage misclassified as Bluetooth")
        print("PASS: Bluetooth class matching accepts device/interface E0/01/01 and rejects keyboard/storage")

        qemu = load_json(ROOT / "evidence" / "qemu-macos-arm64-observed.json")
        require(qemu["status"] == "OBSERVED-MANUAL-QEMU-USB-BLUETOOTH-PROBE", "QEMU evidence status changed")
        for field in ("probe_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(qemu["bindings"][field] == report_a[field], f"QEMU {field} binding changed")
        require(qemu["observation"]["visible_version"] == "v0.1", "QEMU version marker changed")
        require(
            qemu["observation"]["usb_interfaces"]
            == [{
                "vendor_id": "0627",
                "product_id": "0001",
                "device_class": "00/00/00",
                "interface_number": "00",
                "interface_class": "03/01/01",
                "bluetooth_candidate": False,
            }],
            "QEMU USB keyboard observation changed",
        )
        require(qemu["observation"]["described_interfaces"] == 1, "QEMU interface count changed")
        require(qemu["observation"]["bluetooth_candidates"] == 0, "QEMU Bluetooth count changed")
        require(qemu["physical_dell_status"] == "NOT-OBSERVED", "QEMU evidence overclaims physical Dell")
        require(qemu["execution"]["physical_execution_verified"] is False, "QEMU evidence claims physical execution")
        print("PASS: exact QEMU evidence classifies the USB keyboard as non-Bluetooth and makes no physical claim")

        physical = load_json(ROOT / "evidence" / "dell-optiplex-3060-physical-observed.json")
        require(physical["status"] == "OBSERVED-PHYSICAL-DELL-USB-BLUETOOTH-INVENTORY", "physical evidence status changed")
        for field in ("probe_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(physical["bindings"][field] == report_a[field], f"physical {field} binding changed")
        require(physical["observation"]["visible_version"] == "v0.1", "physical version marker changed")
        require(physical["observation"]["described_interfaces"] == 5, "physical interface count changed")
        require(physical["observation"]["bluetooth_candidates"] == 2, "physical Bluetooth candidate count changed")
        require(physical["observation"]["distinct_bluetooth_devices"] == ["0CF3:E009"], "physical Bluetooth device changed")
        candidates = [
            item for item in physical["observation"]["usb_interfaces"]
            if item["bluetooth_candidate"]
        ]
        require(len(candidates) == 2, "physical Bluetooth interface evidence changed")
        require({(item["vendor_id"], item["product_id"]) for item in candidates} == {("0CF3", "E009")}, "physical Bluetooth identity changed")
        require({item["interface_number"] for item in candidates} == {"00", "01"}, "physical Bluetooth interfaces changed")
        require(
            physical["safety"]
            == {
                "usb_data_transfers": 0,
                "usb_port_resets": 0,
                "bluetooth_hci_commands": 0,
                "bluetooth_pairing_attempts": 0,
                "radio_packets_sent": 0,
                "persistent_machine_changes": False,
            },
            "physical safety evidence changed",
        )
        print("PASS: exact physical evidence identifies one QCA Rome USB device with two Bluetooth interfaces")

        mutated = copy.deepcopy(probe)
        mutated["mutations"] = ["enable-bluetooth"]
        rejected("a probe that enables Bluetooth", lambda: validate_probe(mutated))
        over_budget = copy.deepcopy(probe)
        over_budget["limits"]["max_usb_interfaces"] = 65535
        rejected("an unbounded USB inventory", lambda: validate_probe(over_budget))
        for field in ("usb_data_transfers", "usb_port_reset", "bluetooth_hci_commands", "bluetooth_pairing", "radio_transmit", "configuration_writes"):
            unsafe = copy.deepcopy(target)
            unsafe["probe_policy"][field] = True
            rejected(f"target permitting {field}", lambda unsafe=unsafe: validate_target(unsafe))
        internal = copy.deepcopy(target)
        internal["installation_policy"]["internal_storage_writes"] = True
        rejected("internal-disk writes", lambda: validate_target(internal))
        tampered = bytearray(inspect_image(image_a))
        tampered[0x200] ^= 1
        rejected("tampered probe instructions", lambda: inspect_efi(bytes(tampered), program))
        rejected("duplicate JSON fields", duplicate_json_is_rejected)
        print("PASS: mutation, budget, transfer, reset, HCI, pairing, radio, storage, and tamper rejection is intact")
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: physical-Dell-observed read-only UEFI USB/Bluetooth inventory contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
