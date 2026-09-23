#!/usr/bin/env python3
"""Verify the read-only x86-64 UEFI QCA Rome status artifact."""

from __future__ import annotations

import copy
import hashlib
import struct
import tempfile
from collections.abc import Callable
from pathlib import Path

from rabbit_qca_status import (
    BuildError, IMAGE_SIZE, PARTITION_LBA, PROGRAM_SHA256, PROGRAM_SIZE,
    PROBE_PATH, SECTOR_SIZE, SOURCE_PATH, TARGET_PATH, build, load_json,
    load_program, validate_probe, validate_target,
)

EXPECTED_PROBE_SHA256 = "9de7842a95fea90b7efda0f0114209ec1101d5d2ebae5e0c0482dabbdace2c5f"
EXPECTED_TARGET_SHA256 = "0f421a52791a69c24eba65b031dd544da8ff75f8123bd9ebf2276006febea413"
EXPECTED_SOURCE_SHA256 = "8cb0c23970d0b8001d677f3c7d5892048678c3f61a416b08f5c7d643d0591e7e"
EXPECTED_EFI_SHA256 = "aa1f1f9dbbd4ae92749ea6c7154066746c16bef2c3b56b4dc2ab69bad31b148d"
EXPECTED_IMAGE_SHA256 = "e7747dbd747ef9add8a5853d01f05e93ebaf20807399a0d697883b15fd235b1f"
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


def parse_qca_version(payload: bytes) -> dict[str, int]:
    if len(payload) != 20:
        raise RuntimeError("QCA target-version response must be exactly 20 bytes")
    rom, patch, ram, chip, platform, flag, reserved = struct.unpack("<IIIBBH4s", payload)
    require(reserved == bytes(4), "QCA target-version reserved bytes are nonzero")
    return {"rom": rom, "patch": patch, "ram": ram, "chip": chip, "platform": platform, "flag": flag}


def parse_qca_status(payload: bytes) -> dict[str, object]:
    if len(payload) != 1:
        raise RuntimeError("QCA setup-status response must be exactly one byte")
    value = payload[0]
    return {"raw": value, "patch_updated": bool(value & 0x80), "syscfg_updated": bool(value & 0x40)}


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
    require(efi[:2] == b"MZ", "missing DOS signature")
    pe = struct.unpack_from("<I", efi, 0x3C)[0]
    require(efi[pe:pe + 4] == b"PE\0\0", "missing PE signature")
    coff = pe + 4
    require(struct.unpack_from("<HH", efi, coff) == (0x8664, 2), "not reviewed x86-64 PE")
    optional = coff + 20
    require(struct.unpack_from("<H", efi, optional)[0] == 0x20B, "not PE32+")
    require(struct.unpack_from("<H", efi, optional + 68)[0] == 10, "not EFI application")
    section = optional + 0xF0
    raw_size, raw_offset = struct.unpack_from("<II", efi, section + 16)
    require(raw_size == 0x800 and raw_offset == 0x200, "program section layout changed")
    require(efi[raw_offset:raw_offset + len(program)] == program, "machine bytes changed")


def inspect_program(program: bytes) -> None:
    require(len(program) == PROGRAM_SIZE, "program size changed")
    require(hashlib.sha256(program).hexdigest() == PROGRAM_SHA256, "program identity changed")
    require(program.count(USB_IO_GUID) == 1, "UEFI USB I/O GUID changed")
    require(program.count(bytes.fromhex("48 8b 46 30 ff d0")) == 1, "device descriptor call changed")
    require(program.count(bytes.fromhex("48 8b 46 40 ff d0")) == 1, "interface descriptor call changed")
    require(program.count(bytes.fromhex("49 8b 45 00 ff d0")) == 2, "vendor-IN transfer count changed")
    require(bytes.fromhex("49 8b 45 18 ff d0") not in program, "interrupt-transfer path appeared")
    for marker in (
        b"RABBIT QCA ROME STATUS v0.1", b"TARGET VERSION (0x09)",
        b"SETUP STATUS (0x05)", b"PATCH_UPDATED=YES", b"PATCH_UPDATED=NO",
        b"SYSCFG_UPDATED=YES", b"SYSCFG_UPDATED=NO",
        b"NO DOWNLOAD; NO RESET; NO HCI; NO RADIO",
        b"TARGET NOT FOUND; NO VENDOR REQUEST SENT",
    ):
        require(marker in program, f"required marker changed: {marker!r}")


def duplicate_json_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="rabbit-qca-status-json-") as temp_dir:
        path = Path(temp_dir) / "duplicate.json"
        path.write_text('{"schema_version":1,"schema_version":1}\n', encoding="utf-8")
        load_json(path)


def main() -> int:
    try:
        probe, target = load_json(PROBE_PATH), load_json(TARGET_PATH)
        image_a, report_a = build(probe, target)
        image_b, report_b = build(copy.deepcopy(probe), copy.deepcopy(target))
        require(image_a == image_b and report_a == report_b, "repeated builds differ")
        for field, expected in (
            ("probe_sha256", EXPECTED_PROBE_SHA256), ("target_sha256", EXPECTED_TARGET_SHA256),
            ("source_sha256", EXPECTED_SOURCE_SHA256), ("program_sha256", PROGRAM_SHA256),
            ("efi_sha256", EXPECTED_EFI_SHA256), ("image_sha256", EXPECTED_IMAGE_SHA256),
        ):
            require(report_a[field] == expected, f"{field} changed")
        require(report_a["vendor_in_requests"] == ["0x09:20", "0x05:1"], "vendor-IN authority changed")
        require(report_a["vendor_out_requests"] == 0, "vendor-OUT authority appeared")
        require(report_a["firmware_download_authorized"] is False, "firmware download became authorized")
        require(report_a["controller_reset_authorized"] is False, "controller reset became authorized")
        require(report_a["hci_commands_authorized"] == 0 and report_a["radio_operations_authorized"] == 0, "HCI or radio authority appeared")
        require(report_a["writes_performed"] == [], "builder claims a physical write")
        program = load_program()
        inspect_program(program)
        inspect_efi(inspect_image(image_a), program)
        source = SOURCE_PATH.read_text(encoding="ascii")
        require(source.count("USB vendor device-to-host") == 2, "source vendor-IN transfer count changed")
        require(source.count("mov byte ptr [rsp + 0x80], 0xc0") == 2, "source request direction changed")
        require(source.count("mov rax, [r13 + 0x00]") == 2, "source control-transfer call count changed")
        for forbidden in ("UsbBulkTransfer", "UsbSyncInterruptTransfer", "UsbPortReset"):
            require(forbidden not in source, f"forbidden USB path appears: {forbidden}")
        print("PASS: deterministic UEFI image binds two read-only QCA vendor-IN requests to exact USB 0CF3:E009")
        print("PASS: machine path has no vendor-OUT, interrupt, HCI, reset, firmware-download, or radio operation")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")

        sample = struct.pack("<IIIBBH4s", 0x00000302, 0x11223344, 0x55667788, 0x01, 0x02, 0xA1B2, bytes(4))
        parsed = parse_qca_version(sample)
        require(parsed == {"rom": 0x302, "patch": 0x11223344, "ram": 0x55667788, "chip": 1, "platform": 2, "flag": 0xA1B2}, "QCA version parser changed")
        require(parse_qca_status(b"\xC0") == {"raw": 0xC0, "patch_updated": True, "syscfg_updated": True}, "updated status parser changed")
        require(parse_qca_status(b"\x00") == {"raw": 0, "patch_updated": False, "syscfg_updated": False}, "missing status parser changed")
        rejected("a short target-version response", lambda: parse_qca_version(sample[:-1]))
        rejected("a long setup-status response", lambda: parse_qca_status(b"\xC0\x00"))
        print("PASS: independent parsers decode ROM/PATCH/RAM and PATCH_UPDATED/SYSCFG_UPDATED bits")

        qemu = load_json(Path(__file__).resolve().parent / "evidence" / "qemu-macos-arm64-observed.json")
        require(qemu["status"] == "OBSERVED-MANUAL-QEMU-QCA-STATUS-FAIL-CLOSED", "QEMU evidence status changed")
        for field in ("probe_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(qemu["bindings"][field] == report_a[field], f"QEMU {field} binding changed")
        observation = qemu["observation"]
        require(observation["visible_version"] == "v0.1", "QEMU version marker changed")
        require(observation["result"] == "TARGET NOT FOUND; NO VENDOR REQUEST SENT", "QEMU fail-closed result changed")
        require(observation["target_found"] is False, "QEMU evidence claims exact target")
        require(observation["vendor_in_requests_sent"] == observation["vendor_out_requests_sent"] == 0, "QEMU evidence claims a vendor request")
        require(observation["firmware_download_performed"] is False and observation["controller_reset_performed"] is False, "QEMU evidence claims mutation")
        require(observation["radio_operations_requested"] == 0, "QEMU evidence claims radio activity")
        require(qemu["execution"]["physical_execution_verified"] is False, "QEMU evidence claims physical execution")
        print("PASS: exact QEMU evidence proves both vendor reads fail closed without 0CF3:E009")

        physical = load_json(Path(__file__).resolve().parent / "evidence" / "dell-optiplex-3060-physical-observed.json")
        require(physical["status"] == "OBSERVED-MANUAL-PHYSICAL-QCA-STATUS-MISSING-SETUP", "physical evidence status changed")
        for field in ("probe_sha256", "target_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(physical["bindings"][field] == report_a[field], f"physical {field} binding changed")
        observation = physical["observation"]
        require(observation["target_found"] is True and observation["rom_version"] == "00000302", "physical target identity changed")
        require(observation["setup_status"] == "20", "physical setup status changed")
        require(observation["patch_updated"] is False and observation["syscfg_updated"] is False, "physical setup-bit result changed")
        require(physical["safety"]["firmware_download_performed"] is False, "physical read probe claims a download")
        require(physical["safety"]["radio_operations_requested"] == 0, "physical read probe claims radio activity")
        print("PASS: physical Dell evidence binds ROM 00000302 and missing patch/syscfg setup bits")

        wrong_device = copy.deepcopy(probe); wrong_device["target_usb_id"] = "FFFF:FFFF"
        rejected("a substituted USB device", lambda: validate_probe(wrong_device))
        extra_request = copy.deepcopy(probe); extra_request["limits"]["vendor_in_requests"] = 3
        rejected("a third vendor-IN request", lambda: validate_probe(extra_request))
        out_request = copy.deepcopy(target); out_request["authority"]["vendor_out_requests"] = 1
        rejected("vendor-OUT authority", lambda: validate_target(out_request))
        for field in ("firmware_download", "controller_reset", "radio_receive", "radio_transmit", "internal_storage_writes", "firmware_writes"):
            unsafe = copy.deepcopy(target); unsafe["authority"][field] = True
            rejected(f"target permitting {field}", lambda unsafe=unsafe: validate_target(unsafe))
        hci = copy.deepcopy(target); hci["authority"]["hci_commands"] = 1
        rejected("an HCI command", lambda: validate_target(hci))
        tampered = bytearray(inspect_image(image_a)); tampered[0x200] ^= 1
        rejected("tampered machine instructions", lambda: inspect_efi(bytes(tampered), program))
        rejected("duplicate JSON fields", duplicate_json_is_rejected)
        print("PASS: request escalation, mutation, radio, storage, tamper, and ambiguous JSON are rejected")
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: physical-Dell-observed read-only QCA Rome setup-status contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
