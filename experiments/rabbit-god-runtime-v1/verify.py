#!/usr/bin/env python3
"""Verify God Runtime v1 transaction, package, target, and rollback boundaries."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Callable

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from rabbit_god_runtime import (
    BOOTSTRAP_PATH, INVENTORY_ROOT, RUNTIME_PATH, TARGET_PATH, GodRuntime,
    GodRuntimeError, identity, load_json, sha256, transfer, unique_pairs,
    validate_contract, validate_target,
)


sys.path.insert(0, str(INVENTORY_ROOT))
from rabbit_inventory import build_share_package  # noqa: E402


ROOT = Path(__file__).resolve().parent
PHYSICAL_EVIDENCE = ROOT.parent / "x86-64-uefi-scene-anima-v2" / "evidence" / "dell-optiplex-3060-physical-observed.json"
EXPECTED_RUNTIME_SHA256 = "d59a36fd72c85732f1f5986ff61bd9b84a190ccaa5e3e9b1f83711b9ac617438"
EXPECTED_TARGET_SHA256 = "821fc353b0d2ab19a44a735360998fcb66869a0ead570a26010bb7e175628141"
EXPECTED_BOOTSTRAP_SHA256 = "c09c1e416d1ea1a044ccf3862072c7825f37b501391db4b5574405068b80474c"
EXPECTED_CAT_PACKAGE_SHA256 = "215172ec52a3eb9c79e6e6dfacc47811c3897d0bdd613286d1953072c05aa5f1"
EXPECTED_CAT_CREATION_SHA256 = "c6e1def6497769bbaa3917a8dacba099b01676af459358d7e6551fb6fa82eab8"
EXPECTED_BALL_CREATION_SHA256 = "1466de62fa8c841e020b5ff34e57abc28cea5bb59240426632418f3c325b2903"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejected(label: str, action: Callable[[], object]) -> None:
    try:
        action()
    except (GodRuntimeError, RuntimeError) as error:
        print(f"PASS: rejected {label}: {error}")
        return
    raise RuntimeError(f"invalid case accepted: {label}")


def send_to_commit(runtime: GodRuntime, package: bytes, transfer_id: str, counter: int) -> None:
    runtime.begin(transfer_id, counter, len(package), sha256(package))
    step = runtime.target["transport"]["frame_payload_bytes"]
    for offset in range(0, len(package), step):
        runtime.chunk(offset, package[offset:offset + step])
    runtime.commit()


def main() -> int:
    try:
        contract = load_json(RUNTIME_PATH)
        target = load_json(TARGET_PATH)
        bootstrap = load_json(BOOTSTRAP_PATH)
        catalog = load_json(INVENTORY_ROOT / "catalog.json")
        cat_merge = load_json(INVENTORY_ROOT / "examples" / "cat-plays-with-ball.merge.json")
        ball_merge = load_json(INVENTORY_ROOT / "examples" / "bouncing-ball.merge.json")
        physical = load_json(PHYSICAL_EVIDENCE)

        require(identity(contract) == EXPECTED_RUNTIME_SHA256, "runtime contract identity changed")
        require(identity(target) == EXPECTED_TARGET_SHA256, "Dell Target Pack identity changed")
        require(identity(bootstrap) == EXPECTED_BOOTSTRAP_SHA256, "bootstrap identity changed")
        require(physical["evidence_id"] == bootstrap["physical_evidence_id"], "bootstrap is not bound to physical evidence")
        require(physical["bindings"]["creation_sha256"] == bootstrap["creation_sha256"], "bootstrap Creation differs from physical evidence")
        require(physical["observation"]["cat_motion_visible"] is True and physical["observation"]["ball_motion_visible"] is True, "bootstrap physical motion is not established")

        creator = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        cat_package, cat_report = build_share_package(catalog, cat_merge, creator)
        ball_package, ball_report = build_share_package(catalog, ball_merge, creator)
        require(cat_report["package_sha256"] == EXPECTED_CAT_PACKAGE_SHA256, "Cat package identity changed")
        require(cat_report["creation_sha256"] == EXPECTED_CAT_CREATION_SHA256, "Cat Creation identity changed")
        require(ball_report["creation_sha256"] == EXPECTED_BALL_CREATION_SHA256, "Ball Creation identity changed")
        require(len(cat_package) == 20329, "Cat package size changed")
        expected_frames = (len(cat_package) + target["transport"]["frame_payload_bytes"] - 1) // target["transport"]["frame_payload_bytes"]
        require(expected_frames == 2542 and expected_frames <= target["transport"]["max_frames"], "Cat package no longer fits Dell BLE frame budget")

        runtime = GodRuntime(contract, target, bootstrap)
        receipt = transfer(runtime, cat_package, "A1", 1)
        require(receipt == {
            "status": "COMMITTED",
            "transfer_id": "A1",
            "counter": 1,
            "package_sha256": EXPECTED_CAT_PACKAGE_SHA256,
            "creation_sha256": EXPECTED_CAT_CREATION_SHA256,
        }, "committed receipt changed")
        require(runtime.active["creation_sha256"] == EXPECTED_CAT_CREATION_SHA256 and runtime.state == "committed", "Cat world did not commit")
        rejected("a replayed in-boot counter", lambda: runtime.begin("A2", 1, len(cat_package), sha256(cat_package)))

        send_to_commit(runtime, ball_package, "B2", 2)
        require(runtime.active["creation_sha256"] == EXPECTED_BALL_CREATION_SHA256 and runtime.state == "provisional", "Ball world did not enter provisional state")
        rollback = runtime.health(False)
        require(rollback["status"] == "ROLLED-BACK", "health failure did not report rollback")
        require(runtime.active["creation_sha256"] == EXPECTED_CAT_CREATION_SHA256, "health failure did not restore previous Cat world")

        corrupted = GodRuntime(contract, target, bootstrap)
        damaged = bytearray(cat_package)
        damaged[-1] ^= 1
        corrupted.begin("C1", 1, len(damaged), sha256(cat_package))
        for offset in range(0, len(damaged), 8):
            corrupted.chunk(offset, bytes(damaged[offset:offset + 8]))
        rejected("a corrupted package", corrupted.commit)
        require(corrupted.active == bootstrap, "corruption replaced the active world")

        reordered = GodRuntime(contract, target, bootstrap)
        reordered.begin("D1", 1, len(cat_package), sha256(cat_package))
        rejected("a missing or reordered chunk", lambda: reordered.chunk(8, cat_package[8:16]))
        require(reordered.active == bootstrap, "reordered data replaced the active world")

        other_creator = Ed25519PrivateKey.from_private_bytes(bytes(reversed(range(32))))
        untrusted_package, _ = build_share_package(catalog, cat_merge, other_creator)
        untrusted = GodRuntime(contract, target, bootstrap)
        untrusted.begin("E1", 1, len(untrusted_package), sha256(untrusted_package))
        for offset in range(0, len(untrusted_package), 8):
            untrusted.chunk(offset, untrusted_package[offset:offset + 8])
        rejected("an untrusted Creator package", untrusted.commit)
        require(untrusted.active == bootstrap, "untrusted Creator replaced the active world")

        too_large = GodRuntime(contract, target, bootstrap)
        rejected("an oversized package", lambda: too_large.begin("F1", 1, contract["limits"]["package_bytes"] + 1, "0" * 64))
        escalated_contract = copy.deepcopy(contract)
        escalated_contract["allowed_authorities"].insert(1, "network.send")
        rejected("runtime authority escalation", lambda: validate_contract(escalated_contract))
        disk_target = copy.deepcopy(target)
        disk_target["authority"]["internal_storage_writes"] = True
        rejected("Target Pack internal-storage writes", lambda: validate_target(disk_target))
        native_target = copy.deepcopy(target)
        native_target["authority"]["native_code_from_package"] = True
        rejected("Target Pack native package execution", lambda: validate_target(native_target))
        rejected("ambiguous duplicate JSON", lambda: json.loads('{"schema_version":1,"schema_version":2}', object_pairs_hook=unique_pairs))

        print("PASS: physical Dell cat-and-ball scene is the exact bootstrap fallback world")
        print("PASS: the signed 20,329-byte Cat Creation fits 2,542 bounded BLE payload frames")
        print("PASS: BEGIN + ordered CHUNK + COMMIT activates only a complete trusted Inventory package")
        print("PASS: receipt is emitted only after health succeeds; failed health restores the previous world")
        print("PASS: corruption, reorder, untrusted signer, replay, overflow, authority, native code, and disk writes are rejected")
        print(f"PASS: runtime={EXPECTED_RUNTIME_SHA256}, target={EXPECTED_TARGET_SHA256}, bootstrap={EXPECTED_BOOTSTRAP_SHA256}")
        print("PASS: GOD-RUNTIME-V1-CONTRACT-HOSTED-VERIFIED-NOT-PHYSICALLY-INSTALLED")
        return 0
    except (GodRuntimeError, OSError, RuntimeError) as error:
        print(f"FAIL: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
