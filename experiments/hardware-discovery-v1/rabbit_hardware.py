#!/usr/bin/env python3
"""Read-only hardware inventory matching and non-executable installation planning."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


IDENTIFIER = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")
INVENTORY_KEYS = {
    "schema_version", "inventory_id", "source", "discovery_mode", "architecture",
    "memory_mib", "firmware", "observable_io", "storage", "controllers",
    "device_ids", "evidence",
}
TARGET_KEYS = {"schema_version", "target_id", "requirements", "installation_policy"}


class HardwareError(ValueError):
    pass


def exact(value: dict[str, Any], keys: set[str], context: str) -> None:
    missing, unknown = keys - set(value), set(value) - keys
    if missing or unknown:
        raise HardwareError(f"{context} fields mismatch: missing={sorted(missing)!r}, unknown={sorted(unknown)!r}")


def identifier(value: Any, context: str) -> str:
    if not isinstance(value, str) or IDENTIFIER.fullmatch(value) is None:
        raise HardwareError(f"{context} is not a safe identifier")
    return value


def integer(value: Any, context: str) -> int:
    if type(value) is not int or value < 0:
        raise HardwareError(f"{context} must be a non-negative integer")
    return value


def string_list(value: Any, context: str, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty) or not all(isinstance(x, str) and x for x in value):
        raise HardwareError(f"{context} must be a string list")
    if len(set(value)) != len(value):
        raise HardwareError(f"{context} contains duplicates")
    return value


def canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def validate_inventory(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise HardwareError("inventory must be an object")
    exact(value, INVENTORY_KEYS, "inventory")
    if value["schema_version"] != 1:
        raise HardwareError("inventory.schema_version must be 1")
    identifier(value["inventory_id"], "inventory.inventory_id")
    if value["source"] not in {"simulated-fixture", "manual-read-only", "probe-read-only"}:
        raise HardwareError("inventory.source is unsupported")
    if value["discovery_mode"] != "read-only":
        raise HardwareError("hardware discovery must be read-only")
    if value["architecture"] not in {"x86-64", "arm64", "riscv32"}:
        raise HardwareError("inventory architecture is unsupported")
    integer(value["memory_mib"], "inventory.memory_mib")
    firmware = value["firmware"]
    if not isinstance(firmware, dict):
        raise HardwareError("inventory.firmware must be an object")
    exact(firmware, {"interface", "secure_boot", "removable_boot", "boot_menu"}, "inventory.firmware")
    if firmware["interface"] not in {"uefi", "bios", "unknown"}:
        raise HardwareError("unknown firmware interface")
    if firmware["secure_boot"] not in {"enabled", "disabled", "not-applicable", "unknown"}:
        raise HardwareError("unknown secure_boot state")
    if type(firmware["removable_boot"]) is not bool or type(firmware["boot_menu"]) is not bool:
        raise HardwareError("firmware boot flags must be boolean")
    io = value["observable_io"]
    if not isinstance(io, dict):
        raise HardwareError("observable_io must be an object")
    exact(io, {"firmware_display", "usb_keyboard", "display_connectors"}, "observable_io")
    if type(io["firmware_display"]) is not bool or type(io["usb_keyboard"]) is not bool:
        raise HardwareError("observable I/O flags must be boolean")
    string_list(io["display_connectors"], "display_connectors")
    storage = value["storage"]
    if not isinstance(storage, list):
        raise HardwareError("inventory.storage must be a list")
    ids: set[str] = set()
    for index, device in enumerate(storage):
        if not isinstance(device, dict):
            raise HardwareError("storage entry must be an object")
        exact(device, {"device_id", "kind", "capacity_mib"}, f"storage[{index}]")
        device_id = identifier(device["device_id"], f"storage[{index}].device_id")
        if device_id in ids:
            raise HardwareError("duplicate storage device id")
        ids.add(device_id)
        if device["kind"] not in {"internal", "removable"}:
            raise HardwareError("storage kind must be internal or removable")
        integer(device["capacity_mib"], "storage capacity")
    string_list(value["controllers"], "inventory.controllers")
    string_list(value["device_ids"], "inventory.device_ids")
    evidence = value["evidence"]
    if not isinstance(evidence, dict):
        raise HardwareError("inventory.evidence must be an object")
    exact(evidence, {"collector", "commands", "writes_performed"}, "inventory.evidence")
    if not isinstance(evidence["collector"], str) or not evidence["collector"]:
        raise HardwareError("inventory evidence collector is required")
    if not isinstance(evidence["commands"], list):
        raise HardwareError("inventory evidence commands must be a list")
    if evidence["writes_performed"] != []:
        raise HardwareError("read-only discovery evidence reports writes")
    return value


def validate_target(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise HardwareError("target must be an object")
    exact(value, TARGET_KEYS, "target")
    if value["schema_version"] != 1:
        raise HardwareError("target.schema_version must be 1")
    identifier(value["target_id"], "target.target_id")
    requirements = value["requirements"]
    if not isinstance(requirements, dict):
        raise HardwareError("target.requirements must be an object")
    required = {
        "architecture": "x86-64", "firmware_interface": "uefi",
        "secure_boot": "disabled", "removable_boot": True, "boot_menu": True,
        "minimum_memory_mib": 1024, "firmware_display": True, "usb_keyboard": True,
        "required_controllers": ["usb-xhci"], "minimum_removable_capacity_mib": 64,
    }
    exact(requirements, set(required), "target.requirements")
    if requirements != required:
        raise HardwareError("target requirements differ from reviewed x86-64 UEFI policy")
    policy = value["installation_policy"]
    expected_policy = {
        "allowed_target_kind": "removable", "internal_storage_writes": False,
        "firmware_writes": False, "secure_boot_changes": False,
        "recovery_method": "power-off-and-remove-usb",
    }
    if not isinstance(policy, dict):
        raise HardwareError("installation_policy must be an object")
    exact(policy, set(expected_policy), "installation_policy")
    if policy != expected_policy:
        raise HardwareError("installation policy permits unreviewed effects")
    return value


def match_inventory(inventory: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    validate_inventory(inventory)
    validate_target(target)
    req, reasons = target["requirements"], []
    checks = [
        (inventory["architecture"] == req["architecture"], "architecture-mismatch"),
        (inventory["firmware"]["interface"] == req["firmware_interface"], "firmware-interface-mismatch"),
        (inventory["firmware"]["secure_boot"] == req["secure_boot"], "secure-boot-state-unsupported"),
        (inventory["firmware"]["removable_boot"] is True, "removable-boot-unavailable"),
        (inventory["firmware"]["boot_menu"] is True, "boot-menu-unavailable"),
        (inventory["memory_mib"] >= req["minimum_memory_mib"], "insufficient-memory"),
        (inventory["observable_io"]["firmware_display"] is True, "firmware-display-unavailable"),
        (inventory["observable_io"]["usb_keyboard"] is True, "usb-keyboard-unavailable"),
        (set(req["required_controllers"]) <= set(inventory["controllers"]), "required-controller-missing"),
        (any(x["kind"] == "removable" and x["capacity_mib"] >= req["minimum_removable_capacity_mib"] for x in inventory["storage"]), "suitable-removable-media-missing"),
    ]
    reasons.extend(reason for passed, reason in checks if not passed)
    return {
        "schema_version": 1,
        "status": "SUPPORTED-FOR-PLANNING" if not reasons else "UNSUPPORTED",
        "inventory_id": inventory["inventory_id"],
        "inventory_sha256": canonical_hash(inventory),
        "target_id": target["target_id"],
        "target_sha256": canonical_hash(target),
        "reasons": reasons,
        "physical_execution_verified": False,
    }


def make_plan(inventory: dict[str, Any], target: dict[str, Any], device_id: str) -> dict[str, Any]:
    match = match_inventory(inventory, target)
    if match["status"] != "SUPPORTED-FOR-PLANNING":
        raise HardwareError(f"inventory is unsupported: {match['reasons']!r}")
    devices = {x["device_id"]: x for x in inventory["storage"]}
    device = devices.get(device_id)
    if device is None:
        raise HardwareError("selected installation device is absent from inventory")
    if device["kind"] != "removable":
        raise HardwareError("installation target must be removable media")
    if device["capacity_mib"] < target["requirements"]["minimum_removable_capacity_mib"]:
        raise HardwareError("selected removable media is too small")
    internal_ids = sorted(x["device_id"] for x in inventory["storage"] if x["kind"] == "internal")
    return {
        "schema_version": 1,
        "status": "PROPOSED",
        "installation_authorized": False,
        "executable": False,
        "inventory_id": inventory["inventory_id"],
        "inventory_sha256": canonical_hash(inventory),
        "target_id": target["target_id"],
        "target_sha256": canonical_hash(target),
        "selected_device": {"device_id": device_id, "kind": "removable", "capacity_mib": device["capacity_mib"]},
        "artifact": {"name": "rabbit-x86-64-uefi-v0.img", "status": "UNBUILT", "maximum_size_bytes": 67108864},
        "planned_writes": [{"action": "write-image", "device_id": device_id, "offset_bytes": 0, "maximum_length_bytes": 67108864}],
        "forbidden_device_ids": internal_ids,
        "firmware_changes": [],
        "security_changes": [],
        "expected_observations": ["UEFI removable entry appears", "Rabbit displays HI on firmware display"],
        "verification": ["verify artifact hash before write", "verify selected removable device id again", "boot once from firmware boot menu"],
        "risks": ["selecting the wrong storage device would destroy data", "prototype may not boot on candidate hardware"],
        "recovery": {"method": "power-off-and-remove-usb", "internal_disk_restore_required": False},
        "writes_performed": [],
    }


def validate_plan(plan: dict[str, Any], inventory: dict[str, Any], target: dict[str, Any], device_id: str) -> dict[str, Any]:
    expected = make_plan(inventory, target, device_id)
    if plan != expected:
        raise HardwareError("installation plan is stale or contains undeclared effects")
    return plan


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(), object_pairs_hook=lambda pairs: _pairs(pairs), parse_constant=lambda x: (_ for _ in ()).throw(HardwareError(f"non-standard number {x}")))
    except (OSError, json.JSONDecodeError) as error:
        raise HardwareError(f"could not load {path}: {error}") from error


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise HardwareError(f"duplicate JSON field {key!r}")
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Match read-only hardware inventory and propose a USB plan")
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--device")
    parser.add_argument("--plan", type=Path)
    args = parser.parse_args()
    try:
        inventory, target = load_json(args.inventory), load_json(args.target)
        match = match_inventory(inventory, target)
        print(f"MATCH: {match['status']}")
        for reason in match["reasons"]:
            print(f"REASON: {reason}")
        if match["status"] == "SUPPORTED-FOR-PLANNING" and args.device:
            plan = make_plan(inventory, target, args.device)
            if args.plan:
                args.plan.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
            print(f"PLAN: {plan['status']}; installation_authorized=false; writes_performed=0")
        return 0 if match["status"] == "SUPPORTED-FOR-PLANNING" else 2
    except HardwareError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
