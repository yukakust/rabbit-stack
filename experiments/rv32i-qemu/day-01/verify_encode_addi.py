#!/usr/bin/env python3
"""Check reviewed vectors and rejection boundaries for ``encode_addi.py``."""

from __future__ import annotations

from encode_addi import encode_addi, encode_addi_bytes


def expect_encoding(
    label: str, rd: int, rs1: int, imm: int, expected_word: int, expected_bytes: str
) -> None:
    word = encode_addi(rd, rs1, imm)
    encoded_bytes = encode_addi_bytes(rd, rs1, imm)
    expected_byte_value = bytes.fromhex(expected_bytes)

    if word != expected_word:
        raise AssertionError(
            f"{label}: expected word 0x{expected_word:08x}, got 0x{word:08x}"
        )
    if encoded_bytes != expected_byte_value:
        raise AssertionError(
            f"{label}: expected bytes {expected_byte_value.hex(' ')}, "
            f"got {encoded_bytes.hex(' ')}"
        )

    print(f"PASS: {label}: 0x{word:08x} -> {encoded_bytes.hex(' ')}")


def expect_rejection(label: str, rd: int, rs1: int, imm: int) -> None:
    try:
        encode_addi(rd, rs1, imm)
    except ValueError:
        print(f"PASS: {label} was rejected")
        return
    raise AssertionError(f"{label}: invalid input was accepted")


def main() -> int:
    # The first two vectors were decoded manually in Day 01 and exercised in QEMU.
    expect_encoding("load ASCII A into t1", 6, 0, 65, 0x04100313, "13 03 10 04")
    expect_encoding("load ASCII B into t1", 6, 0, 66, 0x04200313, "13 03 20 04")

    # This vector changes both register fields while retaining a zero immediate.
    expect_encoding("addi x1, x2, 0", 1, 2, 0, 0x00010093, "93 00 01 00")

    expect_rejection("rd=32", 32, 0, 0)
    expect_rejection("rs1=-1", 0, -1, 0)
    expect_rejection("imm=2048", 0, 0, 2048)
    expect_rejection("imm=-2049", 0, 0, -2049)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
