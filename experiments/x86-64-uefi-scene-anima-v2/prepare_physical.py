#!/usr/bin/env python3
"""Verify and prepare the Dell image while performing no device write."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rabbit_scene_uefi import ROOT, TARGET_PATH, build, load_json


OUTPUT = Path("/tmp/rabbit-scene-anima-v2-dell.img")


def main() -> int:
    verified = subprocess.run([sys.executable, str(ROOT / "verify.py")], check=False)
    if verified.returncode != 0:
        return verified.returncode
    image, report = build(load_json(TARGET_PATH))
    OUTPUT.write_bytes(image)
    print("\nPHYSICAL CANDIDATE PREPARED (NO DEVICE WRITE):")
    print(f"image: {OUTPUT}")
    print(f"EFI SHA256:   {report['efi_sha256']}")
    print(f"IMAGE SHA256: {report['image_sha256']}")
    if sys.platform == "darwin":
        print("\nEXTERNAL PHYSICAL MEDIA (READ-ONLY DISCOVERY):")
        subprocess.run(["diskutil", "list", "external", "physical"], check=False)
    print("\nSTOP: no device was unmounted, erased, or written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
