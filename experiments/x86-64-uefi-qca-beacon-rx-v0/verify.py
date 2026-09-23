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
    "probe_sha256": "3aff095794b0e4e22b9d77010c284b4922efc1a7809b72c6405f17d850d4832d",
    "target_sha256": "8c5aea30745e82600ffddcce9d08b0a65cdff6d7bedb9ffa51d355d97f4118bb",
    "firmware_manifest_sha256": "cabf8be8ee76815a03d1407fd635c983563303a9661f9419d82e9dbcb3e81dfc",
    "source_sha256": "3321921affe4cf0cef0d6a2b87ccb82c0d9937a96dc614305e8ddd397ef8cdea",
    "program_template_sha256": PROGRAM_TEMPLATE_SHA256,
    "program_sha256": PROGRAM_SHA256,
    "efi_sha256": "b5572f8e6f23daea9568d2e07ffc684bbbe4b25e591e3ac61bc8c42354c862ba",
    "image_sha256": "7460a9fce26fc8aea329f0c169492e0c76b60d5df88cfdd0f9901eb9ac56ae5f",
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
        b"RABBIT QCA INIT + BEACON RX v0.2", b"REQUIRE ROM=00000302",
        b"PATCH_UPDATED=YES; SYSCFG_UPDATED=YES", b"BEGIN BOUNDED PASSIVE RABBIT RECEIVE",
        b"RABBIT COMBINED PASSIVE RX v0.2", b"POST-LOAD HCI RESET: OK",
        b"PASSIVE SCAN OFF", b"RABBIT BEACON RECEIVED",
    ):
        require(text in template, f"required marker changed: {text!r}")
    packets = (
        bytes.fromhex("03 0c 00"),
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
        require(report_a["post_load_hci_reset_authorized"] == 1 and report_a["post_load_reset_wait_ms"] == 100, "bounded reset authority missing")
        require(report_a["passive_radio_receive_authorized"] is True, "passive receive authority missing")
        require(not any(report_a[field] for field in ("active_scan_authorized", "radio_transmit_authorized", "pairing_authorized", "connection_authorized")), "forbidden radio authority appeared")
        require(report_a["persistent_writes_authorized"] == 0 and report_a["writes_performed"] == [], "persistent write appeared")
        payloads = fetch_all(); inspect(load_template(), load_program(payloads), image_a, payloads)
        print("PASS: one deterministic boot composes exact QCA RAM initialization, one HCI reset, and passive Rabbit receive")
        print("PASS: both upstream payloads remain pinned by commit, size, and SHA-256")
        print("PASS: passive scan has exact command packets, a 20-second budget, and mandatory disable cleanup")
        print("PASS: only one post-load reset is allowed; active scan, transmit, pair, connect, flash, and persistence remain forbidden")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")

        archived = load_json(Path(__file__).resolve().parent / "evidence" / "dell-optiplex-3060-v01-zero-events-physical-observed.json")
        require(archived["status"] == "OBSERVED-MANUAL-PHYSICAL-QCA-READY-PASSIVE-RX-ZERO-EVENTS", "v0.1 physical evidence status changed")
        require(archived["observation"]["status_after"] == "E0", "v0.1 ready flags changed")
        require(archived["observation"]["rx_events_hex"] == archived["observation"]["le_meta_events_hex"] == archived["observation"]["advertising_reports_hex"] == "00", "v0.1 zero-event observation changed")
        require(archived["safety"]["controller_reset_performed"] is False, "v0.1 unexpectedly claims reset")
        print("PASS: archived physical v0.1 evidence motivates exactly one post-load reset after E0/zero events")

        probe, target = load_json(PROBE_PATH), load_json(TARGET_PATH)
        wrong_rom = copy.deepcopy(probe); wrong_rom["required_rom_version"] = "0x00000300"
        rejected("a substituted ROM", lambda: validate_probe(wrong_rom))
        changed_uuid = copy.deepcopy(probe); changed_uuid["rabbit_service_uuid"] = "0" * 36
        rejected("a substituted Rabbit UUID", lambda: validate_probe(changed_uuid))
        for field in ("controller_flash_write", "active_scan", "radio_transmit", "advertise", "pair", "connect", "internal_storage_writes", "firmware_writes"):
            unsafe = copy.deepcopy(target); unsafe["authority"][field] = True
            rejected(f"target permitting {field}", lambda unsafe=unsafe: validate_target(unsafe))
        extra = copy.deepcopy(target); extra["authority"]["bulk_out_max_transfers"] = 19
        rejected("an extra firmware transfer", lambda: validate_target(extra))
        no_reset = copy.deepcopy(target); no_reset["authority"]["controller_reset"] = False
        rejected("removing the reviewed post-load reset", lambda: validate_target(no_reset))
        extra_reset = copy.deepcopy(target); extra_reset["authority"]["post_load_reset_count"] = 2
        rejected("a second HCI reset", lambda: validate_target(extra_reset))
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
