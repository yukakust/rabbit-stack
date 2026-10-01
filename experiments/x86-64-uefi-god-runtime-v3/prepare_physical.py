#!/usr/bin/env python3
"""Read-only preparation; never unmounts or writes a physical device."""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from build_image import build
from verify import main as verify


def main():
    if verify():return 1
    image,report=build();root=Path(tempfile.gettempdir())
    path=root/"rabbit-god-runtime-v3.img";path.write_bytes(image)
    path.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
    print(f"PHYSICAL CANDIDATE PREPARED (NO DEVICE WRITE):\nimage: {path}\nEFI SHA256: {report['efi_sha256']}\nIMAGE SHA256: {report['image_sha256']}")
    if shutil.which("diskutil"):
        subprocess.run(["diskutil","list","external","physical"],check=False)
    print("STOP: no device unmounted, erased or written. Exact Mac QEMU observation and fresh device identity remain required before physical installation.")
    return 0


if __name__=="__main__":raise SystemExit(main())
