#!/usr/bin/env python3
"""Build, but never install, the exact Dell Scene/Anima v2 candidate image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rabbit_scene_uefi import BuildError, TARGET_PATH, build, load_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()
    try:
        image, report = build(load_json(TARGET_PATH))
        arguments.output.write_bytes(image)
        if arguments.report:
            arguments.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (BuildError, OSError) as error:
        print(f"FAIL: {error}")
        return 1
    print(f"BUILT: {arguments.output} ({len(image)} bytes)")
    print(f"EFI SHA256: {report['efi_sha256']}")
    print(f"IMAGE SHA256: {report['image_sha256']}")
    print("STATUS: PHYSICAL-CANDIDATE-BUILT-NOT-INSTALLED; writes_performed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
