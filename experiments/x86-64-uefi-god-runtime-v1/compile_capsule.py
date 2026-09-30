#!/usr/bin/env python3
"""Verify a signed Inventory package and lower it to a signed physical capsule."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from capsule import CAT_CREATION_SHA256, TOON_CREATION_SHA256, SceneConfig, encode

ROOT = Path(__file__).resolve().parent
INVENTORY = ROOT.parent / "reusable-creation-inventory-v1"
sys.path.insert(0, str(INVENTORY))
from rabbit_inventory import InventoryError, InventoryPackage  # noqa: E402


def compile_package(package: bytes, private_bytes: bytes, counter: int) -> bytes:
    if len(private_bytes) != 32:
        raise InventoryError("Creator private key must contain exactly 32 raw bytes")
    private = Ed25519PrivateKey.from_private_bytes(private_bytes)
    public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    _, payload = InventoryPackage.decode_and_verify(package, public)
    lock = payload["lock"]
    scenes = {CAT_CREATION_SHA256: "cat-ball", TOON_CREATION_SHA256: "toon-cat-mouse"}
    if lock["creation_sha256"] not in scenes or lock["grants"] != ["display.draw", "time.read"]:
        raise InventoryError("Inventory package is not a reviewed Cat Scene/Anima Creation")
    import hashlib
    return encode(SceneConfig(counter=counter, inventory_package_sha256=hashlib.sha256(package).hexdigest(),
                              scene=scenes[lock["creation_sha256"]]), private)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--counter", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise InventoryError("refusing to overwrite capsule output")
        capsule = compile_package(args.package.read_bytes(), args.private_key.read_bytes(), args.counter)
        args.output.write_bytes(capsule)
    except (InventoryError, OSError, ValueError, KeyError) as error:
        print(f"FAIL: {error}")
        return 1
    import hashlib
    print(f"CAPSULE: {args.output} ({len(capsule)} bytes)")
    print(f"SHA256: {hashlib.sha256(capsule).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
