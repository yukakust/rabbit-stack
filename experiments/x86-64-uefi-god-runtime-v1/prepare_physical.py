#!/usr/bin/env python3
"""Verify and prepare the God Runtime image without writing a device."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from build_image import ROOT, build

OUTPUT = Path("/tmp/rabbit-god-runtime-v1.img")


def main() -> int:
    checked = subprocess.run([sys.executable, str(ROOT / "verify.py")], check=False)
    if checked.returncode:
        return checked.returncode
    image, report = build()
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
