#!/usr/bin/env python3
"""Seven-byte BLE framing for one fixed-width God Runtime capsule."""

from __future__ import annotations

from capsule import CAPSULE_SIZE

MAGIC = b"RP"
FRAME_BEGIN, FRAME_CHUNK, FRAME_COMMIT = 1, 2, 3
PAYLOAD_SIZE = 7


class TransportError(ValueError):
    pass


def fnv1a32(data: bytes) -> int:
    value = 0x811C9DC5
    for byte in data:
        value = ((value ^ byte) * 0x01000193) & 0xFFFFFFFF
    return value


def frame(kind: int, transfer: int, sequence: int, payload: bytes) -> bytes:
    if kind not in (1, 2, 3) or not 0 <= transfer <= 255 or not 0 <= sequence <= 255 or len(payload) > 7:
        raise TransportError("invalid frame fields")
    head = MAGIC + bytes((0x10 | kind, transfer, sequence)) + payload.ljust(7, b"\0")
    return head + fnv1a32(head).to_bytes(4, "big")


def decode_frame(value: bytes) -> tuple[int, int, int, bytes]:
    if len(value) != 16 or value[:2] != MAGIC or value[2] >> 4 != 1 or value[2] & 15 not in (1, 2, 3):
        raise TransportError("invalid frame envelope")
    if fnv1a32(value[:12]) != int.from_bytes(value[12:], "big"):
        raise TransportError("frame checksum mismatch")
    return value[2] & 15, value[3], value[4], value[5:12]


def encode_transfer(capsule: bytes) -> list[bytes]:
    if len(capsule) != CAPSULE_SIZE:
        raise TransportError("God Runtime capsule must be exactly 192 bytes")
    digest = fnv1a32(capsule)
    transfer = digest & 255 or 1
    chunks = (len(capsule) + 6) // 7
    result = [frame(FRAME_BEGIN, transfer, 0, len(capsule).to_bytes(2, "little") + digest.to_bytes(4, "big") + bytes((chunks,)))]
    result.extend(frame(FRAME_CHUNK, transfer, sequence, capsule[offset:offset + 7]) for sequence, offset in enumerate(range(0, len(capsule), 7)))
    result.append(frame(FRAME_COMMIT, transfer, chunks, digest.to_bytes(4, "big") + len(capsule).to_bytes(2, "little") + b"\0"))
    return result


def decode_transfer(frames: list[bytes]) -> bytes:
    if len(frames) != 30:
        raise TransportError("capsule transfer must contain BEGIN, 28 CHUNKs, and COMMIT")
    kind, transfer, sequence, begin = decode_frame(frames[0])
    length, digest, count = int.from_bytes(begin[:2], "little"), int.from_bytes(begin[2:6], "big"), begin[6]
    if (kind, sequence, length, count) != (FRAME_BEGIN, 0, CAPSULE_SIZE, 28):
        raise TransportError("invalid BEGIN")
    assembled = bytearray()
    for expected, raw in enumerate(frames[1:-1]):
        item_kind, item_transfer, item_sequence, payload = decode_frame(raw)
        if (item_kind, item_transfer, item_sequence) != (FRAME_CHUNK, transfer, expected):
            raise TransportError("missing, reordered, or substituted CHUNK")
        assembled.extend(payload)
    kind, item_transfer, sequence, commit = decode_frame(frames[-1])
    if (kind, item_transfer, sequence) != (FRAME_COMMIT, transfer, 28):
        raise TransportError("invalid COMMIT envelope")
    if int.from_bytes(commit[:4], "big") != digest or int.from_bytes(commit[4:6], "little") != CAPSULE_SIZE or commit[6]:
        raise TransportError("COMMIT differs from BEGIN")
    result = bytes(assembled[:CAPSULE_SIZE])
    if fnv1a32(result) != digest:
        raise TransportError("assembled capsule checksum mismatch")
    return result


def as_uuid(value: bytes) -> str:
    decode_frame(value)
    encoded = value.hex().upper()
    return f"{encoded[:8]}-{encoded[8:12]}-{encoded[12:16]}-{encoded[16:20]}-{encoded[20:]}"
