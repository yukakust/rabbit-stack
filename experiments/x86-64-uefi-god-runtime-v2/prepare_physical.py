#!/usr/bin/env python3
"""Verify and build v2, then show removable media without writing it."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from build_image import build
from verify import main as verify


def main() -> int:
    if verify():
        return 1
    image, report = build()
    output = Path(tempfile.gettempdir()) / "rabbit-god-runtime-v2.img"
    output.write_bytes(image)
    print("\nPHYSICAL CANDIDATE PREPARED (NO DEVICE WRITE):")
    print(f"image: {output}")
    print(f"EFI SHA256:   {report['efi_sha256']}")
    print(f"IMAGE SHA256: {report['image_sha256']}")
    print("\nEXTERNAL PHYSICAL MEDIA (READ-ONLY DISCOVERY):")
    subprocess.run(["diskutil", "list", "external", "physical"], check=False)
    print("\nSTOP: no device was unmounted, erased, or written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
