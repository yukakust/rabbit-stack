#!/usr/bin/env python3
"""Verify the exact one-boot QCA initialization plus passive Rabbit receiver."""

from __future__ import annotations

import copy
import hashlib
import struct
import tempfile
from pathlib import Path

from fetch_firmware import fetch_all
from rabbit_qca_beacon import (
    BuildError, IMAGE_SIZE, NVM_MARKER, PARTITION_LBA, PROGRAM_SHA256,
    PROGRAM_TEMPLATE_SHA256, PROGRAM_TEMPLATE_SIZE, PROBE_PATH, RAMPATCH_MARKER,
    SECTOR_SIZE, SOURCE_PATH, TARGET_PATH, build_fetched, load_json, load_program,
    load_template, validate_probe, validate_target,
)

EXPECTED = {
    "probe_sha256": "8cd5d6816909566b7aa3ab6981c1d7acaa804d203822b479afcce70c5c9c165b",
    "target_sha256": "fb8c155f73dd88dd8f4842ee17f5b75e2e4f5ba631489646e9d729b1f6cb42ff",
    "firmware_manifest_sha256": "cabf8be8ee76815a03d1407fd635c983563303a9661f9419d82e9dbcb3e81dfc",
    "source_sha256": "c02fc52d28e99ae55a20efe4d14a2ced74efede14cab8e5007618a62c786657d",
    "program_template_sha256": PROGRAM_TEMPLATE_SHA256,
    "program_sha256": PROGRAM_SHA256,
    "efi_sha256": "4a25054ceb2acbb9806786028e1a601536531328a7396cecd7dc081d11f272df",
    "image_sha256": "50d5232d4914e33220d73bff53bd42f428244a96a96c9abbaa19b9766200ab7d",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejected(label, action) -> None:
    try:
        action()
    except (BuildError, RuntimeError):
        print(f"PASS: rejected {label}")
        return
    raise RuntimeError(f"invalid case accepted: {label}")


def short_entry(directory: bytes, name: bytes) -> tuple[int, int]:
    for offset in range(0, len(directory), 32):
        entry = directory[offset:offset + 32]
        if entry[:11] == name:
            cluster = struct.unpack_from("<H", entry, 20)[0] << 16 | struct.unpack_from("<H", entry, 26)[0]
            return cluster, struct.unpack_from("<I", entry, 28)[0]
    raise RuntimeError(f"missing FAT entry {name!r}")


def extract_efi(image: bytes) -> bytes:
    require(len(image) == IMAGE_SIZE and image[510:512] == b"\x55\xaa", "disk envelope changed")
    start = struct.unpack_from("<I", image, 454)[0]
    require(start == PARTITION_LBA, "partition start changed")
    boot = image[start * SECTOR_SIZE:(start + 1) * SECTOR_SIZE]
    reserved, fats = struct.unpack_from("<H", boot, 14)[0], struct.unpack_from("<I", boot, 36)[0]
    data_lba = start + reserved + 2 * fats
    def cluster(number):
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


def inspect(template: bytes, program: bytes, image: bytes, payloads: dict[str, bytes]) -> None:
    require(len(template) == PROGRAM_TEMPLATE_SIZE, "template size changed")
    require(hashlib.sha256(template).hexdigest() == PROGRAM_TEMPLATE_SHA256, "template identity changed")
    require(hashlib.sha256(program).hexdigest() == PROGRAM_SHA256, "program identity changed")
    for marker, name, size in ((RAMPATCH_MARKER, "rampatch_usb_00000302.bin", 68644), (NVM_MARKER, "nvm_usb_00000302.bin", 1998)):
        offset = template.index(marker) + len(marker)
        require(template[offset:offset + size] == bytes(size), f"placeholder changed: {name}")
        require(program[offset:offset + size] == payloads[name], f"payload changed: {name}")
    for text in (
        b"RABBIT QCA INIT + BEACON RX v0.1", b"REQUIRE ROM=00000302",
        b"PATCH_UPDATED=YES; SYSCFG_UPDATED=YES", b"BEGIN BOUNDED PASSIVE RABBIT RECEIVE",
        b"RABBIT COMBINED PASSIVE RX v0.1", b"PASSIVE RX; NO PAIR OR CONNECT",
        b"PASSIVE SCAN OFF", b"RABBIT BEACON RECEIVED",
    ):
        require(text in template, f"required marker changed: {text!r}")
    packets = (
        bytes.fromhex("01 0c 08 00 00 00 00 00 00 00 20"),
        bytes.fromhex("01 20 08 02 00 00 00 00 00 00 00"),
        bytes.fromhex("0b 20 07 00 10 00 10 00 00 00"),
        bytes.fromhex("0c 20 02 01 00"), bytes.fromhex("0c 20 02 00 00"),
    )
    for packet in packets:
        require(template.count(packet) == 1, f"HCI packet changed: {packet.hex()}")
    require(template.index(packets[-2]) < template.index(packets[-1]), "scan cleanup no longer follows enable")
    efi = extract_efi(image)
    require(hashlib.sha256(efi).hexdigest() == EXPECTED["efi_sha256"], "EFI identity changed")
    pe = struct.unpack_from("<I", efi, 0x3C)[0]
    require(efi[pe:pe + 4] == b"PE\0\0" and struct.unpack_from("<H", efi, pe + 4)[0] == 0x8664, "not x86-64 PE")
    require(program in efi, "combined program is not embedded in EFI")


def duplicate_json() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "duplicate.json"
        path.write_text('{"schema_version":1,"schema_version":1}\n')
        load_json(path)


def main() -> int:
    try:
        image_a, report_a = build_fetched(); image_b, report_b = build_fetched()
        require(image_a == image_b and report_a == report_b, "repeated builds differ")
        for field, value in EXPECTED.items():
            require(report_a[field] == value, f"{field} changed")
        require(report_a["transient_controller_ram_write_authorized"] is True, "RAM initialization authority missing")
        require(report_a["passive_radio_receive_authorized"] is True, "passive receive authority missing")
        require(not any(report_a[field] for field in ("active_scan_authorized", "radio_transmit_authorized", "pairing_authorized", "connection_authorized")), "forbidden radio authority appeared")
        require(report_a["persistent_writes_authorized"] == 0 and report_a["writes_performed"] == [], "persistent write appeared")
        payloads = fetch_all(); inspect(load_template(), load_program(payloads), image_a, payloads)
        print("PASS: one deterministic boot composes exact QCA RAM initialization with bounded passive Rabbit receive")
        print("PASS: both upstream payloads remain pinned by commit, size, and SHA-256")
        print("PASS: passive scan has exact command packets, a 20-second budget, and mandatory disable cleanup")
        print("PASS: active scan, transmit, advertise, pair, connect, reset, flash, and persistent writes remain forbidden")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")

        qemu = load_json(Path(__file__).resolve().parent / "evidence" / "qemu-macos-arm64-observed.json")
        require(qemu["status"] == "OBSERVED-MANUAL-QEMU-COMBINED-QCA-RX-FAIL-CLOSED", "QEMU evidence status changed")
        for field in ("probe_sha256", "target_sha256", "firmware_manifest_sha256", "program_sha256", "efi_sha256", "image_sha256"):
            require(qemu["bindings"][field] == report_a[field], f"QEMU {field} binding changed")
        observation = qemu["observation"]
        require(observation["result"] == "TARGET NOT FOUND; NO DEVICE WRITE SENT", "QEMU mismatch result changed")
        require(observation["target_found"] is False and observation["controller_ram_writes"] == 0, "QEMU evidence claims device writes")
        require(observation["receiver_chain_reached"] is False, "QEMU mismatch reached the receive chain")
        require(observation["hci_commands_sent"] == observation["radio_operations_requested"] == 0, "QEMU evidence claims HCI/radio activity")
        print("PASS: exact QEMU evidence fails closed before RAM writes, HCI, and radio")

        probe, target = load_json(PROBE_PATH), load_json(TARGET_PATH)
        wrong_rom = copy.deepcopy(probe); wrong_rom["required_rom_version"] = "0x00000300"
        rejected("a substituted ROM", lambda: validate_probe(wrong_rom))
        changed_uuid = copy.deepcopy(probe); changed_uuid["rabbit_service_uuid"] = "0" * 36
        rejected("a substituted Rabbit UUID", lambda: validate_probe(changed_uuid))
        for field in ("controller_flash_write", "controller_reset", "active_scan", "radio_transmit", "advertise", "pair", "connect", "internal_storage_writes", "firmware_writes"):
            unsafe = copy.deepcopy(target); unsafe["authority"][field] = True
            rejected(f"target permitting {field}", lambda unsafe=unsafe: validate_target(unsafe))
        extra = copy.deepcopy(target); extra["authority"]["bulk_out_max_transfers"] = 19
        rejected("an extra firmware transfer", lambda: validate_target(extra))
        sequence = copy.deepcopy(target); sequence["authority"]["allowed_hci_command_sequence"].insert(0, "0x0C03-reset")
        rejected("an HCI reset", lambda: validate_target(sequence))
        altered = dict(payloads); altered["nvm_usb_00000302.bin"] = payloads["nvm_usb_00000302.bin"][:-1] + b"\0"
        rejected("a modified NVM payload", lambda: load_program(altered))
        rejected("duplicate JSON fields", duplicate_json)
    except (BuildError, OSError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: pre-QEMU combined QCA-init plus Rabbit passive-receive contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
