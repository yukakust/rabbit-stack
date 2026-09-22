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


EXPECTED_PROBE_SHA256 = "c8571ac94a3c901cbf393b024fbb1069736547c09d24b891c526e830f8b089aa"
EXPECTED_TARGET_SHA256 = "46a040fe8f929bff4dc190e5a4f9bb739861c2f96fe3cc94ecfbc03781f2237e"
EXPECTED_SOURCE_SHA256 = "c9171e5cd77cbbda0565937978511a99b2fa63a5257b46c254a6ef76430d16e2"
EXPECTED_EFI_SHA256 = "3711e4dac38dab0b9f7580da3f4166f5cc5fce31a3720eea6dedcb6e840820aa"
EXPECTED_IMAGE_SHA256 = "d9718a582019fc7d82cd3f87048471138d450d62422ccbbf526910372a60ce5e"
SNP_GUID = bytes.fromhex("b9 32 98 a1 25 ac d3 11 9a 2d 00 90 27 3f c1 4d")
WIFI1_GUID = bytes.fromhex("c9 5b a5 0d f8 45 b4 4b 87 19 52 24 f1 8a 4d 45")
WIFI2_GUID = bytes.fromhex("bf b9 0f 1b 9d 69 dd 4f a7 c3 25 46 68 1b f6 3b")
PCI_IO_GUID = bytes.fromhex("00 b2 f5 4c b8 68 a5 4c 9e ec b2 3e 3f 50 02 9a")


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
    for guid in (SNP_GUID, WIFI1_GUID, WIFI2_GUID, PCI_IO_GUID):
        require(program.count(guid) == 1, "reviewed network protocol GUID changed")
    require(bytes.fromhex("48 8b 87 38 01 00 00 ff d0") in program, "LocateHandleBuffer path changed")
    require(bytes.fromhex("48 8b 87 98 00 00 00 ff d0") in program, "HandleProtocol path changed")
    require(bytes.fromhex("48 8b 46 30 ff d0") in program, "Pci.Read path changed")
    require(bytes.fromhex("48 8b 46 70 ff d0") in program, "Pci.GetLocation path changed")
    require(bytes.fromhex("48 8b 47 48 ff d0") in program, "temporary handle-buffer cleanup changed")
    require(bytes.fromhex("66 ba f8 0c ef") not in program, "legacy brute-force PCI I/O remains")
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
        source = SOURCE_PATH.read_bytes()
        require(b"LocateHandleBuffer" in source and b"Pci.Read" in source, "auditable firmware PCI path changed")
        require(b"out dx" not in source and b"in eax" not in source, "source still performs direct PCI port scanning")
        print("PASS: deterministic UEFI image checks SNP, Wi-Fi v1/v2, and PCI network identities")
        print("PASS: reviewed code enumerates only firmware-present PCI I/O handles and frees its temporary buffer")
        print("PASS: probe sends and receives no network packets and performs no persistent machine writes")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")
        failed = load_json(ROOT / "evidence" / "dell-optiplex-3060-v0.1-failed.json")
        require(failed["status"] == "FAILED-SAFE-PCI-BRUTE-FORCE-TIMEOUT", "physical failure status changed")
        require(failed["recovery"]["persistent_machine_changes"] is False, "failure evidence claims persistent changes")
        require(failed["superseded_by_image_sha256"] == report_a["image_sha256"], "failure is not bound to replacement image")
        print("PASS: the slow physical v0.1 attempt is preserved as failed evidence and cannot approve v0.2")

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
    print("PASS: pre-QEMU v0.2 read-only network discovery contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
