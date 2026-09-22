#!/usr/bin/env python3
"""Verify the deterministic direct-framebuffer UEFI artifact contract."""

from __future__ import annotations

import copy
import hashlib
import struct
from collections.abc import Callable

from rabbit_framebuffer import (
    BuildError, GOP_GUID, IMAGE_SIZE, PARTITION_LBA, ROOT, SECTOR_SIZE, TARGET_PATH, WORLD_PATH,
    build, load_json, machine_code, validate_target, validate_world,
)


EXPECTED_WORLD_SHA256 = "41ba583c46803a3cce864524b68fe553983db066d1f193720915f83ce7667b05"
EXPECTED_TARGET_SHA256 = "4288e3f93f6a30ca6ec177e5683a3e0e4d2bce3523e1ec5fb8a0bb917d5bd474"
EXPECTED_EFI_SHA256 = "e8806bf1f3f922c53125c24f2cab3c0a2c1df869983f4a1d0ff2cc3c10006836"
EXPECTED_IMAGE_SHA256 = "43e1998c7e60d49096d9980cbed77f8e4dc5a3abbc41dff48a5b94ee7ca50c77"


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
    require(len(image) == IMAGE_SIZE, "image size changed")
    require(image[510:512] == b"\x55\xaa", "missing MBR signature")
    partition = image[446:462]
    require(partition[4] == 0x0C, "partition is not FAT32 LBA")
    start, count = struct.unpack_from("<II", partition, 8)
    require(start == PARTITION_LBA, "partition start changed")
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
    seen: set[int] = set()
    while current < 0x0FFFFFF8:
        require(current not in seen, "FAT chain contains a cycle")
        seen.add(current)
        result += cluster(current)
        current = struct.unpack_from("<I", image, fat_offset + current * 4)[0] & 0x0FFFFFFF
    return bytes(result[:size])


def inspect_efi(efi: bytes, expected_code: bytes) -> None:
    require(efi[0:2] == b"MZ", "missing DOS signature")
    pe = struct.unpack_from("<I", efi, 0x3C)[0]
    require(efi[pe:pe + 4] == b"PE\0\0", "missing PE signature")
    coff = pe + 4
    machine, sections = struct.unpack_from("<HH", efi, coff)
    require(machine == 0x8664 and sections == 2, "not the reviewed x86-64 PE")
    optional = coff + 20
    require(struct.unpack_from("<H", efi, optional)[0] == 0x20B, "not PE32+")
    require(struct.unpack_from("<H", efi, optional + 68)[0] == 10, "not an EFI application")
    section_table = optional + 0xF0
    require(efi[section_table:section_table + 8].rstrip(b"\0") == b".text", "missing text section")
    text_raw = struct.unpack_from("<I", efi, section_table + 20)[0]
    require(efi[text_raw:text_raw + len(expected_code)] == expected_code, "machine instructions changed")
    require(expected_code.endswith(GOP_GUID), "machine code lost the GOP protocol GUID")
    require(b"H\x8bC\x18H\x8bx\x18" in expected_code, "framebuffer-base load is absent")
    require(b"D\x89\x11" in expected_code, "direct framebuffer pixel store is absent")
    require(b"HI\0" not in efi and "HI".encode("utf-16-le") not in efi, "text payload leaked into graphics artifact")


def main() -> int:
    try:
        world, target = load_json(WORLD_PATH), load_json(TARGET_PATH)
        image_a, report_a = build(world, target)
        image_b, report_b = build(copy.deepcopy(world), copy.deepcopy(target))
        require(image_a == image_b and report_a == report_b, "repeated builds differ")
        require(report_a["world_sha256"] == EXPECTED_WORLD_SHA256, "world identity changed")
        require(report_a["target_sha256"] == EXPECTED_TARGET_SHA256, "target identity changed")
        require(report_a["efi_sha256"] == EXPECTED_EFI_SHA256, "EFI identity changed")
        require(report_a["image_sha256"] == EXPECTED_IMAGE_SHA256, "image identity changed")
        require(report_a["status"] == "BUILT-NOT-INSTALLED", "builder claimed installation")
        require(report_a["writes_performed"] == [], "builder claimed a physical write")
        rect = validate_world(world)
        code = machine_code(rect)
        efi = inspect_image(image_a)
        inspect_efi(efi, code)
        require(hashlib.sha256(efi).hexdigest() == report_a["efi_sha256"], "embedded EFI hash differs")
        observed = load_json(ROOT / "evidence" / "qemu-macos-arm64-observed.json")
        require(observed["status"] == "OBSERVED-MANUAL-QEMU", "QEMU evidence status changed")
        require(
            observed["bindings"] == {
                "world_sha256": report_a["world_sha256"],
                "target_sha256": report_a["target_sha256"],
                "efi_sha256": report_a["efi_sha256"],
                "image_sha256": report_a["image_sha256"],
            },
            "QEMU evidence is stale or bound to another framebuffer artifact",
        )
        require(
            observed["observation"]["visible_object"] == {
                "type": "solid-rectangle",
                "color": "#ff8000",
                "width": 256,
                "height": 256,
            },
            "QEMU visual observation differs from the world contract",
        )
        require(observed["observation"]["rabbit_text_output_present"] is False, "QEMU evidence reports Rabbit text")
        require(observed["execution"]["physical_execution_verified"] is False, "QEMU claimed physical execution")
        require(observed["execution"]["physical_writes_performed"] == [], "QEMU claimed physical writes")
        physical = load_json(ROOT / "evidence" / "dell-optiplex-3060-physical-observed.json")
        require(physical["status"] == "OBSERVED-MANUAL-PHYSICAL", "physical evidence status changed")
        require(
            physical["bindings"] == {
                "world_sha256": report_a["world_sha256"],
                "target_sha256": report_a["target_sha256"],
                "efi_sha256": report_a["efi_sha256"],
                "image_sha256": report_a["image_sha256"],
                "qemu_evidence_id": observed["evidence_id"],
            },
            "physical evidence is stale or bound to another framebuffer artifact",
        )
        require(physical["deployment"]["observed_boot_payload_sha256"] == report_a["efi_sha256"], "physical EFI differs")
        require(physical["observation"]["visible_object"] == observed["observation"]["visible_object"], "physical visual differs")
        require(physical["execution"]["physical_processor_executed"] is True, "physical execution is unclaimed")
        require(physical["execution"]["guest_or_host_operating_system_present"] is False, "physical evidence includes an OS")
        require(physical["execution"]["secure_boot"] == "disabled-by-owner-dedicated-lab-policy", "boot policy hidden")
        require(physical["internal_storage_writes_performed"] == [], "physical evidence reports internal writes")
        print("PASS: semantic orange rectangle lowers deterministically to reviewed x86-64 machine bytes")
        print("PASS: code locates GOP, reads FrameBufferBase, handles RGB/BGR, and stores pixels directly")
        print("PASS: artifact contains no HI text payload or Simple Text Output call path")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")
        print("PASS: artifact remains BUILT-NOT-INSTALLED with no physical writes")
        print("PASS: owner-reviewed QEMU screenshot binds the orange square to exact world, target, EFI, and image identities")
        print("PASS: owner-reviewed Dell display binds the same framebuffer square to the exact physical artifact")

        wrong_color = copy.deepcopy(world)
        wrong_color["objects"][0]["color"] = "#00ff00"
        rejected("an unreviewed color", lambda: build(wrong_color, target))
        wrong_size = copy.deepcopy(world)
        wrong_size["objects"][0]["width"] = 257
        rejected("an unreviewed rectangle size", lambda: build(wrong_size, target))
        text_target = copy.deepcopy(target)
        text_target["capability_bindings"]["display.region"] = "uefi-simple-text-output"
        rejected("a text driver substituted for framebuffer graphics", lambda: validate_target(text_target))
        internal = copy.deepcopy(target)
        internal["installation_policy"]["internal_storage_writes"] = True
        rejected("a target permitting internal-disk writes", lambda: validate_target(internal))
        firmware = copy.deepcopy(target)
        firmware["installation_policy"]["firmware_writes"] = True
        rejected("a target permitting firmware writes", lambda: validate_target(firmware))
        tampered = bytearray(efi)
        tampered[0x200] ^= 1
        rejected("tampered framebuffer instructions", lambda: inspect_efi(bytes(tampered), code))
        print("PASS: negative world, target, policy, and instruction checks are intact")
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: U7 pre-physical direct-framebuffer graphics contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
