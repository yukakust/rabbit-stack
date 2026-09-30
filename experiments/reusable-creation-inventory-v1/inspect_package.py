#!/usr/bin/env python3
"""Verify and summarize one shared Inventory v1 package from a trusted Creator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rabbit_inventory import InventoryError, InventoryPackage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--trusted-public-key", type=Path, required=True, help="path to exactly 32 trusted raw Ed25519 public-key bytes")
    args = parser.parse_args()
    try:
        _, payload = InventoryPackage.decode_and_verify(args.package.read_bytes(), args.trusted_public_key.read_bytes())
    except (OSError, InventoryError, ValueError) as error:
        print(f"REJECTED: {error}")
        return 1
    lock = payload["lock"]
    print(f"VERIFIED CREATOR PACKAGE: {lock['creation']['name']}")
    print(f"CREATION ID: {lock['creation']['creation_id']}@{lock['creation']['version']}")
    print(f"IDENTITY: {lock['creation_sha256']}")
    print(f"COMPONENTS: {len(lock['components'])}")
    print(f"AUTHORITIES: {', '.join(lock['grants'])}")
    print("RESOURCES: " + json.dumps(lock["resources"], sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
