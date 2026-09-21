#!/usr/bin/env python3
"""Verify the complete contract of the first patchable Rabbit World."""

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

from rabbit_world import (
    WorldError,
    apply_patch,
    build_image,
    byte_diff,
    load_json,
    make_report,
    run_image,
    target_hash,
    validate_binding,
    validate_patch,
    validate_target,
    validate_world,
    world_hash,
)


ROOT = Path(__file__).resolve().parent
DAY_01_HEX = ROOT.parent / "day-01" / "hello.hex"


class VerificationError(RuntimeError):
    """The implementation failed one of the World v0 checks."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def expect_rejected(label: str, action: Callable[[], object]) -> None:
    try:
        action()
    except WorldError as error:
        print(f"PASS: rejected {label}: {error}")
        return
    raise VerificationError(f"invalid case was accepted: {label}")


def main() -> int:
    try:
        base = load_json(ROOT / "world.json")
        patch = load_json(ROOT / "patches" / "say-b.json")
        target_path = ROOT / "targets" / "qemu-rv32i.json"
        target = load_json(target_path)
        hosted_target_path = ROOT / "targets" / "hosted-arm64.json"
        hosted_target = load_json(hosted_target_path)
        validate_world(base)
        validate_binding(base, target)
        validate_binding(base, hosted_target)
        validate_patch(patch, base)
        require("target" not in base, "portable world still contains a target field")
        require(
            patch["base_hash"] == world_hash(base),
            "patch does not identify the exact base manifest",
        )

        day_01_image = bytes.fromhex(DAY_01_HEX.read_text(encoding="ascii"))
        target_snapshot = copy.deepcopy(target)
        base_image = build_image(base, target)
        require(len(base_image) == 32, "base image is not exactly 32 bytes")
        require(
            base_image == day_01_image,
            "base world does not lower to the reviewed Day 01 image",
        )
        require(
            build_image(copy.deepcopy(base), copy.deepcopy(target)) == base_image,
            "repeated base builds are not deterministic",
        )
        require(target == target_snapshot, "building an image mutated the Target Pack")
        print(
            "PASS: portable A world plus qemu-rv32i Target Pack lower to the "
            "reviewed 32-byte image "
            f"({hashlib.sha256(base_image).hexdigest()})"
        )
        print(f"PASS: Target Pack hash is {target_hash(target)}")

        base_snapshot = copy.deepcopy(base)
        patched = apply_patch(base, patch)
        patched_image = build_image(patched, target)
        require(base == base_snapshot, "applying a patch mutated the base world")
        require(
            byte_diff(base_image, patched_image)
            == [{"offset": 6, "before": 0x10, "after": 0x20}],
            "A -> B did not produce the predicted one-byte image diff",
        )
        require(
            build_image(copy.deepcopy(patched), copy.deepcopy(target)) == patched_image,
            "repeated patched builds are not deterministic",
        )
        print("PASS: say-b is an overlay with byte diff offset 6: 0x10 -> 0x20")

        hosted_base_image = build_image(base, hosted_target)
        hosted_patched_image = build_image(patched, hosted_target)
        require(
            build_image(copy.deepcopy(base), copy.deepcopy(hosted_target))
            == hosted_base_image,
            "repeated hosted ARM64 builds are not deterministic",
        )
        require(
            hosted_base_image != base_image,
            "different backends unexpectedly produced the same artifact",
        )
        require(
            b".byte 0x41" in hosted_base_image
            and b".byte 0x42" in hosted_patched_image,
            "hosted ARM64 artifacts do not carry the requested UART byte",
        )
        require(
            world_hash(base) == patch["base_hash"],
            "adding another backend changed portable world identity",
        )
        require(
            target_hash(hosted_target) != target_hash(target),
            "the two Target Packs do not have independent identities",
        )
        print(
            "PASS: the unchanged world lowers deterministically to distinct RV32I "
            "and hosted ARM64 artifacts"
        )
        print(f"PASS: hosted ARM64 Target Pack hash is {target_hash(hosted_target)}")

        base_observed = run_image(base_image, target)
        base_report = make_report(
            base, base, None, target, base_image, base_observed
        )
        require(base_report["contract_passed"], "QEMU did not observe A / exit 0")
        require(
            base_report["target"]["sha256"] == target_hash(target),
            "evidence report did not bind the exact Target Pack",
        )
        print("PASS: QEMU observed exactly A on stdout, empty stderr, and exit 0")

        patched_observed = run_image(patched_image, target)
        patched_report = make_report(
            base, patched, patch, target, patched_image, patched_observed
        )
        require(patched_report["contract_passed"], "QEMU did not observe B / exit 0")
        print("PASS: QEMU observed exactly B on stdout, empty stderr, and exit 0")

        hosted_available = (
            platform.system() == "Darwin"
            and platform.machine().lower() in {"arm64", "aarch64"}
        )
        if hosted_available:
            hosted_base_observed = run_image(hosted_base_image, hosted_target)
            hosted_base_report = make_report(
                base,
                base,
                None,
                hosted_target,
                hosted_base_image,
                hosted_base_observed,
            )
            require(
                hosted_base_report["contract_passed"],
                "hosted ARM64 did not observe A / exit 0",
            )
            hosted_patched_observed = run_image(
                hosted_patched_image, hosted_target
            )
            hosted_patched_report = make_report(
                base,
                patched,
                patch,
                hosted_target,
                hosted_patched_image,
                hosted_patched_observed,
            )
            require(
                hosted_patched_report["contract_passed"],
                "hosted ARM64 did not observe B / exit 0",
            )
            require(
                hosted_base_report["base_world_sha256"]
                == base_report["base_world_sha256"],
                "the two backends reported different portable world identities",
            )
            print(
                "PASS: hosted ARM64 observed exactly A and B with empty stderr "
                "and exit 0"
            )
            print(
                "PASS: RV32I and ARM64 share world identity while target and "
                "artifact identities differ"
            )
        else:
            print(
                "SKIP: hosted ARM64 execution requires an Apple Silicon Mac; "
                "its Target Pack and deterministic artifacts were verified"
            )

        rollback_image = build_image(base, target)
        require(base == base_snapshot, "base world changed before rollback")
        require(rollback_image == base_image, "rollback did not restore the base image")
        rollback_observed = run_image(rollback_image, target)
        rollback_report = make_report(
            base, base, None, target, rollback_image, rollback_observed
        )
        require(rollback_report["contract_passed"], "rolled-back world did not emit A")
        print("PASS: removing the overlay rolls back exactly to the A world")

        missing_capability = copy.deepcopy(base)
        missing_capability["capabilities"].remove("uart.write")
        expect_rejected(
            "a UART module without uart.write authority",
            lambda: validate_world(missing_capability),
        )

        coupled_world = copy.deepcopy(base)
        coupled_world["target"] = "qemu-rv32i"
        expect_rejected(
            "a portable world containing a machine-specific target field",
            lambda: validate_world(coupled_world),
        )

        unknown_module = copy.deepcopy(patch)
        unknown_module["changes"][0]["module"] = "unreviewed-device"
        expect_rejected(
            "a patch targeting an unknown module",
            lambda: validate_patch(unknown_module, base),
        )

        excessive_byte = copy.deepcopy(patch)
        excessive_byte["changes"][0]["set"]["value"] = 128
        expect_rejected(
            "a non-ASCII UART value",
            lambda: validate_patch(excessive_byte, base),
        )

        dishonest_contract = copy.deepcopy(patch)
        dishonest_contract["contract"]["stdout"] = "C"
        expect_rejected(
            "a patch whose declared result disagrees with its module value",
            lambda: validate_patch(dishonest_contract, base),
        )

        authority_escalation = copy.deepcopy(patch)
        authority_escalation["new_capability"] = "disk.write"
        expect_rejected(
            "an undeclared capability escalation field",
            lambda: validate_patch(authority_escalation, base),
        )

        stale_base = copy.deepcopy(base)
        stale_base["modules"][0]["value"] = 67
        stale_base["contract"]["stdout"] = "C"
        validate_world(stale_base)
        expect_rejected(
            "a patch applied to a different revision with the same world id",
            lambda: validate_patch(patch, stale_base),
        )

        unsafe_id = copy.deepcopy(patch)
        unsafe_id["patch_id"] = "say-b\nPASS: forged terminal line"
        expect_rejected(
            "a patch id containing terminal control characters",
            lambda: validate_patch(unsafe_id, base),
        )

        tampered_image = patched_image[:-1] + bytes([patched_image[-1] ^ 0x01])
        expect_rejected(
            "an evidence report for bytes not built from the effective world",
            lambda: make_report(
                base, patched, patch, target, tampered_image, patched_observed
            ),
        )

        missing_target_capability = copy.deepcopy(target)
        del missing_target_capability["capabilities"]["uart.write"]
        expect_rejected(
            "a Target Pack missing a required capability",
            lambda: validate_binding(base, missing_target_capability),
        )

        unknown_target_field = copy.deepcopy(target)
        unknown_target_field["vendor_sdk"] = "hidden-dependency"
        expect_rejected(
            "an undeclared Target Pack field",
            lambda: validate_target(unknown_target_field),
        )

        wrong_architecture = copy.deepcopy(target)
        wrong_architecture["architecture"] = "x86-64"
        expect_rejected(
            "a Target Pack for an unsupported backend",
            lambda: validate_target(wrong_architecture),
        )

        stale_target = copy.deepcopy(target)
        stale_target["capabilities"]["uart.write"]["address"] += 0x1000
        validate_target(stale_target)
        require(
            target_hash(stale_target) != target_hash(target),
            "different Target Pack revisions have the same hash",
        )
        expect_rejected(
            "an image built for a stale Target Pack revision",
            lambda: make_report(
                base, patched, patch, stale_target, patched_image, patched_observed
            ),
        )

        expect_rejected(
            "QEMU evidence reused for the hosted ARM64 target",
            lambda: make_report(
                base,
                base,
                None,
                hosted_target,
                hosted_base_image,
                base_observed,
            ),
        )

        wrong_hosted_driver = copy.deepcopy(hosted_target)
        wrong_hosted_driver["capabilities"]["uart.write"]["driver"] = (
            "unreviewed-stdout"
        )
        expect_rejected(
            "an unsupported hosted capability binding",
            lambda: validate_target(wrong_hosted_driver),
        )

        stale_hosted_target = copy.deepcopy(hosted_target)
        stale_hosted_target["runner"]["timeout_seconds"] = 4
        validate_target(stale_hosted_target)
        hosted_claim = copy.deepcopy(base_observed)
        hosted_claim["binding"] = {
            "target_sha256": target_hash(hosted_target),
            "image_sha256": hashlib.sha256(hosted_base_image).hexdigest(),
        }
        expect_rejected(
            "hosted evidence bound to a stale Target Pack revision",
            lambda: make_report(
                base,
                base,
                None,
                stale_hosted_target,
                hosted_base_image,
                hosted_claim,
            ),
        )

        runner_revision = copy.deepcopy(target)
        runner_revision["runner"]["timeout_seconds"] = 4
        validate_target(runner_revision)
        require(
            world_hash(base) == patch["base_hash"],
            "changing only a Target Pack changed portable world identity",
        )
        require(
            target_hash(runner_revision) != target_hash(target),
            "Target Pack runner revision did not change target identity",
        )
        print("PASS: world and Target Pack revisions have independent identities")

        with tempfile.TemporaryDirectory(prefix="rabbit-world-verify-") as temp_dir:
            temp_root = Path(temp_dir)
            duplicate_json = temp_root / "duplicate.json"
            duplicate_json.write_text(
                '{"schema_version": 1, "schema_version": 1}\n',
                encoding="utf-8",
            )
            expect_rejected(
                "ambiguous JSON with a duplicate field",
                lambda: load_json(duplicate_json),
            )

            nonstandard_json = temp_root / "nonstandard-number.json"
            nonstandard_json.write_text(
                '{"schema_version": NaN}\n', encoding="utf-8"
            )
            expect_rejected(
                "non-standard JSON numeric constants",
                lambda: load_json(nonstandard_json),
            )

            baseline_cli = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "rabbit_world.py"),
                    str(ROOT / "world.json"),
                    "--target",
                    str(target_path),
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=5,
            )
            require(baseline_cli.returncode == 0, "baseline CLI returned failure")
            require(baseline_cli.stderr == b"", "baseline CLI wrote to stderr")
            require(
                b"PASS: observed behavior matches the typed contract"
                in baseline_cli.stdout,
                "baseline CLI did not print its success evidence",
            )

            output_path = temp_root / "patched.bin"
            report_path = temp_root / "patched-report.json"
            patched_cli = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "rabbit_world.py"),
                    str(ROOT / "world.json"),
                    "--target",
                    str(target_path),
                    "--patch",
                    str(ROOT / "patches" / "say-b.json"),
                    "--output",
                    str(output_path),
                    "--report",
                    str(report_path),
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=5,
            )
            require(patched_cli.returncode == 0, "patched CLI returned failure")
            require(patched_cli.stderr == b"", "patched CLI wrote to stderr")
            require(output_path.read_bytes() == patched_image, "CLI image is incorrect")
            cli_report = json.loads(report_path.read_text(encoding="utf-8"))
            require(cli_report == patched_report, "CLI evidence report is incorrect")
            if hosted_available:
                hosted_cli = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "rabbit_world.py"),
                        str(ROOT / "world.json"),
                        "--target",
                        str(hosted_target_path),
                        "--patch",
                        str(ROOT / "patches" / "say-b.json"),
                    ],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=40,
                )
                require(hosted_cli.returncode == 0, "hosted ARM64 CLI returned failure")
                require(hosted_cli.stderr == b"", "hosted ARM64 CLI wrote to stderr")
                require(
                    b"PASS: observed behavior matches the typed contract"
                    in hosted_cli.stdout,
                    "hosted ARM64 CLI did not print its success evidence",
                )
            print("PASS: documented CLI workflows are intact")
    except (OSError, ValueError, VerificationError) as error:
        print(f"FAIL: {error}")
        return 1

    if hosted_available:
        print("PASS: complete U2 two-backend World v0 contract")
    else:
        print("PASS: U2 implementation contract; Apple Silicon execution pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
