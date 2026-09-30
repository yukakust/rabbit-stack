#!/usr/bin/env python3
"""Lower a strict data-only world description to Rabbit Universal Package v2."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from package import Object, PackageError, Program, Sprite, build_package


FIELDS = {"schema_version", "world_id", "palette", "sprites", "programs", "objects"}
SPRITE_FIELDS = {"id", "name", "width", "height", "frames"}
PROGRAM_FIELDS = {"id", "name", "code"}
OBJECT_FIELDS = {"id", "sprite", "program", "x", "y", "vx", "vy", "target"}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PackageError(f"duplicate JSON field {key!r}")
        result[key] = value
    return result


def compile_world(path: Path, counter: int, private: Ed25519PrivateKey) -> bytes:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs,
                       parse_constant=lambda item: (_ for _ in ()).throw(PackageError(f"non-standard number {item}")))
    if not isinstance(value, dict) or set(value) != FIELDS or value["schema_version"] != 2:
        raise PackageError("world fields or schema differ from v2")
    if not isinstance(value["world_id"], str) or re.fullmatch(r"[a-z0-9][a-z0-9.-]{0,63}", value["world_id"]) is None:
        raise PackageError("world_id is invalid")
    if any(not isinstance(item, str) or re.fullmatch(r"[0-9a-f]{6}", item) is None for item in value["palette"]):
        raise PackageError("palette entries must be lowercase six-digit RGB")
    if any(not isinstance(item, dict) or set(item) != SPRITE_FIELDS for item in value["sprites"]):
        raise PackageError("sprite fields differ from v2")
    if any(not isinstance(item, dict) or set(item) != PROGRAM_FIELDS for item in value["programs"]):
        raise PackageError("program fields differ from v2")
    if any(not isinstance(item, dict) or set(item) != OBJECT_FIELDS for item in value["objects"]):
        raise PackageError("object fields differ from v2")
    palette = tuple(int(item, 16) for item in value["palette"])
    sprites = tuple(Sprite(item["id"], item["width"], item["height"], tuple(bytes(int(character, 16) for character in frame) for frame in item["frames"])) for item in value["sprites"])
    programs = tuple(Program(item["id"], bytes(item["code"])) for item in value["programs"])
    objects = tuple(Object(item["id"], item["sprite"], item["program"], item["x"], item["y"], item["vx"], item["vy"], item["target"]) for item in value["objects"])
    return build_package(counter=counter, palette=palette, sprites=sprites, objects=objects, programs=programs, private_key=private)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("world", type=Path)
    parser.add_argument("--counter", type=int, required=True)
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        private_bytes = args.private_key.read_bytes()
        if len(private_bytes) != 32:
            raise PackageError("private key must contain exactly 32 bytes")
        package = compile_world(args.world, args.counter, Ed25519PrivateKey.from_private_bytes(private_bytes))
        args.output.write_bytes(package)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL: {error}")
        return 1
    print(f"BUILT: {args.output} ({len(package)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
