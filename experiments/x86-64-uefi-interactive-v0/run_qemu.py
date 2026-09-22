#!/usr/bin/env python3
"""Launch the interactive Rabbit world under QEMU UEFI."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from rabbit_interactive import TARGET_PATH, WORLD_PATH, build, load_json


def firmware_roots(qemu: Path) -> list[Path]:
    prefix = qemu.resolve().parent.parent
    return [
        prefix / "share" / "qemu",
        Path("/opt/homebrew/share/qemu"),
        Path("/usr/local/share/qemu"),
        Path("/usr/share/qemu"),
        Path("/usr/share/OVMF"),
    ]


def candidates(qemu: Path, names: list[str]) -> list[Path]:
    return [root / name for root in firmware_roots(qemu) for name in names]


def main() -> int:
    executable = shutil.which("qemu-system-x86_64")
    if executable is None:
        print("FAIL: qemu-system-x86_64 is not on PATH")
        return 1
    qemu = Path(executable)
    code = next((p for p in candidates(qemu, ["edk2-x86_64-code.fd", "OVMF_CODE.fd", "OVMF_CODE_4M.fd"]) if p.is_file()), None)
    variables = next((p for p in candidates(qemu, ["edk2-i386-vars.fd", "OVMF_VARS.fd", "OVMF_VARS_4M.fd"]) if p.is_file()), None)
    if code is None or variables is None:
        print("FAIL: could not find QEMU x86-64 UEFI firmware")
        return 1
    image, report = build(load_json(WORLD_PATH), load_json(TARGET_PATH))
    with tempfile.TemporaryDirectory(prefix="rabbit-interactive-qemu-") as temp_dir:
        temp = Path(temp_dir)
        image_path = temp / "rabbit-interactive.img"
        variables_path = temp / "edk2-vars.fd"
        image_path.write_bytes(image)
        shutil.copyfile(variables, variables_path)
        command = [
            str(qemu), "-machine", "q35", "-m", "256M", "-nic", "none", "-no-reboot",
            "-drive", f"if=pflash,format=raw,unit=0,readonly=on,file={code}",
            "-drive", f"if=pflash,format=raw,unit=1,file={variables_path}",
            "-drive", f"file={image_path},format=raw,snapshot=on",
        ]
        print(f"IMAGE SHA256: {report['image_sha256']}")
        print("Expected: black screen with one orange 128x128 square at (100,100).")
        print("Arrow keys move it by 16 pixels; movement is clamped to the screen; Escape exits.")
        print("No physical device is used.")
        try:
            completed = subprocess.run(command, check=False)
        except KeyboardInterrupt:
            print("QEMU stopped by user")
            return 0
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
