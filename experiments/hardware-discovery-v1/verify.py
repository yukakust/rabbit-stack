#!/usr/bin/env python3
"""Verify read-only inventory matching and non-executable USB planning."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from rabbit_hardware import (
    HardwareError, canonical_hash, load_json, make_plan, match_inventory,
    validate_inventory, validate_plan, validate_target,
)


ROOT = Path(__file__).resolve().parent


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rejected(label: str, action: Callable[[], object]) -> None:
    try:
        action()
    except HardwareError as error:
        print(f"PASS: rejected {label}: {error}")
        return
    raise RuntimeError(f"invalid case accepted: {label}")


def main() -> int:
    try:
        supported = load_json(ROOT / "inventories" / "simulated-supported-pc.json")
        unsupported = load_json(ROOT / "inventories" / "simulated-unsupported-pc.json")
        observed = load_json(ROOT / "inventories" / "dell-optiplex-3060-observed.json")
        target = load_json(ROOT / "targets" / "x86-64-uefi-usb.json")
        validate_inventory(supported)
        validate_inventory(unsupported)
        validate_inventory(observed)
        validate_target(target)

        good_match = match_inventory(supported, target)
        require(good_match["status"] == "SUPPORTED-FOR-PLANNING", "supported fixture did not match")
        require(good_match["physical_execution_verified"] is False, "planning claimed physical proof")
        bad_match = match_inventory(unsupported, target)
        require(bad_match["status"] == "UNSUPPORTED", "unsupported fixture matched")
        require("firmware-interface-mismatch" in bad_match["reasons"], "missing firmware rejection")
        require("suitable-removable-media-missing" in bad_match["reasons"], "missing removable-media rejection")
        print("PASS: matcher distinguishes planning-compatible and unsupported inventories")

        observed_match = match_inventory(observed, target)
        require(observed_match["status"] == "UNSUPPORTED", "observed Dell unexpectedly matched")
        require(
            observed_match["reasons"] == [
                "secure-boot-state-unsupported",
                "suitable-removable-media-missing",
            ],
            "observed Dell rejection reasons changed",
        )
        require(observed["storage"] == [], "observed inventory invented a storage device")
        require(observed["evidence"]["writes_performed"] == [], "observed discovery performed writes")
        print("PASS: real Dell inventory is read-only and rejected for exact observed blockers")
        print(f"PASS: observed-inventory={canonical_hash(observed)}")

        plan = make_plan(supported, target, "usb-demo")
        validate_plan(plan, supported, target, "usb-demo")
        require(plan["status"] == "PROPOSED", "plan is not proposed")
        require(plan["installation_authorized"] is False and plan["executable"] is False, "plan authorizes installation")
        require(plan["writes_performed"] == [], "planning performed writes")
        require(plan["selected_device"]["kind"] == "removable", "plan did not select removable media")
        require(plan["forbidden_device_ids"] == ["internal-demo"], "internal disk is not forbidden")
        require(plan["firmware_changes"] == [] and plan["security_changes"] == [], "plan mutates firmware/security")
        print("PASS: canonical plan names only removable media and authorizes no execution")
        print(f"PASS: inventory={canonical_hash(supported)}, target={canonical_hash(target)}, plan={canonical_hash(plan)}")

        internal = copy.deepcopy(plan)
        internal["selected_device"] = {"device_id": "internal-demo", "kind": "internal", "capacity_mib": 238000}
        internal["planned_writes"][0]["device_id"] = "internal-demo"
        rejected("a plan targeting the internal disk", lambda: validate_plan(internal, supported, target, "usb-demo"))

        firmware_write = copy.deepcopy(plan)
        firmware_write["firmware_changes"] = ["disable-secure-boot"]
        rejected("a firmware or Secure Boot change", lambda: validate_plan(firmware_write, supported, target, "usb-demo"))

        no_recovery = copy.deepcopy(plan)
        del no_recovery["recovery"]
        rejected("a plan without recovery", lambda: validate_plan(no_recovery, supported, target, "usb-demo"))

        executed = copy.deepcopy(plan)
        executed["writes_performed"] = ["usb-demo"]
        rejected("discovery combined with installation", lambda: validate_plan(executed, supported, target, "usb-demo"))

        stale_inventory = copy.deepcopy(supported)
        stale_inventory["memory_mib"] = 8192
        validate_inventory(stale_inventory)
        rejected("a plan bound to a stale inventory", lambda: validate_plan(plan, stale_inventory, target, "usb-demo"))

        discovery_write = copy.deepcopy(supported)
        discovery_write["evidence"]["writes_performed"] = ["probe-marker"]
        rejected("inventory discovery that performed a write", lambda: validate_inventory(discovery_write))

        secure_boot = copy.deepcopy(supported)
        secure_boot["firmware"]["secure_boot"] = "enabled"
        validate_inventory(secure_boot)
        require(match_inventory(secure_boot, target)["status"] == "UNSUPPORTED", "enabled Secure Boot was accepted")
        print("PASS: enabled Secure Boot is unsupported rather than silently changed")

        with tempfile.TemporaryDirectory(prefix="rabbit-hardware-verify-") as temp_dir:
            plan_path = Path(temp_dir) / "plan.json"
            good_cli = subprocess.run(
                [sys.executable, str(ROOT / "rabbit_hardware.py"), str(ROOT / "inventories" / "simulated-supported-pc.json"), "--target", str(ROOT / "targets" / "x86-64-uefi-usb.json"), "--device", "usb-demo", "--plan", str(plan_path)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=5,
            )
            require(good_cli.returncode == 0 and good_cli.stderr == b"", "supported CLI failed")
            require(json.loads(plan_path.read_text()) == plan, "CLI plan differs")
            bad_cli = subprocess.run(
                [sys.executable, str(ROOT / "rabbit_hardware.py"), str(ROOT / "inventories" / "simulated-unsupported-pc.json"), "--target", str(ROOT / "targets" / "x86-64-uefi-usb.json")],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=5,
            )
            require(bad_cli.returncode == 2, "unsupported CLI did not return 2")
            print("PASS: documented supported and unsupported CLI workflows are intact")
    except (OSError, ValueError, RuntimeError) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: U6 real hardware discovery and planning contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
