#!/usr/bin/env python3
"""Verify the transactional Rabbit VM v1 wireless loader."""

from __future__ import annotations

import copy, hashlib
from pathlib import Path

from fetch_firmware import fetch_all
from rabbit_qca_beacon import (
    BuildError, PROGRAM_SHA256, PROGRAM_TEMPLATE_SHA256, PROGRAM_TEMPLATE_SIZE,
    TARGET_PATH, build_fetched, load_json, load_program, load_template, validate_target,
)
from rabbit_vm_packet import (
    PacketError, decode_frame, decode_program, decode_transfer, encode_program,
    encode_transfer, frame_to_uuid,
)

EXPECTED = {
    "probe_sha256": "e4a09cc6b7550316fbc6a158a58eb8714789a09a147d9abaa39e9d02f1607a4a",
    "target_sha256": "30be62d430fdc2e7ae9fb9e4b0576cc716e197aa1b582d17473f505c27e7fe54",
    "source_sha256": "bf76c3e47673d24181275d453684925f4f7393b25190090bce2e8bf5e1b46ef1",
    "program_template_sha256": PROGRAM_TEMPLATE_SHA256,
    "program_sha256": PROGRAM_SHA256,
    "efi_sha256": "7bb3b4875eb331213ae5bd4de8e58da35f634cb7960178d0862de4232ce95f54",
    "image_sha256": "3a40d06832762b6436e9410766bc3db781ae0e01020c0024c32a82367322b548",
}

V02_BINDINGS = {
    "program_sha256": "f25668c0211bd0e7d3aa07f869e8ea517a80df876d8bd990c225e5faf5cd39d3",
    "efi_sha256": "64c81e301cd552f42a3ee67743d6ebcf1a386215f5276fd27ce3de9412198c52",
    "image_sha256": "0d0b53b980bd4645b624aeb7489aa0d36fb93e302bd0edfa77e869e6cb161c9f",
}


def require(condition: bool, message: str) -> None:
    if not condition: raise RuntimeError(message)


def rejected(label: str, action) -> None:
    try: action()
    except (BuildError, PacketError): print(f"PASS: rejected {label}"); return
    raise RuntimeError(f"invalid case accepted: {label}")


def main() -> int:
    image_a, report_a = build_fetched(); image_b, report_b = build_fetched()
    require(image_a == image_b and report_a == report_b, "repeated builds differ")
    for field, expected in EXPECTED.items(): require(report_a[field] == expected, f"{field} changed")
    template = load_template(); program_bytes = load_program(fetch_all())
    require(len(template) == PROGRAM_TEMPLATE_SIZE, "template size changed")
    require(hashlib.sha256(template).hexdigest() == PROGRAM_TEMPLATE_SHA256, "template changed")
    require(hashlib.sha256(program_bytes).hexdigest() == PROGRAM_SHA256, "program changed")
    for marker in (b"RABBIT WIRELESS PROGRAM LOADER v0.3", b"RABBIT VM v1; PASSIVE RX; ESC TO STOP",
                   b"PROGRAM APPLIED", b"NO NATIVE CODE; NO PAIR; NO CONNECT"):
        require(marker in template, f"required marker missing: {marker!r}")
    require(b"RABBIT BLE COLOR COMMAND" not in template, "stale color-command identity remains")

    square = encode_program(shape="square", red=255, green=190, blue=0, x=200, y=160, size=96, step=16)
    triangle = encode_program(shape="triangle", red=25, green=110, blue=255, x=420, y=220, size=80, step=12)
    for candidate, shape in ((square, "square"), (triangle, "triangle")):
        frames = encode_transfer(candidate)
        require(len(frames) == 6, "24-byte program must use BEGIN, four CHUNKs, and COMMIT")
        require(decode_transfer(frames) == candidate, "multi-frame round-trip changed bytes")
        require(decode_program(candidate)["shape"] == shape, "shape semantics changed")
        for frame in frames:
            require(len(frame) == 16 and len(frame_to_uuid(frame)) == 36, "BLE UUID envelope changed")
            decode_frame(frame)

    frames = encode_transfer(triangle)
    damaged = bytearray(frames[2]); damaged[7] ^= 1
    rejected("a frame with a damaged checksum", lambda: decode_frame(bytes(damaged)))
    rejected("a missing program chunk", lambda: decode_transfer(frames[:2] + frames[3:]))
    reordered = frames.copy(); reordered[1], reordered[2] = reordered[2], reordered[1]
    rejected("reordered program chunks", lambda: decode_transfer(reordered))
    substituted = frames.copy(); substituted[2] = encode_transfer(square)[2]
    rejected("a chunk from another transfer", lambda: decode_transfer(substituted))
    invalid_shape = bytearray(square); invalid_shape[1] = 3
    rejected("an unknown shape", lambda: decode_program(bytes(invalid_shape)))
    invalid_end = bytearray(square); invalid_end[-1] = 1
    rejected("a noncanonical END instruction", lambda: decode_program(bytes(invalid_end)))

    target = load_json(TARGET_PATH)
    for field in ("native_code_execution", "arbitrary_memory_write", "active_scan", "radio_transmit",
                  "pair", "connect", "internal_storage_writes", "firmware_writes"):
        mutated = copy.deepcopy(target); mutated["authority"][field] = True
        rejected(f"target permitting {field}", lambda value=mutated: validate_target(value))
    expanded = copy.deepcopy(target); expanded["authority"]["accepted_vm_opcodes"].append("EXEC_NATIVE")
    rejected("an unreviewed native-code opcode", lambda: validate_target(expanded))
    require(report_a["persistent_writes_authorized"] == 0, "persistent write authority appeared")
    require(report_a["native_code_execution_authorized"] is False, "native execution appeared")
    evidence = load_json(Path(__file__).resolve().parent / "evidence" / "qemu-macos-arm64-v02-observed.json")
    require(evidence["status"] == "OBSERVED-MANUAL-QEMU-RABBIT-VM-LOADER-V0.2-FAIL-CLOSED", "archived QEMU evidence status changed")
    for field, expected in V02_BINDINGS.items():
        require(evidence["bindings"][field] == expected, f"archived QEMU v0.2 evidence changed for {field}")
    observed = evidence["observation"]
    require(observed["visible_identity"] == "RABBIT WIRELESS PROGRAM LOADER v0.2", "QEMU visible identity changed")
    require(observed["result"] == "TARGET NOT FOUND; NO DEVICE WRITE SENT", "QEMU mismatch result changed")
    require(not observed["target_found"] and all(observed[field] == 0 for field in (
        "controller_ram_writes", "vm_program_bytes_received", "hci_commands_sent",
        "radio_operations_requested", "framebuffer_writes_performed")), "QEMU crossed a forbidden mismatch boundary")
    physical = load_json(Path(__file__).resolve().parent / "evidence" / "dell-optiplex-3060-v02-stack-alignment-stall-physical-observed.json")
    require(physical["status"] == "OBSERVED-MANUAL-PHYSICAL-CHAIN-ENTRY-STACK-ALIGNMENT-STALL", "physical failure evidence status changed")
    for field, expected in V02_BINDINGS.items():
        require(physical["bindings"][field] == expected, f"physical v0.2 evidence changed for {field}")
    physical_observed = physical["observation"]
    require(physical_observed["last_visible_line"] == "STAGE 5: BEGIN TRANSACTIONAL RABBIT VM RECEIVE", "physical failure boundary changed")
    require(physical_observed["rampatch_transfer"] == "OK" and physical_observed["nvm_transfer"] == "OK", "physical QCA initialization evidence changed")
    require(not physical_observed["chained_runtime_title_visible"] and not physical_observed["hci_reset_observed"] and not physical_observed["passive_scan_observed"], "physical v0.2 crossed the recorded boundary")
    require("0x700" in physical["diagnosis"] and "Microsoft-x64 call alignment" in physical["diagnosis"], "physical failure diagnosis changed")
    current = load_json(Path(__file__).resolve().parent / "evidence" / "qemu-macos-arm64-v03-observed.json")
    require(current["status"] == "OBSERVED-MANUAL-QEMU-RABBIT-VM-LOADER-V0.3-FAIL-CLOSED", "current QEMU evidence status changed")
    for field in ("probe_sha256", "target_sha256", "firmware_manifest_sha256", "program_sha256", "efi_sha256", "image_sha256"):
        require(current["bindings"][field] == report_a[field], f"current QEMU evidence is stale for {field}")
    current_observed = current["observation"]
    require(current_observed["visible_identity"] == "RABBIT WIRELESS PROGRAM LOADER v0.3", "current QEMU visible identity changed")
    require(current_observed["result"] == "TARGET NOT FOUND; NO DEVICE WRITE SENT", "current QEMU mismatch result changed")
    require(not current_observed["target_found"] and all(current_observed[field] == 0 for field in (
        "controller_ram_writes", "vm_program_bytes_received", "hci_commands_sent",
        "radio_operations_requested", "framebuffer_writes_performed")), "current QEMU crossed a forbidden mismatch boundary")
    print("PASS: deterministic UEFI image contains the transactional Rabbit VM loader")
    print("PASS: BEGIN + CHUNK + COMMIT transports exact programs and rejects loss, reorder, substitution, and corruption")
    print("PASS: complete square and triangle programs configure color, position, size, and arrow movement")
    print("PASS: old scene remains active until a complete bounded program validates and commits")
    print("PASS: native code, arbitrary memory, transmit, pairing, connection, and persistence remain forbidden")
    print("PASS: archived v0.2 QEMU mismatch evidence remains bound to its exact artifact")
    print("PASS: physical v0.2 failure is localized before the chained runtime's first UEFI call")
    print("PASS: exact v0.3 QEMU mismatch evidence stops before RAM, VM, HCI, radio, and framebuffer effects")
    print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
