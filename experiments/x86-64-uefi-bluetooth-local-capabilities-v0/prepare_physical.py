#!/usr/bin/env python3
"""Verify, build, hash, and identify media without writing a device."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from rabbit_hci_capabilities import PROBE_PATH, ROOT, TARGET_PATH, build, load_json


OUTPUT = Path("/tmp/rabbit-bluetooth-local-capabilities-v01.img")
REPORT = Path("/tmp/rabbit-bluetooth-local-capabilities-v01.json")


def run_verifier() -> None:
    completed = subprocess.run([sys.executable, str(ROOT / "verify.py")], check=False)
    if completed.returncode != 0:
        raise RuntimeError("verification failed; no physical candidate was prepared")
    evidence = ROOT / "evidence" / "qemu-macos-arm64-observed.json"
    if not evidence.is_file():
        raise RuntimeError("QEMU gate is not recorded yet; physical preparation remains closed")


def show_external_disks() -> None:
    diskutil = shutil.which("diskutil")
    if diskutil is None:
        print("MEDIA: diskutil is unavailable; identify removable media separately on macOS")
        return
    listing = subprocess.run([diskutil, "list", "external", "physical"], check=False, capture_output=True, text=True)
    if listing.returncode != 0:
        raise RuntimeError(f"diskutil list failed: {listing.stderr.strip()}")
    print("\nEXTERNAL PHYSICAL MEDIA (READ-ONLY DISCOVERY):")
    print(listing.stdout.rstrip() or "none")
    devices = re.findall(r"^(/dev/disk\d+) \(external, physical\):$", listing.stdout, re.MULTILINE)
    for device in devices:
        info = subprocess.run([diskutil, "info", device], check=False, capture_output=True, text=True)
        if info.returncode != 0:
            raise RuntimeError(f"diskutil info failed for {device}: {info.stderr.strip()}")
        print(f"\nIDENTITY FOR {device}:")
        print(info.stdout.rstrip())


def main() -> int:
    try:
        run_verifier()
        image, report = build(load_json(PROBE_PATH), load_json(TARGET_PATH))
        OUTPUT.write_bytes(image)
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("\nPHYSICAL CANDIDATE PREPARED (NO DEVICE WRITE):")
        print(f"image:  {OUTPUT}")
        print(f"report: {REPORT}")
        print(f"EFI SHA256:   {report['efi_sha256']}")
        print(f"IMAGE SHA256: {report['image_sha256']}")
        show_external_disks()
        print("\nSTOP: no device was unmounted, erased, or written.")
        print("This image adds three local USB HCI queries; exact-device review and explicit authorization remain required.")
    except (OSError, RuntimeError) as error:
        print(f"FAIL: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
