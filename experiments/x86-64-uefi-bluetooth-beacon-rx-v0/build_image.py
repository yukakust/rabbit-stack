#!/usr/bin/env python3
"""Build the deterministic receive-only UEFI Rabbit BLE beacon image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rabbit_beacon_rx import PROBE_PATH, TARGET_PATH, build, load_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    image, report = build(load_json(PROBE_PATH), load_json(TARGET_PATH))
    args.output.write_bytes(image)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILT: {args.output} ({len(image)} bytes)")
    print(f"EFI SHA256: {report['efi_sha256']}")
    print(f"IMAGE SHA256: {report['image_sha256']}")
    print("STATUS: BUILT-NOT-INSTALLED; passive radio receive authorized; radio transmit authorized=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
