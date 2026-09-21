#!/usr/bin/env python3
"""Validate, build, patch, and run the first Rabbit World.

World v0 is intentionally narrow. It accepts one UART-byte module, one successful exit
module, and a separately validated Target Pack, then lowers them either to the reviewed
32-byte RV32I/QEMU image or to hosted ARM64 assembly for Apple Silicon macOS.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
UART_CAPABILITY = "uart.write"
EXIT_CAPABILITY = "machine.exit"
KNOWN_CAPABILITIES = {UART_CAPABILITY, EXIT_CAPABILITY}

WORLD_KEYS = {
    "schema_version",
    "world_id",
    "capabilities",
    "modules",
    "contract",
}
TARGET_KEYS = {
    "schema_version",
    "target_id",
    "execution_envelope",
    "architecture",
    "byte_order",
    "image",
    "capabilities",
    "runner",
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
RV32I_IMAGE_KEYS = {"load_address", "size"}
HOSTED_ARM64_IMAGE_KEYS = {"format"}
UART_BINDING_KEYS = {"driver", "address"}
EXIT_BINDING_KEYS = {"driver", "address", "success_value"}
HOSTED_UART_BINDING_KEYS = {"driver", "file_descriptor"}
HOSTED_EXIT_BINDING_KEYS = {"driver", "status"}
QEMU_RUNNER_KEYS = {
    "kind",
    "executable",
    "machine",
    "bios",
    "nographic",
    "cpu_num",
    "timeout_seconds",
}
HOSTED_RUNNER_KEYS = {
    "kind",
    "compiler",
    "architecture",
    "minimum_os",
    "compile_timeout_seconds",
    "timeout_seconds",
}
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


def _require_page_address(value: Any, context: str) -> int:
    address = _require_integer(value, context)
    if not 0 <= address <= 0xFFFFF000 or address % 0x1000 != 0:
        raise WorldError(
            f"{context} must be a 32-bit address aligned to a 4 KiB page"
        )
    return address


def _validate_timeout(runner: dict[str, Any]) -> None:
    timeout = _require_integer(
        runner["timeout_seconds"], "target.runner.timeout_seconds"
    )
    if not 1 <= timeout <= 30:
        raise WorldError("target.runner.timeout_seconds must be from 1 to 30")


def _validate_compile_timeout(runner: dict[str, Any]) -> None:
    timeout = _require_integer(
        runner["compile_timeout_seconds"],
        "target.runner.compile_timeout_seconds",
    )
    if not 1 <= timeout <= 120:
        raise WorldError(
            "target.runner.compile_timeout_seconds must be from 1 to 120"
        )


def _validate_qemu_rv32i_target(target: dict[str, Any]) -> None:
    if target["execution_envelope"] != "native":
        raise WorldError("RV32I target.execution_envelope must be 'native'")
    if target["byte_order"] != "little":
        raise WorldError("RV32I target.byte_order must be 'little'")

    image = _require_object(target["image"], "target.image")
    _require_exact_keys(image, RV32I_IMAGE_KEYS, "target.image")
    load_address = _require_integer(
        image["load_address"], "target.image.load_address"
    )
    if not 0 <= load_address <= 0xFFFFFFFF or load_address % 4 != 0:
        raise WorldError("target.image.load_address must be an aligned 32-bit address")
    if _require_integer(image["size"], "target.image.size") != 32:
        raise WorldError("target.image.size must be 32 in World v0")

    capabilities = _require_object(target["capabilities"], "target.capabilities")
    _require_exact_keys(capabilities, KNOWN_CAPABILITIES, "target.capabilities")

    uart = _require_object(
        capabilities[UART_CAPABILITY], f"target.capabilities.{UART_CAPABILITY}"
    )
    _require_exact_keys(
        uart, UART_BINDING_KEYS, f"target.capabilities.{UART_CAPABILITY}"
    )
    if uart["driver"] != "qemu-virt-uart":
        raise WorldError("target uart.write driver must be 'qemu-virt-uart'")
    _require_page_address(
        uart["address"], f"target.capabilities.{UART_CAPABILITY}.address"
    )

    exit_device = _require_object(
        capabilities[EXIT_CAPABILITY], f"target.capabilities.{EXIT_CAPABILITY}"
    )
    _require_exact_keys(
        exit_device,
        EXIT_BINDING_KEYS,
        f"target.capabilities.{EXIT_CAPABILITY}",
    )
    if exit_device["driver"] != "qemu-sifive-test":
        raise WorldError("target machine.exit driver must be 'qemu-sifive-test'")
    _require_page_address(
        exit_device["address"],
        f"target.capabilities.{EXIT_CAPABILITY}.address",
    )
    success_value = _require_integer(
        exit_device["success_value"],
        f"target.capabilities.{EXIT_CAPABILITY}.success_value",
    )
    if not 0 <= success_value <= 0x7FFFFFFF:
        raise WorldError("target machine.exit success_value must fit signed 32 bits")

    runner = _require_object(target["runner"], "target.runner")
    _require_exact_keys(runner, QEMU_RUNNER_KEYS, "target.runner")
    expected_strings = {
        "kind": "qemu",
        "executable": "qemu-system-riscv32",
        "machine": "virt",
        "bios": "none",
    }
    for field, expected in expected_strings.items():
        if runner[field] != expected:
            raise WorldError(f"target.runner.{field} must be {expected!r}")
    if runner["nographic"] is not True:
        raise WorldError("target.runner.nographic must be true")
    if _require_integer(runner["cpu_num"], "target.runner.cpu_num") != 0:
        raise WorldError("target.runner.cpu_num must be 0 in World v0")
    _validate_timeout(runner)


def _validate_hosted_arm64_target(target: dict[str, Any]) -> None:
    if target["execution_envelope"] != "hosted":
        raise WorldError("ARM64 target.execution_envelope must be 'hosted'")
    if target["byte_order"] != "little":
        raise WorldError("ARM64 target.byte_order must be 'little'")

    image = _require_object(target["image"], "target.image")
    _require_exact_keys(image, HOSTED_ARM64_IMAGE_KEYS, "target.image")
    if image["format"] != "darwin-arm64-assembly":
        raise WorldError(
            "ARM64 target.image.format must be 'darwin-arm64-assembly'"
        )

    capabilities = _require_object(target["capabilities"], "target.capabilities")
    _require_exact_keys(capabilities, KNOWN_CAPABILITIES, "target.capabilities")

    stdout = _require_object(
        capabilities[UART_CAPABILITY], f"target.capabilities.{UART_CAPABILITY}"
    )
    _require_exact_keys(
        stdout,
        HOSTED_UART_BINDING_KEYS,
        f"target.capabilities.{UART_CAPABILITY}",
    )
    if stdout["driver"] != "darwin-posix-write":
        raise WorldError("ARM64 target uart.write driver must be 'darwin-posix-write'")
    if _require_integer(
        stdout["file_descriptor"],
        f"target.capabilities.{UART_CAPABILITY}.file_descriptor",
    ) != 1:
        raise WorldError("ARM64 target uart.write file_descriptor must be 1")

    process_exit = _require_object(
        capabilities[EXIT_CAPABILITY], f"target.capabilities.{EXIT_CAPABILITY}"
    )
    _require_exact_keys(
        process_exit,
        HOSTED_EXIT_BINDING_KEYS,
        f"target.capabilities.{EXIT_CAPABILITY}",
    )
    if process_exit["driver"] != "darwin-main-return":
        raise WorldError(
            "ARM64 target machine.exit driver must be 'darwin-main-return'"
        )
    if _require_integer(
        process_exit["status"],
        f"target.capabilities.{EXIT_CAPABILITY}.status",
    ) != 0:
        raise WorldError("ARM64 target machine.exit status must be 0")

    runner = _require_object(target["runner"], "target.runner")
    _require_exact_keys(runner, HOSTED_RUNNER_KEYS, "target.runner")
    expected_strings = {
        "kind": "darwin-clang",
        "compiler": "clang",
        "architecture": "arm64",
        "minimum_os": "14.0",
    }
    for field, expected in expected_strings.items():
        if runner[field] != expected:
            raise WorldError(f"target.runner.{field} must be {expected!r}")
    _validate_compile_timeout(runner)
    _validate_timeout(runner)


def validate_target(value: Any) -> dict[str, Any]:
    """Validate and return a supported World v0 Target Pack."""

    target = _require_object(value, "target")
    _require_exact_keys(target, TARGET_KEYS, "target")

    if _require_integer(target["schema_version"], "target.schema_version") != SCHEMA_VERSION:
        raise WorldError(f"target.schema_version must be {SCHEMA_VERSION}")
    _require_identifier(target["target_id"], "target.target_id")

    architecture = target["architecture"]
    if architecture == "rv32i":
        _validate_qemu_rv32i_target(target)
    elif architecture == "arm64":
        _validate_hosted_arm64_target(target)
    else:
        raise WorldError("target.architecture must be 'rv32i' or 'arm64'")
    return target


def validate_binding(
    world: dict[str, Any], target: dict[str, Any]
) -> None:
    """Require the Target Pack to satisfy every capability requested by the world."""

    validate_world(world)
    validate_target(target)
    missing = sorted(set(world["capabilities"]) - set(target["capabilities"]))
    if missing:
        values = ", ".join(repr(item) for item in missing)
        raise WorldError(f"target is missing required capabilities: {values}")


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


def target_hash(target: dict[str, Any]) -> str:
    """Return the canonical manifest hash for an exact valid Target Pack revision."""

    validate_target(target)
    canonical = json.dumps(
        target,
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


def _encode_lui(rd: int, immediate: int) -> int:
    if not 0 <= rd <= 31:
        raise WorldError("internal lui register is outside 0..31")
    if not 0 <= immediate <= 0xFFFFF:
        raise WorldError("internal lui immediate is outside unsigned 20-bit range")
    return (immediate << 12) | (rd << 7) | 0b0110111


def _encode_store(rs2: int, rs1: int, immediate: int, funct3: int) -> int:
    if not 0 <= rs2 <= 31 or not 0 <= rs1 <= 31:
        raise WorldError("internal store register is outside 0..31")
    if not -2048 <= immediate <= 2047:
        raise WorldError("internal store immediate is outside signed 12-bit range")
    if not 0 <= funct3 <= 0b111:
        raise WorldError("internal store funct3 is outside 3-bit range")
    encoded_immediate = immediate & 0xFFF
    return (
        ((encoded_immediate >> 5) << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | ((encoded_immediate & 0x1F) << 7)
        | 0b0100011
    )


def _split_lui_addi(value: int) -> tuple[int, int]:
    upper = (value + 0x800) >> 12
    lower = value - (upper << 12)
    if not 0 <= upper <= 0xFFFFF or not -2048 <= lower <= 2047:
        raise WorldError("target value cannot be materialized by the World v0 template")
    return upper, lower


def _build_rv32i_image(world: dict[str, Any], target: dict[str, Any]) -> bytes:
    bindings = target["capabilities"]
    uart_address = bindings[UART_CAPABILITY]["address"]
    exit_device = bindings[EXIT_CAPABILITY]
    exit_address = exit_device["address"]
    exit_upper, exit_lower = _split_lui_addi(exit_device["success_value"])
    words = (
        _encode_lui(5, uart_address >> 12),
        _encode_addi(6, 0, _uart_value(world)),
        _encode_store(6, 5, 0, 0b000),
        _encode_lui(5, exit_address >> 12),
        _encode_lui(6, exit_upper),
        _encode_addi(6, 6, exit_lower),
        _encode_store(6, 5, 0, 0b010),
        0x0000006F,
    )
    image = b"".join(
        word.to_bytes(4, byteorder=target["byte_order"]) for word in words
    )
    if len(image) != target["image"]["size"]:
        raise WorldError("built image size does not match the Target Pack")
    return image


def _build_hosted_arm64_image(
    world: dict[str, Any], target: dict[str, Any]
) -> bytes:
    value = _uart_value(world)
    file_descriptor = target["capabilities"][UART_CAPABILITY]["file_descriptor"]
    exit_status = target["capabilities"][EXIT_CAPABILITY]["status"]
    source = f""".section __TEXT,__text,regular,pure_instructions
.globl _main
.p2align 2
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    mov w0, #{file_descriptor}
    adrp x1, _rabbit_byte@PAGE
    add x1, x1, _rabbit_byte@PAGEOFF
    mov w2, #1
    bl _write
    mov w0, #{exit_status}
    ldp x29, x30, [sp], #16
    ret

.section __TEXT,__const
_rabbit_byte:
    .byte 0x{value:02x}
"""
    return source.encode("ascii")


def build_image(world: dict[str, Any], target: dict[str, Any]) -> bytes:
    """Lower a portable World v0 object through a validated Target Pack."""

    validate_binding(world, target)
    if target["architecture"] == "rv32i":
        return _build_rv32i_image(world, target)
    return _build_hosted_arm64_image(world, target)


def byte_diff(before: bytes, after: bytes) -> list[dict[str, int]]:
    if len(before) != len(after):
        raise WorldError("cannot diff images of different sizes in World v0")
    return [
        {"offset": offset, "before": left, "after": right}
        for offset, (left, right) in enumerate(zip(before, after))
        if left != right
    ]


def run_image(
    image: bytes,
    target: dict[str, Any],
    qemu: str | None = None,
    compiler: str | None = None,
) -> dict[str, Any]:
    """Run an image with its Target Pack and return raw observed behavior."""

    validate_target(target)
    if target["architecture"] == "rv32i":
        observed = _run_qemu_rv32i(image, target, qemu)
    else:
        observed = _run_hosted_arm64(image, target, compiler)
    observed["binding"] = {
        "target_sha256": target_hash(target),
        "image_sha256": hashlib.sha256(image).hexdigest(),
    }
    return observed


def _run_qemu_rv32i(
    image: bytes, target: dict[str, Any], qemu: str | None
) -> dict[str, Any]:
    if len(image) != target["image"]["size"]:
        raise WorldError("image size does not match the Target Pack")
    runner = target["runner"]
    executable = qemu or runner["executable"]
    with tempfile.TemporaryDirectory(prefix="rabbit-world-v0-") as temp_dir:
        image_path = Path(temp_dir) / "world.bin"
        image_path.write_bytes(image)
        command = [
            executable,
            "-machine",
            runner["machine"],
        ]
        if runner["nographic"]:
            command.append("-nographic")
        command.extend([
            "-bios",
            runner["bios"],
            "-device",
            "loader,file="
            f"{image_path},addr=0x{target['image']['load_address']:x},"
            f"cpu-num={runner['cpu_num']}",
        ])
        try:
            completed = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=runner["timeout_seconds"],
            )
        except FileNotFoundError as error:
            raise WorldError(f"QEMU executable not found: {executable}") from error
        except subprocess.TimeoutExpired as error:
            raise WorldError(
                "QEMU did not exit within "
                f"{runner['timeout_seconds']} seconds"
            ) from error

    return {
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_status": completed.returncode,
        "execution": {
            "runner": runner["kind"],
            "executable": executable,
            "machine": runner["machine"],
            "bios": runner["bios"],
        },
    }


def _run_hosted_arm64(
    image: bytes, target: dict[str, Any], compiler: str | None
) -> dict[str, Any]:
    if platform.system() != "Darwin" or platform.machine().lower() not in {
        "arm64",
        "aarch64",
    }:
        raise WorldError("hosted ARM64 target requires an Apple Silicon Mac")

    runner = target["runner"]
    compiler_executable = compiler or runner["compiler"]
    with tempfile.TemporaryDirectory(prefix="rabbit-world-v0-arm64-") as temp_dir:
        temp_root = Path(temp_dir)
        source_path = temp_root / "world.s"
        executable_path = temp_root / "world"
        source_path.write_bytes(image)
        compile_command = [
            compiler_executable,
            "-arch",
            runner["architecture"],
            f"-mmacosx-version-min={runner['minimum_os']}",
            str(source_path),
            "-o",
            str(executable_path),
        ]
        try:
            compiled = subprocess.run(
                compile_command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=runner["compile_timeout_seconds"],
            )
        except FileNotFoundError as error:
            raise WorldError(
                f"ARM64 compiler not found: {compiler_executable}"
            ) from error
        except subprocess.TimeoutExpired as error:
            raise WorldError("ARM64 compilation timed out") from error
        if compiled.returncode != 0:
            diagnostic = compiled.stderr.decode(errors="replace").strip()
            raise WorldError(f"ARM64 compilation failed: {diagnostic}")

        try:
            completed = subprocess.run(
                [str(executable_path)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=runner["timeout_seconds"],
            )
        except subprocess.TimeoutExpired as error:
            raise WorldError("hosted ARM64 program timed out") from error

    return {
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_status": completed.returncode,
        "execution": {
            "runner": runner["kind"],
            "compiler": compiler_executable,
            "architecture": runner["architecture"],
            "minimum_os": runner["minimum_os"],
        },
    }


def make_report(
    base_world: dict[str, Any],
    effective_world: dict[str, Any],
    patch: dict[str, Any] | None,
    target: dict[str, Any],
    image: bytes,
    observed: dict[str, Any],
) -> dict[str, Any]:
    validate_world(base_world)
    validate_world(effective_world)
    validate_binding(effective_world, target)
    expected_world = apply_patch(base_world, patch) if patch else base_world
    if world_hash(effective_world) != world_hash(expected_world):
        raise WorldError("effective world does not match the supplied base and patch")

    base_image = build_image(base_world, target)
    expected_image = build_image(effective_world, target)
    if image != expected_image:
        raise WorldError(
            "report image does not match the effective world and Target Pack"
        )
    binding = _require_object(observed.get("binding"), "observed.binding")
    _require_exact_keys(
        binding, {"target_sha256", "image_sha256"}, "observed.binding"
    )
    if binding["target_sha256"] != target_hash(target):
        raise WorldError("observed evidence belongs to a different Target Pack")
    if binding["image_sha256"] != hashlib.sha256(image).hexdigest():
        raise WorldError("observed evidence belongs to a different image")
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
        "target": {
            "target_id": target["target_id"],
            "sha256": target_hash(target),
            "execution_envelope": target["execution_envelope"],
            "architecture": target["architecture"],
        },
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
        "evidence_binding": dict(binding),
        "execution": dict(observed["execution"]),
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
    print(
        f"TARGET: {report['target']['target_id']} "
        f"({report['target']['architecture']}, "
        f"sha256={report['target']['sha256']})"
    )
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
    parser.add_argument(
        "--target",
        required=True,
        type=Path,
        help="path to a separately validated Target Pack JSON file",
    )
    parser.add_argument("--patch", type=Path, help="optional patch overlay")
    parser.add_argument("--output", type=Path, help="optional built artifact output path")
    parser.add_argument("--report", type=Path, help="optional JSON report output path")
    parser.add_argument(
        "--qemu", help="optional override for the Target Pack QEMU executable"
    )
    parser.add_argument(
        "--compiler", help="optional override for the hosted Target Pack compiler"
    )
    args = parser.parse_args()

    try:
        base_world = load_json(args.world)
        validate_world(base_world)
        target = load_json(args.target)
        validate_binding(base_world, target)
        patch = load_json(args.patch) if args.patch else None
        effective_world = apply_patch(base_world, patch) if patch else base_world
        image = build_image(effective_world, target)
        observed = run_image(
            image, target, qemu=args.qemu, compiler=args.compiler
        )
        report = make_report(
            base_world, effective_world, patch, target, image, observed
        )

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
