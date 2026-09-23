#!/usr/bin/env python3
"""Build and advertise one exact BLUE or YELLOW Rabbit command on macOS."""

from __future__ import annotations

import argparse, hashlib, os, shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "mac_color_command.m"
PLIST = ROOT / "RabbitColorCommand-Info.plist"
UUIDS = {
    "blue": "52414242-4954-4C45-8000-000000000002",
    "yellow": "52414242-4954-4C45-8000-000000000003",
}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=sorted(UUIDS))
    args = parser.parse_args()
    xcrun = shutil.which("xcrun")
    if xcrun is None:
        print("FAIL: xcrun is not installed or not on PATH"); return 1
    with tempfile.TemporaryDirectory(prefix="rabbit-color-command-") as temp_dir:
        executable = Path(temp_dir) / "rabbit-color-command"
        compile_command = [xcrun, "--sdk", "macosx", "clang", "-fobjc-arc",
            str(SOURCE), "-o", str(executable), "-framework", "Foundation",
            "-framework", "CoreBluetooth", "-Xlinker", "-sectcreate",
            "-Xlinker", "__TEXT", "-Xlinker", "__info_plist", "-Xlinker", str(PLIST)]
        print(f"Source SHA256: {sha256(SOURCE)}")
        print(f"COMMAND={args.command.upper()} UUID={UUIDS[args.command]}")
        env = os.environ.copy()
        for name in ("CPATH", "C_INCLUDE_PATH", "CPLUS_INCLUDE_PATH", "SDKROOT"):
            env.pop(name, None)
        completed = subprocess.run(compile_command, check=False, env=env)
        if completed.returncode:
            print(f"FAIL: Apple clang exited with status {completed.returncode}"); return 1
        print("Advertising. Wait for Dell to change color, then press Ctrl-C.")
        try:
            return subprocess.run([str(executable), args.command], check=False).returncode
        except KeyboardInterrupt:
            return 0

if __name__ == "__main__":
    raise SystemExit(main())
