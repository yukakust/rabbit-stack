#!/usr/bin/env python3
"""Verify the complete contract of the first direct RV32I image."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HEX_PATH = ROOT / "hello.hex"
EXPECTED = bytes.fromhex(
    "b7 02 00 10 "
    "13 03 10 04 "
    "23 80 62 00 "
    "b7 02 10 00 "
    "37 53 00 00 "
    "13 03 53 55 "
    "23 a0 62 00 "
    "6f 00 00 00"
)


def main() -> int:
    try:
        image = bytes.fromhex(HEX_PATH.read_text(encoding="ascii"))
    except (OSError, ValueError) as error:
        print(f"FAIL: could not decode {HEX_PATH.name}: {error}")
        return 1

    if image != EXPECTED:
        print("FAIL: decoded image does not match the reviewed instruction bytes")
        return 1

    print(f"PASS: image is exactly {len(image)} bytes")

    with tempfile.TemporaryDirectory(prefix="rabbit-rv32i-") as temp_dir:
        image_path = Path(temp_dir) / "hello.bin"
        image_path.write_bytes(image)

        command = [
            "qemu-system-riscv32",
            "-machine",
            "virt",
            "-nographic",
            "-bios",
            "none",
            "-device",
            f"loader,file={image_path},addr=0x80000000,cpu-num=0",
        ]

        try:
            completed = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=3,
            )
        except FileNotFoundError:
            print("FAIL: qemu-system-riscv32 is not installed or not on PATH")
            return 1
        except subprocess.TimeoutExpired:
            print("FAIL: QEMU did not exit within three seconds")
            return 1

    if completed.returncode != 0:
        print(f"FAIL: QEMU exit status was {completed.returncode}")
        if completed.stderr:
            print(completed.stderr.decode(errors="replace"))
        return 1

    if completed.stdout != b"A":
        print(f"FAIL: expected stdout b'A', got {completed.stdout!r}")
        return 1

    if completed.stderr:
        print(f"FAIL: expected empty stderr, got {completed.stderr!r}")
        return 1

    print("PASS: QEMU wrote exactly b'A' and exited with status 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
