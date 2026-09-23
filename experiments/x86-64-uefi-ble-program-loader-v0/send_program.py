#!/usr/bin/env python3
"""Compile a Rabbit VM scene and advertise its transfer frames from macOS."""

from __future__ import annotations

import argparse, hashlib, os, shutil, subprocess, tempfile
from pathlib import Path

from rabbit_vm_packet import decode_program, encode_program, encode_transfer, fnv1a32, frame_to_uuid

ROOT = Path(__file__).resolve().parent
SOURCE, PLIST = ROOT / "mac_vm_program.m", ROOT / "RabbitColorCommand-Info.plist"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("shape", choices=("square", "triangle"))
    parser.add_argument("--rgb", required=True, help="six RGB hexadecimal digits")
    parser.add_argument("--x", type=int, default=300); parser.add_argument("--y", type=int, default=300)
    parser.add_argument("--size", type=int, default=96); parser.add_argument("--step", type=int, default=16)
    parser.add_argument("--no-arrows", action="store_true")
    args = parser.parse_args()
    value = args.rgb.removeprefix("#")
    try:
        if len(value) != 6: raise ValueError
        red, green, blue = bytes.fromhex(value)
    except ValueError:
        parser.error("--rgb must contain exactly six hexadecimal digits")
    program = encode_program(shape=args.shape, red=red, green=green, blue=blue,
        x=args.x, y=args.y, size=args.size, step=args.step, arrows=not args.no_arrows)
    frames = encode_transfer(program); uuids = [frame_to_uuid(frame) for frame in frames]
    program_hash = fnv1a32(program); transfer_id = frames[0][3]
    print(f"PROGRAM={decode_program(program)}")
    print(f"BYTECODE={program.hex(' ').upper()}")
    print(f"PROGRAM_FNV1A32={program_hash:08X}")
    print(f"FRAMES={len(frames)}; each frame will repeat for 450 ms")
    for index, uuid in enumerate(uuids): print(f"FRAME[{index}]={uuid}")
    xcrun = shutil.which("xcrun")
    if xcrun is None: print("FAIL: xcrun is not installed or not on PATH"); return 1
    with tempfile.TemporaryDirectory(prefix="rabbit-vm-program-") as directory:
        executable = Path(directory) / "rabbit-vm-program"
        command = [xcrun, "--sdk", "macosx", "clang", "-fobjc-arc", str(SOURCE), "-o", str(executable),
            "-framework", "Foundation", "-framework", "CoreBluetooth", "-Xlinker", "-sectcreate",
            "-Xlinker", "__TEXT", "-Xlinker", "__info_plist", "-Xlinker", str(PLIST)]
        env = os.environ.copy()
        for name in ("CPATH", "C_INCLUDE_PATH", "CPLUS_INCLUDE_PATH", "SDKROOT"): env.pop(name, None)
        print(f"Source SHA256: {hashlib.sha256(SOURCE.read_bytes()).hexdigest()}")
        if subprocess.run(command, check=False, env=env).returncode: return 1
        try:
            return subprocess.run([str(executable), f"{transfer_id:02X}", f"{program_hash:08X}", *uuids], check=False).returncode
        except KeyboardInterrupt:
            return 0


if __name__ == "__main__": raise SystemExit(main())
