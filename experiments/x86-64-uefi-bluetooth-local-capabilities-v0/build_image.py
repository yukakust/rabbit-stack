#!/usr/bin/env python3
"""Build the deterministic UEFI Bluetooth local-capability image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rabbit_hci_capabilities import PROBE_PATH, TARGET_PATH, build, load_json


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
    print("STATUS: BUILT-NOT-INSTALLED; local HCI opcodes 0x1002/0x1003/0x2003; radio packets authorized=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
