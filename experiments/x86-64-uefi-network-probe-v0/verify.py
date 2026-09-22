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


EXPECTED_PROBE_SHA256 = "a78eef05dc116f80351b0ed979663e33f6b458591d183de1bc5b53c4e67dd14d"
EXPECTED_TARGET_SHA256 = "46a040fe8f929bff4dc190e5a4f9bb739861c2f96fe3cc94ecfbc03781f2237e"
EXPECTED_SOURCE_SHA256 = "65a7064ad86e9f3620e1f57c9be4ce0662c159559fd29fe375f0689a87351fbc"
EXPECTED_EFI_SHA256 = "2ef0a4b872e9879769090195792de840fc8a7f53282fd5931f13b5ccf48edd2c"
EXPECTED_IMAGE_SHA256 = "cef4a46e3e3c73445f480cab1f19efc195163831f2423fb3aa7e63ed325614b4"
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
    require(
        program.count(bytes.fromhex("48 83 ec 28 ff d0 48 83 c4 28 c3")) == 1,
        "nested firmware call lacks reviewed shadow space and alignment",
    )
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
        require(
            failed["superseded_by_image_sha256"] == "d9718a582019fc7d82cd3f87048471138d450d62422ccbbf526910372a60ce5e",
            "v0.1 failure is not bound to its v0.2 replacement",
        )
        print("PASS: the slow physical v0.1 attempt is preserved as failed evidence and cannot approve v0.2")
        failed_v02 = load_json(ROOT / "evidence" / "dell-optiplex-3060-v0.2-failed.json")
        require(failed_v02["status"] == "FAILED-SAFE-BEFORE-FIRST-TEXT", "v0.2 physical failure status changed")
        require(failed_v02["recovery"]["persistent_machine_changes"] is False, "v0.2 failure claims persistent changes")
        require(
            failed_v02["superseded_by_image_sha256"]
            == "afac5e6d866fcb6e0e7bd770d37bc77b755837dd0bdb2a8553aabd07ef502a61",
            "v0.2 failure is not bound to v0.3",
        )
        print("PASS: the dark physical v0.2 attempt is preserved and cannot approve staged-text v0.3")

        failed_v03 = load_json(ROOT / "evidence" / "dell-optiplex-3060-v0.3-failed.json")
        require(failed_v03["status"] == "FAILED-SAFE-BEFORE-FIRST-STAGE", "v0.3 physical failure status changed")
        require(failed_v03["observation"]["stage_1_visible"] is False, "v0.3 failure suddenly claims stage output")
        require(failed_v03["observation"]["cause_confirmed"] is False, "v0.3 hypothesis is mislabeled as confirmed")
        require(failed_v03["recovery"]["persistent_machine_changes"] is False, "v0.3 failure claims persistent changes")
        require(failed_v03["superseded_by_image_sha256"] == report_a["image_sha256"], "v0.3 failure is not bound to v0.4")
        print("PASS: the dark physical v0.3 attempt is preserved and its ABI diagnosis remains a hypothesis")

        qemu_v03 = load_json(ROOT / "evidence" / "qemu-macos-arm64-v0.3-observed.json")
        require(qemu_v03["status"] == "OBSERVED-MANUAL-QEMU-STAGED-NETWORK-PROBE", "v0.3 QEMU status changed")
        require(qemu_v03["bindings"]["probe_sha256"] == "e48f50e41c9ecc134bbb64cefb936414c5a93862d29d169a8ed3756af587d8d5", "v0.3 QEMU probe binding changed")
        require(qemu_v03["bindings"]["target_sha256"] == EXPECTED_TARGET_SHA256, "v0.3 QEMU target binding changed")
        require(qemu_v03["bindings"]["program_sha256"] == "eaf88bd663d5f51753bf31c559ed39887ccaf23825643cd4a327c9ca75787f67", "v0.3 QEMU program binding changed")
        require(qemu_v03["bindings"]["efi_sha256"] == "4547120eae006c8fcddb96f7a3956a9fa9ea19ee5ef63bd0dcd4bddad39b150d", "v0.3 QEMU EFI binding changed")
        require(qemu_v03["bindings"]["image_sha256"] == "afac5e6d866fcb6e0e7bd770d37bc77b755837dd0bdb2a8553aabd07ef502a61", "v0.3 QEMU image binding changed")
        require(
            qemu_v03["observation"]["visible_stages"]
            == ["STAGE 1: TEXT OK", "STAGE 2: PROTOCOL CHECKS", "STAGE 3: PCI HANDLES"],
            "v0.3 stage evidence changed",
        )
        require(qemu_v03["observation"]["uefi_simple_network"] is True, "v0.3 SNP observation changed")
        require(qemu_v03["observation"]["uefi_wifi_v1"] is False, "v0.3 Wi-Fi v1 observation changed")
        require(qemu_v03["observation"]["uefi_wifi_v2"] is False, "v0.3 Wi-Fi v2 observation changed")
        require(qemu_v03["observation"]["total"] == 1, "v0.3 PCI controller count changed")
        require(qemu_v03["physical_dell_status"] == "NOT-OBSERVED-WITH-V0.3", "v0.3 evidence overclaims physical execution")
        require(qemu_v03["execution"]["physical_execution_verified"] is False, "v0.3 QEMU evidence claims physical execution")
        print("PASS: exact historical v0.3 QEMU evidence cannot approve ABI-corrected v0.4")

        qemu_v04 = load_json(ROOT / "evidence" / "qemu-macos-arm64-observed.json")
        require(qemu_v04["status"] == "OBSERVED-MANUAL-QEMU-ABI-CORRECTED-NETWORK-PROBE", "v0.4 QEMU status changed")
        for field in ("probe_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(qemu_v04["bindings"][field] == report_a[field], f"v0.4 QEMU {field} binding changed")
        require(qemu_v04["observation"]["visible_version"] == "v0.4", "v0.4 version marker changed")
        require(
            qemu_v04["observation"]["visible_stages"]
            == ["STAGE 1: TEXT OK", "STAGE 2: PROTOCOL CHECKS", "STAGE 3: PCI HANDLES"],
            "v0.4 stage evidence changed",
        )
        require(qemu_v04["observation"]["uefi_simple_network"] is True, "v0.4 SNP observation changed")
        require(qemu_v04["observation"]["uefi_wifi_v1"] is False, "v0.4 Wi-Fi v1 observation changed")
        require(qemu_v04["observation"]["uefi_wifi_v2"] is False, "v0.4 Wi-Fi v2 observation changed")
        require(qemu_v04["observation"]["total"] == 1, "v0.4 PCI controller count changed")
        require(qemu_v04["physical_dell_status"] == "NOT-OBSERVED-WITH-V0.4", "v0.4 evidence overclaims physical execution")
        require(qemu_v04["execution"]["physical_execution_verified"] is False, "v0.4 QEMU evidence claims physical execution")
        print("PASS: exact v0.4 QEMU evidence shows the ABI-corrected path and makes no physical claim")

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
    print("PASS: QEMU-observed ABI-corrected v0.4 read-only network discovery contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
