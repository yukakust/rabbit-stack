#!/usr/bin/env python3
"""Verify the read-only x86-64 UEFI network discovery artifact."""

from __future__ import annotations

import copy
import hashlib
import struct
from collections.abc import Callable

from rabbit_network_probe import (
    BuildError, IMAGE_SIZE, PARTITION_LBA, PROGRAM_SHA256, PROGRAM_SIZE, PROBE_PATH, ROOT,
    SECTOR_SIZE, SOURCE_PATH, TARGET_PATH, build, load_json, load_program,
    validate_probe, validate_target,
)


EXPECTED_PROBE_SHA256 = "532488524036c2f59fdb70d498ab017a144b5981501813bf58d5c49c553cd2af"
EXPECTED_TARGET_SHA256 = "aa5951299999243680b62569cd62fbc74ddef6af53c1caf6c0f425a1cccca36f"
EXPECTED_SOURCE_SHA256 = "7436da89ea1c19f91ccc4a9ce20c9e86e93fd3fa7945bfaea19ecb581be1d403"
EXPECTED_EFI_SHA256 = "d48db92f82e10642f980906379d4dd11db20f51754d46886f3ca35cb9b8efd8f"
EXPECTED_IMAGE_SHA256 = "a6a34c676d6772cfd378397e312f4d99faf4a233b8a20307420503864fc35598"
SNP_GUID = bytes.fromhex("b9 32 98 a1 25 ac d3 11 9a 2d 00 90 27 3f c1 4d")
WIFI1_GUID = bytes.fromhex("c9 5b a5 0d f8 45 b4 4b 87 19 52 24 f1 8a 4d 45")
WIFI2_GUID = bytes.fromhex("bf b9 0f 1b 9d 69 dd 4f a7 c3 25 46 68 1b f6 3b")


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
    require(program.count(b"\x48\x8b\x87\x40\x01\x00\x00\xff\xd0") == 3, "LocateProtocol checks changed")
    for guid in (SNP_GUID, WIFI1_GUID, WIFI2_GUID):
        require(program.count(guid) == 1, "reviewed network protocol GUID changed")
    require(program.count(bytes.fromhex("66 ba f8 0c ef")) == 2, "PCI address-selection path changed")
    require(program.count(bytes.fromhex("66 ba fc 0c ed")) == 2, "PCI data-read path changed")
    require(bytes.fromhex("66 ba fc 0c ef") not in program, "program writes PCI configuration data")
    require(b"PCI NETWORK CONTROLLERS:\r\n" in program, "PCI result format changed")
    require(b"PHOTOGRAPH THIS SCREEN" in program, "observation instruction changed")


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
        require(report_a["network_packets_sent"] == 0, "probe claims network transmission")
        require(report_a["configuration_data_writes"] == 0, "probe claims PCI configuration writes")
        require(report_a["writes_performed"] == [], "builder claims physical writes")
        program = load_program()
        inspect_program(program)
        inspect_efi(inspect_image(image_a), program)
        require(b"out dx, eax" in SOURCE_PATH.read_bytes(), "auditable source lost PCI selector operation")
        observed = load_json(ROOT / "evidence" / "qemu-macos-arm64-observed.json")
        require(observed["status"] == "OBSERVED-MANUAL-QEMU-NETWORK-PROBE", "QEMU evidence status changed")
        require(
            observed["bindings"] == {
                "probe_sha256": report_a["probe_sha256"],
                "target_sha256": report_a["target_sha256"],
                "program_sha256": report_a["program_sha256"],
                "efi_sha256": report_a["efi_sha256"],
                "image_sha256": report_a["image_sha256"],
            },
            "QEMU evidence is stale or bound to another probe",
        )
        observation = observed["observation"]
        require(observation["uefi_simple_network"] is True, "QEMU did not expose Simple Network")
        require(observation["uefi_wifi_v1"] is False and observation["uefi_wifi_v2"] is False, "QEMU Wi-Fi observation changed")
        require(
            observation["pci_network_controllers"] == [
                {"bus": 0, "device": 2, "function": 0, "vendor_id": "8086", "device_id": "10D3", "subclass": "00"}
            ] and observation["total"] == 1,
            "QEMU PCI observation changed",
        )
        require(observed["execution"]["physical_execution_verified"] is False, "QEMU evidence claims physical execution")
        require(observed["physical_dell_status"] == "NOT-OBSERVED-YET", "physical Dell status is overstated")
        print("PASS: deterministic UEFI image checks SNP, Wi-Fi v1/v2, and PCI network identities")
        print("PASS: reviewed code writes only the PCI address selector and reads PCI configuration data")
        print("PASS: probe sends and receives no network packets and performs no persistent machine writes")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")
        print("PASS: QEMU observed SNP=YES, Wi-Fi v1/v2=NO, and emulated 8086:10D3; Dell remains unobserved")

        mutated = copy.deepcopy(probe)
        mutated["mutations"] = ["connect-wifi"]
        rejected("discovery that connects to Wi-Fi", lambda: validate_probe(mutated))
        transmitting = copy.deepcopy(target)
        transmitting["probe_policy"]["network_transmit"] = True
        rejected("a probe target allowed to transmit", lambda: validate_target(transmitting))
        config_write = copy.deepcopy(target)
        config_write["probe_policy"]["configuration_data_writes"] = True
        rejected("PCI configuration writes", lambda: validate_target(config_write))
        internal = copy.deepcopy(target)
        internal["installation_policy"]["internal_storage_writes"] = True
        rejected("internal-disk writes", lambda: validate_target(internal))
        tampered = bytearray(inspect_image(image_a))
        tampered[0x200] ^= 1
        rejected("tampered probe instructions", lambda: inspect_efi(bytes(tampered), program))
        print("PASS: mutation, transmission, configuration-write, storage, and tamper rejection is intact")
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: QEMU-gated read-only network discovery contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
