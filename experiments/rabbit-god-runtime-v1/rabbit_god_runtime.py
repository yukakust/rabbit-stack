#!/usr/bin/env python3
"""Target-independent transactional core contract for Rabbit God Runtime v1."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parent.parent
INVENTORY_ROOT = REPOSITORY / "experiments" / "reusable-creation-inventory-v1"
sys.path.insert(0, str(INVENTORY_ROOT))

from rabbit_inventory import InventoryError, InventoryPackage, canonical_bytes  # noqa: E402


RUNTIME_PATH = ROOT / "runtime.json"
TARGET_PATH = ROOT / "targets" / "dell-optiplex-3060-ble.json"
BOOTSTRAP_PATH = ROOT / "bootstrap.json"
TRANSFER_RE = re.compile(r"[0-9A-F]{2}\Z")
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
RUNTIME_FIELDS = {
    "schema_version", "runtime_id", "version", "accepted_package", "transaction",
    "limits", "allowed_authorities", "forbidden_effects", "security",
}
TARGET_FIELDS = {
    "schema_version", "target_id", "architecture", "firmware", "runtime_envelope",
    "bindings", "transport", "authority", "recovery",
}
BOOTSTRAP_FIELDS = {
    "schema_version", "slot", "source", "creation_id", "creation_sha256",
    "inventory_package_sha256", "component_count", "physical_evidence_id", "fallback",
}


class GodRuntimeError(ValueError):
    pass


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GodRuntimeError(f"duplicate JSON field: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
    except (OSError, json.JSONDecodeError) as error:
        raise GodRuntimeError(f"could not load {path}: {error}") from error
    if not isinstance(value, dict):
        raise GodRuntimeError(f"{path.name} must contain an object")
    return value


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def identity(value: Any) -> str:
    return sha256(canonical_bytes(value))


def exact_fields(value: dict[str, Any], fields: set[str], label: str) -> None:
    if set(value) != fields:
        raise GodRuntimeError(f"{label} fields differ from the reviewed contract")


def validate_contract(contract: dict[str, Any]) -> None:
    exact_fields(contract, RUNTIME_FIELDS, "runtime")
    if contract["schema_version"] != 1 or contract["runtime_id"] != "rabbit.god-runtime" or contract["version"] != "1.0.0":
        raise GodRuntimeError("runtime identity is unsupported")
    package = contract["accepted_package"]
    if set(package) != {"format", "trusted_creator_public_keys", "signature", "content_hash"}:
        raise GodRuntimeError("accepted package contract changed")
    if package["format"] != "rabbit-inventory-v1" or package["signature"] != "ed25519" or package["content_hash"] != "sha256":
        raise GodRuntimeError("package verification mechanism changed")
    keys = package["trusted_creator_public_keys"]
    if not isinstance(keys, list) or not keys or keys != sorted(set(keys)) or any(re.fullmatch(r"[0-9a-f]{64}", key) is None for key in keys):
        raise GodRuntimeError("trusted Creator keys are invalid")
    transaction = contract["transaction"]
    if transaction != {
        "states": ["active", "receiving", "validated", "provisional", "committed", "rolled-back"],
        "activation": "whole-package-only",
        "health_check_required": True,
        "failure_policy": "retain-or-restore-previous-active-slot",
        "receipt_after": "health-check",
    }:
        raise GodRuntimeError("transaction contract changed")
    limits = contract["limits"]
    expected_limits = {"package_bytes", "components", "memory_bytes", "persistent_bytes", "objects", "pixels_per_frame", "ticks_per_second"}
    if set(limits) != expected_limits or any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in limits.values()):
        raise GodRuntimeError("runtime limits are invalid")
    if contract["allowed_authorities"] != ["display.draw", "time.read"]:
        raise GodRuntimeError("runtime authority set changed")
    required_forbidden = {"arbitrary-memory-write", "firmware-write", "internal-storage-write", "native-code-execution", "unreviewed-device-io"}
    if set(contract["forbidden_effects"]) != required_forbidden:
        raise GodRuntimeError("forbidden effect set changed")
    security = contract["security"]
    if security != {
        "creator_authentication": "required",
        "corruption_detection": "sha256",
        "in_boot_monotonic_counter": "required",
        "cross-reboot_replay_protection": "deferred-debt",
        "transport_encryption": "deferred-debt",
    }:
        raise GodRuntimeError("security boundary changed")


def validate_target(target: dict[str, Any]) -> None:
    exact_fields(target, TARGET_FIELDS, "target")
    if target["schema_version"] != 1 or target["target_id"] != "dell-optiplex-3060-qca-ble-god-runtime-v1":
        raise GodRuntimeError("Target Pack identity is unsupported")
    if target["architecture"] != "x86-64" or target["firmware"] != "uefi" or target["runtime_envelope"] != "removable-usb-resident":
        raise GodRuntimeError("Target Pack machine envelope changed")
    if target["bindings"] != {
        "display.draw": "uefi-gop-bounded",
        "time.read": "uefi-boot-services-stall",
        "package.receive": "qca-rome-passive-ble-advertisement-burst-v2",
        "receipt.emit": "qca-rome-nonconnectable-ble-advertisement-v1",
    }:
        raise GodRuntimeError("Target Pack bindings changed")
    if target["transport"] != {
        "mode": "transactional-begin-chunk-commit",
        "frame_payload_bytes": 8,
        "max_frames": 4096,
        "receive": "passive",
        "acknowledgement": "bounded-nonconnectable-advertisement",
        "pairing": False,
        "connection": False,
    }:
        raise GodRuntimeError("Target Pack transport changed")
    authority = target["authority"]
    if authority != {
        "controller_ram_write": "hash-pinned-qca-rampatch-and-nvm-only",
        "radio_receive": "bounded-reviewed-rabbit-frames-only",
        "radio_transmit": "bounded-correlated-receipt-only",
        "gop_framebuffer_write": "bounded-runtime-surface-only",
        "keyboard_read": "escape-only-runtime-exit",
        "internal_storage_writes": False,
        "firmware_writes": False,
        "native_code_from_package": False,
    }:
        raise GodRuntimeError("Target Pack authority changed")


def validate_bootstrap(bootstrap: dict[str, Any]) -> None:
    exact_fields(bootstrap, BOOTSTRAP_FIELDS, "bootstrap")
    if bootstrap != {
        "schema_version": 1,
        "slot": "active",
        "source": "embedded-reviewed-creation",
        "creation_id": "creation.cat-plays-with-ball",
        "creation_sha256": "c6e1def6497769bbaa3917a8dacba099b01676af459358d7e6551fb6fa82eab8",
        "inventory_package_sha256": "215172ec52a3eb9c79e6e6dfacc47811c3897d0bdd613286d1953072c05aa5f1",
        "component_count": 13,
        "physical_evidence_id": "dell-optiplex-3060-scene-anima-v2-2026-09-30",
        "fallback": "always-available-until-a-new-world-passes-validation-and-health",
    }:
        raise GodRuntimeError("bootstrap world changed")


def validate_lock(lock: dict[str, Any], contract: dict[str, Any]) -> None:
    limits = contract["limits"]
    if len(lock["components"]) > limits["components"]:
        raise GodRuntimeError("Creation exceeds component limit")
    if not set(lock["grants"]).issubset(set(contract["allowed_authorities"])):
        raise GodRuntimeError("Creation requests unsupported authority")
    for field in ("memory_bytes", "persistent_bytes", "objects", "pixels_per_frame", "ticks_per_second"):
        if lock["resources"][field] > limits[field]:
            raise GodRuntimeError(f"Creation exceeds runtime limit {field}")


@dataclass
class StagingTransfer:
    transfer_id: str
    counter: int
    size: int
    expected_sha256: str
    received: bytearray


class GodRuntime:
    """Deterministic model of receive, validate, activate, health, and rollback."""

    def __init__(self, contract: dict[str, Any], target: dict[str, Any], bootstrap: dict[str, Any]):
        validate_contract(contract)
        validate_target(target)
        validate_bootstrap(bootstrap)
        self.contract = contract
        self.target = target
        self.active = dict(bootstrap)
        self.previous: dict[str, Any] | None = None
        self.staging: StagingTransfer | None = None
        self.last_counter = 0
        self.state = "active"
        self.receipt: dict[str, Any] | None = None

    def begin(self, transfer_id: str, counter: int, size: int, package_sha256: str) -> None:
        if self.staging is not None or self.state == "provisional":
            raise GodRuntimeError("another transaction is active")
        if TRANSFER_RE.fullmatch(transfer_id) is None:
            raise GodRuntimeError("transfer id must be two uppercase hexadecimal digits")
        if isinstance(counter, bool) or not isinstance(counter, int) or counter <= self.last_counter:
            raise GodRuntimeError("transfer counter is stale or invalid")
        if isinstance(size, bool) or not isinstance(size, int) or not 1 <= size <= self.contract["limits"]["package_bytes"]:
            raise GodRuntimeError("package size exceeds the runtime limit")
        if HASH_RE.fullmatch(package_sha256) is None:
            raise GodRuntimeError("package SHA-256 is invalid")
        frames = (size + self.target["transport"]["frame_payload_bytes"] - 1) // self.target["transport"]["frame_payload_bytes"]
        if frames > self.target["transport"]["max_frames"]:
            raise GodRuntimeError("package exceeds the Target Pack frame budget")
        self.staging = StagingTransfer(transfer_id, counter, size, package_sha256, bytearray())
        self.state = "receiving"

    def chunk(self, offset: int, payload: bytes) -> None:
        if self.staging is None or self.state != "receiving":
            raise GodRuntimeError("no receiving transaction exists")
        if offset != len(self.staging.received):
            raise GodRuntimeError("package chunk is missing or reordered")
        if not payload or len(payload) > self.target["transport"]["frame_payload_bytes"]:
            raise GodRuntimeError("package chunk size is invalid")
        if offset + len(payload) > self.staging.size:
            raise GodRuntimeError("package chunk exceeds declared size")
        self.staging.received.extend(payload)

    def commit(self) -> dict[str, Any]:
        if self.staging is None or self.state != "receiving":
            raise GodRuntimeError("no receiving transaction exists")
        transfer = self.staging
        encoded = bytes(transfer.received)
        if len(encoded) != transfer.size:
            raise GodRuntimeError("package is incomplete")
        if sha256(encoded) != transfer.expected_sha256:
            raise GodRuntimeError("package SHA-256 mismatch")
        trusted = bytes.fromhex(self.contract["accepted_package"]["trusted_creator_public_keys"][0])
        try:
            _, payload = InventoryPackage.decode_and_verify(encoded, trusted)
        except InventoryError as error:
            raise GodRuntimeError(f"Inventory package rejected: {error}") from error
        validate_lock(payload["lock"], self.contract)
        self.state = "validated"
        self.previous = self.active
        self.active = {
            "schema_version": 1,
            "slot": "provisional",
            "source": "received-signed-inventory-package",
            "creation_id": payload["lock"]["creation"]["creation_id"],
            "creation_sha256": payload["lock"]["creation_sha256"],
            "inventory_package_sha256": transfer.expected_sha256,
            "component_count": len(payload["lock"]["components"]),
            "transfer_id": transfer.transfer_id,
            "counter": transfer.counter,
        }
        self.state = "provisional"
        return dict(self.active)

    def health(self, healthy: bool) -> dict[str, Any]:
        if self.state != "provisional" or self.staging is None or self.previous is None:
            raise GodRuntimeError("no provisional world awaits health check")
        transfer = self.staging
        if not healthy:
            self.active = self.previous
            self.previous = None
            self.staging = None
            self.state = "rolled-back"
            self.receipt = None
            return {"status": "ROLLED-BACK", "active_creation_sha256": self.active["creation_sha256"]}
        self.active["slot"] = "active"
        self.last_counter = transfer.counter
        self.receipt = {
            "status": "COMMITTED",
            "transfer_id": transfer.transfer_id,
            "counter": transfer.counter,
            "package_sha256": transfer.expected_sha256,
            "creation_sha256": self.active["creation_sha256"],
        }
        self.previous = None
        self.staging = None
        self.state = "committed"
        return dict(self.receipt)

    def abort(self) -> None:
        if self.state == "provisional" and self.previous is not None:
            self.active = self.previous
        self.previous = None
        self.staging = None
        self.receipt = None
        self.state = "active"


def transfer(runtime: GodRuntime, package: bytes, transfer_id: str, counter: int) -> dict[str, Any]:
    runtime.begin(transfer_id, counter, len(package), sha256(package))
    step = runtime.target["transport"]["frame_payload_bytes"]
    for offset in range(0, len(package), step):
        runtime.chunk(offset, package[offset:offset + step])
    runtime.commit()
    return runtime.health(True)
