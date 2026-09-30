#!/usr/bin/env python3
"""Verify exact physical lowering without claiming a Dell observation."""

from __future__ import annotations

import copy
import hashlib
import struct
from collections.abc import Callable

from rabbit_scene_uefi import (
    BuildError, IMAGE_SIZE, PARTITION_LBA, PROGRAM_SHA256, ROOT, SECTOR_SIZE,
    TARGET_PATH, build, canonical_bytes, load_json, load_program, reference_execution,
    sha256, sprite_indices, trace_bytes, validate_program, validate_target,
)


EXPECTED_TARGET_SHA256 = "64a872e45f151547f8a52592f1ebfc610a8172f44b7129a2f31caa69a5578d17"
EXPECTED_EFI_SHA256 = "afe6bb29cfdb5cdfdcf7acb375b3bbacdb344360365007a8f6aba4e1f3f5b834"
EXPECTED_IMAGE_SHA256 = "31d2dfb3cd8e8acdbf85893829022cf768f21c379b3bc4ea3409088cfa253480"
EXPECTED_SOURCE_SHA256 = "f2eb11ec7b0e26bb0348326b1b55c33e2f8047288a394123adfbd11f647094e5"
EVIDENCE_PATH = ROOT / "evidence" / "qemu-linux-x86-64-observed.json"
PHYSICAL_EVIDENCE_PATH = ROOT / "evidence" / "dell-optiplex-3060-physical-observed.json"


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
    require(raw_size == 0xA00 and raw_offset == 0x200, "program section layout changed")
    require(efi[raw_offset:raw_offset + len(program)] == program, "machine bytes changed in PE")


def main() -> int:
    try:
        target = load_json(TARGET_PATH)
        reference = reference_execution()
        image_a, report_a = build(target)
        image_b, report_b = build(copy.deepcopy(target))
        require(image_a == image_b and report_a == report_b, "repeated physical builds differ")
        require(report_a["target_sha256"] == EXPECTED_TARGET_SHA256, "Target Pack identity changed")
        require(report_a["efi_sha256"] == EXPECTED_EFI_SHA256, "EFI identity changed")
        require(report_a["image_sha256"] == EXPECTED_IMAGE_SHA256, "image identity changed")
        require(report_a["physical_execution_verified"] is False, "builder claimed Dell execution")
        require(report_a["writes_performed"] == [], "builder claimed a device write")
        require(report_a["status"] == "PHYSICAL-CANDIDATE-BUILT-NOT-INSTALLED", "candidate status changed")
        require(sha256(canonical_bytes(target)) == EXPECTED_TARGET_SHA256, "canonical Target Pack changed")
        require(hashlib.sha256((ROOT / "program.S").read_bytes()).hexdigest() == EXPECTED_SOURCE_SHA256, "reviewed assembly source changed")

        evidence = load_json(EVIDENCE_PATH)
        require(evidence["status"] == "OBSERVED-QEMU-SCENE-ANIMA-V2-MOTION", "QEMU evidence status changed")
        require(evidence["bindings"]["creation_sha256"] == report_a["creation_sha256"], "QEMU evidence belongs to another Creation")
        require(evidence["bindings"]["trace_sha256"] == report_a["trace_sha256"], "QEMU evidence belongs to another trace")
        require(evidence["bindings"]["target_sha256"] == report_a["target_sha256"], "QEMU evidence belongs to another Target Pack")
        require(evidence["bindings"]["program_sha256"] == report_a["program_sha256"], "QEMU evidence belongs to another program")
        require(evidence["bindings"]["efi_sha256"] == report_a["efi_sha256"], "QEMU evidence belongs to another EFI artifact")
        require(evidence["bindings"]["image_sha256"] == report_a["image_sha256"], "QEMU evidence belongs to another disk image")
        observation = evidence["observation"]
        require(observation["orange_cat_visible_in_both"] is True, "QEMU did not establish a visible cat")
        require(observation["blue_ball_visible_in_both"] is True, "QEMU did not establish a visible ball")
        require(observation["cat_position_changed"] is True, "QEMU did not establish cat motion")
        require(observation["ball_position_changed"] is True, "QEMU did not establish ball motion")
        require(evidence["execution"]["physical_execution_verified"] is False, "QEMU evidence claimed physical execution")

        physical = load_json(PHYSICAL_EVIDENCE_PATH)
        require(physical["status"] == "OWNER-OBSERVED-PHYSICAL-SCENE-ANIMA-V2-MOTION", "physical evidence status changed")
        for field in ("creation_sha256", "trace_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(physical["bindings"][field] == report_a[field], f"physical evidence {field} binding changed")
        physical_observation = physical["observation"]
        require(all(physical_observation[field] is True for field in (
            "orange_cat_visible", "blue_ball_visible", "cat_motion_visible", "ball_motion_visible",
            "same_expected_scene_as_qemu",
        )), "physical evidence does not establish the complete moving scene")
        require(physical_observation["persistent_machine_writes"] == 0, "physical evidence reports a persistent machine write")

        program = load_program(reference)
        require(sha256(program) == PROGRAM_SHA256, "program identity changed")
        require(program.endswith(trace_bytes(reference)), "canonical trace is not the final immutable data table")
        require(program.count(bytes.fromhex("48 8b 85 f8 00 00 00 ff d0")) == 1, "bounded UEFI Stall call changed")
        require(program.count(bytes.fromhex("66 83 7c 24 40 17")) == 1, "Escape-only exit check changed")
        for component, frame in (("rabbit.asset.cat-pixel", 0), ("rabbit.asset.cat-pixel", 1), ("rabbit.asset.ball-pixel", 0)):
            require(program.count(sprite_indices(reference, component, frame)) == 1, f"{component} frame {frame} binding changed")
        inspect_efi(inspect_image(image_a), program)

        wrong_trace = copy.deepcopy(target)
        wrong_trace["accepted_creation"]["trace_sha256"] = "0" * 64
        rejected("a stale semantic trace", lambda: build(wrong_trace))
        internal_write = copy.deepcopy(target)
        internal_write["authority"]["internal_storage_writes"] = True
        rejected("internal-storage authority", lambda: validate_target(internal_write, reference))
        network = copy.deepcopy(target)
        network["authority"]["network"] = True
        rejected("undeclared network authority", lambda: validate_target(network, reference))
        larger_region = copy.deepcopy(target)
        larger_region["authority"]["gop_framebuffer_write"] = "whole-screen"
        rejected("an enlarged drawing region", lambda: validate_target(larger_region, reference))
        tampered = bytearray(program)
        tampered[0] ^= 1
        rejected("tampered physical instructions", lambda: validate_program(bytes(tampered), reference))

        print("PASS: exact Inventory Creation and hosted runner lower to one deterministic Dell Target Pack")
        print("PASS: physical program embeds the exact 241-frame trace and exact reusable sprite identities")
        print("PASS: UEFI runtime is bounded to GOP 480x270, 33333-us Stall, and Escape input")
        print("PASS: disk contains the reviewed PE32+ application at EFI/BOOT/BOOTX64.EFI")
        print("PASS: two QEMU frames show the exact cat and ball at changed positions")
        print("PASS: owner observed the exact moving cat-and-ball scene on the physical Dell")
        print(f"PASS: program={PROGRAM_SHA256}, efi={EXPECTED_EFI_SHA256}, image={EXPECTED_IMAGE_SHA256}")
        print("PASS: PHYSICAL-DELL-SCENE-ANIMA-V2-OBSERVED")
        return 0
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
