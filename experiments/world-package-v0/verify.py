#!/usr/bin/env python3
"""Verify the first target-independent Rabbit World Package."""

from __future__ import annotations

import copy
import hashlib
import json
import struct
import tempfile
from collections.abc import Callable
from pathlib import Path

from rabbit_package import (
    HEADER, INTERPRETATION_PATH, MAGIC, VERSION, WORLD_PATH, PackageError,
    build_package, canonical_bytes, decode_package, load_json,
)


EXPECTED_WORLD_SHA256 = "94a67cd0e7b83e56a12f07bf32ffc783af694220fcb2a746943e074435998cc0"
EXPECTED_INTERPRETATION_SHA256 = "abf91417fdd737d412cdf50e16b82464a8b2a323949039aacfa2a4b5af611db5"
EXPECTED_MANIFEST_SHA256 = "2b494b110b1a8f5da03a49a6a0f5f8fdde521eb40e2621196a8d18cbe1ce1c0a"
EXPECTED_BYTECODE_SHA256 = "b276fe8e4fe87f2eddd1db7a4ad0cf850fac5b54438c5e089523556b32a60831"
EXPECTED_PACKAGE_SHA256 = "e7d642aef7810cb8edfeb51693b29c7909024ae5d3dc4fb9741e44e4b42b8d9b"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejected(label: str, action: Callable[[], object]) -> None:
    try:
        action()
    except (PackageError, KeyError, TypeError, ValueError) as error:
        print(f"PASS: rejected {label}: {error}")
        return
    raise RuntimeError(f"invalid case accepted: {label}")


def decode_instructions(code: bytes) -> list[tuple[object, ...]]:
    """Independent, deliberately tiny decoder for the reviewed opcode set."""
    result: list[tuple[object, ...]] = []
    offset = 0
    formats = {
        0x01: "<HHBB3B", 0x02: "<BB3B", 0x10: "<B", 0x11: "<BBI",
        0x12: "<BBB", 0x20: "", 0x21: "", 0xFE: "<BB", 0xFF: "",
    }
    while offset < len(code):
        opcode = code[offset]
        offset += 1
        if opcode not in formats:
            raise RuntimeError(f"unknown bytecode opcode 0x{opcode:02x}")
        fmt = formats[opcode]
        size = struct.calcsize(fmt)
        require(offset + size <= len(code), "truncated bytecode instruction")
        values = struct.unpack_from(fmt, code, offset) if fmt else ()
        offset += size
        result.append((opcode, *values))
        if opcode == 0xFF:
            require(offset == len(code), "bytes follow END instruction")
    return result


def rewrite_manifest(package: bytes, change: Callable[[dict[str, object]], None]) -> bytes:
    _, _, _, manifest_size, code_size, _ = HEADER.unpack_from(package)
    manifest = json.loads(package[HEADER.size:HEADER.size + manifest_size].decode("ascii"))
    change(manifest)
    encoded = canonical_bytes(manifest)
    header = HEADER.pack(MAGIC, VERSION, 0, len(encoded), code_size, hashlib.sha256(encoded).digest())
    return header + encoded + package[-code_size:]


def main() -> int:
    try:
        world = load_json(WORLD_PATH)
        interpretation = load_json(INTERPRETATION_PATH)
        package_a, report_a = build_package(world, interpretation)
        package_b, report_b = build_package(copy.deepcopy(world), copy.deepcopy(interpretation))
        require(package_a == package_b and report_a == report_b, "repeated package builds differ")
        require(report_a["world_sha256"] == EXPECTED_WORLD_SHA256, "world identity changed")
        require(report_a["interpretation_sha256"] == EXPECTED_INTERPRETATION_SHA256, "interpretation identity changed")
        require(report_a["manifest_sha256"] == EXPECTED_MANIFEST_SHA256, "manifest identity changed")
        require(report_a["bytecode_sha256"] == EXPECTED_BYTECODE_SHA256, "bytecode identity changed")
        require(report_a["package_sha256"] == EXPECTED_PACKAGE_SHA256, "package identity changed")
        require(report_a["package_size_bytes"] < 2048, "v0 package no longer fits in two KiB")
        require(report_a["deployments_performed"] == [], "package builder claimed deployment")

        decoded_world, code = decode_package(package_a)
        require(decoded_world == world, "package round trip changed the world")
        require(
            decode_instructions(code) == [
                (0x01, 100, 100, 64, 16, 255, 212, 0),
                (0x02, 16, 1, 255, 212, 0),
                (0x10, 16),
                (0x11, 32, 32, 120000),
                (0x12, 90, 122, 1),
                (0x20,), (0x21,), (0xFE, 23, 0), (0xFF,),
            ],
            "decoded opcode contract changed",
        )
        lowered = package_a.lower()
        for forbidden in (b"uefi", b"x86", b"qemu", b"framebuffer", b"firmware", b"usb"):
            require(forbidden not in lowered, f"target word {forbidden!r} leaked into package")
        print("PASS: one approved Russian intent compiles deterministically to a target-independent package")
        print(f"PASS: package is {len(package_a)} bytes with world={report_a['world_sha256']}")
        print("PASS: independent decoder recovered player, movement, jump, stone, collision, and exit operations")
        print("PASS: package contains no x86, UEFI, QEMU, framebuffer, firmware, or USB binding")

        tampered = bytearray(package_a)
        tampered[HEADER.size + 10] ^= 1
        rejected("a tampered manifest", lambda: decode_package(bytes(tampered)))
        tampered = bytearray(package_a)
        tampered[-2] ^= 1
        rejected("tampered bytecode", lambda: decode_package(bytes(tampered)))
        truncated = package_a[:-1]
        rejected("a truncated package", lambda: decode_package(truncated))
        stale_interpretation = rewrite_manifest(
            package_a, lambda value: value.__setitem__("interpretation_sha256", "0" * 64)
        )
        rejected("an unapproved interpretation", lambda: decode_package(stale_interpretation))
        changed_world = copy.deepcopy(world)
        changed_world["player"]["movement_step"] = 32
        rejected("semantic drift from the observed world", lambda: build_package(changed_world, interpretation))
        changed_decision = copy.deepcopy(interpretation)
        changed_decision["resolved_decisions"]["stone_count"] = 2
        rejected("interpretation drift", lambda: build_package(world, changed_decision))
        with tempfile.TemporaryDirectory(prefix="rabbit-package-") as directory:
            duplicate = Path(directory) / "duplicate.json"
            duplicate.write_text('{"schema_version":1,"schema_version":1}\n', encoding="utf-8")
            rejected("duplicate JSON fields", lambda: load_json(duplicate))
        print("PASS: tamper, truncation, stale approval, semantic drift, and ambiguous JSON checks are intact")
    except (OSError, PackageError, RuntimeError, struct.error) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: World Package v0 contract; no runtime or physical deployment claimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
