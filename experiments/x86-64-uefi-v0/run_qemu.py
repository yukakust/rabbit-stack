#!/usr/bin/env python3
"""Launch the generated USB image under QEMU's bundled x86-64 UEFI firmware."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from build_image import TARGET_PATH, WORLD_PATH, build, load_json


def firmware_roots(qemu: Path) -> list[Path]:
    resolved_prefix = qemu.resolve().parent.parent
    return [
        resolved_prefix / "share" / "qemu",
        Path("/opt/homebrew/share/qemu"),
        Path("/usr/local/share/qemu"),
        Path("/usr/share/qemu"),
        Path("/usr/share/OVMF"),
    ]


def code_candidates(qemu: Path) -> list[Path]:
    names = ["edk2-x86_64-code.fd", "OVMF_CODE.fd", "OVMF_CODE_4M.fd"]
    return [root / name for root in firmware_roots(qemu) for name in names]


def vars_candidates(qemu: Path) -> list[Path]:
    # QEMU's x86-64 EDK2 build intentionally shares the i386 variable-store template.
    names = ["edk2-i386-vars.fd", "OVMF_VARS.fd", "OVMF_VARS_4M.fd"]
    return [root / name for root in firmware_roots(qemu) for name in names]


def main() -> int:
    executable = shutil.which("qemu-system-x86_64")
    if executable is None:
        print("FAIL: qemu-system-x86_64 is not on PATH")
        return 1
    qemu = Path(executable)
    code = next((path for path in code_candidates(qemu) if path.is_file()), None)
    variables = next((path for path in vars_candidates(qemu) if path.is_file()), None)
    if code is None or variables is None:
        print("FAIL: could not find QEMU's x86-64 UEFI code and variable-store files")
        print("Checked:")
        for path in code_candidates(qemu) + vars_candidates(qemu):
            print(f"  {path}")
        return 1

    world, target = load_json(WORLD_PATH), load_json(TARGET_PATH)
    image, report = build(world, target)
    with tempfile.TemporaryDirectory(prefix="rabbit-uefi-qemu-") as temp_dir:
        image_path = Path(temp_dir) / "rabbit-x86-64-uefi-v0.img"
        variables_path = Path(temp_dir) / "edk2-vars.fd"
        image_path.write_bytes(image)
        # Firmware variables are mutable by design, so QEMU receives only a temporary
        # copy. The Homebrew template and physical firmware remain untouched.
        shutil.copyfile(variables, variables_path)
        command = [
            str(qemu),
            "-machine", "q35",
            "-m", "256M",
            "-nic", "none",
            "-no-reboot",
            "-drive", f"if=pflash,format=raw,unit=0,readonly=on,file={code}",
            "-drive", f"if=pflash,format=raw,unit=1,file={variables_path}",
            "-drive", f"file={image_path},format=raw,readonly=on",
        ]
        print(f"IMAGE SHA256: {report['image_sha256']}")
        print(f"UEFI code: {code} ({code.stat().st_size} bytes, read-only)")
        print(f"UEFI variables template: {variables} ({variables.stat().st_size} bytes)")
        print("UEFI variables working copy: temporary")
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
