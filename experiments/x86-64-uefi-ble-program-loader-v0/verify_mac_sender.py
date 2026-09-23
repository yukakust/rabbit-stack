#!/usr/bin/env python3
"""Compile, but do not run, the exact macOS program sender/ACK receiver."""

from __future__ import annotations

import os, shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "mac_vm_program.m"
PLIST = ROOT / "RabbitColorCommand-Info.plist"


def main() -> int:
    xcrun = shutil.which("xcrun")
    if xcrun is None:
        print("SKIP: xcrun unavailable; exact Mac sender compile gate requires macOS")
        return 0
    with tempfile.TemporaryDirectory(prefix="rabbit-vm-sender-check-") as directory:
        output = Path(directory) / "rabbit-vm-program"
        command = [xcrun, "--sdk", "macosx", "clang", "-fobjc-arc", str(SOURCE),
            "-o", str(output), "-framework", "Foundation", "-framework", "CoreBluetooth",
            "-Xlinker", "-sectcreate", "-Xlinker", "__TEXT", "-Xlinker", "__info_plist",
            "-Xlinker", str(PLIST)]
        env = os.environ.copy()
        for name in ("CPATH", "C_INCLUDE_PATH", "CPLUS_INCLUDE_PATH", "SDKROOT"):
            env.pop(name, None)
        completed = subprocess.run(command, check=False, env=env)
        if completed.returncode:
            print("FAIL: exact Mac sender/ACK receiver did not compile")
            return 1
    print("PASS: exact Mac sender/ACK receiver compiles without starting Bluetooth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
