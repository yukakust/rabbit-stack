#!/usr/bin/env python3
"""Verify, build, hash, and inspect media without writing it."""

from __future__ import annotations

import json, re, shutil, subprocess, sys
from pathlib import Path
from rabbit_qca_beacon import ROOT, build_fetched

OUTPUT = Path("/tmp/rabbit-vm-loader-v01.img")
REPORT = Path("/tmp/rabbit-vm-loader-v01.json")


def show_external_disks() -> None:
    diskutil = shutil.which("diskutil")
    if diskutil is None:
        print("MEDIA: diskutil unavailable"); return
    listing = subprocess.run([diskutil, "list", "external", "physical"], check=False, capture_output=True, text=True)
    if listing.returncode:
        raise RuntimeError(f"diskutil list failed: {listing.stderr.strip()}")
    print("\nEXTERNAL PHYSICAL MEDIA (READ-ONLY DISCOVERY):")
    print(listing.stdout.rstrip() or "none")
    for device in re.findall(r"^(/dev/disk\d+) \(external, physical\):$", listing.stdout, re.MULTILINE):
        info = subprocess.run([diskutil, "info", device], check=False, capture_output=True, text=True)
        if info.returncode:
            raise RuntimeError(f"diskutil info failed for {device}: {info.stderr.strip()}")
        print(f"\nIDENTITY FOR {device}:\n{info.stdout.rstrip()}")


def main() -> int:
    try:
        if subprocess.run([sys.executable, str(ROOT / "verify.py")], check=False).returncode:
            raise RuntimeError("verification failed; no candidate was prepared")
        if not (ROOT / "evidence" / "qemu-macos-arm64-observed.json").is_file():
            raise RuntimeError("exact loader v0.1 QEMU mismatch gate is not recorded")
        image, report = build_fetched()
        OUTPUT.write_bytes(image)
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("\nPHYSICAL CANDIDATE PREPARED (NO DEVICE WRITE):")
        print(f"image:  {OUTPUT}\nreport: {REPORT}")
        print(f"EFI SHA256:   {report['efi_sha256']}\nIMAGE SHA256: {report['image_sha256']}")
        show_external_disks()
        print("\nSTOP: no device was unmounted, erased, or written.")
    except (OSError, RuntimeError) as error:
        print(f"FAIL: {error}"); return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
