#!/usr/bin/env python3
import argparse, json
from pathlib import Path
from rabbit_qca_beacon import build_fetched

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--report", type=Path, required=True)
args = parser.parse_args()
image, report = build_fetched()
args.output.write_bytes(image)
args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"BUILT: {args.output} ({len(image)} bytes)")
print(f"EFI SHA256: {report['efi_sha256']}")
print(f"IMAGE SHA256: {report['image_sha256']}")
print("STATUS: BUILT-NOT-INSTALLED; passive BLUE/YELLOW command runtime; persistent writes=0")
