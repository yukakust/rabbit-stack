#!/usr/bin/env python3
"""Rabbit BLE transport v2 with 16-bit ordered chunk numbers."""

from __future__ import annotations

from package import MAX_PACKAGE_BYTES

MAGIC = b"RP"
FRAME_BEGIN, FRAME_CHUNK, FRAME_COMMIT = 1, 2, 3
PAYLOAD_SIZE = 6


class TransportError(ValueError):
    pass


def fnv1a32(data: bytes) -> int:
    value = 0x811C9DC5
    for byte in data:
        value = ((value ^ byte) * 0x01000193) & 0xFFFFFFFF
    return value


def frame(kind: int, transfer: int, sequence: int, payload: bytes) -> bytes:
    if kind not in (1, 2, 3) or not 0 <= transfer <= 255 or not 0 <= sequence <= 0xFFFF or len(payload) > PAYLOAD_SIZE:
        raise TransportError("invalid frame fields")
    head = MAGIC + bytes((0x20 | kind, transfer)) + sequence.to_bytes(2, "little") + payload.ljust(PAYLOAD_SIZE, b"\0")
    return head + fnv1a32(head).to_bytes(4, "big")


def decode_frame(value: bytes) -> tuple[int, int, int, bytes]:
    if len(value) != 16 or value[:2] != MAGIC or value[2] >> 4 != 2 or value[2] & 15 not in (1, 2, 3):
        raise TransportError("invalid v2 frame envelope")
    if fnv1a32(value[:12]) != int.from_bytes(value[12:], "big"):
        raise TransportError("frame checksum mismatch")
    return value[2] & 15, value[3], int.from_bytes(value[4:6], "little"), value[6:12]


def encode_transfer(package: bytes) -> list[bytes]:
    if not 1 <= len(package) <= MAX_PACKAGE_BYTES:
        raise TransportError("package exceeds the physical RAM budget")
    digest = fnv1a32(package)
    transfer = digest & 255 or 1
    chunks = (len(package) + PAYLOAD_SIZE - 1) // PAYLOAD_SIZE
    result = [frame(FRAME_BEGIN, transfer, 0, len(package).to_bytes(2, "little") + digest.to_bytes(4, "big"))]
    result.extend(frame(FRAME_CHUNK, transfer, sequence, package[offset:offset + PAYLOAD_SIZE]) for sequence, offset in enumerate(range(0, len(package), PAYLOAD_SIZE)))
    result.append(frame(FRAME_COMMIT, transfer, chunks, digest.to_bytes(4, "big") + len(package).to_bytes(2, "little")))
    return result


def decode_transfer(frames: list[bytes]) -> bytes:
    if len(frames) < 3:
        raise TransportError("transfer is incomplete")
    kind, transfer, sequence, begin = decode_frame(frames[0])
    length, digest = int.from_bytes(begin[:2], "little"), int.from_bytes(begin[2:], "big")
    chunks = (length + PAYLOAD_SIZE - 1) // PAYLOAD_SIZE
    if kind != FRAME_BEGIN or sequence or not 1 <= length <= MAX_PACKAGE_BYTES or len(frames) != chunks + 2:
        raise TransportError("invalid BEGIN or frame count")
    assembled = bytearray()
    for expected, raw in enumerate(frames[1:-1]):
        item_kind, item_transfer, item_sequence, payload = decode_frame(raw)
        if (item_kind, item_transfer, item_sequence) != (FRAME_CHUNK, transfer, expected):
            raise TransportError("missing, reordered, or substituted CHUNK")
        assembled.extend(payload)
    kind, item_transfer, sequence, commit = decode_frame(frames[-1])
    if (kind, item_transfer, sequence) != (FRAME_COMMIT, transfer, chunks) or int.from_bytes(commit[:4], "big") != digest or int.from_bytes(commit[4:], "little") != length:
        raise TransportError("COMMIT differs from BEGIN")
    result = bytes(assembled[:length])
    if fnv1a32(result) != digest:
        raise TransportError("assembled package checksum mismatch")
    return result


def as_uuid(value: bytes) -> str:
    decode_frame(value)
    encoded = value.hex().upper()
    return f"{encoded[:8]}-{encoded[8:12]}-{encoded[12:16]}-{encoded[16:20]}-{encoded[20:]}"


def encode_segments(package, block_chunks=32):
    """Same v2 envelopes, prefix checkpoints; an ACK never authorizes a world."""
    if type(block_chunks) is not int or not 1 <= block_chunks <= 64:
        raise TransportError("checkpoint block size outside budget")
    complete = encode_transfer(package)
    digest = fnv1a32(package); transfer = complete[0][3]
    segments = []; hashes = []
    chunks = complete[1:-1]
    for start in range(0, len(chunks), block_chunks):
        end = min(start+block_chunks, len(chunks)); length = min(end*6,len(package))
        prefix_hash = fnv1a32(package[:length])
        block = ([complete[0]] if start == 0 else []) + chunks[start:end]
        block.append(frame(FRAME_COMMIT,transfer,end,prefix_hash.to_bytes(4,"big")+length.to_bytes(2,"little")))
        segments.append([as_uuid(value) for value in block]); hashes.append(f"{prefix_hash:08X}")
    return {"segments":segments,"hashes":hashes}
