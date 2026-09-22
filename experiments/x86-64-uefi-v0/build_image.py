#!/usr/bin/env python3
"""Build a deterministic x86-64 UEFI application inside a FAT32 USB image."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
WORLD_PATH = ROOT.parent / "capability-negotiation-v1" / "world.json"
TARGET_PATH = ROOT / "target.json"
CAPABILITY_ROOT = ROOT.parent / "capability-negotiation-v1"
PATCH_PATH = CAPABILITY_ROOT / "patches" / "add-bang.json"
sys.path.insert(0, str(CAPABILITY_ROOT))
import rabbit_capabilities as capabilities  # noqa: E402
SECTOR_SIZE = 512
IMAGE_SIZE = 64 * 1024 * 1024
TOTAL_SECTORS = IMAGE_SIZE // SECTOR_SIZE
PARTITION_LBA = 2048
RESERVED_SECTORS = 32
NUMBER_OF_FATS = 2
SECTORS_PER_CLUSTER = 1


class BuildError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"could not load {path}: {error}") from error
    if not isinstance(value, dict):
        raise BuildError(f"{path.name} must contain an object")
    return value


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BuildError(f"duplicate JSON field: {key!r}")
        result[key] = value
    return result


def effective_world(base: dict[str, Any], patch: dict[str, Any] | None) -> dict[str, Any]:
    if patch is None:
        return base
    try:
        return capabilities.apply_patch(base, patch)
    except capabilities.GraphError as error:
        raise BuildError(f"invalid semantic patch: {error}") from error


def reviewed_text(world: dict[str, Any]) -> str:
    contract = world.get("contract")
    if not isinstance(contract, dict) or set(contract) != {"stdout", "exit_status"}:
        raise BuildError("world contract is not the reviewed display/exit contract")
    text = contract["stdout"]
    if text not in {"HI", "HI!"} or contract["exit_status"] != 0:
        raise BuildError("UEFI v0 accepts only the reviewed exact HI or HI!/exit-0 world")
    capabilities = world.get("capabilities")
    if not isinstance(capabilities, list):
        raise BuildError("world capabilities are missing")
    required = {
        item.get("capability")
        for item in capabilities
        if isinstance(item, dict) and item.get("required") is True
    }
    if required != {"display.text", "machine.exit"}:
        raise BuildError("world required capabilities changed")
    module_bytes = [
        item.get("value")
        for item in world.get("modules", [])
        if isinstance(item, dict) and item.get("type") == "console-byte"
    ]
    expected_bytes = [72, 73] if text == "HI" else [72, 73, 33]
    if module_bytes != expected_bytes or bytes(module_bytes).decode("ascii") != text:
        raise BuildError("world graph bytes disagree with its observable contract")
    return text


def validate_target(target: dict[str, Any]) -> None:
    expected = {
        "schema_version": 1,
        "target_id": "x86-64-uefi-usb-v0",
        "architecture": "x86-64",
        "firmware": "uefi",
        "executable_format": "pe32-plus-efi-application",
        "media": {
            "layout": "mbr-fat32",
            "size_bytes": IMAGE_SIZE,
            "partition_start_lba": PARTITION_LBA,
            "default_boot_path": "EFI/BOOT/BOOTX64.EFI",
        },
        "capability_bindings": {
            "display.text": "uefi-simple-text-output",
            "machine.exit": "return-efi-success",
        },
        "boot_policy": {"secure_boot": "disabled", "signed": False},
        "installation_policy": {
            "removable_media_only": True,
            "internal_storage_writes": False,
            "firmware_writes": False,
            "recovery": "power-off-and-remove-usb",
        },
    }
    if target != expected:
        raise BuildError("target differs from the reviewed x86-64 UEFI USB v0 contract")


def machine_code(message_offset: int) -> bytes:
    # Microsoft x64 ABI: preserve RBX, reserve shadow space, SystemTable arrives in RDX.
    prefix = bytes.fromhex(
        "53"              # push rbx
        "4883ec30"        # sub rsp, 0x30
        "4889d3"          # mov rbx, rdx
        "488b4b40"        # mov rcx, [rbx + 0x40] (ConOut)
        "488d15"          # lea rdx, [rip + message]
    )
    suffix = bytes.fromhex(
        "488b4108"        # mov rax, [rcx + 8] (OutputString)
        "ffd0"            # call rax
        "488b4b30"        # wait: mov rcx, [rbx + 0x30] (ConIn)
        "488d542420"      # lea rdx, [rsp + 0x20] (EFI_INPUT_KEY)
        "488b4108"        # mov rax, [rcx + 8] (ReadKeyStroke)
        "ffd0"            # call rax
        "4885c0"          # test rax, rax
        "75ec"            # jnz wait
        "31c0"            # xor eax, eax (EFI_SUCCESS)
        "4883c430"        # add rsp, 0x30
        "5b"              # pop rbx
        "c3"              # ret
    )
    rip_after_lea = len(prefix) + 4
    displacement = message_offset - rip_after_lea
    return prefix + struct.pack("<i", displacement) + suffix


def build_efi(text: str) -> bytes:
    encoded_text = text.encode("utf-16-le") + b"\0\0"
    provisional = machine_code(0)
    code = machine_code(len(provisional)) + encoded_text
    if len(code) > SECTOR_SIZE:
        raise BuildError("UEFI text section exceeds one file sector")

    dos = bytearray(0x80)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x80)

    coff = struct.pack(
        "<HHIIIHH",
        0x8664, 2, 0, 0, 0, 0xF0, 0x0022,
    )
    optional = bytearray()
    optional += struct.pack("<HBBIIIII", 0x20B, 1, 0, 0x200, 0x200, 0, 0x1000, 0x1000)
    optional += struct.pack("<QII", 0, 0x1000, 0x200)
    optional += struct.pack("<HHHHHH", 0, 0, 0, 0, 2, 0)
    optional += struct.pack("<IIII", 0, 0x3000, 0x200, 0)
    optional += struct.pack("<HH", 10, 0x0100)
    optional += struct.pack("<QQQQII", 0x100000, 0x1000, 0x100000, 0x1000, 0, 16)
    directories = [(0, 0)] * 16
    directories[5] = (0x2000, 8)
    optional += b"".join(struct.pack("<II", *entry) for entry in directories)
    if len(optional) != 0xF0:
        raise AssertionError(f"bad optional header size: {len(optional)}")

    text_section = struct.pack(
        "<8sIIIIIIHHI", b".text\0\0\0", len(code), 0x1000, 0x200, 0x200,
        0, 0, 0, 0, 0x60000020,
    )
    reloc_section = struct.pack(
        "<8sIIIIIIHHI", b".reloc\0\0", 8, 0x2000, 0x200, 0x400,
        0, 0, 0, 0, 0x42000040,
    )
    headers = bytes(dos) + b"PE\0\0" + coff + bytes(optional) + text_section + reloc_section
    headers = headers.ljust(0x200, b"\0")
    text_raw = code.ljust(0x200, b"\0")
    reloc_raw = struct.pack("<II", 0x1000, 8).ljust(0x200, b"\0")
    return headers + text_raw + reloc_raw


def fat_size(partition_sectors: int) -> tuple[int, int]:
    size = 1
    while True:
        clusters = (partition_sectors - RESERVED_SECTORS - NUMBER_OF_FATS * size) // SECTORS_PER_CLUSTER
        needed = ((clusters + 2) * 4 + SECTOR_SIZE - 1) // SECTOR_SIZE
        if needed == size:
            return size, clusters
        size = needed


def directory_entry(name: bytes, attributes: int, cluster: int, size: int) -> bytes:
    if len(name) != 11:
        raise AssertionError("FAT short name must be 11 bytes")
    entry = bytearray(32)
    entry[0:11] = name
    entry[11] = attributes
    struct.pack_into("<H", entry, 20, cluster >> 16)
    struct.pack_into("<H", entry, 26, cluster & 0xFFFF)
    struct.pack_into("<I", entry, 28, size)
    return bytes(entry)


def build_image(efi: bytes) -> bytes:
    image = bytearray(IMAGE_SIZE)
    partition_sectors = TOTAL_SECTORS - PARTITION_LBA
    fat_sectors, clusters = fat_size(partition_sectors)
    if clusters < 65525:
        raise BuildError("filesystem would not be FAT32")
    data_lba = PARTITION_LBA + RESERVED_SECTORS + NUMBER_OF_FATS * fat_sectors
    file_clusters = (len(efi) + SECTOR_SIZE - 1) // SECTOR_SIZE
    first_file_cluster = 5
    if first_file_cluster + file_clusters >= clusters:
        raise BuildError("UEFI application does not fit")

    mbr = memoryview(image)[:SECTOR_SIZE]
    partition = struct.pack(
        "<B3sB3sII", 0, b"\xfe\xff\xff", 0x0C, b"\xfe\xff\xff",
        PARTITION_LBA, partition_sectors,
    )
    mbr[446:462] = partition
    mbr[510:512] = b"\x55\xaa"

    boot_offset = PARTITION_LBA * SECTOR_SIZE
    boot = memoryview(image)[boot_offset:boot_offset + SECTOR_SIZE]
    boot[0:3] = b"\xeb\x58\x90"
    boot[3:11] = b"RABBIT  "
    struct.pack_into("<H", boot, 11, SECTOR_SIZE)
    boot[13] = SECTORS_PER_CLUSTER
    struct.pack_into("<H", boot, 14, RESERVED_SECTORS)
    boot[16] = NUMBER_OF_FATS
    struct.pack_into("<H", boot, 17, 0)
    struct.pack_into("<H", boot, 19, 0)
    boot[21] = 0xF8
    struct.pack_into("<H", boot, 22, 0)
    struct.pack_into("<H", boot, 24, 63)
    struct.pack_into("<H", boot, 26, 255)
    struct.pack_into("<I", boot, 28, PARTITION_LBA)
    struct.pack_into("<I", boot, 32, partition_sectors)
    struct.pack_into("<I", boot, 36, fat_sectors)
    struct.pack_into("<H", boot, 40, 0)
    struct.pack_into("<H", boot, 42, 0)
    struct.pack_into("<I", boot, 44, 2)
    struct.pack_into("<H", boot, 48, 1)
    struct.pack_into("<H", boot, 50, 6)
    boot[64] = 0x80
    boot[66] = 0x29
    struct.pack_into("<I", boot, 67, 0x52414242)
    boot[71:82] = b"RABBITBOOT "
    boot[82:90] = b"FAT32   "
    boot[510:512] = b"\x55\xaa"

    fsinfo_offset = (PARTITION_LBA + 1) * SECTOR_SIZE
    fsinfo = memoryview(image)[fsinfo_offset:fsinfo_offset + SECTOR_SIZE]
    struct.pack_into("<I", fsinfo, 0, 0x41615252)
    struct.pack_into("<I", fsinfo, 484, 0x61417272)
    struct.pack_into("<I", fsinfo, 488, clusters - (3 + file_clusters))
    struct.pack_into("<I", fsinfo, 492, first_file_cluster + file_clusters)
    struct.pack_into("<I", fsinfo, 508, 0xAA550000)
    image[(PARTITION_LBA + 6) * SECTOR_SIZE:(PARTITION_LBA + 7) * SECTOR_SIZE] = boot
    image[(PARTITION_LBA + 7) * SECTOR_SIZE:(PARTITION_LBA + 8) * SECTOR_SIZE] = fsinfo

    fat = bytearray(fat_sectors * SECTOR_SIZE)
    entries = [0x0FFFFFF8, 0xFFFFFFFF, 0x0FFFFFFF, 0x0FFFFFFF, 0x0FFFFFFF]
    for index, value in enumerate(entries):
        struct.pack_into("<I", fat, index * 4, value)
    for index in range(file_clusters):
        cluster = first_file_cluster + index
        next_cluster = 0x0FFFFFFF if index == file_clusters - 1 else cluster + 1
        struct.pack_into("<I", fat, cluster * 4, next_cluster)
    first_fat = (PARTITION_LBA + RESERVED_SECTORS) * SECTOR_SIZE
    second_fat = first_fat + len(fat)
    image[first_fat:first_fat + len(fat)] = fat
    image[second_fat:second_fat + len(fat)] = fat

    def cluster_offset(cluster: int) -> int:
        return (data_lba + (cluster - 2) * SECTORS_PER_CLUSTER) * SECTOR_SIZE

    root = (
        directory_entry(b"RABBITBOOT ", 0x08, 0, 0)
        + directory_entry(b"EFI        ", 0x10, 3, 0)
    )
    efi_dir = (
        directory_entry(b".          ", 0x10, 3, 0)
        + directory_entry(b"..         ", 0x10, 0, 0)
        + directory_entry(b"BOOT       ", 0x10, 4, 0)
    )
    boot_dir = (
        directory_entry(b".          ", 0x10, 4, 0)
        + directory_entry(b"..         ", 0x10, 3, 0)
        + directory_entry(b"BOOTX64 EFI", 0x20, first_file_cluster, len(efi))
    )
    image[cluster_offset(2):cluster_offset(2) + len(root)] = root
    image[cluster_offset(3):cluster_offset(3) + len(efi_dir)] = efi_dir
    image[cluster_offset(4):cluster_offset(4) + len(boot_dir)] = boot_dir
    image[cluster_offset(first_file_cluster):cluster_offset(first_file_cluster) + len(efi)] = efi
    return bytes(image)


def build(
    world: dict[str, Any],
    target: dict[str, Any],
    patch: dict[str, Any] | None = None,
) -> tuple[bytes, dict[str, Any]]:
    effective = effective_world(world, patch)
    text = reviewed_text(effective)
    validate_target(target)
    efi = build_efi(text)
    image = build_image(efi)
    report = {
        "schema_version": 1,
        "status": "BUILT-NOT-INSTALLED",
        "world_sha256": sha256(canonical_bytes(effective)),
        "base_world_sha256": sha256(canonical_bytes(world)),
        "patch_id": patch["patch_id"] if patch else None,
        "patch_sha256": sha256(canonical_bytes(patch)) if patch else None,
        "target_sha256": sha256(canonical_bytes(target)),
        "efi_sha256": sha256(efi),
        "image_sha256": sha256(image),
        "image_size_bytes": len(image),
        "boot_path": "EFI/BOOT/BOOTX64.EFI",
        "expected_display_text": text,
        "physical_execution_verified": False,
        "writes_performed": [],
    }
    return image, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the reviewed Rabbit x86-64 UEFI USB image")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--patch", choices=["add-bang"])
    args = parser.parse_args()
    try:
        world, target = load_json(WORLD_PATH), load_json(TARGET_PATH)
        patch = load_json(PATCH_PATH) if args.patch == "add-bang" else None
        image, report = build(world, target, patch)
        args.output.write_bytes(image)
        if args.report:
            args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"BUILT: {args.output} ({len(image)} bytes)")
        print(f"SHA256: {report['image_sha256']}")
        print("STATUS: BUILT-NOT-INSTALLED; writes_performed=0")
        return 0
    except (BuildError, OSError) as error:
        print(f"FAIL: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
