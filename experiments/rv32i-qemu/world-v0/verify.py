#!/usr/bin/env python3
"""Verify the complete contract of the first patchable Rabbit World."""

from __future__ import annotations

import copy
import hashlib
import json
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
    validate_patch,
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
        validate_world(base)
        validate_patch(patch, base)
        require(
            patch["base_hash"] == world_hash(base),
            "patch does not identify the exact base manifest",
        )

        day_01_image = bytes.fromhex(DAY_01_HEX.read_text(encoding="ascii"))
        base_image = build_image(base)
        require(len(base_image) == 32, "base image is not exactly 32 bytes")
        require(
            base_image == day_01_image,
            "base world does not lower to the reviewed Day 01 image",
        )
        require(
            build_image(copy.deepcopy(base)) == base_image,
            "repeated base builds are not deterministic",
        )
        print(
            "PASS: immutable A world lowers to the reviewed 32-byte image "
            f"({hashlib.sha256(base_image).hexdigest()})"
        )

        base_snapshot = copy.deepcopy(base)
        patched = apply_patch(base, patch)
        patched_image = build_image(patched)
        require(base == base_snapshot, "applying a patch mutated the base world")
        require(
            byte_diff(base_image, patched_image)
            == [{"offset": 6, "before": 0x10, "after": 0x20}],
            "A -> B did not produce the predicted one-byte image diff",
        )
        require(
            build_image(copy.deepcopy(patched)) == patched_image,
            "repeated patched builds are not deterministic",
        )
        print("PASS: say-b is an overlay with byte diff offset 6: 0x10 -> 0x20")

        base_observed = run_image(base_image)
        base_report = make_report(base, base, None, base_image, base_observed)
        require(base_report["contract_passed"], "QEMU did not observe A / exit 0")
        print("PASS: QEMU observed exactly A on stdout, empty stderr, and exit 0")

        patched_observed = run_image(patched_image)
        patched_report = make_report(
            base, patched, patch, patched_image, patched_observed
        )
        require(patched_report["contract_passed"], "QEMU did not observe B / exit 0")
        print("PASS: QEMU observed exactly B on stdout, empty stderr, and exit 0")

        rollback_image = build_image(base)
        require(base == base_snapshot, "base world changed before rollback")
        require(rollback_image == base_image, "rollback did not restore the base image")
        rollback_observed = run_image(rollback_image)
        rollback_report = make_report(
            base, base, None, rollback_image, rollback_observed
        )
        require(rollback_report["contract_passed"], "rolled-back world did not emit A")
        print("PASS: removing the overlay rolls back exactly to the A world")

        missing_capability = copy.deepcopy(base)
        missing_capability["capabilities"].remove("uart.write")
        expect_rejected(
            "a UART module without uart.write authority",
            lambda: validate_world(missing_capability),
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
                base, patched, patch, tampered_image, patched_observed
            ),
        )

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
                [sys.executable, str(ROOT / "rabbit_world.py"), str(ROOT / "world.json")],
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
            print("PASS: documented baseline and patched CLI workflows are intact")
    except (OSError, ValueError, VerificationError) as error:
        print(f"FAIL: {error}")
        return 1

    print("PASS: complete World v0 contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
