#!/usr/bin/env python3
"""Verify Reusable Creation Inventory v1, sharing, provenance, and rejection rules."""

from __future__ import annotations

import copy
import json
import subprocess
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from rabbit_inventory import (
    InventoryError,
    InventoryPackage,
    build_share_package,
    canonical_bytes,
    load_json,
    resolve_merge,
    sha256_hex,
    unique_pairs,
)


ROOT = Path(__file__).resolve().parent
EXPECTED_CAT_IDENTITY = "c6e1def6497769bbaa3917a8dacba099b01676af459358d7e6551fb6fa82eab8"
EXPECTED_BALL_IDENTITY = "1466de62fa8c841e020b5ff34e57abc28cea5bb59240426632418f3c325b2903"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rejected(label: str, action: object) -> None:
    try:
        action()  # type: ignore[operator]
    except InventoryError as error:
        print(f"PASS: rejected {label}: {error}")
        return
    raise AssertionError(f"did not reject {label}")


def main() -> int:
    catalog = load_json(ROOT / "catalog.json")
    cat_merge = load_json(ROOT / "examples" / "cat-plays-with-ball.merge.json")
    ball_merge = load_json(ROOT / "examples" / "bouncing-ball.merge.json")
    cat_lock = resolve_merge(catalog, cat_merge)
    ball_lock = resolve_merge(catalog, ball_merge)
    require(cat_lock["creation_sha256"] == EXPECTED_CAT_IDENTITY, "cat Creation identity changed")
    require(ball_lock["creation_sha256"] == EXPECTED_BALL_IDENTITY, "ball Creation identity changed")
    require(cat_lock["grants"] == ["display.draw", "time.read"], "cat authority changed")
    require(cat_lock["resources"] == {
        "memory_bytes": 39680,
        "persistent_bytes": 5568,
        "objects": 52,
        "pixels_per_frame": 307328,
        "ticks_per_second": 240,
    }, "cat resources changed")
    cat_components = {(item["component_id"], item["version"], item["sha256"]) for item in cat_lock["components"]}
    ball_components = {(item["component_id"], item["version"], item["sha256"]) for item in ball_lock["components"]}
    require(len(cat_components) == 13 and len(ball_components) == 10, "resolved component counts changed")
    require(len(cat_components & ball_components) == 10, "bouncing-ball did not reuse exact component identities")
    require(not any(word in canonical_bytes(cat_lock).lower() for word in (b"uefi", b"x86", b"dell", b"qemu")), "cat lock leaked target facts")

    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    package, report = build_share_package(catalog, cat_merge, private)
    decoded, payload = InventoryPackage.decode_and_verify(package, public)
    require(decoded.encode() == package and payload["lock"] == cat_lock, "signed package did not round-trip")
    require(report["status"] == "SIGNED-INVENTORY-PACKAGE-NOT-DEPLOYED" and report["deployments_performed"] == [], "package report made a deployment claim")
    require(report["package_sha256"] == sha256_hex(package), "package report hash changed")
    require(len(payload["catalog"]["components"]) == 13, "sharing package contains unrelated catalog components")

    damaged = bytearray(package)
    damaged[-1] ^= 1
    rejected("tampered package bytes", lambda: InventoryPackage.decode_and_verify(bytes(damaged), public))
    other_public = Ed25519PrivateKey.from_private_bytes(bytes(reversed(range(32)))).public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    rejected("an untrusted Creator", lambda: InventoryPackage.decode_and_verify(package, other_public))
    stale_payload = copy.deepcopy(payload)
    stale_payload["catalog"]["components"][0]["summary"] += " changed"
    stale_package = InventoryPackage.sign(stale_payload, private).encode()
    rejected("a re-signed package with a stale lock", lambda: InventoryPackage.decode_and_verify(stale_package, public))

    hidden_authority = copy.deepcopy(catalog)
    hidden_authority["components"][0]["authorities"] = ["network.send"]
    rejected("a hidden component authority", lambda: resolve_merge(hidden_authority, cat_merge))
    extra_grant = copy.deepcopy(cat_merge)
    extra_grant["grants"] = ["display.draw", "microphone.read", "time.read"]
    rejected("an unused authority grant", lambda: resolve_merge(catalog, extra_grant))
    missing_dependency = copy.deepcopy(cat_merge)
    missing_dependency["members"] = [item for item in missing_dependency["members"] if item["component_id"] != "rabbit.capability.clock-tick"]
    rejected("an omitted dependency", lambda: resolve_merge(catalog, missing_dependency))
    wrong_type = copy.deepcopy(cat_merge)
    wrong_type["bindings"][3]["to"] = {"component_id": "rabbit.capability.animation-frames", "port": "frames"}
    rejected("an incompatible typed binding", lambda: resolve_merge(catalog, wrong_type))
    too_small = copy.deepcopy(cat_merge)
    too_small["budgets"]["memory_bytes"] = 39679
    rejected("a resource budget overflow", lambda: resolve_merge(catalog, too_small))
    target_leak = copy.deepcopy(catalog)
    target_leak["components"][0]["summary"] = "Special behavior for Dell"
    rejected("target-specific vocabulary", lambda: resolve_merge(target_leak, cat_merge))
    native_code = copy.deepcopy(catalog)
    native_code["components"][0]["implementation"] = {"format": "rabbit.native-code.v1", "bytes": "90"}
    rejected("an unreviewed native-code implementation", lambda: resolve_merge(native_code, cat_merge))
    bad_sprite = copy.deepcopy(catalog)
    for component in bad_sprite["components"]:
        if component["component_id"] == "rabbit.asset.cat-pixel":
            component["implementation"]["frames"][0][0] = "TOO-SHORT"
    rejected("a malformed reusable sprite", lambda: resolve_merge(bad_sprite, cat_merge))
    cycle_catalog = copy.deepcopy(catalog)
    cycle_catalog["components"][0]["dependencies"] = [
        {"component_id": "rabbit.anima.bouncing-ball", "version": "1.0.0"},
        *cycle_catalog["components"][0]["dependencies"],
    ]
    rejected("a component dependency cycle", lambda: resolve_merge(cycle_catalog, cat_merge))
    rejected("ambiguous duplicate JSON", lambda: json.loads('{"schema_version":1,"schema_version":2}', object_pairs_hook=unique_pairs))

    with tempfile.TemporaryDirectory(prefix="rabbit-inventory-v1-") as temporary:
        temp = Path(temporary)
        private_path = temp / "creator.key"
        public_path = temp / "creator.pub"
        package_path = temp / "cat.rabbit-inventory"
        report_path = temp / "cat.report.json"
        private_path.write_bytes(bytes(range(32)))
        public_path.write_bytes(public)
        built = subprocess.run([
            "python3", str(ROOT / "build_package.py"),
            "--merge", str(ROOT / "examples" / "cat-plays-with-ball.merge.json"),
            "--private-key", str(private_path),
            "--output", str(package_path),
            "--report", str(report_path),
        ], check=False, capture_output=True, text=True)
        require(built.returncode == 0 and package_path.read_bytes() == package, f"CLI build failed: {built.stdout}{built.stderr}")
        inspected = subprocess.run([
            "python3", str(ROOT / "inspect_package.py"), str(package_path),
            "--trusted-public-key", str(public_path),
        ], check=False, capture_output=True, text=True)
        require(inspected.returncode == 0 and "VERIFIED CREATOR PACKAGE: Cat Plays With Ball" in inspected.stdout, f"CLI inspect failed: {inspected.stdout}{inspected.stderr}")

    print("PASS: exact component identities are shared across Cat and Bouncing Ball Creations")
    print("PASS: Merge resolves typed ports, exact dependencies, authorities, budgets, provenance, and licenses")
    print("PASS: Cat Plays With Ball resolves to 13 reusable components without target facts")
    print("PASS: Ed25519 package export/import binds one trusted Creator and the exact resolved lock")
    print(f"PASS: cat={EXPECTED_CAT_IDENTITY}, ball={EXPECTED_BALL_IDENTITY}, package={report['package_sha256']}")
    print("PASS: INVENTORY-V1-BUILT-NOT-EXECUTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
