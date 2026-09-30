#!/usr/bin/env python3
"""Compile, sign, transmit, and await a Universal Package v2 receipt."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from compile_world import compile_world
from transport import as_uuid, encode_transfer, fnv1a32

ROOT = Path(__file__).resolve().parent
LEGACY = ROOT.parent / "x86-64-uefi-ble-program-loader-v0"


def sender_source() -> str:
    source = (LEGACY / "mac_vm_program.m").read_text(encoding="utf-8")
    return (source.replace("could not advertise Rabbit VM frame", "could not advertise Rabbit Universal Package frame")
            .replace("usage: rabbit-vm-program TRANSFER HASH UUID...", "usage: rabbit-universal-package TRANSFER HASH UUID...")
            .replace("RABBIT VM PROGRAM TRANSFER STARTED", "RABBIT UNIVERSAL PACKAGE TRANSFER STARTED"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("world", nargs="?", type=Path, default=ROOT / "worlds" / "cat-chases-mouse.json")
    parser.add_argument("--counter", type=int, required=True)
    args = parser.parse_args()
    try:
        private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        package = compile_world(args.world, args.counter, private)
        frames = encode_transfer(package)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL: could not build package: {error}")
        return 1
    uuids = [as_uuid(item) for item in frames]
    digest = fnv1a32(package)
    transfer = frames[0][3]
    print(f"WORLD={args.world}")
    print(f"PACKAGE_BYTES={len(package)}; SHA256={hashlib.sha256(package).hexdigest()}")
    print(f"PACKAGE_FNV1A32={digest:08X}; TRANSFER={transfer:02X}; COUNTER={args.counter}")
    print(f"FRAMES={len(frames)}; transport=v2; exact ACK required")
    xcrun = shutil.which("xcrun")
    if xcrun is None:
        print("FAIL: xcrun is not installed or not on PATH")
        return 1
    with tempfile.TemporaryDirectory(prefix="rabbit-universal-package-") as temporary:
        directory = Path(temporary)
        source = directory / "mac_package_sender.m"
        executable = directory / "rabbit-universal-package"
        source.write_text(sender_source(), encoding="utf-8")
        environment = os.environ.copy()
        for name in ("CPATH", "C_INCLUDE_PATH", "CPLUS_INCLUDE_PATH", "SDKROOT"):
            environment.pop(name, None)
        command = [xcrun, "--sdk", "macosx", "clang", "-fobjc-arc", str(source), "-o", str(executable),
                   "-framework", "Foundation", "-framework", "CoreBluetooth", "-Xlinker", "-sectcreate",
                   "-Xlinker", "__TEXT", "-Xlinker", "__info_plist", "-Xlinker", str(LEGACY / "RabbitColorCommand-Info.plist")]
        print(f"SENDER_SOURCE_SHA256={hashlib.sha256(source.read_bytes()).hexdigest()}")
        if subprocess.run(command, check=False, env=environment).returncode:
            return 1
        try:
            return subprocess.run([str(executable), f"{transfer:02X}", f"{digest:08X}", *uuids], check=False).returncode
        except KeyboardInterrupt:
            return 130


if __name__ == "__main__":
    raise SystemExit(main())
