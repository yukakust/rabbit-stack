#!/usr/bin/env python3
import argparse, json
from pathlib import Path
from rabbit_qca_status import PROBE_PATH, TARGET_PATH, build, load_json

parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--report", type=Path, required=True)
args = parser.parse_args(); image, report = build(load_json(PROBE_PATH), load_json(TARGET_PATH))
args.output.write_bytes(image); args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(f"BUILT: {args.output} ({len(image)} bytes)"); print(f"EFI SHA256: {report['efi_sha256']}"); print(f"IMAGE SHA256: {report['image_sha256']}")
print("STATUS: BUILT-NOT-INSTALLED; vendor-IN reads=2; writes=0; radio operations=0")
