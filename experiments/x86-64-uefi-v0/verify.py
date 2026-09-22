#!/usr/bin/env python3
"""Verify the deterministic UEFI executable and removable-media image."""

from __future__ import annotations

import copy
import struct
import tempfile
from collections.abc import Callable
from pathlib import Path

from build_image import (
    BuildError, IMAGE_SIZE, PARTITION_LBA, PATCH_PATH, ROOT, SECTOR_SIZE, TARGET_PATH,
    WORLD_PATH, build, build_efi, load_json, machine_code, validate_target,
)


EXPECTED_EFI_SHA256 = "a82d77b43d636d63af9bfa76e0a998ed4b62746a0eab10ad0f6c1777dc8c6128"
EXPECTED_IMAGE_SHA256 = "806d4fef5a33c1bc7d0451bd06d4c665ef21612acd32bddea93fd3f9ca56a594"
EXPECTED_PATCHED_EFI_SHA256 = "b20888a358ddd69c42d249a76f128f4684dc460098db6863614d51b0d322c796"
EXPECTED_PATCHED_IMAGE_SHA256 = "2099b5e4cd07551ecabda7262a6ae2b882bfe495dd32d45070e3d35d10fd26b5"


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
            size = struct.unpack_from("<I", entry, 28)[0]
            return cluster, size
    raise RuntimeError(f"missing FAT entry {name!r}")


def inspect_image(image: bytes) -> bytes:
    require(len(image) == IMAGE_SIZE, "image size changed")
    require(image[510:512] == b"\x55\xaa", "missing MBR signature")
    partition = image[446:462]
    require(partition[4] == 0x0C, "partition is not FAT32 LBA")
    start, count = struct.unpack_from("<II", partition, 8)
    require(start == PARTITION_LBA, "partition start changed")
    require(count == len(image) // SECTOR_SIZE - start, "partition length changed")

    boot_offset = start * SECTOR_SIZE
    boot = image[boot_offset:boot_offset + SECTOR_SIZE]
    require(boot[510:512] == b"\x55\xaa", "missing FAT boot signature")
    require(struct.unpack_from("<H", boot, 11)[0] == SECTOR_SIZE, "unexpected FAT sector size")
    require(boot[13] == 1 and boot[16] == 2, "unexpected FAT geometry")
    reserved = struct.unpack_from("<H", boot, 14)[0]
    fat_sectors = struct.unpack_from("<I", boot, 36)[0]
    root_cluster = struct.unpack_from("<I", boot, 44)[0]
    require(root_cluster == 2, "unexpected root cluster")
    data_lba = start + reserved + 2 * fat_sectors

    def cluster(cluster_number: int) -> bytes:
        offset = (data_lba + cluster_number - 2) * SECTOR_SIZE
        return image[offset:offset + SECTOR_SIZE]

    efi_cluster, _ = short_entry(cluster(2), b"EFI        ")
    boot_cluster, _ = short_entry(cluster(efi_cluster), b"BOOT       ")
    file_cluster, file_size = short_entry(cluster(boot_cluster), b"BOOTX64 EFI")
    require(file_size > 0, "empty UEFI application")
    file_data = bytearray()
    fat_offset = (start + reserved) * SECTOR_SIZE
    current = file_cluster
    seen: set[int] = set()
    while current < 0x0FFFFFF8:
        require(current not in seen, "FAT chain contains a cycle")
        seen.add(current)
        file_data += cluster(current)
        current = struct.unpack_from("<I", image, fat_offset + current * 4)[0] & 0x0FFFFFFF
    return bytes(file_data[:file_size])


def inspect_efi(efi: bytes, expected_text: str) -> None:
    require(efi[0:2] == b"MZ", "missing DOS signature")
    pe_offset = struct.unpack_from("<I", efi, 0x3C)[0]
    require(efi[pe_offset:pe_offset + 4] == b"PE\0\0", "missing PE signature")
    coff = pe_offset + 4
    machine, sections = struct.unpack_from("<HH", efi, coff)
    require(machine == 0x8664 and sections == 2, "not the reviewed x86-64 two-section PE")
    optional = coff + 20
    require(struct.unpack_from("<H", efi, optional)[0] == 0x20B, "not PE32+")
    require(struct.unpack_from("<I", efi, optional + 16)[0] == 0x1000, "entry point changed")
    require(struct.unpack_from("<H", efi, optional + 68)[0] == 10, "not an EFI application")
    section_table = optional + 0xF0
    require(efi[section_table:section_table + 8].rstrip(b"\0") == b".text", "missing text section")
    text_size, text_raw = struct.unpack_from("<II", efi, section_table + 16)
    require(text_size == 0x200 and text_raw == 0x200, "text file layout changed")
    expected_message = expected_text.encode("utf-16-le") + b"\0\0"
    expected_code = machine_code(len(machine_code(0)))
    require(efi[text_raw:text_raw + len(expected_code)] == expected_code, "machine instructions changed")
    message_start = text_raw + len(expected_code)
    require(efi[message_start:message_start + len(expected_message)] == expected_message, "UEFI message changed")


def main() -> int:
    try:
        world = load_json(WORLD_PATH)
        target = load_json(TARGET_PATH)
        image_a, report_a = build(world, target)
        image_b, report_b = build(copy.deepcopy(world), copy.deepcopy(target))
        require(image_a == image_b and report_a == report_b, "repeated builds differ")
        require(report_a["status"] == "BUILT-NOT-INSTALLED", "build claimed installation")
        require(report_a["writes_performed"] == [], "build claimed a physical write")
        require(report_a["physical_execution_verified"] is False, "build claimed physical execution")
        require(report_a["efi_sha256"] == EXPECTED_EFI_SHA256, "reviewed EFI identity changed")
        require(report_a["image_sha256"] == EXPECTED_IMAGE_SHA256, "reviewed image identity changed")
        observed = load_json(ROOT / "evidence" / "qemu-macos-arm64-observed.json")
        require(observed["schema_version"] == 1, "observed evidence schema changed")
        require(observed["status"] == "OBSERVED-MANUAL-QEMU", "manual evidence status changed")
        require(
            observed["bindings"] == {
                "world_sha256": report_a["world_sha256"],
                "target_sha256": report_a["target_sha256"],
                "efi_sha256": report_a["efi_sha256"],
                "image_sha256": report_a["image_sha256"],
            },
            "manual evidence is stale or bound to another artifact",
        )
        require(observed["observation"]["display_text"] == "HI", "manual evidence reports another display")
        require(observed["physical_execution_verified"] is False, "QEMU evidence claimed physical execution")
        require(observed["physical_writes_performed"] == [], "QEMU evidence claimed physical writes")
        usb = load_json(ROOT / "evidence" / "kingston-usb-write-observed.json")
        require(usb["schema_version"] == 1, "USB evidence schema changed")
        require(
            usb["status"] == "INSTALLED-REMOVABLE-PAYLOAD-VERIFIED",
            "USB evidence status changed",
        )
        require(usb["authorization"]["given_by_owner"] is True, "USB write lacks owner authorization")
        require(usb["device"]["whole_disk"] is True, "USB evidence does not name a whole disk")
        require(usb["device"]["location"] == "External", "USB evidence does not name external media")
        require(usb["device"]["removable"] is True, "USB evidence does not name removable media")
        require(usb["device"]["virtual"] is False, "USB evidence names a virtual device")
        require(usb["write"]["source_image_sha256"] == report_a["image_sha256"], "USB source image is stale")
        require(usb["write"]["bytes_written"] == len(image_a), "USB write length changed")
        post_write = usb["post_write_observation"]
        require(post_write["exact_whole_image_match"] is False, "USB evidence hides the image mutation")
        require(post_write["macos_automounted"] is True, "USB evidence hides the host mount")
        require(
            post_write["expected_boot_payload_sha256"]
            == post_write["observed_boot_payload_sha256"]
            == report_a["efi_sha256"],
            "USB boot payload differs from the reviewed EFI application",
        )
        require(usb["physical_execution_verified"] is False, "USB write claimed physical execution")
        require(usb["internal_storage_writes_performed"] == [], "USB evidence claims an internal write")
        require(usb["firmware_writes_performed"] == [], "USB evidence claims a firmware write")
        physical = load_json(ROOT / "evidence" / "dell-optiplex-3060-physical-observed.json")
        require(physical["schema_version"] == 1, "physical evidence schema changed")
        require(physical["status"] == "OBSERVED-MANUAL-PHYSICAL", "physical evidence status changed")
        require(
            physical["bindings"] == {
                "world_sha256": report_a["world_sha256"],
                "target_sha256": report_a["target_sha256"],
                "efi_sha256": report_a["efi_sha256"],
                "image_sha256": report_a["image_sha256"],
                "removable_media_evidence_id": usb["evidence_id"],
            },
            "physical evidence is stale or bound to another artifact",
        )
        require(physical["observation"]["display_text"] == "HI", "physical display differs from contract")
        require(physical["execution"]["physical_processor_executed"] is True, "physical execution is unclaimed")
        require(
            physical["execution"]["guest_or_host_operating_system_present"] is False,
            "physical evidence unexpectedly includes an operating system",
        )
        policy = physical["firmware_policy"]
        require(policy["secure_boot_during_execution"] == "disabled", "physical evidence hides boot policy")
        require(policy["secure_boot_restored"] is False, "physical evidence falsely claims restoration")
        require(policy["keys_deleted_or_replaced"] is False, "physical evidence reports key mutation")
        require(policy["legacy_boot_enabled"] is False, "physical evidence reports legacy boot")
        require(physical["internal_storage_writes_performed"] == [], "physical evidence reports internal writes")
        efi = inspect_image(image_a)
        inspect_efi(efi, "HI")
        require(report_a["efi_sha256"] == __import__("hashlib").sha256(efi).hexdigest(), "EFI hash mismatch")
        print("PASS: unchanged semantic HI world lowers deterministically to x86-64 UEFI PE32+")
        print("PASS: 64 MiB MBR/FAT32 image contains EFI/BOOT/BOOTX64.EFI")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")
        print("PASS: artifact is built but not installed, written, or physically verified")
        print("PASS: owner-reviewed QEMU screenshot is bound to the exact world, target, EFI, and image")
        print("PASS: authorized removable-media write preserves the exact EFI payload and records host metadata mutation")
        print("PASS: owner-reviewed Dell display binds physical HI to the exact world, target, EFI, image, and USB evidence")

        patch = load_json(PATCH_PATH)
        patched_a, patched_report_a = build(world, target, patch)
        patched_b, patched_report_b = build(copy.deepcopy(world), copy.deepcopy(target), copy.deepcopy(patch))
        require(patched_a == patched_b and patched_report_a == patched_report_b, "patched builds differ")
        require(patched_report_a["patch_id"] == "add-bang", "patched report lost patch identity")
        require(patched_report_a["expected_display_text"] == "HI!", "patched display contract changed")
        require(patched_report_a["efi_sha256"] == EXPECTED_PATCHED_EFI_SHA256, "patched EFI identity changed")
        require(patched_report_a["image_sha256"] == EXPECTED_PATCHED_IMAGE_SHA256, "patched image identity changed")
        require(patched_report_a["base_world_sha256"] == report_a["world_sha256"], "patch lost base identity")
        patched_efi = inspect_image(patched_a)
        inspect_efi(patched_efi, "HI!")
        require(patched_a != image_a and patched_efi != efi, "patch did not change the artifact")
        rolled_back, rolled_back_report = build(world, target)
        require(rolled_back == image_a and rolled_back_report == report_a, "removing patch did not restore base")
        print("PASS: immutable add-bang patch builds exact HI! UEFI identities and removal restores exact HI")

        wrong_text = copy.deepcopy(world)
        wrong_text["contract"]["stdout"] = "BYE"
        rejected("a world whose display contract changed", lambda: build(wrong_text, target))
        wrong_graph = copy.deepcopy(world)
        wrong_graph["modules"][1]["value"] = 66
        rejected("graph bytes that disagree with the contract", lambda: build(wrong_graph, target))
        wrong_exit = copy.deepcopy(world)
        wrong_exit["contract"]["exit_status"] = 1
        rejected("a nonzero exit contract", lambda: build(wrong_exit, target))
        stale_patch = copy.deepcopy(patch)
        stale_patch["base_hash"] = "0" * 64
        rejected("an add-bang patch bound to a stale base", lambda: build(world, target, stale_patch))
        signed = copy.deepcopy(target)
        signed["boot_policy"]["signed"] = True
        rejected("a false claim that the image is signed", lambda: validate_target(signed))
        internal = copy.deepcopy(target)
        internal["installation_policy"]["internal_storage_writes"] = True
        rejected("a target permitting internal-disk writes", lambda: validate_target(internal))
        firmware = copy.deepcopy(target)
        firmware["installation_policy"]["firmware_writes"] = True
        rejected("a target permitting firmware writes", lambda: validate_target(firmware))

        tampered = bytearray(image_a)
        embedded = inspect_image(image_a)
        location = image_a.find(embedded)
        require(location >= 0, "could not locate embedded EFI file")
        tampered[location + 0x200] ^= 1
        rejected(
            "tampered machine instructions",
            lambda: inspect_efi(inspect_image(bytes(tampered)), "HI"),
        )

        with tempfile.TemporaryDirectory(prefix="rabbit-uefi-v0-") as temp_dir:
            path = Path(temp_dir) / "rabbit-x86-64-uefi-v0.img"
            path.write_bytes(image_a)
            require(path.stat().st_size == IMAGE_SIZE, "temporary image write was incomplete")
        print("PASS: negative UEFI target and artifact checks are intact")
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: U7 first physical x86-64 UEFI target contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
