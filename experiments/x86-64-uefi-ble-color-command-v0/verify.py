#!/usr/bin/env python3
"""Verify the exact bounded BLE BLUE/YELLOW framebuffer-command runtime."""

from __future__ import annotations

import copy, hashlib

from fetch_firmware import fetch_all
from rabbit_qca_beacon import (
    BuildError, PROGRAM_SHA256, PROGRAM_TEMPLATE_SHA256, PROGRAM_TEMPLATE_SIZE,
    PROBE_PATH, TARGET_PATH, build_fetched, load_json, load_program,
    load_template, validate_probe, validate_target,
)

EXPECTED = {
    "probe_sha256": "96370f2a03d785068a50154104294ffa444fa21a795b7bc3b6bff627242ea15a",
    "target_sha256": "a90a9aa0d35cca26b5e0d612505fe60b2859aae549f427ae5078fe79b295e804",
    "source_sha256": "aade26f1923d4093809764c1e9b896effa30bea9ce4f62f8ce4571495ec16756",
    "program_template_sha256": PROGRAM_TEMPLATE_SHA256,
    "program_sha256": PROGRAM_SHA256,
    "efi_sha256": "732dbc41f27f28a6a5e06583e4d47c5191d8c61d39fb5cc2122090013bddbac1",
    "image_sha256": "ebe4b6e3bdfb3cf081864de0237b70c76a3f3972ddeb01d47f404e252c770061",
}

def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)

def rejected(label, action) -> None:
    try:
        action()
    except (BuildError, RuntimeError):
        print(f"PASS: rejected {label}"); return
    raise RuntimeError(f"invalid case accepted: {label}")

def main() -> int:
    try:
        image_a, report_a = build_fetched(); image_b, report_b = build_fetched()
        require(image_a == image_b and report_a == report_b, "repeated builds differ")
        for field, value in EXPECTED.items():
            require(report_a[field] == value, f"{field} changed")
        template = load_template(); payloads = fetch_all(); program = load_program(payloads)
        require(len(template) == PROGRAM_TEMPLATE_SIZE, "template size changed")
        require(hashlib.sha256(template).hexdigest() == PROGRAM_TEMPLATE_SHA256, "template hash changed")
        require(hashlib.sha256(program).hexdigest() == PROGRAM_SHA256, "program hash changed")
        for text in (
            b"RABBIT BLE COLOR COMMAND v0.1", b"INITIAL SQUARE=YELLOW",
            b"COMMAND BLUE RECEIVED; SQUARE=BLUE",
            b"COMMAND YELLOW RECEIVED; SQUARE=YELLOW",
            b"PASSIVE SCAN OFF", b"MAX 120 SECONDS",
        ):
            require(text in template, f"required marker changed: {text!r}")
        blue = bytes.fromhex("02 00 00 00 00 00 00 80 45 4c 54 49 42 42 41 52")
        yellow = bytes.fromhex("03 00 00 00 00 00 00 80 45 4c 54 49 42 42 41 52")
        require(template.count(blue) == 1 and template.count(yellow) == 1, "command UUID bytes changed")
        packets = (
            bytes.fromhex("03 0c 00"), bytes.fromhex("01 0c 08 00 00 00 00 00 00 00 20"),
            bytes.fromhex("01 20 08 02 00 00 00 00 00 00 00"),
            bytes.fromhex("0b 20 07 00 10 00 10 00 00 00"),
            bytes.fromhex("0c 20 02 01 00"), bytes.fromhex("0c 20 02 00 00"),
        )
        for packet in packets:
            require(template.count(packet) == 1, f"HCI packet changed: {packet.hex()}")
        require(template.index(packets[-2]) < template.index(packets[-1]), "scan cleanup order changed")
        require(report_a["gop_framebuffer_write_authorized"] == "centered-128x128-square-only", "display authority changed")
        require(report_a["command_service_uuids"] == {
            "blue": "52414242-4954-4C45-8000-000000000002",
            "yellow": "52414242-4954-4C45-8000-000000000003"}, "command identities changed")
        require(report_a["persistent_writes_authorized"] == 0 and report_a["writes_performed"] == [], "persistent write appeared")
        require(not any(report_a[field] for field in (
            "active_scan_authorized", "radio_transmit_authorized",
            "pairing_authorized", "connection_authorized")), "forbidden radio authority appeared")
        print("PASS: one deterministic image loads exact QCA RAM and exposes only BLUE/YELLOW")
        print("PASS: initial yellow square and bounded centered framebuffer writes are pinned")
        print("PASS: passive scan has a 120-second ceiling and mandatory disable cleanup")
        print("PASS: Dell transmit, active scan, pairing, connection, storage, and firmware writes remain forbidden")
        print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")

        probe, target = load_json(PROBE_PATH), load_json(TARGET_PATH)
        third = copy.deepcopy(probe); third["commands"]["red"] = "52414242-4954-4C45-8000-000000000004"
        rejected("a third command", lambda: validate_probe(third))
        long_window = copy.deepcopy(probe); long_window["limits"]["max_scan_events"] = 601
        rejected("a larger receive window", lambda: validate_probe(long_window))
        broad_pixels = copy.deepcopy(target); broad_pixels["authority"]["gop_framebuffer_write"] = "unbounded"
        rejected("unbounded framebuffer writes", lambda: validate_target(broad_pixels))
        for field in ("active_scan", "radio_transmit", "advertise", "pair", "connect", "internal_storage_writes", "firmware_writes"):
            unsafe = copy.deepcopy(target); unsafe["authority"][field] = True
            rejected(f"target permitting {field}", lambda unsafe=unsafe: validate_target(unsafe))
    except (BuildError, OSError, RuntimeError) as error:
        print(f"FAIL: {error}"); return 1
    print("PASS: pre-QEMU BLE color-command runtime contract")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
