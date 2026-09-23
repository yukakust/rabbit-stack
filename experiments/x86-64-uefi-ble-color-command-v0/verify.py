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
    "probe_sha256": "4a26f0563f759b9670cea083fbb8b0d84826031131e0b449b57275075f678453",
    "target_sha256": "a90a9aa0d35cca26b5e0d612505fe60b2859aae549f427ae5078fe79b295e804",
    "source_sha256": "8363da22819d4db5cc7f421424345dc121149c4ae05e0271336359f634c37b7c",
    "program_template_sha256": PROGRAM_TEMPLATE_SHA256,
    "program_sha256": PROGRAM_SHA256,
    "efi_sha256": "9aafb29440b31cd99303c4176c6d82f8b3f64589eeb5154241470bd5ba081056",
    "image_sha256": "63ea281431ca09cce91d7bedf0ca9684f17f2020422fee17bfe42021bac34f1f",
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
            b"RABBIT BLE COLOR COMMAND v0.3", b"INITIAL SQUARE DRAWN=YELLOW",
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
        qemu_v02 = load_json(Path(__file__).resolve().parent / "evidence" / "qemu-macos-arm64-v02-observed.json")
        require(qemu_v02["status"] == "OBSERVED-MANUAL-QEMU-BLE-COLOR-COMMAND-V0.2-FAIL-CLOSED", "v0.2 QEMU evidence status changed")
        require(qemu_v02["bindings"]["program_sha256"] == "7e9a0490a95a3f3be8854678ce69d038985f1a9d69aa0d4333451aa458912372", "v0.2 QEMU program binding changed")
        require(qemu_v02["bindings"]["image_sha256"] == "669b11d4313a1cb0c0d26404ffbbc0c56dd5321361e309beebe1ac2df69a8107", "v0.2 QEMU image binding changed")
        observation = qemu_v02["observation"]
        require(observation["visible_identity"] == "RABBIT BLE COLOR COMMAND v0.2", "v0.2 visible identity changed")
        require(observation["result"] == "TARGET NOT FOUND; NO DEVICE WRITE SENT" and not observation["target_found"], "v0.2 mismatch result changed")
        require(observation["controller_ram_writes"] == observation["hci_commands_sent"] == observation["radio_operations_requested"] == observation["framebuffer_writes_performed"] == 0, "v0.2 mismatch crossed an authority boundary")
        print("PASS: exact v0.2 QEMU mismatch stops before RAM, corrected GOP, HCI, and radio")
        physical_v02 = load_json(Path(__file__).resolve().parent / "evidence" / "dell-optiplex-3060-v02-framebuffer-pointer-blackout-physical-observed.json")
        require(physical_v02["status"] == "OBSERVED-MANUAL-PHYSICAL-FRAMEBUFFER-POINTER-BLACKOUT", "v0.2 physical evidence status changed")
        require(physical_v02["observation"]["last_visible_line"] == "TARGET FOUND; EVENT ENDPOINT=81", "v0.2 failure boundary changed")
        require(physical_v02["observation"]["passive_scan_observed"] is False, "v0.2 incorrectly claims a scan")
        print("PASS: archived v0.2 evidence localizes the blackout to the first framebuffer draw")

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
    print("PASS: corrected pre-QEMU BLE color-command v0.3 contract")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
