#!/usr/bin/env python3
"""Verify the exact bounded BLE BLUE/YELLOW framebuffer-command runtime."""

from __future__ import annotations

import copy, hashlib
from pathlib import Path

from fetch_firmware import fetch_all
from rabbit_qca_beacon import (
    BuildError, PROGRAM_SHA256, PROGRAM_TEMPLATE_SHA256, PROGRAM_TEMPLATE_SIZE,
    PROBE_PATH, TARGET_PATH, build_fetched, load_json, load_program,
    load_template, validate_probe, validate_target,
)

EXPECTED = {
    "probe_sha256": "d43e7fcdda0ec3c2f83085663d078bd27f86763fbbd162f68642ddd851aab977",
    "target_sha256": "a90a9aa0d35cca26b5e0d612505fe60b2859aae549f427ae5078fe79b295e804",
    "source_sha256": "d99e3065a803d721b299a0ddf77290a6901984c4296cefbc957b6081bebf1a3e",
    "program_template_sha256": PROGRAM_TEMPLATE_SHA256,
    "program_sha256": PROGRAM_SHA256,
    "efi_sha256": "972197a4938695f0b331a60b610102970b9bcf465dad1d1b707281b6d8208f72",
    "image_sha256": "669b11d4313a1cb0c0d26404ffbbc0c56dd5321361e309beebe1ac2df69a8107",
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
            b"RABBIT BLE COLOR COMMAND v0.2", b"INITIAL SQUARE=YELLOW",
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

        old_qemu = load_json(Path(__file__).resolve().parent / "evidence" / "qemu-macos-arm64-v01-observed.json")
        require(old_qemu["bindings"]["image_sha256"] == "bce85e8c67d71f45c0c118c3616e9a62c1d4ee6228d0b29a1bbe6b4ed52aa00d", "v0.1 QEMU evidence changed")
        physical_failure = load_json(Path(__file__).resolve().parent / "evidence" / "dell-optiplex-3060-v01-gop-entry-stall-physical-observed.json")
        require(physical_failure["status"] == "OBSERVED-MANUAL-PHYSICAL-GOP-ENTRY-STALL", "v0.1 failure evidence changed")
        require(physical_failure["observation"]["last_visible_line"] == "TARGET FOUND; EVENT ENDPOINT=81", "v0.1 failure boundary changed")
        require(physical_failure["observation"]["passive_scan_observed"] is False, "v0.1 failure incorrectly claims radio scan")
        print("PASS: archived v0.1 evidence localizes the physical stop before GOP, HCI, and radio")

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
    print("PASS: corrected pre-QEMU BLE color-command v0.2 contract")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
