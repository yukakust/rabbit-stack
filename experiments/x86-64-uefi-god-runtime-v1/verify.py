#!/usr/bin/env python3
"""Verify the physical Rabbit God Runtime v1 artifact and transaction."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from build_image import ROOT, build, fetch_crypto, transformed_source
from capsule import CAPSULE_SIZE, CapsuleError, SceneConfig, TransactionModel, decode, encode
from compile_capsule import compile_package
from send_capsule import reviewed_capsule
from transport import TransportError, decode_transfer, encode_transfer

INVENTORY = ROOT.parent / "reusable-creation-inventory-v1"
sys.path.insert(0, str(INVENTORY))
from rabbit_inventory import InventoryPackage, build_share_package, load_json, resolve_merge  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejected(label: str, action) -> None:
    try:
        action()
    except (CapsuleError, TransportError, ValueError):
        print(f"PASS: rejected {label}")
        return
    raise RuntimeError(f"invalid case accepted: {label}")


def host_crypto_check(capsule: bytes, should_accept: bool) -> None:
    compiler = shutil.which("cc")
    if compiler is None:
        raise RuntimeError("host C compiler is required")
    with tempfile.TemporaryDirectory(prefix="rabbit-god-host-") as temporary:
        directory = Path(temporary)
        fetch_crypto(directory)
        capsule_path = directory / "capsule.bin"
        capsule_path.write_bytes(capsule)
        harness = directory / "harness.c"
        harness.write_text('''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
int rabbit_capsule_verify_only(const uint8_t*,uint32_t,uint32_t);
int main(int argc,char**argv){uint8_t b[192];FILE*f=fopen(argv[1],"rb");
if(!f||fread(b,1,192,f)!=192)return 9;fclose(f);
return rabbit_capsule_verify_only(b,192,(uint32_t)strtoul(argv[2],0,10));}
''', encoding="ascii")
        output = directory / "check"
        command = [compiler, "-std=c11", "-O2", "-Wno-attributes", "-I", str(directory),
                   str(ROOT / "runtime_core.c"), str(directory / "monocypher.c"),
                   str(directory / "monocypher-ed25519.c"), str(harness), "-o", str(output)]
        compiled = subprocess.run(command, capture_output=True, text=True)
        require(compiled.returncode == 0, "host capsule verifier did not compile: " + compiled.stderr)
        result = subprocess.run([str(output), str(capsule_path), "0"], check=False)
        accepted = result.returncode == 0
        require(accepted == should_accept, f"freestanding C verifier returned {result.returncode}")


def main() -> int:
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    catalog = load_json(INVENTORY / "catalog.json")
    merge = load_json(INVENTORY / "examples" / "cat-plays-with-ball.merge.json")
    package, _ = build_share_package(catalog, merge, private)
    inventory_digest = hashlib.sha256(package).hexdigest()
    capsule = encode(SceneConfig(1, inventory_digest), private)
    require(len(capsule) == CAPSULE_SIZE, "capsule size changed")
    decoded = decode(capsule, public)
    require(decoded["counter"] == 1 and decoded["inventory_package_sha256"] == inventory_digest, "capsule meaning changed")
    compiled = compile_package(package, bytes(range(32)), 1)
    require(compiled == capsule, "Inventory lowering differs from direct capsule construction")
    require(reviewed_capsule(SceneConfig(1, "")) == capsule, "physical sender differs from reviewed capsule")
    frames = encode_transfer(capsule)
    require(len(frames) == 30 and decode_transfer(frames) == capsule, "30-frame transport round-trip changed")
    print("PASS: trusted Inventory lowers deterministically to one 192-byte signed capsule and 30 BLE frames")

    damaged = bytearray(capsule); damaged[80] ^= 1
    rejected("a capsule changed after signing", lambda: decode(bytes(damaged), public))
    reordered = frames.copy(); reordered[4], reordered[5] = reordered[5], reordered[4]
    rejected("reordered capsule chunks", lambda: decode_transfer(reordered))
    other = Ed25519PrivateKey.from_private_bytes(bytes(reversed(range(32))))
    rejected("an untrusted Creator", lambda: decode(encode(SceneConfig(2, inventory_digest), other), public))
    rejected("an in-boot replay", lambda: decode(capsule, public, 1))
    print("PASS: corruption, reorder, untrusted signer, and stale in-boot replay are rejected")

    model = TransactionModel(public)
    committed = model.apply(capsule)
    require(committed["status"] == "COMMITTED" and model.last_counter == 1, "healthy capsule did not commit")
    faulty = encode(SceneConfig(2, inventory_digest, health_fault=True), private)
    before = model.active
    rollback = model.apply(faulty)
    require(rollback["status"] == "ROLLED-BACK" and model.active is before and model.last_counter == 1,
            "failed health did not restore the exact prior world")
    print("PASS: health success commits; health failure restores the exact previous active world")

    host_crypto_check(capsule, True)
    host_crypto_check(bytes(damaged), False)
    print("PASS: the same freestanding C Ed25519 verifier accepts the capsule and rejects tampering")

    image_a, report_a = build(); image_b, report_b = build()
    require(image_a == image_b and report_a == report_b, "repeated physical builds differ")
    require(len(image_a) == 67108864 and report_a["persistent_writes"] == 0, "image envelope changed")
    source = transformed_source()
    for marker in ("RABBIT GOD RUNTIME v1.1", "rabbit_capsule_verify_activate", "HEALTH FAILED: PREVIOUS WORLD RESTORED",
                   "CAPSULE HEALTHY: PROVISIONAL WORLD COMMITTED"):
        require(marker in source, f"generated UEFI source lacks {marker}")
    require(source.count("cmp r12d, 32") == 2 and "cmp r12d, 8" not in source,
            "HCI command event budget is not the reviewed bounded 32 events")
    target = json.loads((ROOT / "target.json").read_text(encoding="utf-8"))
    forbidden = ("native_code_from_capsule", "arbitrary_memory_write", "internal_storage_write", "firmware_write", "pair", "connect")
    require(all(target["authority"][field] is False for field in forbidden), "forbidden target authority appeared")
    print(f"PASS: deterministic one-image UEFI artifact {report_a['image_sha256']}")
    print("PASS: one image composes Scene/Anima, passive Bluetooth, staging, Ed25519, health, commit, rollback, and receipt")

    exact_artifact_evidence = []
    for evidence_path in sorted((ROOT / "evidence").glob("qemu-*-observed.json")):
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        bindings = evidence["bindings"]
        require(evidence["status"] in ("OBSERVED-HEADLESS-QEMU-FAIL-CLOSED", "OBSERVED-QEMU-FAIL-CLOSED"),
                f"QEMU evidence status changed: {evidence_path.name}")
        if bindings["generated_source_sha256"] != report_a["source_sha256"]:
            continue  # immutable evidence for an older implementation revision
        require(bindings["runtime_core_sha256"] == report_a["runtime_core_sha256"],
                f"current QEMU evidence runtime core is stale: {evidence_path.name}")
        require(bindings["target_sha256"] == report_a["target_sha256"],
                f"current QEMU evidence Target Pack is stale: {evidence_path.name}")
        observation = evidence["observation"]
        require(observation["target_found"] is False, "QEMU mismatch evidence unexpectedly found hardware")
        require(all(observation[field] == 0 for field in (
            "controller_ram_writes", "hci_commands_sent", "radio_operations_requested",
            "capsule_bytes_received", "framebuffer_writes_performed",
        )), "QEMU mismatch evidence reports a forbidden effect")
        if bindings["image_sha256"] == report_a["image_sha256"]:
            if "efi_sha256" in bindings:
                require(bindings["efi_sha256"] == report_a["efi_sha256"], "QEMU evidence EFI is stale")
            exact_artifact_evidence.append(evidence_path.name)
    require(len(exact_artifact_evidence) == 1,
            "this host-built image lacks one exact QEMU observation: " + report_a["image_sha256"])
    print(f"PASS: exact zero-effect QEMU evidence matches this toolchain artifact ({exact_artifact_evidence[0]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
