#!/usr/bin/env python3
"""Build the first target-independent Rabbit World Package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rabbit_package import INTERPRETATION_PATH, WORLD_PATH, build_package, load_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a target-independent Rabbit World Package")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    package, report = build_package(load_json(WORLD_PATH), load_json(INTERPRETATION_PATH))
    args.output.write_bytes(package)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILT: {args.output} ({len(package)} bytes)")
    print(f"SHA256: {report['package_sha256']}")
    print("STATUS: PACKAGE-BUILT-NOT-DEPLOYED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
