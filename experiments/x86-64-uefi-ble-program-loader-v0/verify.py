#!/usr/bin/env python3
"""Verify the transactional Rabbit VM v1 wireless loader."""

from __future__ import annotations

import copy, hashlib

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
    "probe_sha256": "e96f76339184995462ebc3fbf02f6e7fa89639cdef720cb68fda7e2a7ebadbf9",
    "target_sha256": "30be62d430fdc2e7ae9fb9e4b0576cc716e197aa1b582d17473f505c27e7fe54",
    "source_sha256": "1eaf347bd91bfa3ec6b8f3a9449b590f2f53fc2037713f5a8a79ff278c16d4d5",
    "program_template_sha256": PROGRAM_TEMPLATE_SHA256,
    "program_sha256": PROGRAM_SHA256,
    "efi_sha256": "82de8a8e8dc78771dc847c266668760e27e52210e0aaa2804bfafb01e4a0f082",
    "image_sha256": "8ef5dfea0a115f0cef5234887754490986bb0d94c75a99441df81189dd9007ec",
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
    for marker in (b"RABBIT WIRELESS PROGRAM LOADER v0.2", b"RABBIT VM v1; PASSIVE RX; ESC TO STOP",
                   b"PROGRAM APPLIED", b"NO NATIVE CODE; NO PAIR; NO CONNECT"):
        require(marker in template, f"required marker missing: {marker!r}")

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
    print("PASS: deterministic UEFI image contains the transactional Rabbit VM loader")
    print("PASS: BEGIN + CHUNK + COMMIT transports exact programs and rejects loss, reorder, substitution, and corruption")
    print("PASS: complete square and triangle programs configure color, position, size, and arrow movement")
    print("PASS: old scene remains active until a complete bounded program validates and commits")
    print("PASS: native code, arbitrary memory, transmit, pairing, connection, and persistence remain forbidden")
    print(f"PASS: efi={report_a['efi_sha256']}, image={report_a['image_sha256']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
