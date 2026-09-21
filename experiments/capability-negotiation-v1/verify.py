#!/usr/bin/env python3
"""Verify semantic capability negotiation and plan-bound execution."""

from __future__ import annotations

import copy
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from rabbit_capabilities import (
    GraphError,
    apply_patch,
    build_artifact,
    load_json,
    make_report,
    plan_hash,
    resolve_capabilities,
    run_artifact,
    target_hash,
    validate_patch,
    validate_plan,
    validate_target,
    validate_world,
    world_hash,
)


ROOT = Path(__file__).resolve().parent


class VerificationError(RuntimeError):
    """A U4 capability-negotiation invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def expect_rejected(label: str, action: Callable[[], object]) -> None:
    try:
        action()
    except GraphError as error:
        print(f"PASS: rejected {label}: {error}")
        return
    raise VerificationError(f"invalid case was accepted: {label}")


def request(world: dict, capability: str) -> dict:
    return next(
        item for item in world["capabilities"] if item["capability"] == capability
    )


def main() -> int:
    try:
        base = load_json(ROOT / "world.json")
        patch = load_json(ROOT / "patches" / "add-bang.json")
        rv_path = ROOT / "targets" / "qemu-rv32i.json"
        arm_path = ROOT / "targets" / "hosted-arm64.json"
        rv_target = load_json(rv_path)
        arm_target = load_json(arm_path)
        validate_world(base)
        validate_patch(patch, base)
        validate_target(rv_target)
        validate_target(arm_target)
        require(
            all(
                name not in json.dumps(base)
                for name in (
                    "qemu-virt-uart",
                    "darwin-posix-write",
                    "qemu-sifive-test",
                    "darwin-main-return",
                )
            ),
            "portable world contains a target driver name",
        )
        require(patch["base_hash"] == world_hash(base), "patch base hash is stale")

        effective = apply_patch(base, patch)
        rv_base_plan = resolve_capabilities(base, rv_target)
        arm_base_plan = resolve_capabilities(base, arm_target)
        rv_plan = resolve_capabilities(effective, rv_target)
        arm_plan = resolve_capabilities(effective, arm_target)
        for plan in (rv_base_plan, arm_base_plan, rv_plan, arm_plan):
            require(
                plan["omitted_optional"]
                == [
                    {
                        "capability": "light.emit",
                        "version": 1,
                        "reason": "not-offered",
                    }
                ],
                "optional light.emit was not explicitly reported as unavailable",
            )
        require(
            rv_plan["bindings"][0]["driver"] == "qemu-virt-uart",
            "QEMU display.text did not bind to its UART",
        )
        require(
            arm_plan["bindings"][0]["driver"] == "darwin-posix-write",
            "Darwin display.text did not bind to POSIX stdout",
        )
        require(
            rv_plan["world_sha256"] == arm_plan["world_sha256"],
            "targets resolved different semantic world identities",
        )
        require(
            plan_hash(rv_plan, effective, rv_target)
            != plan_hash(arm_plan, effective, arm_target),
            "different bindings unexpectedly have the same plan identity",
        )
        print(
            "PASS: one semantic display.text request resolves to QEMU UART and "
            "Darwin stdout with distinct canonical plans"
        )
        print("PASS: optional light.emit is explicitly omitted as not-offered")

        rv_base_artifact = build_artifact(base, rv_target, rv_base_plan)
        rv_artifact = build_artifact(effective, rv_target, rv_plan)
        arm_base_artifact = build_artifact(base, arm_target, arm_base_plan)
        arm_artifact = build_artifact(effective, arm_target, arm_plan)
        require(len(rv_base_artifact) == 40, "RV32I base artifact is not 40 bytes")
        require(len(rv_artifact) == 48, "RV32I patched artifact is not 48 bytes")
        require(
            b".byte 0x48, 0x49, 0x21\n" in arm_artifact,
            "ARM64 negotiated artifact is not HI!",
        )
        print("PASS: negotiated plans lower deterministically to existing graph backends")

        rv_base_observed = run_artifact(
            rv_base_artifact, base, rv_target, rv_base_plan
        )
        rv_base_report = make_report(
            base,
            base,
            None,
            rv_target,
            rv_base_plan,
            rv_base_artifact,
            rv_base_observed,
        )
        require(rv_base_report["contract_passed"], "QEMU did not observe HI")
        rv_observed = run_artifact(rv_artifact, effective, rv_target, rv_plan)
        rv_report = make_report(
            base,
            effective,
            patch,
            rv_target,
            rv_plan,
            rv_artifact,
            rv_observed,
        )
        require(rv_report["contract_passed"], "QEMU did not observe HI!")
        require(
            rv_report["evidence_binding"]["plan_sha256"]
            == plan_hash(rv_plan, effective, rv_target),
            "execution evidence does not bind the deployment plan",
        )
        print("PASS: QEMU plan observed exactly HI and patched HI! with exit 0")

        rollback_plan = resolve_capabilities(base, rv_target)
        rollback_artifact = build_artifact(base, rv_target, rollback_plan)
        require(rollback_plan == rv_base_plan, "rollback plan differs from base plan")
        require(
            rollback_artifact == rv_base_artifact,
            "rollback artifact differs from base artifact",
        )
        print("PASS: removing the patch restores exact world, plan, and artifact")

        hosted_available = (
            platform.system() == "Darwin"
            and platform.machine().lower() in {"arm64", "aarch64"}
        )
        if hosted_available:
            arm_base_observed = run_artifact(
                arm_base_artifact, base, arm_target, arm_base_plan
            )
            arm_base_report = make_report(
                base,
                base,
                None,
                arm_target,
                arm_base_plan,
                arm_base_artifact,
                arm_base_observed,
            )
            arm_observed = run_artifact(
                arm_artifact, effective, arm_target, arm_plan
            )
            arm_report = make_report(
                base,
                effective,
                patch,
                arm_target,
                arm_plan,
                arm_artifact,
                arm_observed,
            )
            require(
                arm_base_report["contract_passed"] and arm_report["contract_passed"],
                "ARM64 negotiated behavior failed",
            )
            require(
                arm_report["effective_world_sha256"]
                == rv_report["effective_world_sha256"],
                "targets disagree on semantic world identity",
            )
            print("PASS: hosted ARM64 plan observed exactly HI and patched HI! with exit 0")
            print("PASS: different drivers preserve one semantic world and contract")
        else:
            print(
                "SKIP: hosted ARM64 negotiated execution requires Apple Silicon; "
                "its plan and artifact were verified"
            )

        required_light = copy.deepcopy(base)
        request(required_light, "light.emit")["required"] = True
        validate_world(required_light)
        expect_rejected(
            "required light.emit on a target without a light",
            lambda: resolve_capabilities(required_light, rv_target),
        )

        incompatible_version = copy.deepcopy(base)
        request(incompatible_version, "display.text")["version"] = 2
        validate_world(incompatible_version)
        expect_rejected(
            "an incompatible required capability version",
            lambda: resolve_capabilities(incompatible_version, rv_target),
        )

        exceeds_limit = copy.deepcopy(base)
        request(exceeds_limit, "display.text")["constraints"]["max_bytes"] = 17
        validate_world(exceeds_limit)
        expect_rejected(
            "a requested display budget beyond the target offer",
            lambda: resolve_capabilities(exceeds_limit, rv_target),
        )

        hidden_driver = copy.deepcopy(rv_target)
        hidden_driver["capability_offers"][0]["driver"] = "secret-vendor-sdk"
        expect_rejected(
            "an unreviewed hidden target driver",
            lambda: validate_target(hidden_driver),
        )

        hidden_effect = copy.deepcopy(rv_target)
        hidden_effect["capability_offers"][0]["effects"].append("writes-host-disk")
        expect_rejected(
            "an undeclared authority effect",
            lambda: validate_target(hidden_effect),
        )

        stale_plan = copy.deepcopy(rv_plan)
        stale_plan["world_sha256"] = world_hash(base)
        expect_rejected(
            "a plan from a stale world revision",
            lambda: validate_plan(stale_plan, effective, rv_target),
        )

        expect_rejected(
            "a QEMU plan used with the Darwin target",
            lambda: build_artifact(effective, arm_target, rv_plan),
        )

        tampered_plan = copy.deepcopy(rv_plan)
        tampered_plan["bindings"][0]["driver"] = "darwin-posix-write"
        expect_rejected(
            "a deployment plan with a substituted driver",
            lambda: validate_plan(tampered_plan, effective, rv_target),
        )

        tampered_evidence = copy.deepcopy(rv_observed)
        tampered_evidence["binding"]["plan_sha256"] = "0" * 64
        expect_rejected(
            "execution evidence for a different plan",
            lambda: make_report(
                base,
                effective,
                patch,
                rv_target,
                rv_plan,
                rv_artifact,
                tampered_evidence,
            ),
        )

        stale_target = copy.deepcopy(arm_target)
        stale_target["runner"]["timeout_seconds"] = 4
        validate_target(stale_target)
        expect_rejected(
            "a plan used with a stale Target Pack revision",
            lambda: validate_plan(arm_plan, effective, stale_target),
        )

        with tempfile.TemporaryDirectory(prefix="rabbit-capabilities-verify-") as temp_dir:
            temp_root = Path(temp_dir)
            plan_path = temp_root / "plan.json"
            report_path = temp_root / "report.json"
            cli = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "rabbit_capabilities.py"),
                    str(ROOT / "world.json"),
                    "--target",
                    str(rv_path),
                    "--patch",
                    str(ROOT / "patches" / "add-bang.json"),
                    "--plan",
                    str(plan_path),
                    "--report",
                    str(report_path),
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=10,
            )
            require(cli.returncode == 0, "QEMU capability CLI failed")
            require(cli.stderr == b"", "QEMU capability CLI wrote stderr")
            require(
                json.loads(plan_path.read_text()) == rv_plan,
                "CLI deployment plan differs from resolver",
            )
            require(
                json.loads(report_path.read_text()) == rv_report,
                "CLI evidence report differs from verifier",
            )
            if hosted_available:
                arm_cli = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "rabbit_capabilities.py"),
                        str(ROOT / "world.json"),
                        "--target",
                        str(arm_path),
                        "--patch",
                        str(ROOT / "patches" / "add-bang.json"),
                    ],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=40,
                )
                require(arm_cli.returncode == 0, "ARM64 capability CLI failed")
                require(arm_cli.stderr == b"", "ARM64 capability CLI wrote stderr")
            print("PASS: documented capability CLI workflows are intact")
    except (OSError, ValueError, VerificationError) as error:
        print(f"FAIL: {error}")
        return 1

    if hosted_available:
        print("PASS: complete U4 capability negotiation contract")
    else:
        print("PASS: U4 implementation contract; Apple Silicon execution pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
