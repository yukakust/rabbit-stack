#!/usr/bin/env python3
"""Fetch exact unmodified QCA payloads into a disposable cache."""

from __future__ import annotations

import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "firmware.json"
CACHE = Path(tempfile.gettempdir()) / "rabbit-qca-rome-00000302-797d34e6"


class FirmwareError(RuntimeError):
    pass


def load_manifest() -> dict:
    value = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise FirmwareError("firmware manifest is invalid")
    return value


def verify_file(path: Path, expected: dict) -> bytes:
    data = path.read_bytes()
    if len(data) != expected["size"]:
        raise FirmwareError(f"{expected['name']} size mismatch")
    if hashlib.sha256(data).hexdigest() != expected["sha256"]:
        raise FirmwareError(f"{expected['name']} SHA-256 mismatch")
    return data


def fetch_all() -> dict[str, bytes]:
    manifest = load_manifest()
    CACHE.mkdir(mode=0o700, parents=True, exist_ok=True)
    result: dict[str, bytes] = {}
    for expected in manifest["files"]:
        path = CACHE / expected["name"]
        try:
            result[expected["name"]] = verify_file(path, expected)
            continue
        except (OSError, FirmwareError):
            pass
        request = urllib.request.Request(expected["url"], headers={"User-Agent": "Rabbit-Stack-QCA-fetch/1"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read(expected["size"] + 1)
        except OSError as error:
            raise FirmwareError(f"could not fetch {expected['name']}: {error}") from error
        if len(data) != expected["size"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
            raise FirmwareError(f"downloaded {expected['name']} does not match pinned size and SHA-256")
        path.write_bytes(data)
        result[expected["name"]] = verify_file(path, expected)
    return result


if __name__ == "__main__":
    for name, data in fetch_all().items():
        print(f"VERIFIED: {name} size={len(data)} sha256={hashlib.sha256(data).hexdigest()}")
    print(f"CACHE: {CACHE}")
