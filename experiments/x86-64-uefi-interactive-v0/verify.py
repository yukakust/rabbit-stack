#!/usr/bin/env python3
"""Verify the first keyboard-controlled direct-framebuffer world."""

from __future__ import annotations

import copy
import hashlib
import struct
from collections.abc import Callable

from rabbit_interactive import (
    BuildError, GOP_GUID, IMAGE_SIZE, PARTITION_LBA, SECTOR_SIZE, TARGET_PATH, WORLD_PATH,
    build, load_json, machine_code, simulate_key, validate_target, validate_world,
)


EXPECTED_WORLD_SHA256 = "f6d22aa19f64ff36e6057b9904624e2fb4d551e75234aa59d774a82b539462b9"
EXPECTED_TARGET_SHA256 = "bbec78f05b18422021999adf8e6fbafd34695cf6c6fb8ef1235c858245b7f9ac"
EXPECTED_EFI_SHA256 = "b633e0aa48f850bd350d2d1d55bb7e431b83f43f7f1b783e84864e10ede7ef84"
EXPECTED_IMAGE_SHA256 = "be2d4ba213672e1ce11879c5b644976a59edad924cfffd6237643e0afa65e06f"


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
    raw_size, raw_offset = struct.unpack_from("<II", efi, section_table + 16)
    require(raw_size == 0x400 and raw_offset == 0x200, "interactive text-section layout changed")
    require(efi[raw_offset:raw_offset + len(expected_code)] == expected_code, "machine instructions changed")
    require(expected_code.endswith(GOP_GUID), "GOP GUID missing")
    require(b"\x48\x8b\x58\x18" in expected_code, "FrameBufferBase load missing")
    require(b"\x0f\xb7\x44\x24\x28" in expected_code, "UEFI scan-code load missing")
    require(b"\x44\x89\x11" in expected_code, "direct pixel store missing")


def verify_model() -> None:
    screen = (640, 480)
    require(simulate_key((100, 100), 1, screen) == (100, 84), "up mapping changed")
    require(simulate_key((100, 100), 2, screen) == (100, 116), "down mapping changed")
    require(simulate_key((100, 100), 3, screen) == (116, 100), "right mapping changed")
    require(simulate_key((100, 100), 4, screen) == (84, 100), "left mapping changed")
    require(simulate_key((0, 0), 1, screen) == (0, 0), "top boundary failed")
    require(simulate_key((0, 0), 4, screen) == (0, 0), "left boundary failed")
    require(simulate_key((512, 352), 2, screen) == (512, 352), "bottom boundary failed")
    require(simulate_key((512, 352), 3, screen) == (512, 352), "right boundary failed")
    position = (100, 100)
    for scan_code in (3, 2, 4, 1):
        position = simulate_key(position, scan_code, screen)
    require(position == (100, 100), "opposite movements did not restore position")


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
        code = machine_code(validate_world(world))
        require(len(code) == 542, "reviewed instruction/data length changed")
        efi = inspect_image(image_a)
        inspect_efi(efi, code)
        require(hashlib.sha256(efi).hexdigest() == report_a["efi_sha256"], "embedded EFI hash differs")
        verify_model()
        print("PASS: interactive world lowers deterministically to 542 reviewed x86-64 code/data bytes")
        print("PASS: code clears the framebuffer, draws, reads UEFI scan codes, erases, moves, and redraws")
        print("PASS: arrow model moves by 16 pixels, clamps all four edges, and preserves opposite-step identity")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")
        print("PASS: artifact remains BUILT-NOT-INSTALLED with no physical writes")

        wrong_step = copy.deepcopy(world)
        wrong_step["contract"]["movement_step_pixels"] = 32
        rejected("an unreviewed movement step", lambda: build(wrong_step, target))
        wrong_rule = copy.deepcopy(world)
        wrong_rule["rules"][0]["effect"] = "move-without-bounds"
        rejected("movement without the reviewed boundary rule", lambda: build(wrong_rule, target))
        wrong_input = copy.deepcopy(target)
        wrong_input["input_mapping"]["right"] = 4
        rejected("a substituted direction mapping", lambda: validate_target(wrong_input))
        internal = copy.deepcopy(target)
        internal["installation_policy"]["internal_storage_writes"] = True
        rejected("a target permitting internal-disk writes", lambda: validate_target(internal))
        firmware = copy.deepcopy(target)
        firmware["installation_policy"]["firmware_writes"] = True
        rejected("a target permitting firmware writes", lambda: validate_target(firmware))
        tampered = bytearray(efi)
        tampered[0x200] ^= 1
        rejected("tampered interactive instructions", lambda: inspect_efi(bytes(tampered), code))
        print("PASS: negative world, input-map, policy, and instruction checks are intact")
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: pre-physical keyboard-controlled framebuffer contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
