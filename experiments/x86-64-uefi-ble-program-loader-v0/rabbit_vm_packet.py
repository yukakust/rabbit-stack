#!/usr/bin/env python3
"""Rabbit VM bytecode and its 16-byte multi-frame BLE transport."""

from __future__ import annotations

MAGIC = b"RP"
ACK_MAGIC = b"RA"
PROTOCOL_VERSION = 1
FRAME_BEGIN, FRAME_CHUNK, FRAME_COMMIT = 1, 2, 3
ACK_APPLIED = 1
FRAME_SIZE, PAYLOAD_SIZE = 16, 7
VM_VERSION = 1
OP_DEFINE_SHAPE, OP_SET_POSITION, OP_END = 1, 2, 0xFF
SHAPES = {"square": 1, "triangle": 2}
MAX_PROGRAM_SIZE = 224


class PacketError(ValueError):
    pass


def fnv1a32(data: bytes) -> int:
    value = 0x811C9DC5
    for byte in data:
        value ^= byte
        value = (value * 0x01000193) & 0xFFFFFFFF
    return value


def _frame(frame_type: int, transfer_id: int, sequence: int, payload: bytes) -> bytes:
    if len(payload) > PAYLOAD_SIZE:
        raise PacketError("frame payload exceeds seven bytes")
    head = MAGIC + bytes(((PROTOCOL_VERSION << 4) | frame_type, transfer_id, sequence))
    body = head + payload.ljust(PAYLOAD_SIZE, b"\0")
    return body + fnv1a32(body).to_bytes(4, "big")


def decode_frame(frame: bytes) -> dict[str, object]:
    if len(frame) != FRAME_SIZE or frame[:2] != MAGIC:
        raise PacketError("invalid Rabbit transport frame")
    if frame[2] >> 4 != PROTOCOL_VERSION or frame[2] & 0x0F not in (1, 2, 3):
        raise PacketError("unsupported Rabbit transport version or frame type")
    if int.from_bytes(frame[12:], "big") != fnv1a32(frame[:12]):
        raise PacketError("Rabbit transport checksum mismatch")
    return {"type": frame[2] & 0x0F, "transfer_id": frame[3], "sequence": frame[4], "payload": frame[5:12]}


def encode_program(*, shape: str, red: int, green: int, blue: int,
                   x: int, y: int, size: int, step: int, arrows: bool = True) -> bytes:
    if shape not in SHAPES:
        raise PacketError("shape must be square or triangle")
    values = (red, green, blue)
    if any(isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 255 for v in values):
        raise PacketError("RGB components must be integers from 0 through 255")
    if not 8 <= size <= 128:
        raise PacketError("size must be from 8 through 128")
    if not 1 <= step <= 64:
        raise PacketError("step must be from 1 through 64")
    if not 0 <= x <= 65535 or not 0 <= y <= 65535:
        raise PacketError("position must fit unsigned 16-bit coordinates")
    define = bytes((OP_DEFINE_SHAPE, SHAPES[shape], red, green, blue, size, int(arrows), step))
    position = bytes((OP_SET_POSITION,)) + x.to_bytes(2, "little") + y.to_bytes(2, "little") + b"\0\0\0"
    end = bytes((OP_END, 0, 0, 0, 0, 0, 0, 0))
    return define + position + end


def decode_program(program: bytes) -> dict[str, object]:
    if len(program) != 24:
        raise PacketError("Rabbit VM v1 scene program must be exactly 24 bytes")
    define, position, end = program[:8], program[8:16], program[16:24]
    if define[0] != OP_DEFINE_SHAPE or define[1] not in SHAPES.values():
        raise PacketError("program must begin with DEFINE_SHAPE")
    if not 8 <= define[5] <= 128 or define[6] & ~1 or not 1 <= define[7] <= 64:
        raise PacketError("invalid shape size, control flags, or movement step")
    if position[0] != OP_SET_POSITION or position[5:] != b"\0\0\0":
        raise PacketError("program must contain a canonical SET_POSITION")
    if end != bytes((OP_END, 0, 0, 0, 0, 0, 0, 0)):
        raise PacketError("program must end canonically")
    shape = next(name for name, value in SHAPES.items() if value == define[1])
    return {
        "vm_version": VM_VERSION, "shape": shape,
        "rgb": list(define[2:5]), "size": define[5], "arrows": bool(define[6]),
        "step": define[7], "x": int.from_bytes(position[1:3], "little"),
        "y": int.from_bytes(position[3:5], "little"),
    }


def encode_transfer(program: bytes) -> list[bytes]:
    decoded = decode_program(program)
    del decoded
    if len(program) > MAX_PROGRAM_SIZE:
        raise PacketError("program exceeds the v1 RAM budget")
    digest = fnv1a32(program)
    transfer_id = digest & 0xFF or 1
    begin_payload = len(program).to_bytes(2, "little") + digest.to_bytes(4, "big") + bytes((len(program) // 8,))
    frames = [_frame(FRAME_BEGIN, transfer_id, 0, begin_payload)]
    for sequence, offset in enumerate(range(0, len(program), PAYLOAD_SIZE)):
        frames.append(_frame(FRAME_CHUNK, transfer_id, sequence, program[offset:offset + PAYLOAD_SIZE]))
    commit_payload = digest.to_bytes(4, "big") + len(program).to_bytes(2, "little") + b"\0"
    frames.append(_frame(FRAME_COMMIT, transfer_id, len(frames) - 1, commit_payload))
    return frames


def decode_transfer(frames: list[bytes]) -> bytes:
    if len(frames) < 3:
        raise PacketError("transfer is incomplete")
    begin = decode_frame(frames[0])
    if begin["type"] != FRAME_BEGIN or begin["sequence"] != 0:
        raise PacketError("transfer does not begin canonically")
    transfer_id = int(begin["transfer_id"]); payload = bytes(begin["payload"])
    length = int.from_bytes(payload[:2], "little"); expected_hash = int.from_bytes(payload[2:6], "big")
    if length <= 0 or length > MAX_PROGRAM_SIZE or payload[6] != length // 8:
        raise PacketError("invalid declared program size")
    chunks = bytearray(); expected_sequence = 0
    for raw in frames[1:-1]:
        frame = decode_frame(raw)
        if frame["type"] != FRAME_CHUNK or frame["transfer_id"] != transfer_id or frame["sequence"] != expected_sequence:
            raise PacketError("missing, reordered, or substituted program chunk")
        chunks.extend(bytes(frame["payload"])); expected_sequence += 1
    commit = decode_frame(frames[-1]); commit_payload = bytes(commit["payload"])
    if commit["type"] != FRAME_COMMIT or commit["transfer_id"] != transfer_id or commit["sequence"] != expected_sequence:
        raise PacketError("invalid transfer commit")
    if int.from_bytes(commit_payload[:4], "big") != expected_hash or int.from_bytes(commit_payload[4:6], "little") != length or commit_payload[6] != 0:
        raise PacketError("commit does not match begin")
    program = bytes(chunks[:length])
    if len(program) != length or fnv1a32(program) != expected_hash:
        raise PacketError("assembled program hash mismatch")
    decode_program(program)
    return program


def frame_to_uuid(frame: bytes) -> str:
    decode_frame(frame)
    return bytes_to_uuid(frame)


def encode_ack(*, transfer_id: int, program_hash: int, applied_counter: int) -> bytes:
    if not 0 <= transfer_id <= 255:
        raise PacketError("ACK transfer id must fit one byte")
    if not 0 <= program_hash <= 0xFFFFFFFF or not 1 <= applied_counter <= 0xFFFFFFFF:
        raise PacketError("ACK hash or application counter is out of range")
    body = (ACK_MAGIC + bytes(((PROTOCOL_VERSION << 4) | ACK_APPLIED, transfer_id))
        + program_hash.to_bytes(4, "big") + applied_counter.to_bytes(4, "big"))
    return body + fnv1a32(body).to_bytes(4, "big")


def decode_ack(value: bytes) -> dict[str, int]:
    if len(value) != FRAME_SIZE or value[:2] != ACK_MAGIC:
        raise PacketError("invalid Rabbit acknowledgement")
    if value[2] != (PROTOCOL_VERSION << 4) | ACK_APPLIED:
        raise PacketError("unsupported Rabbit acknowledgement version or status")
    if int.from_bytes(value[12:], "big") != fnv1a32(value[:12]):
        raise PacketError("Rabbit acknowledgement checksum mismatch")
    return {
        "transfer_id": value[3],
        "program_hash": int.from_bytes(value[4:8], "big"),
        "applied_counter": int.from_bytes(value[8:12], "big"),
    }


def bytes_to_uuid(value: bytes) -> str:
    if len(value) != FRAME_SIZE:
        raise PacketError("Rabbit UUID payload must be exactly 16 bytes")
    encoded = value.hex().upper()
    return f"{encoded[:8]}-{encoded[8:12]}-{encoded[12:16]}-{encoded[16:20]}-{encoded[20:]}"
