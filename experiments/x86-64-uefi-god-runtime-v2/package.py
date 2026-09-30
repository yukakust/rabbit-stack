#!/usr/bin/env python3
"""Compile and validate bounded, signed Rabbit Universal Package v2 files."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Iterable

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


MAGIC = b"RUP2"
VERSION = 2
HEADER_SIZE = 32
SIGNATURE_SIZE = 64
MAX_PACKAGE_BYTES = 4096
MAX_PALETTE = 16
MAX_SPRITES = 16
MAX_OBJECTS = 16
MAX_PROGRAMS = 16
MAX_PROGRAM_BYTES = 32

OP_END = 0
OP_MOVE = 1
OP_BOUNCE = 2
OP_CHASE = 3
OP_FLEE = 4
OP_ANIMATE = 5
OP_COLLIDE = 6


class PackageError(ValueError):
    pass


@dataclass(frozen=True)
class Sprite:
    sprite_id: int
    width: int
    height: int
    frames: tuple[bytes, ...]


@dataclass(frozen=True)
class Program:
    program_id: int
    code: bytes


@dataclass(frozen=True)
class Object:
    object_id: int
    sprite_id: int
    program_id: int
    x: int
    y: int
    vx: int = 0
    vy: int = 0
    target_id: int = 0xFF


def _u8(value: int, label: str) -> int:
    if isinstance(value, bool) or not 0 <= value <= 255:
        raise PackageError(f"{label} must fit uint8")
    return value


def _unique(values: Iterable[int], label: str) -> None:
    items = list(values)
    if len(items) != len(set(items)):
        raise PackageError(f"duplicate {label} id")


def _validate_program(code: bytes, object_ids: set[int]) -> None:
    if not code or len(code) > MAX_PROGRAM_BYTES:
        raise PackageError("program length is outside the VM budget")
    cursor = 0
    ended = False
    while cursor < len(code):
        opcode = code[cursor]
        cursor += 1
        if opcode == OP_END:
            ended = cursor == len(code)
            break
        if opcode in (OP_MOVE, OP_BOUNCE):
            continue
        if opcode in (OP_CHASE, OP_FLEE, OP_COLLIDE):
            if cursor + 2 > len(code) or code[cursor] not in object_ids or code[cursor + 1] == 0:
                raise PackageError("behavior target or magnitude is invalid")
            cursor += 2
            continue
        if opcode == OP_ANIMATE:
            if cursor >= len(code) or code[cursor] == 0:
                raise PackageError("animation period is invalid")
            cursor += 1
            continue
        raise PackageError(f"unknown Rabbit VM opcode {opcode}")
    if not ended:
        raise PackageError("program must end with one canonical END")


def _pack_pixels(frames: tuple[bytes, ...], width: int, height: int, palette_count: int) -> bytes:
    raw = b"".join(frames)
    if not frames or len(frames) > 16 or any(len(frame) != width * height for frame in frames):
        raise PackageError("sprite frame geometry is inconsistent")
    if any(pixel >= palette_count for pixel in raw):
        raise PackageError("sprite references an unknown palette entry")
    result = bytearray()
    for offset in range(0, len(raw), 2):
        high = raw[offset]
        low = raw[offset + 1] if offset + 1 < len(raw) else 0
        result.append((high << 4) | low)
    return bytes(result)


def build_package(*, counter: int, palette: tuple[int, ...], sprites: tuple[Sprite, ...],
                  objects: tuple[Object, ...], programs: tuple[Program, ...],
                  private_key: Ed25519PrivateKey, health_fault: bool = False) -> bytes:
    if isinstance(counter, bool) or not 1 <= counter <= 0xFFFFFFFF:
        raise PackageError("counter must fit nonzero uint32")
    if not 1 <= len(palette) <= MAX_PALETTE or any(not 0 <= value <= 0xFFFFFF for value in palette):
        raise PackageError("palette is outside its budget")
    if not 1 <= len(sprites) <= MAX_SPRITES or not 1 <= len(objects) <= MAX_OBJECTS or not 1 <= len(programs) <= MAX_PROGRAMS:
        raise PackageError("component count is outside the package budget")
    _unique((item.sprite_id for item in sprites), "sprite")
    _unique((item.object_id for item in objects), "object")
    _unique((item.program_id for item in programs), "program")
    sprite_ids = {item.sprite_id for item in sprites}
    object_ids = {item.object_id for item in objects}
    program_ids = {item.program_id for item in programs}
    for item in objects:
        if item.sprite_id not in sprite_ids or item.program_id not in program_ids:
            raise PackageError("object references an unknown component")
        if item.target_id != 0xFF and item.target_id not in object_ids:
            raise PackageError("object target is unknown")
        if not 0 <= item.x < 160 or not 0 <= item.y < 90 or not -8 <= item.vx <= 8 or not -8 <= item.vy <= 8:
            raise PackageError("object state exceeds the reviewed surface or velocity")
    for item in programs:
        _validate_program(item.code, object_ids)

    palette_blob = b"".join(value.to_bytes(3, "big") for value in palette)
    sprite_blob = bytearray()
    for item in sprites:
        _u8(item.sprite_id, "sprite id")
        if not 1 <= item.width <= 16 or not 1 <= item.height <= 16:
            raise PackageError("sprite geometry exceeds 16x16")
        pixels = _pack_pixels(item.frames, item.width, item.height, len(palette))
        sprite_blob += struct.pack("<BBBBHH", item.sprite_id, item.width, item.height, len(item.frames), len(pixels), 0)
        sprite_blob += pixels
    object_blob = bytearray()
    for item in objects:
        object_blob += struct.pack("<BBBBHHbbBBHH", item.object_id, item.sprite_id, item.program_id, 0,
                                   item.x, item.y, item.vx, item.vy, item.target_id, 0, 0, 0)
    program_blob = bytearray()
    for item in programs:
        program_blob += bytes((_u8(item.program_id, "program id"), len(item.code))) + item.code

    palette_offset = HEADER_SIZE
    sprite_offset = palette_offset + len(palette_blob)
    object_offset = sprite_offset + len(sprite_blob)
    program_offset = object_offset + len(object_blob)
    signature_offset = program_offset + len(program_blob)
    total = signature_offset + SIGNATURE_SIZE
    if total > MAX_PACKAGE_BYTES:
        raise PackageError("package exceeds the 4096-byte RAM budget")
    header = struct.pack(
        "<4sBBHIBBBBHHHHHHH", MAGIC, VERSION, int(health_fault), total, counter,
        len(palette), len(sprites), len(objects), len(programs), palette_offset,
        sprite_offset, object_offset, program_offset, signature_offset, 33, 160,
    ) + struct.pack("<H", 90)
    if len(header) != HEADER_SIZE:
        raise AssertionError("header layout changed")
    body = header + palette_blob + bytes(sprite_blob) + bytes(object_blob) + bytes(program_blob)
    return body + private_key.sign(body)


def decode_package(encoded: bytes, public_key: bytes, minimum_counter: int = 0) -> dict[str, object]:
    if not HEADER_SIZE + SIGNATURE_SIZE <= len(encoded) <= MAX_PACKAGE_BYTES:
        raise PackageError("package length is outside the RAM budget")
    fields = struct.unpack_from("<4sBBHIBBBBHHHHHHHH", encoded)
    magic, version, flags, total, counter, palette_count, sprite_count, object_count, program_count, palette_off, sprite_off, object_off, program_off, signature_off, tick_ms, surface_w, surface_h = fields
    if magic != MAGIC or version != VERSION or flags & 0xFE or total != len(encoded):
        raise PackageError("package header is unsupported")
    if counter <= minimum_counter:
        raise PackageError("package counter is stale")
    if (tick_ms, surface_w, surface_h) != (33, 160, 90):
        raise PackageError("runtime surface or clock changed")
    if not (1 <= palette_count <= MAX_PALETTE and 1 <= sprite_count <= MAX_SPRITES and 1 <= object_count <= MAX_OBJECTS and 1 <= program_count <= MAX_PROGRAMS):
        raise PackageError("component count exceeds the runtime budget")
    if not (palette_off == HEADER_SIZE <= sprite_off <= object_off <= program_off <= signature_off == len(encoded) - SIGNATURE_SIZE):
        raise PackageError("package sections overlap or are reordered")
    if sprite_off - palette_off != palette_count * 3 or object_off > len(encoded) or program_off - object_off != object_count * 16:
        raise PackageError("package section size is inconsistent")
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(encoded[signature_off:], encoded[:signature_off])
    except Exception as error:
        raise PackageError("package signature is invalid") from error

    palette = tuple(int.from_bytes(encoded[offset:offset + 3], "big") for offset in range(palette_off, sprite_off, 3))
    sprites: list[dict[str, object]] = []
    cursor = sprite_off
    sprite_ids: set[int] = set()
    while cursor < object_off:
        if cursor + 8 > object_off:
            raise PackageError("sprite header is truncated")
        sprite_id, width, height, frames, data_len, reserved = struct.unpack_from("<BBBBHH", encoded, cursor)
        cursor += 8
        expected = (width * height * frames + 1) // 2
        if reserved or not 1 <= width <= 16 or not 1 <= height <= 16 or not 1 <= frames <= 16 or data_len != expected or cursor + data_len > object_off:
            raise PackageError("sprite record is invalid")
        packed = encoded[cursor:cursor + data_len]
        cursor += data_len
        pixels = []
        for byte in packed:
            pixels.extend((byte >> 4, byte & 15))
        pixels = pixels[:width * height * frames]
        if any(pixel >= palette_count for pixel in pixels) or sprite_id in sprite_ids:
            raise PackageError("sprite palette or identity is invalid")
        sprite_ids.add(sprite_id)
        sprites.append({"id": sprite_id, "width": width, "height": height, "frames": frames, "pixels": bytes(pixels)})
    if len(sprites) != sprite_count or cursor != object_off:
        raise PackageError("sprite count differs from header")

    objects_out = []
    object_ids = set()
    for cursor in range(object_off, program_off, 16):
        object_id, sprite_id, program_id, frame, x, y, vx, vy, target, reserved, r1, r2 = struct.unpack_from("<BBBBHHbbBBHH", encoded, cursor)
        if reserved or r1 or r2 or sprite_id not in sprite_ids or object_id in object_ids or x >= 160 or y >= 90:
            raise PackageError("object record is invalid")
        object_ids.add(object_id)
        objects_out.append({"id": object_id, "sprite": sprite_id, "program": program_id, "frame": frame, "x": x, "y": y, "vx": vx, "vy": vy, "target": target})

    programs_out = []
    program_ids = set()
    cursor = program_off
    while cursor < signature_off:
        if cursor + 2 > signature_off:
            raise PackageError("program header is truncated")
        program_id, length = encoded[cursor], encoded[cursor + 1]
        cursor += 2
        if not 1 <= length <= MAX_PROGRAM_BYTES or cursor + length > signature_off or program_id in program_ids:
            raise PackageError("program record is invalid")
        code = encoded[cursor:cursor + length]
        cursor += length
        _validate_program(code, object_ids)
        program_ids.add(program_id)
        programs_out.append({"id": program_id, "code": code})
    if len(programs_out) != program_count or any(item["program"] not in program_ids or (item["target"] != 0xFF and item["target"] not in object_ids) for item in objects_out):
        raise PackageError("program references or count are invalid")
    return {"counter": counter, "health_fault": bool(flags & 1), "palette": palette, "sprites": sprites, "objects": objects_out, "programs": programs_out}


def demo_package(counter: int, private_key: Ed25519PrivateKey) -> bytes:
    palette = (0x121826, 0x4E79A7, 0xFFFFFF, 0x111111, 0xA9683A, 0xFFF2D6, 0xF2A6B3)
    cat0 = bytes((1,0,0,0,0,0,0,1, 1,1,0,1,1,0,1,1, 0,1,1,1,1,1,1,0, 1,3,1,2,1,2,3,1, 0,1,1,6,1,1,1,0, 0,0,1,1,1,1,0,0, 0,1,1,0,0,1,1,0, 1,0,0,0,0,0,0,1))
    cat1 = cat0[:-16] + bytes((1,0,0,1,1,0,0,1, 0,1,1,0,0,1,1,0))
    mouse0 = bytes((0,4,4,0,0,4,4,0, 4,5,4,4,4,4,5,4, 0,4,4,4,4,4,4,0, 0,0,3,4,6,0,0,0, 0,4,4,4,4,4,0,0, 0,0,4,4,4,0,4,0, 0,4,0,0,0,4,0,4, 4,0,0,0,0,0,0,0))
    mouse1 = mouse0[:-16] + bytes((0,4,0,4,4,4,0,0, 4,0,4,0,0,0,4,0))
    sprites = (Sprite(1, 8, 8, (cat0, cat1)), Sprite(2, 8, 8, (mouse0, mouse1)))
    programs = (Program(1, bytes((OP_CHASE, 2, 2, OP_MOVE, OP_BOUNCE, OP_ANIMATE, 4, OP_END))),
                Program(2, bytes((OP_MOVE, OP_BOUNCE, OP_ANIMATE, 3, OP_END))))
    objects = (Object(1, 1, 1, 20, 60, target_id=2), Object(2, 2, 2, 125, 26, -2, 2, target_id=1))
    return build_package(counter=counter, palette=palette, sprites=sprites, objects=objects, programs=programs, private_key=private_key)
