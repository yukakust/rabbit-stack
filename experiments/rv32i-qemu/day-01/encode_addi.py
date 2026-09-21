#!/usr/bin/env python3
"""Encode one base-RV32I ``addi`` instruction without an assembler.

The encoder accepts reviewed *fields*, not free-form assembly text:

    encode_addi(rd=6, rs1=0, imm=65)
        -> 0x04100313
        -> b"\x13\x03\x10\x04" in little-endian memory order
"""

from __future__ import annotations

import argparse


OPCODE_OP_IMM = 0b0010011
FUNCT3_ADDI = 0b000
REGISTER_MIN = 0
REGISTER_MAX = 31
IMM_MIN = -2048
IMM_MAX = 2047


def _require_register(name: str, value: int) -> None:
    if not REGISTER_MIN <= value <= REGISTER_MAX:
        raise ValueError(
            f"{name} must be a RISC-V register number from "
            f"{REGISTER_MIN} to {REGISTER_MAX}, got {value}"
        )


def _require_immediate(value: int) -> None:
    if not IMM_MIN <= value <= IMM_MAX:
        raise ValueError(
            f"imm must fit in a signed 12-bit field "
            f"({IMM_MIN} to {IMM_MAX}), got {value}"
        )


def encode_addi(rd: int, rs1: int, imm: int) -> int:
    """Return the 32-bit RV32I word for ``addi rd, rs1, imm``.

    ``rd`` and ``rs1`` are register numbers from 0 through 31. ``imm`` is a
    signed 12-bit integer. The returned Python integer represents the logical
    instruction word; memory byte order is handled separately.
    """

    _require_register("rd", rd)
    _require_register("rs1", rs1)
    _require_immediate(imm)

    return (
        ((imm & 0xFFF) << 20)
        | (rs1 << 15)
        | (FUNCT3_ADDI << 12)
        | (rd << 7)
        | OPCODE_OP_IMM
    )


def encode_addi_bytes(rd: int, rs1: int, imm: int) -> bytes:
    """Return ``addi`` in the little-endian byte order used by RV32I memory."""

    return encode_addi(rd, rs1, imm).to_bytes(4, byteorder="little")


def _parse_integer(text: str) -> int:
    """Accept decimal values such as ``65`` and hexadecimal values such as ``0x41``."""

    return int(text, 0)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Encode one RV32I addi instruction without an assembler."
    )
    parser.add_argument("rd", type=_parse_integer, help="destination register number")
    parser.add_argument("rs1", type=_parse_integer, help="source register number")
    parser.add_argument("imm", type=_parse_integer, help="signed 12-bit immediate")
    args = parser.parse_args()

    try:
        word = encode_addi(args.rd, args.rs1, args.imm)
    except ValueError as error:
        parser.error(str(error))

    encoded_bytes = word.to_bytes(4, byteorder="little")
    print(f"word:  0x{word:08x}")
    print(f"bytes: {encoded_bytes.hex(' ')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
