#!/usr/bin/env python3
"""Exhaustively verify Pill v1's one-byte input contract."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROMPT = b"Choose [r]ed or [b]lue:\n"
RED = PROMPT + b"Wake up, Neo.\n"
BLUE = PROMPT + b"The story ends.\n"
INVALID = PROMPT + b"Invalid choice.\n"


class ProgramRunError(RuntimeError):
    """The program could not complete one test case safely."""


def expected_result(value: int) -> tuple[bytes, int]:
    if value in (ord("r"), ord("R")):
        return RED, 0
    if value == ord("b"):
        return BLUE, 0
    return INVALID, 2


def run_case(executable: Path, data: bytes) -> tuple[bytes, int, bytes]:
    try:
        completed = subprocess.run(
            [str(executable)],
            input=data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=2.0,
        )
    except subprocess.TimeoutExpired as error:
        raise ProgramRunError(f"program timed out for input {data!r}") from error
    except OSError as error:
        raise ProgramRunError(f"could not run {executable}: {error}") from error
    return completed.stdout, completed.returncode, completed.stderr


def main() -> int:
    executable = Path(sys.argv[1] if len(sys.argv) > 1 else "./pill").resolve()
    if not executable.is_file():
        print(f"ERROR: executable not found: {executable}", file=sys.stderr)
        return 2

    failures: list[str] = []

    try:
        for value in range(256):
            expected_stdout, expected_status = expected_result(value)
            stdout, status, stderr = run_case(executable, bytes([value]))

            if stdout != expected_stdout or status != expected_status or stderr:
                failures.append(
                    f"byte {value:3d} (0x{value:02x}): "
                    f"status={status}, stdout={stdout!r}, stderr={stderr!r}; "
                    f"expected status={expected_status}, stdout={expected_stdout!r}"
                )

        eof_stdout, eof_status, eof_stderr = run_case(executable, b"")
    except ProgramRunError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if eof_stdout != INVALID or eof_status != 2 or eof_stderr:
        failures.append(
            "EOF: "
            f"status={eof_status}, stdout={eof_stdout!r}, stderr={eof_stderr!r}; "
            f"expected status=2, stdout={INVALID!r}"
        )

    if failures:
        print(f"FAIL: {len(failures)} of 257 cases failed")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("PASS: all 256 one-byte inputs match the contract")
    print("PASS: EOF matches the contract")
    print("  red ending:     2 inputs (r, R), status 0")
    print("  blue ending:    1 input  (b),    status 0")
    print("  invalid ending: 253 inputs,      status 2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
