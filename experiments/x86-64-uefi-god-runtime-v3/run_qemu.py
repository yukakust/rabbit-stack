#!/usr/bin/env python3
"""Run Universal Package Runtime v3 through its zero-effect QEMU gate."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from build_image import build


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
    image, report = build()
    with tempfile.TemporaryDirectory(prefix="rabbit-v3-qemu-") as directory:
        temporary = Path(directory); disk=temporary/"rabbit.img"; vars_copy=temporary/"vars.fd"
        disk.write_bytes(image); shutil.copyfile(variables, vars_copy)
        print(f"IMAGE SHA256: {report['image_sha256']}")
        print("Expected: RABBIT GOD RUNTIME v3.0, then TARGET NOT FOUND; NO DEVICE WRITE SENT.")
        print("QEMU lacks the exact Dell controller, so RAM staging, graphics, crypto, and radio stay unreachable.")
        try:
            return subprocess.run([str(qemu), "-machine", "q35", "-m", "256M", "-nic", "none", "-no-reboot",
                "-drive", f"if=pflash,format=raw,unit=0,readonly=on,file={code}",
                "-drive", f"if=pflash,format=raw,unit=1,file={vars_copy}",
                "-drive", f"file={disk},format=raw,snapshot=on", "-device", "qemu-xhci,id=rabbit-xhci",
                "-device", "usb-kbd,bus=rabbit-xhci.0"], check=False).returncode
        except KeyboardInterrupt:
            print("QEMU stopped by user"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
