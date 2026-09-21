#!/usr/bin/env python3
"""Validate, build, patch, and run the first Rabbit World.

World v0 is intentionally narrow. It accepts one UART-byte module and one successful
exit module, then lowers that typed world to the reviewed 32-byte RV32I/QEMU image.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
TARGET = "qemu-virt-rv32i"
UART_CAPABILITY = "uart.write"
EXIT_CAPABILITY = "machine.exit"
KNOWN_CAPABILITIES = {UART_CAPABILITY, EXIT_CAPABILITY}

WORLD_KEYS = {
    "schema_version",
    "world_id",
    "target",
    "capabilities",
    "modules",
    "contract",
}
PATCH_KEYS = {
    "schema_version",
    "patch_id",
    "base_world",
    "base_hash",
    "changes",
    "contract",
}
CONTRACT_KEYS = {"stdout", "exit_status"}
IDENTIFIER_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")


class WorldError(ValueError):
    """A world or patch violated the reviewed v0 contract."""


def _require_object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise WorldError(f"{context} must be a JSON object")
    return value


def _require_exact_keys(
    value: dict[str, Any], expected: set[str], context: str
) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing:
        fields = ", ".join(repr(field) for field in missing)
        raise WorldError(f"{context} is missing fields: {fields}")
    if unknown:
        fields = ", ".join(repr(field) for field in unknown)
        raise WorldError(f"{context} has unknown fields: {fields}")


def _require_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise WorldError(f"{context} must be a non-empty string")
    return value


def _require_identifier(value: Any, context: str) -> str:
    identifier = _require_string(value, context)
    if IDENTIFIER_PATTERN.fullmatch(identifier) is None:
        raise WorldError(
            f"{context} must match [a-z0-9][a-z0-9-]{{0,63}}"
        )
    return identifier


def _require_integer(value: Any, context: str) -> int:
    if type(value) is not int:
        raise WorldError(f"{context} must be an integer")
    return value


def _validate_contract(value: Any, context: str) -> dict[str, Any]:
    contract = _require_object(value, context)
    _require_exact_keys(contract, CONTRACT_KEYS, context)

    stdout = _require_string(contract["stdout"], f"{context}.stdout")
    try:
        stdout_bytes = stdout.encode("ascii")
    except UnicodeEncodeError as error:
        raise WorldError(f"{context}.stdout must be one ASCII byte") from error
    if len(stdout_bytes) != 1:
        raise WorldError(f"{context}.stdout must encode to exactly one byte")

    exit_status = _require_integer(
        contract["exit_status"], f"{context}.exit_status"
    )
    if exit_status != 0:
        raise WorldError(f"{context}.exit_status must be 0 in World v0")
    return contract


def validate_world(value: Any) -> dict[str, Any]:
    """Validate and return a World v0 object without mutating it."""

    world = _require_object(value, "world")
    _require_exact_keys(world, WORLD_KEYS, "world")

    if _require_integer(world["schema_version"], "world.schema_version") != SCHEMA_VERSION:
        raise WorldError(f"world.schema_version must be {SCHEMA_VERSION}")
    _require_identifier(world["world_id"], "world.world_id")
    target = _require_string(world["target"], "world.target")
    if target != TARGET:
        raise WorldError(f"world.target must be {TARGET!r}")

    capabilities = world["capabilities"]
    if not isinstance(capabilities, list) or not all(
        isinstance(item, str) for item in capabilities
    ):
        raise WorldError("world.capabilities must be a list of strings")
    if len(set(capabilities)) != len(capabilities):
        raise WorldError("world.capabilities must not contain duplicates")
    unknown_capabilities = sorted(set(capabilities) - KNOWN_CAPABILITIES)
    if unknown_capabilities:
        values = ", ".join(repr(item) for item in unknown_capabilities)
        raise WorldError(
            f"world.capabilities contains unsupported values: {values}"
        )

    modules = world["modules"]
    if not isinstance(modules, list):
        raise WorldError("world.modules must be a list")

    modules_by_id: dict[str, dict[str, Any]] = {}
    uart_modules: list[dict[str, Any]] = []
    exit_modules: list[dict[str, Any]] = []
    for index, raw_module in enumerate(modules):
        context = f"world.modules[{index}]"
        module = _require_object(raw_module, context)
        module_type = _require_string(module.get("type"), f"{context}.type")

        if module_type == "uart-byte":
            _require_exact_keys(module, {"id", "type", "value"}, context)
            byte_value = _require_integer(module["value"], f"{context}.value")
            if not 0 <= byte_value <= 127:
                raise WorldError(f"{context}.value must be an ASCII byte from 0 to 127")
            uart_modules.append(module)
        elif module_type == "successful-exit":
            _require_exact_keys(module, {"id", "type"}, context)
            exit_modules.append(module)
        else:
            raise WorldError(f"{context}.type {module_type!r} is unsupported in World v0")

        module_id = _require_identifier(module["id"], f"{context}.id")
        if module_id in modules_by_id:
            raise WorldError(f"duplicate module id: {module_id!r}")
        modules_by_id[module_id] = module

    if len(uart_modules) != 1 or len(exit_modules) != 1 or len(modules) != 2:
        raise WorldError(
            "World v0 requires exactly one uart-byte module and one successful-exit module"
        )
    if UART_CAPABILITY not in capabilities:
        raise WorldError("uart-byte requires the uart.write capability")
    if EXIT_CAPABILITY not in capabilities:
        raise WorldError("successful-exit requires the machine.exit capability")

    contract = _validate_contract(world["contract"], "world.contract")
    uart_value = uart_modules[0]["value"]
    if contract["stdout"].encode("ascii") != bytes([uart_value]):
        raise WorldError(
            "world.contract.stdout does not match the uart-byte module value"
        )
    return world


def world_hash(world: dict[str, Any]) -> str:
    """Return the canonical manifest hash for an exact valid world revision."""

    validate_world(world)
    canonical = json.dumps(
        world,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def _materialize_patch(
    base_world: dict[str, Any], patch: dict[str, Any]
) -> dict[str, Any]:
    candidate = copy.deepcopy(base_world)
    modules_by_id = {module["id"]: module for module in candidate["modules"]}
    for change in patch["changes"]:
        modules_by_id[change["module"]].update(change["set"])
    candidate["contract"] = copy.deepcopy(patch["contract"])
    return candidate


def validate_patch(value: Any, base_world: dict[str, Any]) -> dict[str, Any]:
    """Validate a patch against its immutable base world."""

    validate_world(base_world)
    patch = _require_object(value, "patch")
    _require_exact_keys(patch, PATCH_KEYS, "patch")

    if _require_integer(patch["schema_version"], "patch.schema_version") != SCHEMA_VERSION:
        raise WorldError(f"patch.schema_version must be {SCHEMA_VERSION}")
    _require_identifier(patch["patch_id"], "patch.patch_id")
    base_world_id = _require_identifier(patch["base_world"], "patch.base_world")
    if base_world_id != base_world["world_id"]:
        raise WorldError(
            f"patch.base_world must be {base_world['world_id']!r}, "
            f"got {base_world_id!r}"
        )
    base_hash = _require_string(patch["base_hash"], "patch.base_hash")
    expected_base_hash = world_hash(base_world)
    if base_hash != expected_base_hash:
        raise WorldError(
            "patch.base_hash does not match the exact base world revision: "
            f"expected {expected_base_hash}, got {base_hash!r}"
        )

    modules_by_id = {module["id"]: module for module in base_world["modules"]}
    changes = patch["changes"]
    if not isinstance(changes, list) or not changes:
        raise WorldError("patch.changes must be a non-empty list")

    changed_modules: set[str] = set()
    for index, raw_change in enumerate(changes):
        context = f"patch.changes[{index}]"
        change = _require_object(raw_change, context)
        _require_exact_keys(change, {"module", "set"}, context)
        module_id = _require_identifier(change["module"], f"{context}.module")
        if module_id in changed_modules:
            raise WorldError(f"patch changes module {module_id!r} more than once")
        changed_modules.add(module_id)

        module = modules_by_id.get(module_id)
        if module is None:
            raise WorldError(f"patch refers to unknown module {module_id!r}")
        if module["type"] != "uart-byte":
            raise WorldError(
                f"World v0 can patch only uart-byte modules, not {module['type']!r}"
            )

        settings = _require_object(change["set"], f"{context}.set")
        _require_exact_keys(settings, {"value"}, f"{context}.set")
        byte_value = _require_integer(settings["value"], f"{context}.set.value")
        if not 0 <= byte_value <= 127:
            raise WorldError(f"{context}.set.value must be an ASCII byte from 0 to 127")

    _validate_contract(patch["contract"], "patch.contract")
    validate_world(_materialize_patch(base_world, patch))
    return patch


def apply_patch(
    base_world: dict[str, Any], patch: dict[str, Any]
) -> dict[str, Any]:
    """Return a patched copy; never mutate the base world."""

    validate_patch(patch, base_world)
    return _materialize_patch(base_world, patch)


def _uart_value(world: dict[str, Any]) -> int:
    return next(
        module["value"]
        for module in world["modules"]
        if module["type"] == "uart-byte"
    )


def _encode_addi(rd: int, rs1: int, imm: int) -> int:
    if not 0 <= rd <= 31 or not 0 <= rs1 <= 31:
        raise WorldError("internal addi register is outside 0..31")
    if not -2048 <= imm <= 2047:
        raise WorldError("internal addi immediate is outside signed 12-bit range")
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (rd << 7) | 0b0010011


def build_image(world: dict[str, Any]) -> bytes:
    """Lower a valid World v0 object to its canonical 32-byte RV32I image."""

    validate_world(world)
    words = (
        0x100002B7,  # lui  t0, 0x10000      (UART address)
        _encode_addi(6, 0, _uart_value(world)),
        0x00628023,  # sb   t1, 0(t0)
        0x001002B7,  # lui  t0, 0x100        (SiFive test address)
        0x00005337,  # lui  t1, 0x5
        0x55530313,  # addi t1, t1, 0x555
        0x0062A023,  # sw   t1, 0(t0)        (successful exit)
        0x0000006F,  # jal  zero, 0          (safety loop)
    )
    return b"".join(word.to_bytes(4, byteorder="little") for word in words)


def byte_diff(before: bytes, after: bytes) -> list[dict[str, int]]:
    if len(before) != len(after):
        raise WorldError("cannot diff images of different sizes in World v0")
    return [
        {"offset": offset, "before": left, "after": right}
        for offset, (left, right) in enumerate(zip(before, after))
        if left != right
    ]


def run_image(image: bytes, qemu: str = "qemu-system-riscv32") -> dict[str, Any]:
    """Run an image in QEMU and return raw observed behavior."""

    with tempfile.TemporaryDirectory(prefix="rabbit-world-v0-") as temp_dir:
        image_path = Path(temp_dir) / "world.bin"
        image_path.write_bytes(image)
        command = [
            qemu,
            "-machine",
            "virt",
            "-nographic",
            "-bios",
            "none",
            "-device",
            f"loader,file={image_path},addr=0x80000000,cpu-num=0",
        ]
        try:
            completed = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=3,
            )
        except FileNotFoundError as error:
            raise WorldError(f"QEMU executable not found: {qemu}") from error
        except subprocess.TimeoutExpired as error:
            raise WorldError("QEMU did not exit within three seconds") from error

    return {
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_status": completed.returncode,
    }


def make_report(
    base_world: dict[str, Any],
    effective_world: dict[str, Any],
    patch: dict[str, Any] | None,
    image: bytes,
    observed: dict[str, Any],
) -> dict[str, Any]:
    validate_world(base_world)
    validate_world(effective_world)
    expected_world = apply_patch(base_world, patch) if patch else base_world
    if world_hash(effective_world) != world_hash(expected_world):
        raise WorldError("effective world does not match the supplied base and patch")

    base_image = build_image(base_world)
    expected_image = build_image(effective_world)
    if image != expected_image:
        raise WorldError("report image does not match the effective world")
    expected_stdout = effective_world["contract"]["stdout"].encode("ascii")
    expected_status = effective_world["contract"]["exit_status"]
    contract_passed = (
        observed["stdout"] == expected_stdout
        and observed["stderr"] == b""
        and observed["exit_status"] == expected_status
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "world_id": base_world["world_id"],
        "base_world_sha256": world_hash(base_world),
        "effective_world_sha256": world_hash(effective_world),
        "patch_id": patch["patch_id"] if patch else None,
        "target": effective_world["target"],
        "capabilities": list(effective_world["capabilities"]),
        "intent": {
            "base_uart_byte": _uart_value(base_world),
            "effective_uart_byte": _uart_value(effective_world),
        },
        "image": {
            "size": len(image),
            "sha256": hashlib.sha256(image).hexdigest(),
            "bytes_hex": image.hex(" "),
        },
        "byte_diff": byte_diff(base_image, image),
        "expected": {
            "stdout_hex": expected_stdout.hex(),
            "exit_status": expected_status,
            "stderr_hex": "",
        },
        "observed": {
            "stdout_hex": observed["stdout"].hex(),
            "stderr_hex": observed["stderr"].hex(),
            "exit_status": observed["exit_status"],
        },
        "contract_passed": contract_passed,
    }


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise WorldError(f"duplicate JSON field: {key!r}")
        value[key] = item
    return value


def _reject_nonstandard_number(value: str) -> None:
    raise WorldError(f"non-standard JSON number is not allowed: {value}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_number,
        )
    except OSError as error:
        raise WorldError(f"could not read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise WorldError(f"could not decode {path}: {error}") from error
    return _require_object(value, str(path))


def _write_bytes(path: Path, value: bytes) -> None:
    try:
        path.write_bytes(value)
    except OSError as error:
        raise WorldError(f"could not write {path}: {error}") from error


def _write_report(path: Path, report: dict[str, Any]) -> None:
    try:
        path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except OSError as error:
        raise WorldError(f"could not write {path}: {error}") from error


def print_report(report: dict[str, Any]) -> None:
    patch_name = report["patch_id"] or "none (immutable base)"
    print(f"WORLD: {report['world_id']}")
    print(f"PATCH: {patch_name}")
    print(f"CAPABILITIES: {', '.join(report['capabilities'])}")
    print(
        "INTENT: UART byte "
        f"{report['intent']['base_uart_byte']} -> "
        f"{report['intent']['effective_uart_byte']}"
    )
    print(
        f"IMAGE: {report['image']['size']} bytes, "
        f"sha256={report['image']['sha256']}"
    )
    if report["byte_diff"]:
        for change in report["byte_diff"]:
            print(
                f"BYTE DIFF: offset {change['offset']}: "
                f"0x{change['before']:02x} -> 0x{change['after']:02x}"
            )
    else:
        print("BYTE DIFF: none")
    print(
        "OBSERVED: stdout=0x"
        f"{report['observed']['stdout_hex']}, "
        f"stderr=0x{report['observed']['stderr_hex']}, "
        f"exit={report['observed']['exit_status']}"
    )
    if report["contract_passed"]:
        print("PASS: observed behavior matches the typed contract")
    else:
        print("FAIL: observed behavior does not match the typed contract")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and run the first typed, patchable Rabbit World."
    )
    parser.add_argument("world", type=Path, help="path to a World v0 JSON file")
    parser.add_argument("--patch", type=Path, help="optional patch overlay")
    parser.add_argument("--output", type=Path, help="optional raw image output path")
    parser.add_argument("--report", type=Path, help="optional JSON report output path")
    parser.add_argument(
        "--qemu", default="qemu-system-riscv32", help="QEMU executable name or path"
    )
    args = parser.parse_args()

    try:
        base_world = load_json(args.world)
        validate_world(base_world)
        patch = load_json(args.patch) if args.patch else None
        effective_world = apply_patch(base_world, patch) if patch else base_world
        image = build_image(effective_world)
        observed = run_image(image, qemu=args.qemu)
        report = make_report(base_world, effective_world, patch, image, observed)

        if args.output:
            _write_bytes(args.output, image)
        if args.report:
            _write_report(args.report, report)
        print_report(report)
        return 0 if report["contract_passed"] else 1
    except WorldError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
