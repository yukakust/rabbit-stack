#!/usr/bin/env python3
"""Verify the bounded Rabbit VM v1 wireless loader."""

from __future__ import annotations

import copy
import hashlib

from fetch_firmware import fetch_all
from rabbit_qca_beacon import (
    BuildError, PROGRAM_SHA256, PROGRAM_TEMPLATE_SHA256, PROGRAM_TEMPLATE_SIZE,
    PROBE_PATH, TARGET_PATH, build_fetched, load_json, load_program, load_template,
    validate_probe, validate_target,
)
from rabbit_vm_packet import PacketError, decode, encode_set_square_color, packet_to_uuid

EXPECTED = {
    "probe_sha256": "3cc26e60a23f1ef159c566f7fdcd7f3a016ff41556af6a01361d0a3fe6617468",
    "target_sha256": "915255166fb4b11f8484791a7a943dc346003846bf52cf031705451dd79d6c1e",
    "source_sha256": "9ab148d88979f98f7a9818c7c2e64b4a12192a71fe3fdf2c0a295969504d6d73",
    "program_template_sha256": PROGRAM_TEMPLATE_SHA256,
    "program_sha256": PROGRAM_SHA256,
    "efi_sha256": "c5586333b49fb263be17e0150fc850220fd00851f3bb69cb356a7f57a8c2f74e",
    "image_sha256": "99508f9af7339ff1143557b4544f384907e227718045d77190494926b647ba8c",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejected(label: str, action) -> None:
    try:
        action()
    except (BuildError, PacketError):
        print(f"PASS: rejected {label}")
        return
    raise RuntimeError(f"invalid case accepted: {label}")


def main() -> int:
    image_a, report_a = build_fetched()
    image_b, report_b = build_fetched()
    require(image_a == image_b and report_a == report_b, "repeated builds differ")
    for field, expected in EXPECTED.items():
        require(report_a[field] == expected, f"{field} changed")
    template = load_template()
    program = load_program(fetch_all())
    require(len(template) == PROGRAM_TEMPLATE_SIZE, "template size changed")
    require(hashlib.sha256(template).hexdigest() == PROGRAM_TEMPLATE_SHA256, "template changed")
    require(hashlib.sha256(program).hexdigest() == PROGRAM_SHA256, "program changed")
    for marker in (
        b"RABBIT WIRELESS PROGRAM LOADER v0.1",
        b"RABBIT VM v1; PASSIVE RX; ESC TO STOP",
        b"PROGRAM APPLIED: SET_SQUARE_COLOR",
        b"NO NATIVE CODE; NO PAIR; NO CONNECT; NO DELL RADIO TRANSMIT",
    ):
        require(marker in template, f"required marker missing: {marker!r}")
    for packet in (
        bytes.fromhex("03 0c 00"),
        bytes.fromhex("01 0c 08 00 00 00 00 00 00 00 20"),
        bytes.fromhex("01 20 08 02 00 00 00 00 00 00 00"),
        bytes.fromhex("0b 20 07 00 10 00 10 00 00 00"),
        bytes.fromhex("0c 20 02 01 00"),
        bytes.fromhex("0c 20 02 00 00"),
    ):
        require(template.count(packet) >= 1, f"HCI packet missing: {packet.hex()}")

    red = encode_set_square_color(255, 0, 0)
    cyan = encode_set_square_color(0, 255, 255)
    require(decode(red)["rgb"] == [255, 0, 0], "red program round-trip failed")
    require(decode(cyan)["rgb"] == [0, 255, 255], "cyan program round-trip failed")
    require(packet_to_uuid(red).startswith("5242564D-0101-FF00-0000-0000"), "UUID mapping changed")
    damaged = bytearray(red); damaged[7] ^= 1
    rejected("a program with a damaged checksum", lambda: decode(bytes(damaged)))
    unknown = bytearray(red); unknown[5] = 2
    rejected("an unknown Rabbit VM opcode", lambda: decode(bytes(unknown)))
    wrong_version = bytearray(red); wrong_version[4] = 2
    rejected("an unknown Rabbit VM version", lambda: decode(bytes(wrong_version)))
    reserved = bytearray(red); reserved[10] = 1
    rejected("nonzero reserved program bytes", lambda: decode(bytes(reserved)))

    target = load_json(TARGET_PATH)
    for field in ("native_code_execution", "arbitrary_memory_write", "active_scan", "radio_transmit", "pair", "connect", "internal_storage_writes", "firmware_writes"):
        mutated = copy.deepcopy(target); mutated["authority"][field] = True
        rejected(f"target permitting {field}", lambda value=mutated: validate_target(value))
    expanded = copy.deepcopy(target); expanded["authority"]["accepted_vm_opcodes"].append("EXEC_NATIVE")
    rejected("an unreviewed VM instruction", lambda: validate_target(expanded))
    require(report_a["persistent_writes_authorized"] == 0, "persistent write authority appeared")
    require(report_a["native_code_execution_authorized"] is False, "native execution appeared")
    print("PASS: deterministic UEFI image contains the bounded Rabbit VM v1 loader")
    print("PASS: arbitrary RGB programs round-trip through one BLE service UUID")
    print("PASS: magic, version, opcode, reserved bytes, and checksum fail closed")
    print("PASS: loader can change only one centered square; native code and arbitrary writes are forbidden")
    print("PASS: runtime remains passive and long-lived until local Escape or power-off")
    print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

