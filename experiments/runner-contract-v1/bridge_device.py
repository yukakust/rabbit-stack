#!/usr/bin/env python3
"""Deterministic simulated device for the Rabbit framed bridge contract."""

from __future__ import annotations

import hashlib
import json
import struct
import sys


def canonical(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def main() -> int:
    raw = sys.stdin.buffer.read()
    if len(raw) < 4:
        return fail("missing frame header")
    size = struct.unpack(">I", raw[:4])[0]
    body = raw[4:]
    if size != len(body) or size > 4096:
        return fail("invalid frame length")
    try:
        request = json.loads(body.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return fail("invalid frame JSON")
    expected = {
        "protocol", "plan_sha256", "artifact_sha256", "output_hex", "exit_status"
    }
    if not isinstance(request, dict) or set(request) != expected:
        return fail("invalid request fields")
    if request["protocol"] != "rabbit-frame/1" or request["exit_status"] != 0:
        return fail("unsupported request contract")
    try:
        output = bytes.fromhex(request["output_hex"])
        output.decode("ascii")
    except (ValueError, UnicodeDecodeError):
        return fail("output must be ASCII hex")
    if hashlib.sha256(output).hexdigest() != request["artifact_sha256"]:
        return fail("artifact hash mismatch")
    response = {
        "protocol": "rabbit-frame/1",
        "request_sha256": hashlib.sha256(body).hexdigest(),
        "output_hex": output.hex(),
        "exit_status": 0,
    }
    encoded = canonical(response)
    sys.stdout.buffer.write(struct.pack(">I", len(encoded)) + encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
