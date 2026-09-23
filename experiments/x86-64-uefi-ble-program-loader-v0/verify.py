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
    PacketError, bytes_to_uuid, decode_ack, decode_frame, decode_program, decode_transfer,
    encode_ack, encode_program, encode_transfer, fnv1a32, frame_to_uuid,
)

EXPECTED = {
    "probe_sha256": "95259cef1d95f92425f1ce910f327a335868d069080ce61dff36467929df008b",
    "target_sha256": "59df2392ddd963429d85cfb9e79a699ae1535d35c1a46fb2f834286ff4aa250f",
    "source_sha256": "b90dd30f3ebf23482a80d65712f5fbc0d1760168fd3d9da65c9cb74613bbd049",
    "program_template_sha256": PROGRAM_TEMPLATE_SHA256,
    "program_sha256": PROGRAM_SHA256,
    "efi_sha256": "484cc5d420ed2691649412bf2651ee228e553cf38c15882143d548b55cbcabcc",
    "image_sha256": "a56c358736c4122d0f9aeb8b69d862d306bbcc370e5ad29681d9d0be2de05077",
}

V02_BINDINGS = {
    "program_sha256": "f25668c0211bd0e7d3aa07f869e8ea517a80df876d8bd990c225e5faf5cd39d3",
    "efi_sha256": "64c81e301cd552f42a3ee67743d6ebcf1a386215f5276fd27ce3de9412198c52",
    "image_sha256": "0d0b53b980bd4645b624aeb7489aa0d36fb93e302bd0edfa77e869e6cb161c9f",
}

V03_BINDINGS = {
    "probe_sha256": "e4a09cc6b7550316fbc6a158a58eb8714789a09a147d9abaa39e9d02f1607a4a",
    "target_sha256": "30be62d430fdc2e7ae9fb9e4b0576cc716e197aa1b582d17473f505c27e7fe54",
    "firmware_manifest_sha256": "cabf8be8ee76815a03d1407fd635c983563303a9661f9419d82e9dbcb3e81dfc",
    "program_sha256": "9304d59a6088c5513558a4b393b4943932df532055805b85f800e7c7a8f89a7c",
    "efi_sha256": "7bb3b4875eb331213ae5bd4de8e58da35f634cb7960178d0862de4232ce95f54",
    "image_sha256": "3a40d06832762b6436e9410766bc3db781ae0e01020c0024c32a82367322b548",
}

SENDER_FILES = {
    "mac_vm_program.m": "815c0f82ba1a70cd3605f16e46502a1ce64ef09a43da14c6e137237d2d9942d1",
    "send_program.py": "7be8e66e476bd1ee5aa84d6beb2815fa72914cc66399d2982954f5bfc6b49985",
    "rabbit_vm_packet.py": "d54b2cea93eebd0053f86d1e6689024cbb73032caa5cdcc8045992129a49ac47",
    "RabbitColorCommand-Info.plist": "b79c9db6d00c4767716e9f6eaa5e3b93ef1f2adcc589897ca49cefcf4f680b47",
    "verify_mac_sender.py": "5312a71becef1bd5add58a8419922a06ed5a504b42cce0d67393a7fc31ed09b6",
}


def require(condition: bool, message: str) -> None:
    if not condition: raise RuntimeError(message)


def rejected(label: str, action) -> None:
    try: action()
    except (BuildError, PacketError): print(f"PASS: rejected {label}"); return
    raise RuntimeError(f"invalid case accepted: {label}")


def main() -> int:
    root = Path(__file__).resolve().parent
    image_a, report_a = build_fetched(); image_b, report_b = build_fetched()
    require(image_a == image_b and report_a == report_b, "repeated builds differ")
    for field, expected in EXPECTED.items(): require(report_a[field] == expected, f"{field} changed")
    template = load_template(); program_bytes = load_program(fetch_all())
    require(len(template) == PROGRAM_TEMPLATE_SIZE, "template size changed")
    require(hashlib.sha256(template).hexdigest() == PROGRAM_TEMPLATE_SHA256, "template changed")
    require(hashlib.sha256(program_bytes).hexdigest() == PROGRAM_SHA256, "program changed")
    for name, expected in SENDER_FILES.items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, f"sender file changed: {name}")
    sender_source = (root / "mac_vm_program.m").read_text(encoding="utf-8")
    require("ACK RECEIVED: TRANSFER=" in sender_source and "scanForPeripheralsWithServices:nil" in sender_source,
            "Mac acknowledgement receiver is missing")
    for marker in (b"RABBIT WIRELESS PROGRAM LOADER v0.4", b"PASSIVE RX + BOUNDED ACK; ESC TO STOP",
                   b"PROGRAM APPLIED", b"ACK ADVERTISED FOR 1500 MS", b"NO NATIVE CODE; NO PAIR; NO CONNECT"):
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
    ack = encode_ack(transfer_id=frames[0][3], program_hash=fnv1a32(triangle), applied_counter=1)
    require(decode_ack(ack) == {"transfer_id": frames[0][3], "program_hash": fnv1a32(triangle), "applied_counter": 1}, "ACK round-trip changed")
    require(len(bytes_to_uuid(ack)) == 36, "ACK UUID envelope changed")
    damaged_ack = bytearray(ack); damaged_ack[8] ^= 1
    rejected("a damaged acknowledgement", lambda: decode_ack(bytes(damaged_ack)))
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
                  "advertise", "pair", "connect", "internal_storage_writes", "firmware_writes"):
        mutated = copy.deepcopy(target); mutated["authority"][field] = True
        rejected(f"target permitting {field}", lambda value=mutated: validate_target(value))
    expanded = copy.deepcopy(target); expanded["authority"]["accepted_vm_opcodes"].append("EXEC_NATIVE")
    rejected("an unreviewed native-code opcode", lambda: validate_target(expanded))
    require(report_a["persistent_writes_authorized"] == 0, "persistent write authority appeared")
    require(report_a["native_code_execution_authorized"] is False, "native execution appeared")
    require(report_a["radio_transmit_authorized"] == "exact-program-acknowledgement-only",
            "build report does not describe exact acknowledgement transmit authority")
    require(report_a["advertising_authorized"] == "nonconnectable-exact-ack-for-1500ms-per-valid-commit",
            "build report does not describe bounded acknowledgement advertising")
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
    for field, expected in V03_BINDINGS.items():
        require(current["bindings"][field] == expected, f"archived QEMU v0.3 evidence changed for {field}")
    current_observed = current["observation"]
    require(current_observed["visible_identity"] == "RABBIT WIRELESS PROGRAM LOADER v0.3", "current QEMU visible identity changed")
    require(current_observed["result"] == "TARGET NOT FOUND; NO DEVICE WRITE SENT", "current QEMU mismatch result changed")
    require(not current_observed["target_found"] and all(current_observed[field] == 0 for field in (
        "controller_ram_writes", "vm_program_bytes_received", "hci_commands_sent",
        "radio_operations_requested", "framebuffer_writes_performed")), "current QEMU crossed a forbidden mismatch boundary")
    physical_success = load_json(Path(__file__).resolve().parent / "evidence" / "dell-optiplex-3060-v03-triangle-program-physical-observed.json")
    require(physical_success["status"] == "OBSERVED-MANUAL-PHYSICAL-RABBIT-VM-PROGRAM-APPLIED", "physical success status changed")
    for field, expected in V03_BINDINGS.items():
        require(physical_success["bindings"][field] == expected, f"physical v0.3 success evidence changed for {field}")
    transferred = physical_success["transferred_program"]
    transferred_bytes = bytes.fromhex(transferred["bytecode_hex"])
    require(decode_program(transferred_bytes) == {
        "vm_version": 1, "shape": "triangle", "rgb": [51, 102, 255], "size": 96,
        "arrows": True, "step": 16, "x": 400, "y": 240,
    }, "physical transferred program changed")
    require(len(encode_transfer(transferred_bytes)) == transferred["transport_frame_count"] == 6, "physical transfer framing changed")
    success_observed = physical_success["observation"]
    require(success_observed["complete_program_applied"] and success_observed["triangle_visible"], "physical program application evidence changed")
    require(not success_observed["usb_moved_after_boot"] and not success_observed["dell_rebooted_for_program"] and success_observed["persistent_writes"] == 0, "physical runtime boundary changed")
    replacement = load_json(Path(__file__).resolve().parent / "evidence" / "dell-optiplex-3060-v03-hot-replacement-physical-observed.json")
    require(replacement["status"] == "OBSERVED-MANUAL-PHYSICAL-RABBIT-VM-HOT-REPLACEMENT", "physical replacement status changed")
    for field, expected in V03_BINDINGS.items():
        require(replacement["bindings"][field] == expected, f"physical v0.3 replacement evidence changed for {field}")
    first_bytes = bytes.fromhex(replacement["session"]["first_program"]["bytecode_hex"])
    replacement_bytes = bytes.fromhex(replacement["session"]["replacement_program"]["bytecode_hex"])
    require(decode_program(first_bytes)["shape"] == "triangle", "recorded first physical shape changed")
    require(decode_program(replacement_bytes) == {
        "vm_version": 1, "shape": "square", "rgb": [34, 204, 102], "size": 64,
        "arrows": True, "step": 24, "x": 650, "y": 350,
    }, "recorded replacement program changed")
    replacement_observed = replacement["observation"]
    require(all(replacement_observed[field] for field in (
        "triangle_moved_up", "triangle_moved_down", "triangle_moved_left", "triangle_moved_right",
        "replacement_program_applied", "old_triangle_removed", "green_square_visible",
        "green_square_arrow_control_worked", "same_loader_runtime")), "physical hot-replacement observation changed")
    require(not replacement_observed["usb_moved_between_programs"] and not replacement_observed["dell_rebooted_between_programs"] and replacement_observed["persistent_writes"] == 0, "physical hot-replacement boundary changed")
    print("PASS: deterministic UEFI image contains the transactional Rabbit VM loader")
    print("PASS: BEGIN + CHUNK + COMMIT transports exact programs and rejects loss, reorder, substitution, and corruption")
    print("PASS: complete square and triangle programs configure color, position, size, and arrow movement")
    print("PASS: old scene remains active until a complete bounded program validates and commits")
    print("PASS: ACK binds transfer, hash, and counter; damaged acknowledgements are rejected")
    print("PASS: Dell transmit is restricted to a 1500 ms nonconnectable exact-program acknowledgement")
    print("PASS: native code, arbitrary memory, arbitrary transmit, pairing, connection, and persistence remain forbidden")
    print("PASS: archived v0.2 QEMU mismatch evidence remains bound to its exact artifact")
    print("PASS: physical v0.2 failure is localized before the chained runtime's first UEFI call")
    print("PASS: archived v0.3 QEMU mismatch evidence remains bound to its exact artifact")
    print("PASS: physical v0.3 accepted and displayed a complete six-frame triangle program without reboot or USB movement")
    print("PASS: one physical runtime moved the triangle and atomically replaced it with an arrow-controlled green square")
    print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
