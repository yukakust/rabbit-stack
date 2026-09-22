#!/usr/bin/env python3
"""Run the jump-and-stone world under QEMU UEFI."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from rabbit_jump_stone import TARGET_PATH, WORLD_PATH, build, load_json


def roots(qemu: Path) -> list[Path]:
    prefix = qemu.resolve().parent.parent
    return [prefix / "share/qemu", Path("/opt/homebrew/share/qemu"), Path("/usr/local/share/qemu"), Path("/usr/share/qemu"), Path("/usr/share/OVMF")]


def find(qemu: Path, names: list[str]) -> Path | None:
    return next((root / name for root in roots(qemu) for name in names if (root / name).is_file()), None)


def main() -> int:
    executable = shutil.which("qemu-system-x86_64")
    if executable is None:
        print("FAIL: qemu-system-x86_64 is not on PATH")
        return 1
    qemu = Path(executable)
    code = find(qemu, ["edk2-x86_64-code.fd", "OVMF_CODE.fd", "OVMF_CODE_4M.fd"])
    variables = find(qemu, ["edk2-i386-vars.fd", "OVMF_VARS.fd", "OVMF_VARS_4M.fd"])
    if code is None or variables is None:
        print("FAIL: could not find QEMU x86-64 UEFI firmware")
        return 1
    image, report = build(load_json(WORLD_PATH), load_json(TARGET_PATH))
    with tempfile.TemporaryDirectory(prefix="rabbit-jump-stone-qemu-") as temp_dir:
        temp = Path(temp_dir)
        image_path = temp / "rabbit-jump-stone.img"
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
        print("Expected: yellow 64x64 player on black; arrows move; Space jumps; Z leaves one solid 16x16 stone behind.")
        print("A later Z relocates that single stone. Escape exits. No physical device is used.")
        try:
            completed = subprocess.run(command, check=False)
        except KeyboardInterrupt:
            print("QEMU stopped by user")
            return 0
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
