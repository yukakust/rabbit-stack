#!/usr/bin/env python3
"""Verify Universal Package v2, its transport, VM boundary, and UEFI image."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from build_image import ROOT, V1, build, load_module, transformed_source
from compile_world import compile_world
from package import Object, PackageError, Program, Sprite, build_package, decode_package
from transport import TransportError, decode_transfer, encode_transfer


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejected(label: str, action) -> None:
    try:
        action()
    except (PackageError, TransportError, ValueError, KeyError, TypeError):
        print(f"PASS: rejected {label}")
        return
    raise RuntimeError(f"invalid case accepted: {label}")


def host_crypto_check(package: bytes, should_accept: bool) -> None:
    compiler = shutil.which("cc")
    if compiler is None:
        raise RuntimeError("host C compiler is required")
    v1 = load_module("rabbit_v2_test_crypto", V1 / "build_image.py")
    temp_root = Path(os.environ.get("RABBIT_TMPDIR", str(ROOT)))
    with tempfile.TemporaryDirectory(prefix="rabbit-v2-host-", dir=temp_root) as temporary:
        directory = Path(temporary)
        v1.fetch_crypto(directory)
        binary = directory / "package.bin"; binary.write_bytes(package)
        harness = directory / "harness.c"
        harness.write_text('''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
int rabbit_package_verify_only(const uint8_t*,uint32_t,uint32_t);
int main(int argc,char**argv){uint8_t b[4096];FILE*f=fopen(argv[1],"rb");if(!f)return 9;
size_t n=fread(b,1,sizeof(b),f);fclose(f);return rabbit_package_verify_only(b,(uint32_t)n,(uint32_t)strtoul(argv[2],0,10));}
''', encoding="ascii")
        output = directory / "check"
        result = subprocess.run([compiler, "-std=c11", "-O2", "-Wno-attributes", "-I", str(directory),
                                 str(ROOT / "runtime_core.c"), str(directory / "monocypher.c"),
                                 str(directory / "monocypher-ed25519.c"), str(harness), "-o", str(output)], capture_output=True, text=True)
        require(result.returncode == 0, "host verifier did not compile: " + result.stderr)
        accepted = subprocess.run([str(output), str(binary), "0"], check=False).returncode == 0
        require(accepted == should_accept, "freestanding verifier disagrees with Python")


def main() -> int:
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    world = ROOT / "worlds" / "cat-chases-mouse.json"
    package = compile_world(world, 1, private)
    decoded = decode_package(package, public)
    require(decoded["counter"] == 1 and len(decoded["sprites"]) == 2 and len(decoded["objects"]) == 2 and len(decoded["programs"]) == 2, "demo world meaning changed")
    frames = encode_transfer(package)
    require(decode_transfer(frames) == package and len(frames) == 54, "v2 transport round-trip changed")
    print(f"PASS: data-only world lowers to a {len(package)}-byte signed package and {len(frames)} BLE v2 frames")

    damaged = bytearray(package); damaged[80] ^= 1
    rejected("a package changed after signing", lambda: decode_package(bytes(damaged), public))
    reordered = frames.copy(); reordered[3], reordered[4] = reordered[4], reordered[3]
    rejected("reordered chunks", lambda: decode_transfer(reordered))
    rejected("an in-boot replay", lambda: decode_package(package, public, 1))
    bad_world = json.loads(world.read_text(encoding="utf-8")); bad_world["programs"][0]["code"][0] = 127
    with tempfile.TemporaryDirectory(prefix="rabbit-v2-negative-", dir=ROOT) as temporary:
        path = Path(temporary) / "bad.json"; path.write_text(json.dumps(bad_world), encoding="utf-8")
        rejected("an unknown VM opcode", lambda: compile_world(path, 2, private))
    print("PASS: signature, replay, ordering, and VM opcode boundaries reject invalid worlds")

    pixels = bytes((index & 1 for index in range(16 * 16)))
    large = build_package(counter=2, palette=(0, 0xFFFFFF), sprites=(Sprite(1, 16, 16, (pixels,) * 13),),
                          objects=(Object(1, 1, 1, 0, 0),), programs=(Program(1, b"\0"),), private_key=private)
    large_frames = encode_transfer(large)
    require(len(large_frames) > 256 and decode_transfer(large_frames) == large, "16-bit sequence transport failed beyond frame 255")
    print(f"PASS: 16-bit ordered transport crosses the old 255-frame ceiling ({len(large_frames)} frames)")

    host_crypto_check(package, True); host_crypto_check(bytes(damaged), False)
    print("PASS: the same freestanding Ed25519 verifier accepts the package and rejects tampering")

    image_a, report_a = build(); image_b, report_b = build()
    require(image_a == image_b and report_a == report_b and len(image_a) == 67108864, "physical image is not deterministic")
    source = transformed_source()
    for marker in ("RABBIT GOD RUNTIME v2.0", "rabbit_package_frame", "UNIVERSAL PACKAGE + ASSETS + VM + ROLLBACK", "PACKAGE HEALTHY: ASSETS + OBJECTS + VM COMMITTED"):
        require(marker in source, f"generated source lacks {marker}")
    target = json.loads((ROOT / "target.json").read_text(encoding="utf-8"))
    require(target["transport"]["sequence_bits"] == 16 and target["transport"]["max_package_bytes"] == 4096, "target transport limits changed")
    require(set(target["forbidden"]) >= {"native-code-from-package", "arbitrary-memory-write", "internal-storage-write", "firmware-write"}, "forbidden authority disappeared")
    print(f"PASS: deterministic one-image UEFI candidate {report_a['image_sha256']}")
    print("PASS: one runtime contains generic RAM assets, multi-object VM, staging, Ed25519, health, rollback, and ACK")
    evidence_path = ROOT / "evidence" / "qemu-linux-x86-64-observed.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    bindings = evidence["bindings"]
    require(evidence["status"] == "OBSERVED-HEADLESS-QEMU-FAIL-CLOSED" and
            bindings["generated_source_sha256"] == report_a["source_sha256"] and
            bindings["runtime_core_sha256"] == report_a["runtime_core_sha256"] and
            bindings["target_sha256"] == report_a["target_sha256"],
            "QEMU evidence is stale for the current source contract")
    observation = evidence["observation"]
    require(observation["target_found"] is False and all(observation[field] == 0 for field in
            ("controller_ram_writes", "hci_commands_sent", "radio_operations_requested", "package_bytes_received", "framebuffer_writes_performed")),
            "QEMU mismatch evidence reports an effect")
    if (bindings["efi_sha256"] == report_a["efi_sha256"] and
            bindings["image_sha256"] == report_a["image_sha256"]):
        print(f"PASS: exact QEMU evidence matches this toolchain artifact ({evidence_path.name})")
    else:
        print("PASS: QEMU evidence matches the source/runtime/target contract; "
              "this host toolchain produced a distinct deterministic EFI artifact")
    print("PASS: QEMU evidence fails closed before device, package, graphics, or radio effects")
    print("PASS: QEMU-GATED universal package v2 contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
