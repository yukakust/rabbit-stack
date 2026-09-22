#!/usr/bin/env python3
"""Launch the generated USB image under QEMU's bundled x86-64 UEFI firmware."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from build_image import TARGET_PATH, WORLD_PATH, build, load_json


def firmware_candidates(qemu: Path) -> list[Path]:
    resolved_prefix = qemu.resolve().parent.parent
    roots = [
        resolved_prefix / "share" / "qemu",
        Path("/opt/homebrew/share/qemu"),
        Path("/usr/local/share/qemu"),
        Path("/usr/share/qemu"),
        Path("/usr/share/OVMF"),
    ]
    names = ["edk2-x86_64-code.fd", "OVMF_CODE.fd", "OVMF_CODE_4M.fd"]
    return [root / name for root in roots for name in names]


def main() -> int:
    executable = shutil.which("qemu-system-x86_64")
    if executable is None:
        print("FAIL: qemu-system-x86_64 is not on PATH")
        return 1
    qemu = Path(executable)
    firmware = next((path for path in firmware_candidates(qemu) if path.is_file()), None)
    if firmware is None:
        print("FAIL: could not find QEMU's x86-64 UEFI firmware")
        print("Checked:")
        for path in firmware_candidates(qemu):
            print(f"  {path}")
        return 1

    world, target = load_json(WORLD_PATH), load_json(TARGET_PATH)
    image, report = build(world, target)
    with tempfile.TemporaryDirectory(prefix="rabbit-uefi-qemu-") as temp_dir:
        image_path = Path(temp_dir) / "rabbit-x86-64-uefi-v0.img"
        image_path.write_bytes(image)
        command = [
            str(qemu),
            "-machine", "q35",
            "-m", "256M",
            "-nic", "none",
            "-no-reboot",
            "-snapshot",
            "-bios", str(firmware),
            "-drive", f"file={image_path},format=raw,readonly=on",
        ]
        print(f"IMAGE SHA256: {report['image_sha256']}")
        print(f"UEFI firmware: {firmware}")
        print("Expected screen: exactly HI; press one key to return to firmware.")
        print("Close the QEMU window after observing the result. No physical device is used.")
        try:
            completed = subprocess.run(command, check=False)
        except KeyboardInterrupt:
            print("QEMU stopped by user")
            return 0
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
