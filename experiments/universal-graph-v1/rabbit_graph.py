#!/usr/bin/env python3
"""Validate, patch, lower, and run the first Universal Rabbit module graph."""

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


WORLD_SCHEMA_VERSION = 1
TARGET_SCHEMA_VERSION = 2
CONSOLE_CAPABILITY = "console.write"
EXIT_CAPABILITY = "machine.exit"
KNOWN_CAPABILITIES = {CONSOLE_CAPABILITY, EXIT_CAPABILITY}
IDENTIFIER_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")

WORLD_KEYS = {
    "schema_version",
    "world_id",
    "imports",
    "dependencies",
    "capabilities",
    "resources",
    "modules",
    "connections",
    "contract",
}
PATCH_KEYS = {
    "schema_version",
    "patch_id",
    "base_world",
    "base_hash",
    "add_modules",
    "remove_connections",
    "add_connections",
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
PORTS: dict[str, dict[str, tuple[str, str]]] = {
    "world-start": {"started": ("output", "event")},
    "console-byte": {
        "trigger": ("input", "event"),
        "done": ("output", "event"),
        "value": ("output", "byte"),
    },
    "successful-exit": {"trigger": ("input", "event")},
}
REQUIRED_IMPORTS = {(name, 1) for name in PORTS}
REQUIRED_DEPENDENCIES = {("rabbit-graph-core", 1)}


class GraphError(ValueError):
    """A world, patch, target, artifact, or evidence object is invalid."""


def _object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GraphError(f"{context} must be a JSON object")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], context: str) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing:
        raise GraphError(
            f"{context} is missing fields: " + ", ".join(repr(item) for item in missing)
        )
    if unknown:
        raise GraphError(
            f"{context} has unknown fields: " + ", ".join(repr(item) for item in unknown)
        )


def _integer(value: Any, context: str) -> int:
    if type(value) is not int:
        raise GraphError(f"{context} must be an integer")
    return value


def _string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise GraphError(f"{context} must be a non-empty string")
    return value


def _identifier(value: Any, context: str) -> str:
    result = _string(value, context)
    if IDENTIFIER_PATTERN.fullmatch(result) is None:
        raise GraphError(f"{context} must match [a-z0-9][a-z0-9-]{{0,63}}")
    return result


def _canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _validate_versioned_names(
    value: Any, context: str, expected: set[tuple[str, int]]
) -> None:
    if not isinstance(value, list):
        raise GraphError(f"{context} must be a list")
    found: set[tuple[str, int]] = set()
    for index, raw_item in enumerate(value):
        item_context = f"{context}[{index}]"
        item = _object(raw_item, item_context)
        _exact_keys(item, {"name", "version"}, item_context)
        key = (
            _identifier(item["name"], f"{item_context}.name"),
            _integer(item["version"], f"{item_context}.version"),
        )
        if key in found:
            raise GraphError(f"{context} contains duplicate {key!r}")
        found.add(key)
    if found != expected:
        raise GraphError(f"{context} must resolve exactly to {sorted(expected)!r}")


def _validate_contract(value: Any, context: str) -> dict[str, Any]:
    contract = _object(value, context)
    _exact_keys(contract, {"stdout", "exit_status"}, context)
    stdout = _string(contract["stdout"], f"{context}.stdout")
    try:
        stdout_bytes = stdout.encode("ascii")
    except UnicodeEncodeError as error:
        raise GraphError(f"{context}.stdout must be ASCII") from error
    if not stdout_bytes:
        raise GraphError(f"{context}.stdout must not be empty")
    if _integer(contract["exit_status"], f"{context}.exit_status") != 0:
        raise GraphError(f"{context}.exit_status must be 0 in graph v1")
    return contract


def _validate_module(value: Any, context: str) -> dict[str, Any]:
    module = _object(value, context)
    module_type = _string(module.get("type"), f"{context}.type")
    if module_type == "console-byte":
        _exact_keys(module, {"id", "type", "value"}, context)
        byte = _integer(module["value"], f"{context}.value")
        if not 0 <= byte <= 127:
            raise GraphError(f"{context}.value must be an ASCII byte from 0 to 127")
    elif module_type in {"world-start", "successful-exit"}:
        _exact_keys(module, {"id", "type"}, context)
    else:
        raise GraphError(f"{context}.type {module_type!r} is not imported")
    _identifier(module["id"], f"{context}.id")
    return module


def _validate_endpoint(
    value: Any,
    context: str,
    modules: dict[str, dict[str, Any]],
    direction: str,
) -> tuple[str, str, str]:
    endpoint = _object(value, context)
    _exact_keys(endpoint, {"module", "port"}, context)
    module_id = _identifier(endpoint["module"], f"{context}.module")
    port_name = _identifier(endpoint["port"], f"{context}.port")
    module = modules.get(module_id)
    if module is None:
        raise GraphError(f"{context} refers to unknown module {module_id!r}")
    port = PORTS[module["type"]].get(port_name)
    if port is None:
        raise GraphError(
            f"{context} refers to unknown port {module_id}.{port_name}"
        )
    actual_direction, port_type = port
    if actual_direction != direction:
        raise GraphError(
            f"{context} port {module_id}.{port_name} is {actual_direction}, "
            f"not {direction}"
        )
    return module_id, port_name, port_type


def _connection_key(connection: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        connection["from"]["module"],
        connection["from"]["port"],
        connection["to"]["module"],
        connection["to"]["port"],
    )


def _analyze_graph(world: dict[str, Any]) -> tuple[list[str], bytes]:
    modules = {module["id"]: module for module in world["modules"]}
    incoming: dict[str, list[str]] = {module_id: [] for module_id in modules}
    outgoing: dict[str, list[str]] = {module_id: [] for module_id in modules}
    seen_connections: set[tuple[str, str, str, str]] = set()

    for index, raw_connection in enumerate(world["connections"]):
        context = f"world.connections[{index}]"
        connection = _object(raw_connection, context)
        _exact_keys(connection, {"from", "to"}, context)
        source_id, _, source_type = _validate_endpoint(
            connection["from"], f"{context}.from", modules, "output"
        )
        target_id, _, target_type = _validate_endpoint(
            connection["to"], f"{context}.to", modules, "input"
        )
        if source_type != target_type:
            raise GraphError(
                f"{context} connects incompatible types {source_type!r} and "
                f"{target_type!r}"
            )
        if source_type != "event":
            raise GraphError(f"{context} must carry an event in graph v1")
        key = _connection_key(connection)
        if key in seen_connections:
            raise GraphError(f"duplicate connection: {key!r}")
        seen_connections.add(key)
        outgoing[source_id].append(target_id)
        incoming[target_id].append(source_id)

    starts = [item["id"] for item in world["modules"] if item["type"] == "world-start"]
    exits = [item["id"] for item in world["modules"] if item["type"] == "successful-exit"]
    if len(starts) != 1 or len(exits) != 1:
        raise GraphError("graph v1 requires exactly one world-start and one successful-exit")
    start, exit_id = starts[0], exits[0]

    for module_id in modules:
        expected_incoming = 0 if module_id == start else 1
        expected_outgoing = 0 if module_id == exit_id else 1
        if len(incoming[module_id]) != expected_incoming:
            raise GraphError(
                f"module {module_id!r} must have {expected_incoming} incoming event connection(s)"
            )
        if len(outgoing[module_id]) != expected_outgoing:
            raise GraphError(
                f"module {module_id!r} must have {expected_outgoing} outgoing event connection(s)"
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(module_id: str) -> None:
        if module_id in visiting:
            raise GraphError(f"event graph contains a cycle through {module_id!r}")
        if module_id in visited:
            return
        visiting.add(module_id)
        for next_id in outgoing[module_id]:
            visit(next_id)
        visiting.remove(module_id)
        visited.add(module_id)

    for module_id in modules:
        visit(module_id)

    order = [start]
    current = start
    while current != exit_id:
        current = outgoing[current][0]
        if current in order:
            raise GraphError(f"event graph contains a cycle through {current!r}")
        order.append(current)
    if set(order) != set(modules):
        unreachable = sorted(set(modules) - set(order))
        raise GraphError(f"event graph has unreachable modules: {unreachable!r}")

    output = bytes(
        modules[module_id]["value"]
        for module_id in order
        if modules[module_id]["type"] == "console-byte"
    )
    return order, output


def validate_world(value: Any) -> dict[str, Any]:
    world = _object(value, "world")
    _exact_keys(world, WORLD_KEYS, "world")
    if _integer(world["schema_version"], "world.schema_version") != WORLD_SCHEMA_VERSION:
        raise GraphError(f"world.schema_version must be {WORLD_SCHEMA_VERSION}")
    _identifier(world["world_id"], "world.world_id")
    _validate_versioned_names(world["imports"], "world.imports", REQUIRED_IMPORTS)
    _validate_versioned_names(
        world["dependencies"], "world.dependencies", REQUIRED_DEPENDENCIES
    )

    capabilities = world["capabilities"]
    if not isinstance(capabilities, list) or not all(
        isinstance(item, str) for item in capabilities
    ):
        raise GraphError("world.capabilities must be a list of strings")
    if len(set(capabilities)) != len(capabilities):
        raise GraphError("world.capabilities must not contain duplicates")
    if set(capabilities) != KNOWN_CAPABILITIES:
        raise GraphError(f"world.capabilities must be exactly {sorted(KNOWN_CAPABILITIES)!r}")

    resources = _object(world["resources"], "world.resources")
    _exact_keys(
        resources,
        {"max_modules", "max_connections", "max_output_bytes"},
        "world.resources",
    )
    limits = {"max_modules": 64, "max_connections": 64, "max_output_bytes": 128}
    for name, upper in limits.items():
        amount = _integer(resources[name], f"world.resources.{name}")
        if not 1 <= amount <= upper:
            raise GraphError(f"world.resources.{name} must be from 1 to {upper}")

    if not isinstance(world["modules"], list):
        raise GraphError("world.modules must be a list")
    modules_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_module in enumerate(world["modules"]):
        module = _validate_module(raw_module, f"world.modules[{index}]")
        if module["id"] in modules_by_id:
            raise GraphError(f"duplicate module id: {module['id']!r}")
        modules_by_id[module["id"]] = module
    if len(world["modules"]) > resources["max_modules"]:
        raise GraphError("world exceeds resources.max_modules")
    if not isinstance(world["connections"], list):
        raise GraphError("world.connections must be a list")
    if len(world["connections"]) > resources["max_connections"]:
        raise GraphError("world exceeds resources.max_connections")

    _, output = _analyze_graph(world)
    if len(output) > resources["max_output_bytes"]:
        raise GraphError("world exceeds resources.max_output_bytes")
    contract = _validate_contract(world["contract"], "world.contract")
    if contract["stdout"].encode("ascii") != output:
        raise GraphError("world.contract.stdout does not match graph event order")
    return world


def world_hash(world: dict[str, Any]) -> str:
    validate_world(world)
    return _canonical_hash(world)


def _materialize_patch(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(base)
    removals = {_connection_key(item) for item in patch["remove_connections"]}
    candidate["connections"] = [
        item for item in candidate["connections"] if _connection_key(item) not in removals
    ]
    candidate["modules"].extend(copy.deepcopy(patch["add_modules"]))
    candidate["connections"].extend(copy.deepcopy(patch["add_connections"]))
    candidate["contract"] = copy.deepcopy(patch["contract"])
    return candidate


def validate_patch(value: Any, base: dict[str, Any]) -> dict[str, Any]:
    validate_world(base)
    patch = _object(value, "patch")
    _exact_keys(patch, PATCH_KEYS, "patch")
    if _integer(patch["schema_version"], "patch.schema_version") != WORLD_SCHEMA_VERSION:
        raise GraphError(f"patch.schema_version must be {WORLD_SCHEMA_VERSION}")
    _identifier(patch["patch_id"], "patch.patch_id")
    if _identifier(patch["base_world"], "patch.base_world") != base["world_id"]:
        raise GraphError(f"patch.base_world must be {base['world_id']!r}")
    expected_hash = world_hash(base)
    if _string(patch["base_hash"], "patch.base_hash") != expected_hash:
        raise GraphError(
            f"patch.base_hash must identify the exact base revision {expected_hash}"
        )

    add_modules = patch["add_modules"]
    if not isinstance(add_modules, list) or not add_modules:
        raise GraphError("patch.add_modules must be a non-empty list")
    base_ids = {item["id"] for item in base["modules"]}
    added_ids: set[str] = set()
    for index, raw_module in enumerate(add_modules):
        module = _validate_module(raw_module, f"patch.add_modules[{index}]")
        if module["type"] != "console-byte":
            raise GraphError("graph v1 patches may add only console-byte modules")
        if module["id"] in base_ids or module["id"] in added_ids:
            raise GraphError(f"patch adds duplicate module id {module['id']!r}")
        added_ids.add(module["id"])

    base_connections = {_connection_key(item) for item in base["connections"]}
    for field in ("remove_connections", "add_connections"):
        if not isinstance(patch[field], list) or not patch[field]:
            raise GraphError(f"patch.{field} must be a non-empty list")
        keys: set[tuple[str, str, str, str]] = set()
        for index, raw_connection in enumerate(patch[field]):
            connection = _object(raw_connection, f"patch.{field}[{index}]")
            _exact_keys(connection, {"from", "to"}, f"patch.{field}[{index}]")
            for endpoint_name in ("from", "to"):
                endpoint = _object(
                    connection[endpoint_name],
                    f"patch.{field}[{index}].{endpoint_name}",
                )
                _exact_keys(
                    endpoint,
                    {"module", "port"},
                    f"patch.{field}[{index}].{endpoint_name}",
                )
                _identifier(endpoint["module"], "patch connection module")
                _identifier(endpoint["port"], "patch connection port")
            key = _connection_key(connection)
            if key in keys:
                raise GraphError(f"patch.{field} contains duplicate connection {key!r}")
            keys.add(key)
        if field == "remove_connections" and not keys <= base_connections:
            raise GraphError("patch removes a connection absent from the base graph")

    _validate_contract(patch["contract"], "patch.contract")
    validate_world(_materialize_patch(base, patch))
    return patch


def apply_patch(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    validate_patch(patch, base)
    return _materialize_patch(base, patch)


def _page_address(value: Any, context: str) -> int:
    address = _integer(value, context)
    if not 0 <= address <= 0xFFFFF000 or address % 0x1000:
        raise GraphError(f"{context} must be a 4 KiB-aligned 32-bit address")
    return address


def _timeout(runner: dict[str, Any], field: str, upper: int = 30) -> None:
    amount = _integer(runner[field], f"target.runner.{field}")
    if not 1 <= amount <= upper:
        raise GraphError(f"target.runner.{field} must be from 1 to {upper}")


def validate_target(value: Any) -> dict[str, Any]:
    target = _object(value, "target")
    _exact_keys(target, TARGET_KEYS, "target")
    if _integer(target["schema_version"], "target.schema_version") != TARGET_SCHEMA_VERSION:
        raise GraphError(f"target.schema_version must be {TARGET_SCHEMA_VERSION}")
    _identifier(target["target_id"], "target.target_id")
    if target["byte_order"] != "little":
        raise GraphError("target.byte_order must be 'little'")
    capabilities = _object(target["capabilities"], "target.capabilities")
    _exact_keys(capabilities, KNOWN_CAPABILITIES, "target.capabilities")
    image = _object(target["image"], "target.image")
    runner = _object(target["runner"], "target.runner")

    if target["architecture"] == "rv32i":
        if target["execution_envelope"] != "native":
            raise GraphError("RV32I graph target must use the native envelope")
        _exact_keys(image, {"load_address", "max_size"}, "target.image")
        load_address = _integer(image["load_address"], "target.image.load_address")
        if not 0 <= load_address <= 0xFFFFFFFF or load_address % 4:
            raise GraphError("target.image.load_address must be an aligned 32-bit address")
        if _integer(image["max_size"], "target.image.max_size") != 256:
            raise GraphError("RV32I target.image.max_size must be 256")
        console = _object(capabilities[CONSOLE_CAPABILITY], "target console.write")
        _exact_keys(console, {"driver", "address"}, "target console.write")
        if console["driver"] != "qemu-virt-uart":
            raise GraphError("RV32I console.write driver must be 'qemu-virt-uart'")
        _page_address(console["address"], "target console.write address")
        machine_exit = _object(capabilities[EXIT_CAPABILITY], "target machine.exit")
        _exact_keys(
            machine_exit, {"driver", "address", "success_value"}, "target machine.exit"
        )
        if machine_exit["driver"] != "qemu-sifive-test":
            raise GraphError("RV32I machine.exit driver must be 'qemu-sifive-test'")
        _page_address(machine_exit["address"], "target machine.exit address")
        success = _integer(machine_exit["success_value"], "target success_value")
        if not 0 <= success <= 0x7FFFFFFF:
            raise GraphError("target success_value must fit signed 32 bits")
        expected_runner = {
            "kind": "qemu",
            "executable": "qemu-system-riscv32",
            "machine": "virt",
            "bios": "none",
            "nographic": True,
            "cpu_num": 0,
            "timeout_seconds": 3,
        }
        _exact_keys(runner, set(expected_runner), "target.runner")
        if runner != expected_runner:
            raise GraphError("RV32I target.runner does not match graph v1 policy")
    elif target["architecture"] == "arm64":
        if target["execution_envelope"] != "hosted":
            raise GraphError("ARM64 graph target must use the hosted envelope")
        _exact_keys(image, {"format", "max_size"}, "target.image")
        if image != {"format": "darwin-arm64-assembly", "max_size": 4096}:
            raise GraphError("ARM64 target.image does not match graph v1 policy")
        console = _object(capabilities[CONSOLE_CAPABILITY], "target console.write")
        _exact_keys(console, {"driver", "file_descriptor"}, "target console.write")
        if console != {"driver": "darwin-posix-write", "file_descriptor": 1}:
            raise GraphError("ARM64 console.write binding does not match graph v1 policy")
        machine_exit = _object(capabilities[EXIT_CAPABILITY], "target machine.exit")
        _exact_keys(machine_exit, {"driver", "status"}, "target machine.exit")
        if machine_exit != {"driver": "darwin-main-return", "status": 0}:
            raise GraphError("ARM64 machine.exit binding does not match graph v1 policy")
        expected_strings = {
            "kind": "darwin-clang",
            "compiler": "clang",
            "architecture": "arm64",
            "minimum_os": "14.0",
        }
        _exact_keys(
            runner,
            set(expected_strings) | {"compile_timeout_seconds", "timeout_seconds"},
            "target.runner",
        )
        for field, expected in expected_strings.items():
            if runner[field] != expected:
                raise GraphError(f"target.runner.{field} must be {expected!r}")
        _timeout(runner, "compile_timeout_seconds", 120)
        _timeout(runner, "timeout_seconds")
    else:
        raise GraphError("target.architecture must be 'rv32i' or 'arm64'")
    return target


def validate_binding(world: dict[str, Any], target: dict[str, Any]) -> None:
    validate_world(world)
    validate_target(target)
    missing = set(world["capabilities"]) - set(target["capabilities"])
    if missing:
        raise GraphError(f"target lacks capabilities {sorted(missing)!r}")


def target_hash(target: dict[str, Any]) -> str:
    validate_target(target)
    return _canonical_hash(target)


def _encode_addi(rd: int, rs1: int, immediate: int) -> int:
    return ((immediate & 0xFFF) << 20) | (rs1 << 15) | (rd << 7) | 0b0010011


def _encode_lui(rd: int, immediate: int) -> int:
    return (immediate << 12) | (rd << 7) | 0b0110111


def _encode_store(rs2: int, rs1: int, funct3: int) -> int:
    return (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | 0b0100011


def _split_lui_addi(value: int) -> tuple[int, int]:
    upper = (value + 0x800) >> 12
    return upper, value - (upper << 12)


def _graph_output(world: dict[str, Any]) -> bytes:
    _, output = _analyze_graph(world)
    return output


def _build_rv32i(world: dict[str, Any], target: dict[str, Any]) -> bytes:
    output = _graph_output(world)
    bindings = target["capabilities"]
    console_address = bindings[CONSOLE_CAPABILITY]["address"]
    exit_binding = bindings[EXIT_CAPABILITY]
    upper, lower = _split_lui_addi(exit_binding["success_value"])
    words = [_encode_lui(5, console_address >> 12)]
    for byte in output:
        words.extend([_encode_addi(6, 0, byte), _encode_store(6, 5, 0b000)])
    words.extend(
        [
            _encode_lui(5, exit_binding["address"] >> 12),
            _encode_lui(6, upper),
            _encode_addi(6, 6, lower),
            _encode_store(6, 5, 0b010),
            0x0000006F,
        ]
    )
    artifact = b"".join(word.to_bytes(4, "little") for word in words)
    if len(artifact) > target["image"]["max_size"]:
        raise GraphError("RV32I artifact exceeds target.image.max_size")
    return artifact


def _build_arm64(world: dict[str, Any], target: dict[str, Any]) -> bytes:
    output = _graph_output(world)
    values = ", ".join(f"0x{byte:02x}" for byte in output)
    fd = target["capabilities"][CONSOLE_CAPABILITY]["file_descriptor"]
    status = target["capabilities"][EXIT_CAPABILITY]["status"]
    source = f""".section __TEXT,__text,regular,pure_instructions
.globl _main
.p2align 2
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    mov w0, #{fd}
    adrp x1, _rabbit_output@PAGE
    add x1, x1, _rabbit_output@PAGEOFF
    mov w2, #{len(output)}
    bl _write
    mov w0, #{status}
    ldp x29, x30, [sp], #16
    ret

.section __TEXT,__const
_rabbit_output:
    .byte {values}
""".encode("ascii")
    if len(source) > target["image"]["max_size"]:
        raise GraphError("ARM64 artifact exceeds target.image.max_size")
    return source


def build_artifact(world: dict[str, Any], target: dict[str, Any]) -> bytes:
    validate_binding(world, target)
    if target["architecture"] == "rv32i":
        return _build_rv32i(world, target)
    return _build_arm64(world, target)


def _run_qemu(artifact: bytes, target: dict[str, Any]) -> dict[str, Any]:
    runner = target["runner"]
    with tempfile.TemporaryDirectory(prefix="rabbit-graph-rv32i-") as temp_dir:
        path = Path(temp_dir) / "world.bin"
        path.write_bytes(artifact)
        command = [
            runner["executable"],
            "-machine",
            runner["machine"],
            "-nographic",
            "-bios",
            runner["bios"],
            "-device",
            f"loader,file={path},addr=0x{target['image']['load_address']:x},cpu-num=0",
        ]
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
            raise GraphError(f"QEMU executable not found: {runner['executable']}") from error
        except subprocess.TimeoutExpired as error:
            raise GraphError("QEMU graph program timed out") from error
    return {
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_status": completed.returncode,
        "execution": {"runner": runner["kind"], "executable": runner["executable"]},
    }


def _run_arm64(artifact: bytes, target: dict[str, Any]) -> dict[str, Any]:
    if platform.system() != "Darwin" or platform.machine().lower() not in {
        "arm64",
        "aarch64",
    }:
        raise GraphError("hosted ARM64 graph target requires an Apple Silicon Mac")
    runner = target["runner"]
    with tempfile.TemporaryDirectory(prefix="rabbit-graph-arm64-") as temp_dir:
        root = Path(temp_dir)
        source = root / "world.s"
        executable = root / "world"
        source.write_bytes(artifact)
        try:
            compiled = subprocess.run(
                [
                    runner["compiler"],
                    "-arch",
                    runner["architecture"],
                    f"-mmacosx-version-min={runner['minimum_os']}",
                    str(source),
                    "-o",
                    str(executable),
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=runner["compile_timeout_seconds"],
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as error:
            raise GraphError(f"ARM64 graph compilation could not finish: {error}") from error
        if compiled.returncode:
            raise GraphError(
                "ARM64 graph compilation failed: "
                + compiled.stderr.decode(errors="replace").strip()
            )
        try:
            completed = subprocess.run(
                [str(executable)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=runner["timeout_seconds"],
            )
        except subprocess.TimeoutExpired as error:
            raise GraphError("hosted ARM64 graph program timed out") from error
    return {
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_status": completed.returncode,
        "execution": {"runner": runner["kind"], "compiler": runner["compiler"]},
    }


def run_artifact(artifact: bytes, target: dict[str, Any]) -> dict[str, Any]:
    validate_target(target)
    if len(artifact) > target["image"]["max_size"]:
        raise GraphError("artifact exceeds target.image.max_size")
    observed = (
        _run_qemu(artifact, target)
        if target["architecture"] == "rv32i"
        else _run_arm64(artifact, target)
    )
    observed["binding"] = {
        "target_sha256": target_hash(target),
        "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
    }
    return observed


def make_report(
    base: dict[str, Any],
    effective: dict[str, Any],
    patch: dict[str, Any] | None,
    target: dict[str, Any],
    artifact: bytes,
    observed: dict[str, Any],
) -> dict[str, Any]:
    expected = apply_patch(base, patch) if patch else base
    if world_hash(effective) != world_hash(expected):
        raise GraphError("effective graph does not match the supplied base and patch")
    expected_artifact = build_artifact(effective, target)
    if artifact != expected_artifact:
        raise GraphError("artifact does not match the effective graph and Target Pack")
    binding = _object(observed.get("binding"), "observed.binding")
    _exact_keys(binding, {"target_sha256", "artifact_sha256"}, "observed.binding")
    if binding["target_sha256"] != target_hash(target):
        raise GraphError("observed evidence belongs to a different Target Pack")
    artifact_hash = hashlib.sha256(artifact).hexdigest()
    if binding["artifact_sha256"] != artifact_hash:
        raise GraphError("observed evidence belongs to a different artifact")
    expected_stdout = effective["contract"]["stdout"].encode("ascii")
    passed = (
        observed["stdout"] == expected_stdout
        and observed["stderr"] == b""
        and observed["exit_status"] == effective["contract"]["exit_status"]
    )
    order, _ = _analyze_graph(effective)
    return {
        "schema_version": 1,
        "world_id": base["world_id"],
        "base_world_sha256": world_hash(base),
        "effective_world_sha256": world_hash(effective),
        "patch_id": patch["patch_id"] if patch else None,
        "target": {
            "target_id": target["target_id"],
            "sha256": target_hash(target),
            "architecture": target["architecture"],
        },
        "graph": {"event_order": order, "module_count": len(effective["modules"])},
        "artifact": {"size": len(artifact), "sha256": artifact_hash},
        "expected": {"stdout_hex": expected_stdout.hex(), "exit_status": 0},
        "observed": {
            "stdout_hex": observed["stdout"].hex(),
            "stderr_hex": observed["stderr"].hex(),
            "exit_status": observed["exit_status"],
        },
        "evidence_binding": dict(binding),
        "execution": dict(observed["execution"]),
        "contract_passed": passed,
    }


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GraphError(f"duplicate JSON field: {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise GraphError(f"non-standard JSON number is not allowed: {value}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (OSError, json.JSONDecodeError) as error:
        raise GraphError(f"could not load {path}: {error}") from error
    return _object(value, str(path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and run Rabbit graph v1")
    parser.add_argument("world", type=Path)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--patch", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        base = load_json(args.world)
        target = load_json(args.target)
        patch = load_json(args.patch) if args.patch else None
        effective = apply_patch(base, patch) if patch else base
        artifact = build_artifact(effective, target)
        observed = run_artifact(artifact, target)
        report = make_report(base, effective, patch, target, artifact, observed)
        if args.output:
            args.output.write_bytes(artifact)
        if args.report:
            args.report.write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        print(
            f"WORLD: {base['world_id']}\n"
            f"TARGET: {target['target_id']}\n"
            f"PATCH: {patch['patch_id'] if patch else 'none'}\n"
            f"GRAPH ORDER: {' -> '.join(report['graph']['event_order'])}\n"
            f"OBSERVED: {bytes.fromhex(report['observed']['stdout_hex'])!r}, "
            f"exit={report['observed']['exit_status']}"
        )
        if report["contract_passed"]:
            print("PASS: observed graph behavior matches the typed contract")
            return 0
        print("FAIL: observed graph behavior does not match the typed contract")
        return 1
    except GraphError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
