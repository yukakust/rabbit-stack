#!/usr/bin/env python3
"""Resolve semantic capabilities before lowering a Universal Rabbit graph."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
GRAPH_ROOT = ROOT.parent / "universal-graph-v1"
sys.path.insert(0, str(GRAPH_ROOT))
import rabbit_graph as graph  # noqa: E402


GraphError = graph.GraphError
WORLD_SCHEMA_VERSION = 1
TARGET_SCHEMA_VERSION = 3
PLAN_SCHEMA_VERSION = 1
SEMANTIC_CAPABILITIES = {"display.text", "machine.exit", "light.emit"}
WORLD_KEYS = graph.WORLD_KEYS
PATCH_KEYS = graph.PATCH_KEYS
TARGET_KEYS = {
    "schema_version",
    "target_id",
    "execution_envelope",
    "architecture",
    "byte_order",
    "image",
    "capability_offers",
    "remaining_layers",
    "runner",
}
REQUEST_KEYS = {"capability", "version", "required", "constraints"}
OFFER_KEYS = {
    "capability",
    "version",
    "driver",
    "limits",
    "binding",
    "effects",
}
PLAN_KEYS = {
    "schema_version",
    "world_id",
    "world_sha256",
    "target_id",
    "target_sha256",
    "bindings",
    "omitted_optional",
    "remaining_layers",
}


def _object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GraphError(f"{context} must be a JSON object")
    return value


def _exact(value: dict[str, Any], expected: set[str], context: str) -> None:
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


def _canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _graph_world(world: dict[str, Any]) -> dict[str, Any]:
    lowered = copy.deepcopy(world)
    lowered["capabilities"] = ["console.write", "machine.exit"]
    return lowered


def _validate_request(value: Any, context: str) -> dict[str, Any]:
    request = _object(value, context)
    _exact(request, REQUEST_KEYS, context)
    capability = _string(request["capability"], f"{context}.capability")
    if capability not in SEMANTIC_CAPABILITIES:
        raise GraphError(f"{context}.capability {capability!r} is unknown")
    version = _integer(request["version"], f"{context}.version")
    if not 1 <= version <= 16:
        raise GraphError(f"{context}.version must be from 1 to 16")
    if type(request["required"]) is not bool:
        raise GraphError(f"{context}.required must be a boolean")
    constraints = _object(request["constraints"], f"{context}.constraints")
    if capability == "display.text":
        _exact(constraints, {"encoding", "max_bytes"}, f"{context}.constraints")
        if constraints["encoding"] != "ascii":
            raise GraphError("display.text encoding must be 'ascii' in v1")
        maximum = _integer(
            constraints["max_bytes"], f"{context}.constraints.max_bytes"
        )
        if not 1 <= maximum <= 128:
            raise GraphError("display.text max_bytes must be from 1 to 128")
    elif capability == "machine.exit":
        _exact(constraints, {"status"}, f"{context}.constraints")
        if _integer(constraints["status"], f"{context}.constraints.status") != 0:
            raise GraphError("machine.exit status must be 0 in v1")
    else:
        _exact(
            constraints,
            {"color", "brightness_percent"},
            f"{context}.constraints",
        )
        if constraints["color"] not in {"white", "red", "green", "blue"}:
            raise GraphError("light.emit color is unsupported in v1")
        brightness = _integer(
            constraints["brightness_percent"],
            f"{context}.constraints.brightness_percent",
        )
        if not 1 <= brightness <= 100:
            raise GraphError("light.emit brightness_percent must be from 1 to 100")
    return request


def validate_world(value: Any) -> dict[str, Any]:
    world = _object(value, "world")
    _exact(world, WORLD_KEYS, "world")
    requests = world["capabilities"]
    if not isinstance(requests, list) or not requests:
        raise GraphError("world.capabilities must be a non-empty request list")
    seen: set[str] = set()
    for index, raw_request in enumerate(requests):
        request = _validate_request(raw_request, f"world.capabilities[{index}]")
        capability = request["capability"]
        if capability in seen:
            raise GraphError(f"duplicate capability request {capability!r}")
        seen.add(capability)
    for required in ("display.text", "machine.exit"):
        request = next((item for item in requests if item["capability"] == required), None)
        if request is None or request["required"] is not True:
            raise GraphError(f"{required} must be requested as required")
    graph.validate_world(_graph_world(world))
    display = next(item for item in requests if item["capability"] == "display.text")
    if len(world["contract"]["stdout"].encode("ascii")) > display["constraints"]["max_bytes"]:
        raise GraphError("world output exceeds requested display.text max_bytes")
    return world


def world_hash(world: dict[str, Any]) -> str:
    validate_world(world)
    return _canonical_hash(world)


def validate_patch(value: Any, base: dict[str, Any]) -> dict[str, Any]:
    validate_world(base)
    patch = _object(value, "patch")
    _exact(patch, PATCH_KEYS, "patch")
    if _string(patch["base_hash"], "patch.base_hash") != world_hash(base):
        raise GraphError(
            f"patch.base_hash must identify exact semantic world {world_hash(base)}"
        )
    translated = copy.deepcopy(patch)
    translated["base_hash"] = graph.world_hash(_graph_world(base))
    graph.validate_patch(translated, _graph_world(base))
    candidate = apply_patch(base, patch, already_validated=True)
    validate_world(candidate)
    return patch


def apply_patch(
    base: dict[str, Any],
    patch: dict[str, Any],
    already_validated: bool = False,
) -> dict[str, Any]:
    if not already_validated:
        validate_patch(patch, base)
    translated = copy.deepcopy(patch)
    translated["base_hash"] = graph.world_hash(_graph_world(base))
    effective_graph = graph.apply_patch(_graph_world(base), translated)
    effective_graph["capabilities"] = copy.deepcopy(base["capabilities"])
    return effective_graph


def _validate_string_list(value: Any, context: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item for item in value
    ):
        raise GraphError(f"{context} must be a non-empty string list")
    if len(set(value)) != len(value):
        raise GraphError(f"{context} must not contain duplicates")
    return value


def _validate_offer(value: Any, context: str, architecture: str) -> dict[str, Any]:
    offer = _object(value, context)
    _exact(offer, OFFER_KEYS, context)
    capability = _string(offer["capability"], f"{context}.capability")
    if capability not in {"display.text", "machine.exit"}:
        raise GraphError(f"{context} advertises undeclared capability {capability!r}")
    if _integer(offer["version"], f"{context}.version") != 1:
        raise GraphError(f"{context}.version must be 1")
    effects = _validate_string_list(offer["effects"], f"{context}.effects")
    limits = _object(offer["limits"], f"{context}.limits")
    binding = _object(offer["binding"], f"{context}.binding")
    driver = _string(offer["driver"], f"{context}.driver")

    if capability == "display.text":
        _exact(limits, {"encodings", "max_bytes"}, f"{context}.limits")
        if limits["encodings"] != ["ascii"]:
            raise GraphError("display.text offer encodings must be ['ascii']")
        if _integer(limits["max_bytes"], f"{context}.limits.max_bytes") != 16:
            raise GraphError("display.text offer max_bytes must be 16")
        if architecture == "rv32i":
            if driver != "qemu-virt-uart":
                raise GraphError("RV32I display.text driver must be 'qemu-virt-uart'")
            _exact(binding, {"address"}, f"{context}.binding")
            if binding["address"] != 268435456 or effects != ["writes-emulated-uart"]:
                raise GraphError("RV32I display.text offer violates reviewed policy")
        else:
            if driver != "darwin-posix-write":
                raise GraphError("ARM64 display.text driver must be 'darwin-posix-write'")
            _exact(binding, {"file_descriptor"}, f"{context}.binding")
            if binding["file_descriptor"] != 1 or effects != ["writes-process-stdout"]:
                raise GraphError("ARM64 display.text offer violates reviewed policy")
    else:
        _exact(limits, {"statuses"}, f"{context}.limits")
        if limits["statuses"] != [0]:
            raise GraphError("machine.exit offer statuses must be [0]")
        if architecture == "rv32i":
            if driver != "qemu-sifive-test":
                raise GraphError("RV32I machine.exit driver must be 'qemu-sifive-test'")
            _exact(binding, {"address", "success_value"}, f"{context}.binding")
            if binding != {"address": 1048576, "success_value": 21845} or effects != [
                "terminates-emulated-machine"
            ]:
                raise GraphError("RV32I machine.exit offer violates reviewed policy")
        else:
            if driver != "darwin-main-return":
                raise GraphError("ARM64 machine.exit driver must be 'darwin-main-return'")
            _exact(binding, {"status"}, f"{context}.binding")
            if binding != {"status": 0} or effects != ["terminates-hosted-process"]:
                raise GraphError("ARM64 machine.exit offer violates reviewed policy")
    return offer


def _offer_map(target: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["capability"]: item for item in target["capability_offers"]}


def _graph_target(target: dict[str, Any]) -> dict[str, Any]:
    offers = _offer_map(target)
    display = offers["display.text"]
    machine_exit = offers["machine.exit"]
    if target["architecture"] == "rv32i":
        capabilities = {
            "console.write": {"driver": display["driver"], **display["binding"]},
            "machine.exit": {"driver": machine_exit["driver"], **machine_exit["binding"]},
        }
    else:
        capabilities = {
            "console.write": {"driver": display["driver"], **display["binding"]},
            "machine.exit": {"driver": machine_exit["driver"], **machine_exit["binding"]},
        }
    return {
        "schema_version": 2,
        "target_id": target["target_id"],
        "execution_envelope": target["execution_envelope"],
        "architecture": target["architecture"],
        "byte_order": target["byte_order"],
        "image": copy.deepcopy(target["image"]),
        "capabilities": capabilities,
        "runner": copy.deepcopy(target["runner"]),
    }


def validate_target(value: Any) -> dict[str, Any]:
    target = _object(value, "target")
    _exact(target, TARGET_KEYS, "target")
    if _integer(target["schema_version"], "target.schema_version") != TARGET_SCHEMA_VERSION:
        raise GraphError(f"target.schema_version must be {TARGET_SCHEMA_VERSION}")
    architecture = target["architecture"]
    if architecture not in {"rv32i", "arm64"}:
        raise GraphError("target.architecture must be 'rv32i' or 'arm64'")
    offers = target["capability_offers"]
    if not isinstance(offers, list):
        raise GraphError("target.capability_offers must be a list")
    seen: set[str] = set()
    for index, raw_offer in enumerate(offers):
        offer = _validate_offer(raw_offer, f"target.capability_offers[{index}]", architecture)
        if offer["capability"] in seen:
            raise GraphError(f"duplicate capability offer {offer['capability']!r}")
        seen.add(offer["capability"])
    if seen != {"display.text", "machine.exit"}:
        raise GraphError("target must advertise exactly display.text and machine.exit")
    layers = _validate_string_list(target["remaining_layers"], "target.remaining_layers")
    expected_layers = (
        ["qemu", "host-operating-system", "physical-host"]
        if architecture == "rv32i"
        else ["apple-clang", "mach-o-linker", "macos", "libsystem"]
    )
    if layers != expected_layers:
        raise GraphError("target.remaining_layers does not match reviewed policy")
    graph.validate_target(_graph_target(target))
    return target


def target_hash(target: dict[str, Any]) -> str:
    validate_target(target)
    return _canonical_hash(target)


def _compatible(request: dict[str, Any], offer: dict[str, Any]) -> tuple[bool, str]:
    if request["version"] != offer["version"]:
        return False, "incompatible-version"
    constraints = request["constraints"]
    limits = offer["limits"]
    if request["capability"] == "display.text":
        if constraints["encoding"] not in limits["encodings"]:
            return False, "unsupported-encoding"
        if constraints["max_bytes"] > limits["max_bytes"]:
            return False, "max-bytes-exceeds-offer"
    elif request["capability"] == "machine.exit":
        if constraints["status"] not in limits["statuses"]:
            return False, "unsupported-exit-status"
    return True, "compatible"


def resolve_capabilities(
    world: dict[str, Any], target: dict[str, Any]
) -> dict[str, Any]:
    validate_world(world)
    validate_target(target)
    offers = _offer_map(target)
    bindings: list[dict[str, Any]] = []
    omitted: list[dict[str, Any]] = []
    for request in world["capabilities"]:
        offer = offers.get(request["capability"])
        if offer is None:
            if request["required"]:
                raise GraphError(
                    f"required capability {request['capability']!r} is not offered"
                )
            omitted.append(
                {
                    "capability": request["capability"],
                    "version": request["version"],
                    "reason": "not-offered",
                }
            )
            continue
        compatible, reason = _compatible(request, offer)
        if not compatible:
            if request["required"]:
                raise GraphError(
                    f"required capability {request['capability']!r} is incompatible: {reason}"
                )
            omitted.append(
                {
                    "capability": request["capability"],
                    "version": request["version"],
                    "reason": reason,
                }
            )
            continue
        bindings.append(
            {
                "capability": request["capability"],
                "version": request["version"],
                "driver": offer["driver"],
                "constraints": copy.deepcopy(request["constraints"]),
                "limits": copy.deepcopy(offer["limits"]),
                "binding": copy.deepcopy(offer["binding"]),
                "effects": copy.deepcopy(offer["effects"]),
            }
        )
    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "world_id": world["world_id"],
        "world_sha256": world_hash(world),
        "target_id": target["target_id"],
        "target_sha256": target_hash(target),
        "bindings": bindings,
        "omitted_optional": omitted,
        "remaining_layers": copy.deepcopy(target["remaining_layers"]),
    }


def validate_plan(
    value: Any, world: dict[str, Any], target: dict[str, Any]
) -> dict[str, Any]:
    plan = _object(value, "plan")
    _exact(plan, PLAN_KEYS, "plan")
    expected = resolve_capabilities(world, target)
    if plan != expected:
        raise GraphError("deployment plan is stale or does not match world and target")
    return plan


def plan_hash(
    plan: dict[str, Any], world: dict[str, Any], target: dict[str, Any]
) -> str:
    validate_plan(plan, world, target)
    return _canonical_hash(plan)


def build_artifact(
    world: dict[str, Any], target: dict[str, Any], plan: dict[str, Any]
) -> bytes:
    validate_plan(plan, world, target)
    return graph.build_artifact(_graph_world(world), _graph_target(target))


def run_artifact(
    artifact: bytes,
    world: dict[str, Any],
    target: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    validate_plan(plan, world, target)
    observed = graph.run_artifact(artifact, _graph_target(target))
    observed["binding"] = {
        "world_sha256": world_hash(world),
        "target_sha256": target_hash(target),
        "plan_sha256": plan_hash(plan, world, target),
        "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
    }
    return observed


def make_report(
    base: dict[str, Any],
    effective: dict[str, Any],
    patch: dict[str, Any] | None,
    target: dict[str, Any],
    plan: dict[str, Any],
    artifact: bytes,
    observed: dict[str, Any],
) -> dict[str, Any]:
    expected_world = apply_patch(base, patch) if patch else base
    if world_hash(effective) != world_hash(expected_world):
        raise GraphError("effective semantic world does not match base and patch")
    validate_plan(plan, effective, target)
    expected_artifact = build_artifact(effective, target, plan)
    if artifact != expected_artifact:
        raise GraphError("artifact does not match semantic world, target, and plan")
    binding = _object(observed.get("binding"), "observed.binding")
    expected_binding = {
        "world_sha256": world_hash(effective),
        "target_sha256": target_hash(target),
        "plan_sha256": plan_hash(plan, effective, target),
        "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
    }
    if binding != expected_binding:
        raise GraphError("observed evidence is not bound to exact world, target, plan, and artifact")
    expected_stdout = effective["contract"]["stdout"].encode("ascii")
    passed = (
        observed["stdout"] == expected_stdout
        and observed["stderr"] == b""
        and observed["exit_status"] == effective["contract"]["exit_status"]
    )
    return {
        "schema_version": 1,
        "world_id": base["world_id"],
        "base_world_sha256": world_hash(base),
        "effective_world_sha256": world_hash(effective),
        "patch_id": patch["patch_id"] if patch else None,
        "target_id": target["target_id"],
        "target_sha256": target_hash(target),
        "plan": copy.deepcopy(plan),
        "plan_sha256": plan_hash(plan, effective, target),
        "artifact": {
            "size": len(artifact),
            "sha256": hashlib.sha256(artifact).hexdigest(),
        },
        "observed": {
            "stdout_hex": observed["stdout"].hex(),
            "stderr_hex": observed["stderr"].hex(),
            "exit_status": observed["exit_status"],
        },
        "evidence_binding": copy.deepcopy(binding),
        "execution": copy.deepcopy(observed["execution"]),
        "contract_passed": passed,
    }


def load_json(path: Path) -> dict[str, Any]:
    return graph.load_json(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Negotiate and run Rabbit capabilities v1")
    parser.add_argument("world", type=Path)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--patch", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        base = load_json(args.world)
        target = load_json(args.target)
        patch = load_json(args.patch) if args.patch else None
        effective = apply_patch(base, patch) if patch else base
        plan = resolve_capabilities(effective, target)
        artifact = build_artifact(effective, target, plan)
        observed = run_artifact(artifact, effective, target, plan)
        report = make_report(base, effective, patch, target, plan, artifact, observed)
        if args.plan:
            args.plan.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
        if args.output:
            args.output.write_bytes(artifact)
        if args.report:
            args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"WORLD: {effective['world_id']} sha256={world_hash(effective)}")
        print(f"TARGET: {target['target_id']} sha256={target_hash(target)}")
        print(f"PLAN: sha256={plan_hash(plan, effective, target)}")
        for binding in plan["bindings"]:
            print(f"BOUND: {binding['capability']} -> {binding['driver']}")
        for omitted in plan["omitted_optional"]:
            print(f"OMITTED OPTIONAL: {omitted['capability']} ({omitted['reason']})")
        print(
            f"OBSERVED: {observed['stdout']!r}, stderr={observed['stderr']!r}, "
            f"exit={observed['exit_status']}"
        )
        if report["contract_passed"]:
            print("PASS: negotiated behavior matches the semantic contract")
            return 0
        print("FAIL: negotiated behavior does not match the semantic contract")
        return 1
    except GraphError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
