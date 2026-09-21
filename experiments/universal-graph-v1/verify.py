#!/usr/bin/env python3
"""Verify the complete Universal Rabbit graph v1 contract."""

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

from rabbit_graph import (
    GraphError,
    apply_patch,
    build_artifact,
    load_json,
    make_report,
    run_artifact,
    target_hash,
    validate_patch,
    validate_target,
    validate_world,
    world_hash,
)


ROOT = Path(__file__).resolve().parent


class VerificationError(RuntimeError):
    """A graph v1 invariant failed."""


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
        require("target" not in base, "portable graph contains a target field")
        require(patch["base_hash"] == world_hash(base), "patch base hash is stale")

        base_snapshot = copy.deepcopy(base)
        rv_snapshot = copy.deepcopy(rv_target)
        arm_snapshot = copy.deepcopy(arm_target)
        effective = apply_patch(base, patch)
        require(base == base_snapshot, "applying graph patch mutated the base")
        require(
            [item["id"] for item in effective["modules"]]
            == ["start", "letter-h", "letter-i", "exit", "punctuation"],
            "patch did not add exactly the punctuation module",
        )
        require(
            effective["contract"]["stdout"] == "HI!",
            "patched graph contract is not HI!",
        )
        print(
            "PASS: immutable patch adds punctuation and rewires HI to HI! "
            "without editing existing modules"
        )

        rv_base = build_artifact(base, rv_target)
        rv_patched = build_artifact(effective, rv_target)
        arm_base = build_artifact(base, arm_target)
        arm_patched = build_artifact(effective, arm_target)
        require(len(rv_base) == 40, "base RV32I graph artifact is not 40 bytes")
        require(len(rv_patched) == 48, "patched RV32I graph artifact is not 48 bytes")
        require(b".byte 0x48, 0x49\n" in arm_base, "ARM64 base data is not HI")
        require(
            b".byte 0x48, 0x49, 0x21\n" in arm_patched,
            "ARM64 patched data is not HI!",
        )
        require(
            build_artifact(copy.deepcopy(base), copy.deepcopy(rv_target)) == rv_base,
            "RV32I graph build is not deterministic",
        )
        require(
            build_artifact(copy.deepcopy(effective), copy.deepcopy(arm_target))
            == arm_patched,
            "ARM64 graph build is not deterministic",
        )
        require(rv_target == rv_snapshot and arm_target == arm_snapshot, "build mutated a target")
        print(
            "PASS: one graph lowers deterministically to 40/48-byte RV32I and "
            "distinct hosted ARM64 artifacts"
        )
        print(
            f"PASS: world={world_hash(base)}, rv32i={target_hash(rv_target)}, "
            f"arm64={target_hash(arm_target)}"
        )

        rv_base_observed = run_artifact(rv_base, rv_target)
        rv_base_report = make_report(
            base, base, None, rv_target, rv_base, rv_base_observed
        )
        require(rv_base_report["contract_passed"], "RV32I did not observe HI / exit 0")
        rv_patch_observed = run_artifact(rv_patched, rv_target)
        rv_patch_report = make_report(
            base, effective, patch, rv_target, rv_patched, rv_patch_observed
        )
        require(rv_patch_report["contract_passed"], "RV32I did not observe HI! / exit 0")
        print("PASS: QEMU RV32I observed exactly HI and patched HI! with exit 0")

        rollback = build_artifact(base, rv_target)
        require(base == base_snapshot, "base changed before rollback")
        require(rollback == rv_base, "removing patch did not restore RV32I artifact")
        rollback_observed = run_artifact(rollback, rv_target)
        rollback_report = make_report(
            base, base, None, rv_target, rollback, rollback_observed
        )
        require(rollback_report["contract_passed"], "rollback did not restore HI")
        print("PASS: removing the graph patch restores exact base graph, artifact, and HI")

        hosted_available = (
            platform.system() == "Darwin"
            and platform.machine().lower() in {"arm64", "aarch64"}
        )
        if hosted_available:
            arm_base_observed = run_artifact(arm_base, arm_target)
            arm_base_report = make_report(
                base, base, None, arm_target, arm_base, arm_base_observed
            )
            arm_patch_observed = run_artifact(arm_patched, arm_target)
            arm_patch_report = make_report(
                base, effective, patch, arm_target, arm_patched, arm_patch_observed
            )
            require(
                arm_base_report["contract_passed"]
                and arm_patch_report["contract_passed"],
                "hosted ARM64 graph behavior failed",
            )
            require(
                arm_patch_report["effective_world_sha256"]
                == rv_patch_report["effective_world_sha256"],
                "targets disagree about effective graph identity",
            )
            print("PASS: hosted ARM64 observed exactly HI and patched HI! with exit 0")
            print("PASS: both targets share graph identity and observable meaning")
        else:
            print(
                "SKIP: hosted ARM64 graph execution requires Apple Silicon; "
                "its artifact and Target Pack were verified"
            )

        dangling = copy.deepcopy(base)
        dangling["connections"][0]["to"]["module"] = "missing-module"
        expect_rejected("a dangling connection", lambda: validate_world(dangling))

        unknown_port = copy.deepcopy(base)
        unknown_port["connections"][0]["from"]["port"] = "magic"
        expect_rejected("an unknown typed port", lambda: validate_world(unknown_port))

        incompatible = copy.deepcopy(base)
        incompatible["connections"][0]["from"] = {
            "module": "letter-h",
            "port": "value",
        }
        expect_rejected(
            "a byte port connected to an event port",
            lambda: validate_world(incompatible),
        )

        cycle = copy.deepcopy(base)
        cycle["connections"] = [
            {
                "from": {"module": "start", "port": "started"},
                "to": {"module": "exit", "port": "trigger"},
            },
            {
                "from": {"module": "letter-h", "port": "done"},
                "to": {"module": "letter-i", "port": "trigger"},
            },
            {
                "from": {"module": "letter-i", "port": "done"},
                "to": {"module": "letter-h", "port": "trigger"},
            },
        ]
        expect_rejected("an event cycle", lambda: validate_world(cycle))

        no_authority = copy.deepcopy(base)
        no_authority["capabilities"].remove("console.write")
        expect_rejected(
            "a console graph without console.write authority",
            lambda: validate_world(no_authority),
        )

        module_overflow = copy.deepcopy(base)
        module_overflow["resources"]["max_modules"] = 3
        expect_rejected("a module budget overflow", lambda: validate_world(module_overflow))

        output_overflow = copy.deepcopy(base)
        output_overflow["resources"]["max_output_bytes"] = 1
        expect_rejected("an output budget overflow", lambda: validate_world(output_overflow))

        tight_base = copy.deepcopy(base)
        tight_base["resources"]["max_modules"] = 4
        validate_world(tight_base)
        over_budget_patch = copy.deepcopy(patch)
        over_budget_patch["base_hash"] = world_hash(tight_base)
        expect_rejected(
            "a patch that exceeds the base graph module budget",
            lambda: validate_patch(over_budget_patch, tight_base),
        )

        stale_base = copy.deepcopy(base)
        stale_base["modules"][1]["value"] = ord("J")
        stale_base["contract"]["stdout"] = "JI"
        validate_world(stale_base)
        expect_rejected(
            "a patch applied to a different graph revision",
            lambda: validate_patch(patch, stale_base),
        )

        runtime_edit = copy.deepcopy(patch)
        runtime_edit["backend_edit"] = "special-case-punctuation"
        expect_rejected(
            "a patch requesting a backend edit",
            lambda: validate_patch(runtime_edit, base),
        )

        expect_rejected(
            "QEMU evidence reused for hosted ARM64",
            lambda: make_report(base, base, None, arm_target, arm_base, rv_base_observed),
        )

        stale_arm = copy.deepcopy(arm_target)
        stale_arm["runner"]["timeout_seconds"] = 4
        validate_target(stale_arm)
        forged_arm_observed = copy.deepcopy(rv_base_observed)
        forged_arm_observed["binding"] = {
            "target_sha256": target_hash(arm_target),
            "artifact_sha256": hashlib.sha256(arm_base).hexdigest(),
        }
        expect_rejected(
            "evidence from a stale graph Target Pack",
            lambda: make_report(
                base, base, None, stale_arm, arm_base, forged_arm_observed
            ),
        )

        with tempfile.TemporaryDirectory(prefix="rabbit-graph-verify-") as temp_dir:
            temp_root = Path(temp_dir)
            duplicate = temp_root / "duplicate.json"
            duplicate.write_text('{"schema_version":1,"schema_version":1}\n')
            expect_rejected("duplicate JSON fields", lambda: load_json(duplicate))
            nonstandard = temp_root / "nan.json"
            nonstandard.write_text('{"schema_version":NaN}\n')
            expect_rejected("non-standard JSON numbers", lambda: load_json(nonstandard))

            report_path = temp_root / "report.json"
            cli = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "rabbit_graph.py"),
                    str(ROOT / "world.json"),
                    "--target",
                    str(rv_path),
                    "--patch",
                    str(ROOT / "patches" / "add-bang.json"),
                    "--report",
                    str(report_path),
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=10,
            )
            require(cli.returncode == 0, "RV32I graph CLI failed")
            require(cli.stderr == b"", "RV32I graph CLI wrote stderr")
            require(
                json.loads(report_path.read_text()) == rv_patch_report,
                "RV32I graph CLI report differs from direct verifier",
            )
            if hosted_available:
                arm_cli = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "rabbit_graph.py"),
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
                require(arm_cli.returncode == 0, "ARM64 graph CLI failed")
                require(arm_cli.stderr == b"", "ARM64 graph CLI wrote stderr")
            print("PASS: documented graph CLI workflows are intact")
    except (OSError, ValueError, VerificationError) as error:
        print(f"FAIL: {error}")
        return 1

    if hosted_available:
        print("PASS: complete U3 universal module graph contract")
    else:
        print("PASS: U3 implementation contract; Apple Silicon execution pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
