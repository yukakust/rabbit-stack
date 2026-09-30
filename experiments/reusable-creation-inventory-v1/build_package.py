#!/usr/bin/env python3
"""Build a signed, shareable Reusable Creation Inventory v1 package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from rabbit_inventory import InventoryError, build_share_package, canonical_bytes, load_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parent / "catalog.json")
    parser.add_argument("--merge", type=Path, required=True)
    parser.add_argument("--private-key", type=Path, required=True, help="path to exactly 32 raw Ed25519 private-key bytes")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        private_bytes = args.private_key.read_bytes()
        if len(private_bytes) != 32:
            raise InventoryError("private key file must contain exactly 32 raw bytes")
        package, report = build_share_package(
            load_json(args.catalog),
            load_json(args.merge),
            Ed25519PrivateKey.from_private_bytes(private_bytes),
        )
        args.output.write_bytes(package)
        args.report.write_bytes(canonical_bytes(report) + b"\n")
    except (OSError, InventoryError, ValueError) as error:
        print(f"FAIL: {error}")
        return 1
    print(f"BUILT: {args.output} ({len(package)} bytes)")
    print(f"CREATION: {report['creation_id']} {report['creation_sha256']}")
    print(f"COMPONENTS: {report['component_count']}")
    print(f"PACKAGE SHA256: {report['package_sha256']}")
    print("STATUS: SIGNED-INVENTORY-PACKAGE-NOT-DEPLOYED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
