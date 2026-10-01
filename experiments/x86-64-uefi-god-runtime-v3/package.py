"""RUP3 graphics: 256 RGBA colors, bounded RLE sprites, unchanged behavior VM."""
import importlib.util
import struct
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

LEGACY = Path(__file__).resolve().parent.parent / "x86-64-uefi-god-runtime-v2"
spec = importlib.util.spec_from_file_location("rabbit_v2_package", LEGACY / "package.py")
v2 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v2
spec.loader.exec_module(v2)
PackageError = v2.PackageError
MAX_PACKAGE_BYTES = 65535
MAX_DECODED_PIXELS = 262144


def rle_encode(pixels):
    out = bytearray()
    cursor = 0
    while cursor < len(pixels):
        end = cursor + 1
        while end < len(pixels) and pixels[end] == pixels[cursor] and end - cursor < 255:
            end += 1
        out.extend((end - cursor, pixels[cursor]))
        cursor = end
    return bytes(out)


def rle_decode(data, expected, palette_count):
    if len(data) % 2:
        raise PackageError("RLE record has an odd byte count")
    out = bytearray()
    for cursor in range(0, len(data), 2):
        count, index = data[cursor:cursor + 2]
        if not count or index >= palette_count or len(out) + count > expected:
            raise PackageError("RLE run is invalid or exceeds decoded geometry")
        out.extend(bytes((index,)) * count)
    if len(out) != expected:
        raise PackageError("RLE output differs from decoded geometry")
    return bytes(out)


def decode_package(data, public, minimum_counter=0):
    if data[:4] == b"RUP2":
        return v2.decode_package(data, public, minimum_counter)
    if not 96 <= len(data) <= MAX_PACKAGE_BYTES:
        raise PackageError("package exceeds the 65535-byte signed RAM budget")
    fields = struct.unpack_from("<4sBBHIBBBBHHHHHHHH", data)
    magic, version, flags, total, counter, pc, sc, oc, nc, po, so, oo, no, sig, tick, width, height = fields
    pc = pc or 256
    if (magic, version) != (b"RUP3", 3) or flags & ~1 or total != len(data) or counter <= minimum_counter:
        raise PackageError("unsupported header or stale counter")
    if not (1 <= pc <= 256 and 1 <= sc <= 16 and 1 <= oc <= 16 and 1 <= nc <= 16):
        raise PackageError("component budget exceeded")
    if (tick, width, height) != (33, 160, 90) or not (po == 32 and so == po + pc * 4 and so <= oo <= no <= sig == total - 64 and no - oo == oc * 16):
        raise PackageError("surface, clock, or section boundaries differ from contract")
    try:
        Ed25519PublicKey.from_public_bytes(public).verify(data[sig:], data[:sig])
    except Exception as error:
        raise PackageError("invalid Creator signature") from error
    palette = [tuple(data[i:i+4]) for i in range(po, so, 4)]
    if palette[0] != (0, 0, 0, 0):
        raise PackageError("palette slot zero must be transparent black")
    sprites = []; ids = set(); cursor = so; decoded_budget = 0
    for _ in range(sc):
        if cursor + 8 > oo:
            raise PackageError("truncated sprite record")
        sid, w, h, frames, length, dw, dh = struct.unpack_from("<BBBBHBB", data, cursor)
        cursor += 8
        if not sid or sid in ids or not (1 <= w <= 128 and 1 <= h <= 128 and 1 <= frames <= 16 and 1 <= dw <= 64 and 1 <= dh <= 64) or cursor + length > oo:
            raise PackageError("invalid sprite geometry, display size, or identity")
        expected = w * h * frames; decoded_budget += expected
        if decoded_budget > MAX_DECODED_PIXELS:
            raise PackageError("decoded sprite budget exceeded")
        pixels = rle_decode(data[cursor:cursor+length], expected, pc)
        cursor += length; ids.add(sid)
        sprites.append({"id": sid, "width": w, "height": h, "frames": frames,
                        "display_width": dw, "display_height": dh, "pixels": pixels})
    if cursor != oo:
        raise PackageError("sprite section has trailing bytes")
    objects = []; object_ids = set()
    for cursor in range(oo, no, 16):
        oid, sid, pid, frame, x, y, vx, vy, target, reserved, r1, r2 = struct.unpack_from("<BBBBHHbbBBHH", data, cursor)
        if not oid or oid in object_ids or sid not in ids or frame or reserved or r1 or r2 or x >= 160 or y >= 90 or abs(vx) > 8 or abs(vy) > 8:
            raise PackageError("invalid initial object state")
        object_ids.add(oid)
        objects.append({"id": oid, "sprite": sid, "program": pid, "frame": frame, "x": x, "y": y, "vx": vx, "vy": vy, "target": target})
    programs = []; program_ids = set(); cursor = no
    for _ in range(nc):
        if cursor + 2 > sig:
            raise PackageError("truncated program record")
        pid, length = data[cursor:cursor+2]; cursor += 2
        if not pid or pid in program_ids or cursor + length > sig:
            raise PackageError("invalid program identity or boundary")
        code = data[cursor:cursor+length]; cursor += length
        v2._validate_program(code, object_ids)
        steps = offset = 0
        while offset < len(code):
            opcode = code[offset]; offset += 1; steps += 1
            if opcode in (3, 4, 6):
                if code[offset+1] > 8:
                    raise PackageError("behavior magnitude exceeds 8")
                offset += 2
            elif opcode == 5:
                offset += 1
        if steps > 16:
            raise PackageError("VM tick instruction budget exceeded")
        program_ids.add(pid); programs.append({"id": pid, "code": code})
    if cursor != sig or any(o["program"] not in program_ids or (o["target"] != 255 and o["target"] not in object_ids) for o in objects):
        raise PackageError("program section or object references are invalid")
    return {"version": 3, "counter": counter, "health_fault": bool(flags), "palette": palette,
            "sprites": sprites, "objects": objects, "programs": programs}


def build_package(world, counter, private):
    palette = bytes.fromhex("".join(world["palette"]))
    sprites = bytearray()
    for item in world["sprites"]:
        raw = bytes.fromhex("".join(item["frames"]))
        if any(len(bytes.fromhex(frame)) != item["width"] * item["height"] for frame in item["frames"]):
            raise PackageError("sprite frame geometry mismatch")
        packed = rle_encode(raw)
        if len(packed) > 65535:
            raise PackageError("sprite encoded bytes exceed section budget")
        sprites += struct.pack("<BBBBHBB", item["id"], item["width"], item["height"], len(item["frames"]), len(packed), item["display_width"], item["display_height"]) + packed
    objects = b"".join(struct.pack("<BBBBHHbbBBHH", o["id"], o["sprite"], o["program"], 0, o["x"], o["y"], o["vx"], o["vy"], o["target"], 0, 0, 0) for o in world["objects"])
    programs = b"".join(bytes((p["id"], len(p["code"]))) + bytes(p["code"]) for p in world["programs"])
    so = 32 + len(palette); oo = so + len(sprites); no = oo + len(objects); sig = no + len(programs); total = sig + 64
    if total > MAX_PACKAGE_BYTES:
        raise PackageError("package exceeds the signed RAM budget")
    header = struct.pack("<4sBBHIBBBBHHHHHHHH", b"RUP3", 3, 0, total, counter,
                         len(world["palette"]) % 256, len(world["sprites"]), len(world["objects"]), len(world["programs"]), 32, so, oo, no, sig, 33, 160, 90)
    body = header + palette + sprites + objects + programs
    result = body + private.sign(body)
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    decode_package(result, private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw))
    return result
