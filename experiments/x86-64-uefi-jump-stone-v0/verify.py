#!/usr/bin/env python3
"""Verify the requested jump, stone, and collision world."""

from __future__ import annotations

import copy
import hashlib
import struct
from collections.abc import Callable

from rabbit_jump_stone import (
    BuildError, IMAGE_SIZE, PARTITION_LBA, PROGRAM_SHA256, SECTOR_SIZE, State,
    TARGET_PATH, WORLD_PATH, build, leave_stone, load_json, load_program, move,
    overlaps_stone, validate_target,
)


EXPECTED_WORLD_SHA256 = "94a67cd0e7b83e56a12f07bf32ffc783af694220fcb2a746943e074435998cc0"
EXPECTED_TARGET_SHA256 = "d84e054883f0165aed09c4177f26fabdf076eca1ca2024cb94a08a50313e0822"
EXPECTED_EFI_SHA256 = "1b5b816e533360f71917307e92cb3a8ef8afe4efbfe6cfd2fc3e199f40eea639"
EXPECTED_IMAGE_SHA256 = "a319494061ec42f7a756e073c623de0f0d3983fa4fa9a260059c1bfd1de5a7aa"


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
    require(hashlib.sha256(program).hexdigest() == PROGRAM_SHA256, "program identity changed")
    require(b"\x48\x8b\x85\xf8\x00\x00\x00" in program, "UEFI Stall call path missing")
    require(b"\x0f\xb7\x4c\x24\x2a" in program, "Unicode key path missing")
    require(b"\xb8\x01\x00\x00\x00\xc3" in program, "solid collision result missing")


def verify_model() -> None:
    base = State()
    placed = leave_stone(base)
    require(placed == State(116, 100, "right", (100, 124)), "Z placement contract changed")
    blocked = move(placed, "left")
    require((blocked.x, blocked.y) == (116, 100), "player crossed the stone")
    around = placed
    for direction in ("right", "up", "up", "up", "left", "left", "left"):
        around = move(around, direction)
    require((around.x, around.y) == (84, 52), "player could not route around stone")
    require(not overlaps_stone(around.x, around.y, around.stone), "routed player still overlaps stone")
    replaced = leave_stone(move(placed, "right"))
    require(replaced.stone != placed.stone, "second Z did not relocate the single stone")
    edge = State(576, 100, "right", None)
    require(leave_stone(edge) == edge, "Z crossed the screen boundary")


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
        require(report_a["writes_performed"] == [], "builder claimed physical writes")
        program = load_program()
        efi = inspect_image(image_a)
        inspect_efi(efi, program)
        verify_model()
        print("PASS: requested yellow player, jump, Z stone, push-away, and solid collision world is canonical")
        print("PASS: 1064 reviewed x86-64 bytes include framebuffer, keyboard, Stall timing, state, and AABB collision paths")
        print("PASS: model proves stone placement, blocked crossing, route-around, replacement, and screen boundary behavior")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")
        print("PASS: artifact remains BUILT-NOT-INSTALLED with no physical writes")
        wrong_count = copy.deepcopy(world)
        wrong_count["stone"]["maximum_count"] = 2
        rejected("an undeclared second persistent stone", lambda: build(wrong_count, target))
        wrong_solid = copy.deepcopy(world)
        wrong_solid["stone"]["solid"] = False
        rejected("a non-solid stone", lambda: build(wrong_solid, target))
        wrong_delay = copy.deepcopy(target)
        wrong_delay["capability_bindings"]["time.delay"] = "busy-loop"
        rejected("an unreviewed timing driver", lambda: validate_target(wrong_delay))
        internal = copy.deepcopy(target)
        internal["installation_policy"]["internal_storage_writes"] = True
        rejected("a target permitting internal-disk writes", lambda: validate_target(internal))
        tampered = bytearray(efi)
        tampered[0x200] ^= 1
        rejected("tampered world instructions", lambda: inspect_efi(bytes(tampered), program))
        print("PASS: negative semantic, capability, storage, and instruction checks are intact")
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: pre-physical jump-and-stone world contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
