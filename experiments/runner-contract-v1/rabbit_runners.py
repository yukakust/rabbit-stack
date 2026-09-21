#!/usr/bin/env python3
"""One explicit Runner Contract for hosted, native, and bridge execution."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CAP_ROOT = ROOT.parent / "capability-negotiation-v1"
sys.path.insert(0, str(CAP_ROOT))
import rabbit_capabilities as caps  # noqa: E402


RunnerError = caps.GraphError
TARGET_KEYS = {
    "schema_version", "target_id", "execution_envelope", "architecture",
    "byte_order", "image", "capability_offers", "runner", "runner_contract",
}
CONTRACT_KEYS = {
    "version", "envelope", "transport", "authority", "remaining_layers",
    "mutations", "timeouts", "recovery", "protocol", "simulation",
}


def canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def exact(value: dict[str, Any], keys: set[str], context: str) -> None:
    missing, unknown = keys - set(value), set(value) - keys
    if missing or unknown:
        raise RunnerError(f"{context} fields mismatch: missing={sorted(missing)!r}, unknown={sorted(unknown)!r}")


def string_list(value: Any, context: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise RunnerError(f"{context} must be a non-empty string list")
    if len(set(value)) != len(value):
        raise RunnerError(f"{context} contains duplicates")
    return value


def validate_runner_contract(value: Any, envelope: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RunnerError("runner_contract must be an object")
    exact(value, CONTRACT_KEYS, "runner_contract")
    if value["version"] != 1 or value["envelope"] != envelope:
        raise RunnerError("runner_contract version or envelope is mislabeled")
    for field in ("authority", "remaining_layers", "mutations"):
        string_list(value[field], f"runner_contract.{field}")
    timeouts = value["timeouts"]
    if not isinstance(timeouts, dict):
        raise RunnerError("runner_contract.timeouts must be an object")
    exact(timeouts, {"startup_seconds", "execution_seconds"}, "runner_contract.timeouts")
    if not all(type(timeouts[x]) is int and 1 <= timeouts[x] <= 120 for x in timeouts):
        raise RunnerError("runner timeouts must be integers from 1 to 120")
    recovery = value["recovery"]
    if not isinstance(recovery, dict):
        raise RunnerError("runner_contract.recovery must be an object")
    exact(recovery, {"method", "persistent_writes"}, "runner_contract.recovery")
    if not isinstance(recovery["method"], str) or not recovery["method"]:
        raise RunnerError("runner recovery method is required")
    if recovery["persistent_writes"] is not False:
        raise RunnerError("runner v1 forbids persistent writes")
    if type(value["simulation"]) is not bool:
        raise RunnerError("runner_contract.simulation must be boolean")
    policies = {
        "native": {
            "transport": "qemu-loader",
            "authority": ["execute-emulated-machine", "write-emulated-uart"],
            "remaining_layers": ["qemu", "host-operating-system", "physical-host"],
            "mutations": ["temporary-artifact-file"],
            "recovery": "terminate-qemu-and-delete-temporary-directory",
            "simulation": True,
        },
        "hosted": {
            "transport": "process-exec",
            "authority": ["compile-temporary-executable", "execute-hosted-process", "write-process-stdout"],
            "remaining_layers": ["apple-clang", "mach-o-linker", "macos", "libsystem"],
            "mutations": ["temporary-source-file", "temporary-executable-file"],
            "recovery": "terminate-process-and-delete-temporary-directory",
            "simulation": False,
        },
        "bridge": {
            "transport": "stdio",
            "authority": ["start-simulated-device", "send-framed-command"],
            "remaining_layers": ["python", "host-operating-system", "simulated-device-process"],
            "mutations": ["none"],
            "recovery": "terminate-child-process",
            "simulation": True,
        },
    }
    policy = policies[envelope]
    for field in ("transport", "authority", "remaining_layers", "mutations", "simulation"):
        if value[field] != policy[field]:
            raise RunnerError(f"runner_contract.{field} violates reviewed {envelope} policy")
    if recovery["method"] != policy["recovery"]:
        raise RunnerError("runner recovery method violates reviewed policy")
    if envelope == "bridge":
        protocol = value["protocol"]
        if not isinstance(protocol, dict):
            raise RunnerError("bridge runner requires a protocol declaration")
        exact(protocol, {"name", "version", "framing", "max_frame_bytes"}, "runner protocol")
        if protocol != {
            "name": "rabbit-frame", "version": 1,
            "framing": "u32-big-endian-length-plus-canonical-json",
            "max_frame_bytes": 4096,
        }:
            raise RunnerError("bridge protocol does not match rabbit-frame/1")
        if value["transport"] != "stdio" or value["simulation"] is not True:
            raise RunnerError("bridge v1 must be an explicitly simulated stdio transport")
    elif value["protocol"] is not None:
        raise RunnerError("hosted/native runner protocol must be null")
    return value


def capability_target(target: dict[str, Any]) -> dict[str, Any]:
    contract = target["runner_contract"]
    return {
        "schema_version": 3,
        "target_id": target["target_id"],
        "execution_envelope": target["execution_envelope"],
        "architecture": target["architecture"],
        "byte_order": target["byte_order"],
        "image": copy.deepcopy(target["image"]),
        "capability_offers": copy.deepcopy(target["capability_offers"]),
        "remaining_layers": copy.deepcopy(contract["remaining_layers"]),
        "runner": copy.deepcopy(target["runner"]),
    }


def validate_bridge_target(target: dict[str, Any]) -> None:
    if target["architecture"] != "protocol-v1" or target["byte_order"] != "not-applicable":
        raise RunnerError("bridge target architecture must be protocol-v1")
    if target["image"] != {"format": "ascii-payload", "max_size": 16}:
        raise RunnerError("bridge artifact policy mismatch")
    runner = target["runner"]
    if runner != {
        "kind": "python-stdio-bridge", "executable": "python3",
        "device": "bridge_device.py", "timeout_seconds": 3,
    }:
        raise RunnerError("bridge runner implementation is unreviewed")
    offers = target["capability_offers"]
    if not isinstance(offers, list) or len(offers) != 2:
        raise RunnerError("bridge must offer display.text and machine.exit")
    display, exit_offer = offers
    if display != {
        "capability": "display.text", "version": 1,
        "driver": "rabbit-frame-display",
        "limits": {"encodings": ["ascii"], "max_bytes": 16},
        "binding": {"channel": "display"},
        "effects": ["writes-simulated-device-display"],
    }:
        raise RunnerError("bridge display.text offer is unreviewed")
    if exit_offer != {
        "capability": "machine.exit", "version": 1,
        "driver": "rabbit-frame-complete",
        "limits": {"statuses": [0]},
        "binding": {"channel": "control", "status": 0},
        "effects": ["completes-simulated-device-command"],
    }:
        raise RunnerError("bridge machine.exit offer is unreviewed")


def validate_target(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RunnerError("target must be an object")
    exact(value, TARGET_KEYS, "target")
    if value["schema_version"] != 4:
        raise RunnerError("target.schema_version must be 4")
    envelope = value["execution_envelope"]
    if envelope not in {"hosted", "native", "bridge"}:
        raise RunnerError("unsupported execution envelope")
    validate_runner_contract(value["runner_contract"], envelope)
    if envelope == "bridge":
        validate_bridge_target(value)
    else:
        caps.validate_target(capability_target(value))
    return value


def target_hash(target: dict[str, Any]) -> str:
    validate_target(target)
    return digest(target)


def runner_hash(target: dict[str, Any]) -> str:
    validate_target(target)
    return digest(target["runner_contract"])


def resolve(world: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    caps.validate_world(world)
    validate_target(target)
    if target["execution_envelope"] != "bridge":
        inner = caps.resolve_capabilities(world, capability_target(target))
        inner["target_sha256"] = target_hash(target)
        inner["remaining_layers"] = copy.deepcopy(target["runner_contract"]["remaining_layers"])
        return inner
    bindings, omitted = [], []
    offers = {x["capability"]: x for x in target["capability_offers"]}
    for request in world["capabilities"]:
        offer = offers.get(request["capability"])
        if offer is None:
            if request["required"]:
                raise RunnerError(f"required capability {request['capability']!r} is not offered")
            omitted.append({"capability": request["capability"], "version": request["version"], "reason": "not-offered"})
            continue
        if request["version"] != offer["version"]:
            raise RunnerError(f"required capability {request['capability']!r} has incompatible version")
        if request["capability"] == "display.text" and request["constraints"]["max_bytes"] > offer["limits"]["max_bytes"]:
            raise RunnerError("display.text exceeds bridge limit")
        bindings.append({
            "capability": request["capability"], "version": request["version"],
            "driver": offer["driver"], "constraints": copy.deepcopy(request["constraints"]),
            "limits": copy.deepcopy(offer["limits"]), "binding": copy.deepcopy(offer["binding"]),
            "effects": copy.deepcopy(offer["effects"]),
        })
    return {
        "schema_version": 1, "world_id": world["world_id"],
        "world_sha256": caps.world_hash(world), "target_id": target["target_id"],
        "target_sha256": target_hash(target), "bindings": bindings,
        "omitted_optional": omitted,
        "remaining_layers": copy.deepcopy(target["runner_contract"]["remaining_layers"]),
    }


def plan_hash(plan: dict[str, Any], world: dict[str, Any], target: dict[str, Any]) -> str:
    if plan != resolve(world, target):
        raise RunnerError("runner deployment plan is stale")
    return digest(plan)


def inner_plan(world: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    return caps.resolve_capabilities(world, capability_target(target))


def build_artifact(world: dict[str, Any], target: dict[str, Any], plan: dict[str, Any]) -> bytes:
    plan_hash(plan, world, target)
    if target["execution_envelope"] == "bridge":
        artifact = world["contract"]["stdout"].encode("ascii")
        if len(artifact) > target["image"]["max_size"]:
            raise RunnerError("bridge payload exceeds target limit")
        return artifact
    return caps.build_artifact(world, capability_target(target), inner_plan(world, target))


def frame(value: dict[str, Any]) -> bytes:
    body = canonical(value)
    return struct.pack(">I", len(body)) + body


def parse_frame(raw: bytes) -> tuple[dict[str, Any], bytes]:
    if len(raw) < 4:
        raise RunnerError("bridge response lacks frame header")
    size = struct.unpack(">I", raw[:4])[0]
    body = raw[4:]
    if size != len(body) or size > 4096:
        raise RunnerError("bridge response frame length is invalid")
    try:
        value = json.loads(body.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RunnerError("bridge response is not canonical JSON") from error
    if canonical(value) != body:
        raise RunnerError("bridge response JSON is not canonical")
    return value, body


def bridge_exchange(world: dict[str, Any], plan: dict[str, Any], artifact: bytes) -> tuple[dict[str, Any], bytes, dict[str, Any], bytes, dict[str, str]]:
    request = {
        "protocol": "rabbit-frame/1", "plan_sha256": digest(plan),
        "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
        "output_hex": artifact.hex(), "exit_status": world["contract"]["exit_status"],
    }
    request_body = canonical(request)
    tx = frame(request)
    response = {
        "protocol": "rabbit-frame/1",
        "request_sha256": hashlib.sha256(request_body).hexdigest(),
        "output_hex": artifact.hex(), "exit_status": 0,
    }
    response_body = canonical(response)
    rx = frame(response)
    transcript = {
        "request_sha256": hashlib.sha256(request_body).hexdigest(),
        "response_sha256": hashlib.sha256(response_body).hexdigest(),
        "transcript_sha256": hashlib.sha256(tx + rx).hexdigest(),
    }
    return request, tx, response, rx, transcript


def communicate_bridge(command: list[str], tx: bytes, timeout: float) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            command, input=tx, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise RunnerError("bridge device timed out") from error


def run_artifact(artifact: bytes, world: dict[str, Any], target: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    current_plan_hash = plan_hash(plan, world, target)
    if target["execution_envelope"] != "bridge":
        observed = caps.run_artifact(artifact, world, capability_target(target), inner_plan(world, target))
        transcript = None
    else:
        request, tx, expected_response, expected_rx, transcript = bridge_exchange(world, plan, artifact)
        device = ROOT / target["runner"]["device"]
        completed = communicate_bridge(
            [sys.executable, str(device)], tx,
            target["runner_contract"]["timeouts"]["execution_seconds"],
        )
        if completed.returncode != 0 or completed.stderr:
            raise RunnerError(f"bridge device rejected frame: {completed.stderr.decode(errors='replace').strip()}")
        response, response_body = parse_frame(completed.stdout)
        if response != expected_response or completed.stdout != expected_rx:
            raise RunnerError("bridge response does not match request")
        observed = {
            "stdout": bytes.fromhex(response["output_hex"]), "stderr": b"",
            "exit_status": response["exit_status"],
            "execution": {"runner": "python-stdio-bridge", "simulation": True},
        }
    observed["runner_binding"] = {
        "world_sha256": caps.world_hash(world), "target_sha256": target_hash(target),
        "plan_sha256": current_plan_hash, "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
        "runner_sha256": runner_hash(target), "transcript": transcript,
    }
    return observed


def make_report(world: dict[str, Any], target: dict[str, Any], plan: dict[str, Any], artifact: bytes, observed: dict[str, Any]) -> dict[str, Any]:
    expected_artifact = build_artifact(world, target, plan)
    if artifact != expected_artifact:
        raise RunnerError("artifact does not match runner plan")
    expected_transcript = (
        bridge_exchange(world, plan, artifact)[4]
        if target["execution_envelope"] == "bridge" else None
    )
    expected_binding = {
        "world_sha256": caps.world_hash(world), "target_sha256": target_hash(target),
        "plan_sha256": plan_hash(plan, world, target),
        "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
        "runner_sha256": runner_hash(target),
        "transcript": expected_transcript,
    }
    if observed.get("runner_binding") != expected_binding:
        raise RunnerError("evidence is not bound to exact world, target, plan, artifact, and runner")
    if target["execution_envelope"] == "bridge" and expected_binding["transcript"] is None:
        raise RunnerError("bridge evidence is missing protocol transcript")
    passed = (
        observed["stdout"] == world["contract"]["stdout"].encode("ascii")
        and observed["stderr"] == b"" and observed["exit_status"] == 0
    )
    return {
        "schema_version": 1, "world_sha256": caps.world_hash(world),
        "target_sha256": target_hash(target), "plan_sha256": plan_hash(plan, world, target),
        "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
        "runner_sha256": runner_hash(target), "envelope": target["execution_envelope"],
        "runner_contract": copy.deepcopy(target["runner_contract"]),
        "transcript": copy.deepcopy(expected_binding["transcript"]),
        "observed": {"stdout_hex": observed["stdout"].hex(), "stderr_hex": observed["stderr"].hex(), "exit_status": observed["exit_status"]},
        "contract_passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one world through Runner Contract v1")
    parser.add_argument("world", type=Path)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--patch", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        base = caps.load_json(args.world)
        patch = caps.load_json(args.patch) if args.patch else None
        world = caps.apply_patch(base, patch) if patch else base
        target = caps.load_json(args.target)
        plan = resolve(world, target)
        artifact = build_artifact(world, target, plan)
        observed = run_artifact(artifact, world, target, plan)
        report = make_report(world, target, plan, artifact, observed)
        if args.report:
            args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"ENVELOPE: {target['execution_envelope']}")
        print(f"RUNNER: sha256={runner_hash(target)}")
        print(f"OBSERVED: {observed['stdout']!r}, exit={observed['exit_status']}")
        if report["transcript"]:
            print(f"TRANSCRIPT: sha256={report['transcript']['transcript_sha256']}")
        print("PASS: Runner Contract observed the semantic contract")
        return 0 if report["contract_passed"] else 1
    except RunnerError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
