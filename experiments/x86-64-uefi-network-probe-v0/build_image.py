#!/usr/bin/env python3
"""Build the reviewed network-probe UEFI USB image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rabbit_network_probe import BuildError, PROBE_PATH, TARGET_PATH, build, load_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Rabbit read-only UEFI network probe")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        image, report = build(load_json(PROBE_PATH), load_json(TARGET_PATH))
        args.output.write_bytes(image)
        if args.report:
            args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"BUILT: {args.output} ({len(image)} bytes)")
        print(f"EFI SHA256: {report['efi_sha256']}")
        print(f"IMAGE SHA256: {report['image_sha256']}")
        print("STATUS: BUILT-NOT-INSTALLED; network_packets_sent=0; configuration_data_writes=0")
        return 0
    except (BuildError, OSError) as error:
        print(f"FAIL: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
