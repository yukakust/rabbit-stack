#!/usr/bin/env python3
"""Run the combined artifact through its fail-closed QEMU mismatch gate."""

from __future__ import annotations

import shutil, subprocess, sys, tempfile
from pathlib import Path
from rabbit_qca_beacon import build_fetched


def find(qemu: Path, names: list[str]) -> Path | None:
    roots = [qemu.resolve().parent.parent / "share/qemu", Path("/opt/homebrew/share/qemu"), Path("/usr/local/share/qemu"), Path("/usr/share/qemu"), Path("/usr/share/OVMF")]
    return next((root / name for root in roots for name in names if (root / name).is_file()), None)


def main() -> int:
    root = Path(__file__).resolve().parent
    if subprocess.run([sys.executable, str(root / "verify.py")], check=False).returncode:
        print("FAIL: verification failed; QEMU was not started"); return 1
    if subprocess.run([sys.executable, str(root / "verify_mac_sender.py")], check=False).returncode:
        print("FAIL: Mac sender compile gate failed; QEMU was not started"); return 1
    executable = shutil.which("qemu-system-x86_64")
    if executable is None:
        print("FAIL: qemu-system-x86_64 is not on PATH"); return 1
    qemu = Path(executable)
    code = find(qemu, ["edk2-x86_64-code.fd", "OVMF_CODE.fd", "OVMF_CODE_4M.fd"])
    variables = find(qemu, ["edk2-i386-vars.fd", "OVMF_VARS.fd", "OVMF_VARS_4M.fd"])
    if code is None or variables is None:
        print("FAIL: could not find QEMU x86-64 UEFI firmware"); return 1
    image, report = build_fetched()
    with tempfile.TemporaryDirectory(prefix="rabbit-combined-qemu-") as directory:
        temp = Path(directory); disk = temp / "rabbit.img"; vars_copy = temp / "vars.fd"
        disk.write_bytes(image); shutil.copyfile(variables, vars_copy)
        command = [str(qemu), "-machine", "q35", "-m", "256M", "-no-reboot",
            "-drive", f"if=pflash,format=raw,unit=0,readonly=on,file={code}",
            "-drive", f"if=pflash,format=raw,unit=1,file={vars_copy}",
            "-drive", f"file={disk},format=raw,snapshot=on",
            "-device", "qemu-xhci,id=rabbit-xhci", "-device", "usb-kbd,bus=rabbit-xhci.0"]
        print(f"IMAGE SHA256: {report['image_sha256']}")
        print("Expected: TARGET NOT FOUND; NO DEVICE WRITE SENT")
        print("The program loader must remain unreachable because QEMU has no exact 0CF3:E009 controller.")
        try:
            return subprocess.run(command, check=False).returncode
        except KeyboardInterrupt:
            print("QEMU stopped by user"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
