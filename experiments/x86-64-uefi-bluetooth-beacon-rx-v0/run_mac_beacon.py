#!/usr/bin/env python3
"""Build and run the exact reviewed Rabbit BLE advertiser on macOS."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "mac_beacon.swift"
PLIST = ROOT / "RabbitBeacon-Info.plist"
UUID = "52414242-4954-4C45-8000-000000000001"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    swiftc = shutil.which("swiftc")
    if swiftc is None:
        print("FAIL: swiftc is not installed or not on PATH")
        return 1
    with tempfile.TemporaryDirectory(prefix="rabbit-beacon-sender-") as temp_dir:
        executable = Path(temp_dir) / "rabbit-beacon"
        command = [
            swiftc,
            str(SOURCE),
            "-o", str(executable),
            "-framework", "CoreBluetooth",
            "-Xlinker", "-sectcreate",
            "-Xlinker", "__TEXT",
            "-Xlinker", "__info_plist",
            "-Xlinker", str(PLIST),
        ]
        print(f"Swift source SHA256: {sha256(SOURCE)}")
        print(f"Embedded plist SHA256: {sha256(PLIST)}")
        print(f"Rabbit UUID: {UUID}")
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            print(f"FAIL: swiftc exited with status {completed.returncode}")
            return 1
        print("Starting the reviewed beacon. Press Ctrl-C only after the Dell result appears.")
        try:
            return subprocess.run([str(executable)], check=False).returncode
        except KeyboardInterrupt:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
