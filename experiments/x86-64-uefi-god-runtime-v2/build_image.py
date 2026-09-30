#!/usr/bin/env python3
"""Build the final-flash candidate: Rabbit Universal Package Runtime v2."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
V1 = REPO / "experiments" / "x86-64-uefi-god-runtime-v1"
MEDIA_PATH = REPO / "experiments" / "x86-64-uefi-v0" / "build_image.py"


class BuildError(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BuildError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transformed_source() -> str:
    v1 = load_module("rabbit_god_v1_builder", V1 / "build_image.py")
    source = v1.transformed_source()
    source = source.replace("cmp r9d, 1                         # transport version 1", "cmp r9d, 2                         # transport version 2")
    start = source.index("scan_frame_begin:")
    end = source.index("    # Build the canonical 16-byte acknowledgement:", start)
    parser = r'''scan_frame_begin:
scan_frame_chunk:
scan_frame_commit:
    lea rcx, [rsp + 0x430]
    mov rdx, [rsp + 0x6f0]
    call rabbit_package_frame
    cmp eax, 1
    je universal_package_accepted
    cmp eax, 2
    je scan_capsule_rolled_back
    cmp eax, 3
    je scan_capsule_rejected
    jmp scan_scan_event_loop

universal_package_accepted:
    mov al, byte ptr [rsp + 0x433]
    mov byte ptr [rsp + 0x441], al
    call rabbit_package_last_hash
    mov dword ptr [rsp + 0x44c], eax
    inc r15d
    lea rdx, [rip + scan_program_applied]
    call scan_print_ascii
    jmp scan_capsule_accepted

scan_capsule_rolled_back:
    lea rdx, [rip + scan_rollback]
    call scan_print_ascii
    jmp scan_scan_event_loop
scan_capsule_rejected:
    lea rdx, [rip + scan_capsule_bad]
    call scan_print_ascii
    jmp scan_scan_event_loop
scan_capsule_accepted:
'''
    source = source[:start] + parser + source[end:]
    source = source.replace("RABBIT GOD RUNTIME v1.2", "RABBIT GOD RUNTIME v2.0")
    source = source.replace("SCENE/ANIMA v2 + SIGNED CAPSULE + ROLLBACK", "UNIVERSAL PACKAGE + ASSETS + VM + ROLLBACK")
    source = source.replace("BOOTSTRAP CAT WORLD ACTIVE; RUNTIME READY", "EMPTY SAFE WORLD ACTIVE; UNIVERSAL RECEIVER READY")
    source = source.replace("CAPSULE HEALTHY: PROVISIONAL WORLD COMMITTED", "PACKAGE HEALTHY: ASSETS + OBJECTS + VM COMMITTED")
    source = source.replace("CAPSULE REJECTED: ACTIVE WORLD UNCHANGED", "PACKAGE REJECTED: ACTIVE WORLD UNCHANGED")
    return source


def compile_efi(source: str, directory: Path) -> bytes:
    v1 = load_module("rabbit_god_v1_crypto", V1 / "build_image.py")
    compiler = shutil.which("x86_64-w64-mingw32-gcc")
    objdump = shutil.which("x86_64-w64-mingw32-objdump")
    if compiler is None or objdump is None:
        raise BuildError("x86-64 MinGW compiler and objdump are required")
    v1.fetch_crypto(directory)
    assembly = directory / "universal_runtime.S"
    assembly.write_text(source, encoding="utf-8")
    output = directory / "BOOTX64.EFI"
    command = [
        compiler, "-std=c11", "-Os", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
        "-fno-builtin", "-fno-stack-protector", "-mno-red-zone", "-nostdlib", "-I", str(directory),
        str(assembly), str(ROOT / "runtime_core.c"), str(directory / "monocypher.c"),
        str(directory / "monocypher-ed25519.c"), "-Wl,--subsystem,10", "-Wl,--entry,rabbit_entry",
        "-Wl,--no-insert-timestamp", "-Wl,--image-base,0", "-Wl,--file-alignment,512",
        "-Wl,--section-alignment,4096", "-o", str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode:
        raise BuildError("UEFI link failed: " + completed.stderr.strip())
    inspection = subprocess.run([objdump, "-p", str(output)], check=True, capture_output=True, text=True).stdout
    if "DLL Name:" in inspection:
        raise BuildError("UEFI image imports an OS DLL")
    return output.read_bytes()


def build() -> tuple[bytes, dict[str, object]]:
    v1 = load_module("rabbit_god_v1_firmware", V1 / "build_image.py")
    media = load_module("rabbit_universal_media", MEDIA_PATH)
    source = transformed_source()
    with tempfile.TemporaryDirectory(prefix="rabbit-universal-runtime-") as temporary:
        efi = v1.inject_firmware(compile_efi(source, Path(temporary)))
    image = media.build_image(efi)
    report = {
        "schema_version": 2,
        "status": "BUILT-NOT-INSTALLED",
        "source_sha256": sha256(source.encode()),
        "runtime_core_sha256": sha256((ROOT / "runtime_core.c").read_bytes()),
        "target_sha256": sha256((ROOT / "target.json").read_bytes()),
        "efi_sha256": sha256(efi),
        "image_sha256": sha256(image),
        "image_size_bytes": len(image),
        "max_package_bytes": 4096,
        "transport": "rabbit-ble-frames-v2/16-bit-sequence/6-byte-payload",
        "package": "rabbit-universal-package-v2/ed25519",
        "transaction": "staging -> signature/bounds -> health -> commit-or-retain-active",
        "persistent_writes": 0,
        "physical_execution_verified": False,
    }
    return image, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        image, report = build()
        args.output.write_bytes(image)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (BuildError, OSError, subprocess.SubprocessError, KeyError, ValueError) as error:
        print(f"FAIL: {error}")
        return 1
    print(f"BUILT: {args.output} ({len(image)} bytes)")
    print(f"EFI SHA256: {report['efi_sha256']}")
    print(f"IMAGE SHA256: {report['image_sha256']}")
    print("STATUS: BUILT-NOT-INSTALLED; writes_performed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
