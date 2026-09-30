#!/usr/bin/env python3
"""Launch the exact physical candidate in QEMU UEFI without touching hardware."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from rabbit_scene_uefi import TARGET_PATH, build, load_json


def roots(qemu: Path) -> list[Path]:
    prefix = qemu.resolve().parent.parent
    return [prefix / "share/qemu", Path("/opt/homebrew/share/qemu"), Path("/usr/local/share/qemu"), Path("/usr/share/qemu"), Path("/usr/share/OVMF")]


def main() -> int:
    executable = shutil.which("qemu-system-x86_64")
    if executable is None:
        print("FAIL: qemu-system-x86_64 is not on PATH")
        return 1
    qemu = Path(executable)
    code = next((root / name for root in roots(qemu) for name in ("edk2-x86_64-code.fd", "OVMF_CODE.fd", "OVMF_CODE_4M.fd") if (root / name).is_file()), None)
    variables = next((root / name for root in roots(qemu) for name in ("edk2-i386-vars.fd", "OVMF_VARS.fd", "OVMF_VARS_4M.fd") if (root / name).is_file()), None)
    if code is None or variables is None:
        print("FAIL: could not find QEMU x86-64 UEFI firmware")
        return 1
    image, report = build(load_json(TARGET_PATH))
    with tempfile.TemporaryDirectory(prefix="rabbit-scene-v2-qemu-") as directory:
        temporary = Path(directory)
        image_path = temporary / "rabbit-scene-v2.img"
        variables_path = temporary / "vars.fd"
        image_path.write_bytes(image)
        shutil.copyfile(variables, variables_path)
        print(f"IMAGE SHA256: {report['image_sha256']}")
        print("Expected: the exact pixel cat repeatedly chases and bats the bouncing blue ball. Press Esc to exit.")
        return subprocess.run([
            str(qemu), "-machine", "q35", "-m", "256M", "-nic", "none", "-no-reboot",
            "-drive", f"if=pflash,format=raw,unit=0,readonly=on,file={code}",
            "-drive", f"if=pflash,format=raw,unit=1,file={variables_path}",
            "-drive", f"file={image_path},format=raw,snapshot=on",
        ], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
