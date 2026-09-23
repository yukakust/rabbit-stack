#!/usr/bin/env python3
"""Encode and advertise one bounded Rabbit VM program from macOS."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from rabbit_vm_packet import decode, encode_set_square_color, packet_to_uuid

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "mac_vm_program.m"
PLIST = ROOT / "RabbitColorCommand-Info.plist"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("set-square-color",))
    parser.add_argument("--rgb", required=True, help="six hexadecimal RGB digits, for example FF0066")
    args = parser.parse_args()
    value = args.rgb.removeprefix("#")
    if len(value) != 6:
        parser.error("--rgb must contain exactly six hexadecimal digits")
    try:
        red, green, blue = bytes.fromhex(value)
    except ValueError:
        parser.error("--rgb must contain exactly six hexadecimal digits")
    packet = encode_set_square_color(red, green, blue)
    uuid = packet_to_uuid(packet)
    decoded = decode(packet)
    print(f"PROGRAM={decoded['opcode']} RGB=#{value.upper()}")
    print(f"BYTECODE={packet.hex(' ').upper()}")
    print(f"CHECKSUM={decoded['checksum']} UUID={uuid}")

    xcrun = shutil.which("xcrun")
    if xcrun is None:
        print("FAIL: xcrun is not installed or not on PATH")
        return 1
    with tempfile.TemporaryDirectory(prefix="rabbit-vm-program-") as temp_dir:
        executable = Path(temp_dir) / "rabbit-vm-program"
        command = [xcrun, "--sdk", "macosx", "clang", "-fobjc-arc", str(SOURCE),
            "-o", str(executable), "-framework", "Foundation", "-framework", "CoreBluetooth",
            "-Xlinker", "-sectcreate", "-Xlinker", "__TEXT", "-Xlinker", "__info_plist",
            "-Xlinker", str(PLIST)]
        env = os.environ.copy()
        for name in ("CPATH", "C_INCLUDE_PATH", "CPLUS_INCLUDE_PATH", "SDKROOT"):
            env.pop(name, None)
        print(f"Source SHA256: {hashlib.sha256(SOURCE.read_bytes()).hexdigest()}")
        completed = subprocess.run(command, check=False, env=env)
        if completed.returncode:
            print(f"FAIL: Apple clang exited with status {completed.returncode}")
            return 1
        try:
            return subprocess.run([str(executable), uuid], check=False).returncode
        except KeyboardInterrupt:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())

