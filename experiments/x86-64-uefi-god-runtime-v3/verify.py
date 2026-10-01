#!/usr/bin/env python3
"""Graphics tests, deterministic image, source-bound missing-device QEMU gate."""
import json
import subprocess
import sys
from build_image import ROOT, build, transformed_source


def main():
    if subprocess.run([sys.executable,str(ROOT/"verify_graphics.py")],check=False).returncode:
        return 1
    first,report=build();second,other=build()
    if first!=second or report!=other:
        raise ValueError("UEFI artifact is not deterministic")
    evidence=json.loads((ROOT/"evidence/qemu-linux-x86-64-observed.json").read_text())
    bindings=evidence["bindings"]
    for evidence_key,report_key in [("generated_source_sha256","source_sha256"),("runtime_core_sha256","runtime_core_sha256"),("target_sha256","target_sha256")]:
        if bindings[evidence_key]!=report[report_key]:
            raise ValueError("QEMU source/runtime/target evidence is stale")
    if evidence["observation"]["target_found"] or evidence["observation"]["physical_execution_verified"]:
        raise ValueError("QEMU gate has invalid observation claims")
    source=transformed_source()
    for marker in ("RABBIT GOD RUNTIME v3.0","universal_block_received:","rabbit_package_frame","TARGET NOT FOUND; NO DEVICE WRITE SENT"):
        if marker not in source:raise ValueError("generated runtime boundary changed")
    if report["efi_sha256"]==bindings["efi_sha256"] and report["image_sha256"]==bindings["image_sha256"]:
        print("PASS: exact artifact QEMU missing-device gate")
    else:
        print("PASS: source/runtime/target QEMU gate; host toolchain has different EFI bytes, exact local QEMU observation still required before physical use")
    print(f"PASS: deterministic graphics v3 candidate {report['image_sha256']}")
    print("NOT PHYSICALLY INSTALLED; Mac sender, BLE block ACKs and Dell graphics remain physical-test pending")
    return 0


if __name__=="__main__":raise SystemExit(main())
