#!/usr/bin/env python3
"""Encode and validate the first 16-byte Rabbit VM wireless program."""

from __future__ import annotations

MAGIC = b"RBVM"
VERSION = 1
OP_SET_SQUARE_COLOR = 1
PACKET_SIZE = 16


class PacketError(ValueError):
    pass


def fnv1a32(data: bytes) -> int:
    value = 0x811C9DC5
    for byte in data:
        value ^= byte
        value = (value * 0x01000193) & 0xFFFFFFFF
    return value


def encode_set_square_color(red: int, green: int, blue: int) -> bytes:
    values = (red, green, blue)
    if any(isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 255 for value in values):
        raise PacketError("RGB components must be integers from 0 through 255")
    body = MAGIC + bytes((VERSION, OP_SET_SQUARE_COLOR, red, green, blue, 0, 0, 0))
    return body + fnv1a32(body).to_bytes(4, "big")


def decode(packet: bytes) -> dict[str, object]:
    if len(packet) != PACKET_SIZE:
        raise PacketError("Rabbit VM packet must be exactly 16 bytes")
    if packet[:4] != MAGIC:
        raise PacketError("Rabbit VM magic mismatch")
    if packet[4] != VERSION:
        raise PacketError("unsupported Rabbit VM version")
    if packet[5] != OP_SET_SQUARE_COLOR:
        raise PacketError("unsupported Rabbit VM opcode")
    if packet[9:12] != b"\0\0\0":
        raise PacketError("reserved Rabbit VM bytes must be zero")
    expected = fnv1a32(packet[:12])
    observed = int.from_bytes(packet[12:16], "big")
    if observed != expected:
        raise PacketError("Rabbit VM checksum mismatch")
    return {
        "version": VERSION,
        "opcode": "SET_SQUARE_COLOR",
        "rgb": [packet[6], packet[7], packet[8]],
        "checksum": f"{observed:08X}",
    }


def packet_to_uuid(packet: bytes) -> str:
    decode(packet)
    value = packet.hex().upper()
    return f"{value[:8]}-{value[8:12]}-{value[12:16]}-{value[16:20]}-{value[20:]}"

