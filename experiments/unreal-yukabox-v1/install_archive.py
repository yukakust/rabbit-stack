#!/usr/bin/env python3
"""Validate and extract an owner-authorized official UE Linux archive on Yukabox."""
import argparse
import hashlib
import json
import platform
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


def install(archive, root):
    if platform.system() != "Linux":
        raise SystemExit("Install only on Yukabox/Linux")
    engine = root / "engine"
    if any(engine.iterdir()):
        raise SystemExit("Engine directory must be empty; preserve any existing installation")
    digest = hashlib.sha256()
    with archive.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024**2), b""):
            digest.update(block)
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            p = PurePosixPath(name)
            if p.is_absolute() or ".." in p.parts or "\\" in name:
                raise SystemExit("Unsafe archive path")
        build = json.loads(z.read("Engine/Build/Build.version"))
        version = tuple(build[k] for k in ("MajorVersion", "MinorVersion", "PatchVersion"))
        if version != (5, 8, 3):
            raise SystemExit(f"Unexpected engine version {version}; do not silently substitute")
        extracted_bytes = sum(i.file_size for i in z.infolist())
        file_count = len(z.infolist())
    # unzip preserves executable modes and verifies CRC as each member is extracted.
    subprocess.run(["unzip", "-q", str(archive), "-d", str(engine)], check=True)
    report = {
        "schema_version": 1, "installed_at": datetime.now(timezone.utc).isoformat(),
        "source": "https://www.unrealengine.com/linux", "artifact": archive.name,
        "archive_bytes": archive.stat().st_size, "archive_sha256": digest.hexdigest(),
        "build_version": build, "extracted_bytes": extracted_bytes, "file_count": file_count,
        "editor_present": (engine / "Engine/Binaries/Linux/UnrealEditor").is_file(),
        "note": "Local artifact hash is recorded, not a vendor-published checksum. "
                "Installation does not prove runtime/GPU rendering.",
    }
    (root / "logs/installation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)
    a = p.parse_args()
    install(a.archive.resolve(), a.root.resolve())
