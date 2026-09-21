#!/usr/bin/env python3
"""Verify one Runner Contract across native, hosted, and bridge envelopes."""

from __future__ import annotations

import copy
import platform
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from rabbit_runners import (
    RunnerError, build_artifact, communicate_bridge, make_report, resolve,
    run_artifact, runner_hash, target_hash, validate_target,
)


ROOT = Path(__file__).resolve().parent
CAP_ROOT = ROOT.parent / "capability-negotiation-v1"
sys.path.insert(0, str(CAP_ROOT))
import rabbit_capabilities as caps  # noqa: E402


class VerificationError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise VerificationError(message)


def rejected(label: str, action: Callable[[], object]) -> None:
    try:
        action()
    except RunnerError as error:
        print(f"PASS: rejected {label}: {error}")
        return
    raise VerificationError(f"invalid case accepted: {label}")


def execute(world: dict, target: dict) -> tuple[dict, bytes, dict, dict]:
    plan = resolve(world, target)
    artifact = build_artifact(world, target, plan)
    observed = run_artifact(artifact, world, target, plan)
    report = make_report(world, target, plan, artifact, observed)
    require(report["contract_passed"], f"{target['target_id']} contract failed")
    return plan, artifact, observed, report


def main() -> int:
    try:
        base = caps.load_json(CAP_ROOT / "world.json")
        patch = caps.load_json(CAP_ROOT / "patches" / "add-bang.json")
        patched = caps.apply_patch(base, patch)
        targets = {
            name: caps.load_json(ROOT / "targets" / filename)
            for name, filename in {
                "native": "native-qemu-rv32i.json",
                "hosted": "hosted-arm64.json",
                "bridge": "bridge-simulator.json",
            }.items()
        }
        for target in targets.values():
            validate_target(target)
            require(
                target["execution_envelope"] == target["runner_contract"]["envelope"],
                "target and runner envelopes differ",
            )
            require(
                target["runner_contract"]["recovery"]["persistent_writes"] is False,
                "runner permits persistent writes",
            )
        require(
            len({runner_hash(target) for target in targets.values()}) == 3,
            "runner contracts lack independent identities",
        )
        print("PASS: hosted, native, and bridge implement one strict Runner Contract")

        native_base = execute(base, targets["native"])
        native_patch = execute(patched, targets["native"])
        bridge_base = execute(base, targets["bridge"])
        bridge_patch = execute(patched, targets["bridge"])
        require(native_base[3]["observed"]["stdout_hex"] == "4849", "native base is not HI")
        require(native_patch[3]["observed"]["stdout_hex"] == "484921", "native patch is not HI!")
        require(bridge_base[3]["observed"]["stdout_hex"] == "4849", "bridge base is not HI")
        require(bridge_patch[3]["observed"]["stdout_hex"] == "484921", "bridge patch is not HI!")
        require(bridge_patch[3]["transcript"] is not None, "bridge transcript is missing")
        print("PASS: native QEMU and simulated bridge observed exactly HI and HI!")
        print(
            "PASS: bridge request, response, and complete transcript have independent hashes"
        )

        hosted_available = (
            platform.system() == "Darwin"
            and platform.machine().lower() in {"arm64", "aarch64"}
        )
        if hosted_available:
            hosted_base = execute(base, targets["hosted"])
            hosted_patch = execute(patched, targets["hosted"])
            require(hosted_base[3]["observed"]["stdout_hex"] == "4849", "hosted base is not HI")
            require(hosted_patch[3]["observed"]["stdout_hex"] == "484921", "hosted patch is not HI!")
            identities = {
                native_patch[3]["world_sha256"], hosted_patch[3]["world_sha256"],
                bridge_patch[3]["world_sha256"],
            }
            require(len(identities) == 1, "three envelopes disagree on world identity")
            print("PASS: hosted ARM64 observed exactly HI and HI!")
            print("PASS: all three envelopes preserve one semantic world and contract")
        else:
            print("SKIP: hosted envelope execution requires Apple Silicon")

        mislabeled = copy.deepcopy(targets["bridge"])
        mislabeled["runner_contract"]["envelope"] = "hosted"
        rejected("a mislabeled execution envelope", lambda: validate_target(mislabeled))

        hidden_write = copy.deepcopy(targets["bridge"])
        hidden_write["runner_contract"]["mutations"] = ["write-internal-disk"]
        rejected("an undocumented persistent mutation", lambda: validate_target(hidden_write))

        persistent = copy.deepcopy(targets["bridge"])
        persistent["runner_contract"]["recovery"]["persistent_writes"] = True
        rejected("a runner permitting persistent writes", lambda: validate_target(persistent))

        missing_recovery = copy.deepcopy(targets["bridge"])
        del missing_recovery["runner_contract"]["recovery"]
        rejected("a runner without recovery information", lambda: validate_target(missing_recovery))

        bad_protocol = copy.deepcopy(targets["bridge"])
        bad_protocol["runner_contract"]["protocol"]["version"] = 2
        rejected("a bridge protocol version mismatch", lambda: validate_target(bad_protocol))

        replayed = copy.deepcopy(bridge_base[2])
        rejected(
            "a base transcript replayed for the patched world",
            lambda: make_report(
                patched, targets["bridge"], bridge_patch[0], bridge_patch[1], replayed
            ),
        )

        tampered = copy.deepcopy(bridge_patch[2])
        tampered["runner_binding"]["transcript"]["transcript_sha256"] = "0" * 64
        rejected(
            "a tampered bridge transcript hash",
            lambda: make_report(
                patched, targets["bridge"], bridge_patch[0], bridge_patch[1], tampered
            ),
        )

        rejected(
            "a bridge timeout",
            lambda: communicate_bridge(
                [sys.executable, "-c", "import time; time.sleep(1)"], b"", 0.01
            ),
        )

        stale_runner = copy.deepcopy(targets["bridge"])
        stale_runner["runner_contract"]["timeouts"]["execution_seconds"] = 4
        validate_target(stale_runner)
        rejected(
            "evidence bound to a stale runner revision",
            lambda: make_report(
                patched, stale_runner, resolve(patched, stale_runner),
                bridge_patch[1], bridge_patch[2]
            ),
        )

        with tempfile.TemporaryDirectory(prefix="rabbit-runner-verify-") as temp_dir:
            for name in ("native", "bridge") + (("hosted",) if hosted_available else ()):
                target_file = {
                    "native": "native-qemu-rv32i.json",
                    "hosted": "hosted-arm64.json",
                    "bridge": "bridge-simulator.json",
                }[name]
                completed = subprocess.run(
                    [
                        sys.executable, str(ROOT / "rabbit_runners.py"),
                        str(CAP_ROOT / "world.json"), "--target",
                        str(ROOT / "targets" / target_file), "--patch",
                        str(CAP_ROOT / "patches" / "add-bang.json"),
                    ],
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, check=False, timeout=40,
                )
                require(completed.returncode == 0, f"{name} runner CLI failed")
                require(completed.stderr == b"", f"{name} runner CLI wrote stderr")
            print("PASS: documented three-envelope CLI workflows are intact")
    except (OSError, ValueError, VerificationError) as error:
        print(f"FAIL: {error}")
        return 1

    if hosted_available:
        print("PASS: complete U5 three-envelope Runner Contract")
    else:
        print("PASS: U5 implementation contract; Apple Silicon execution pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
