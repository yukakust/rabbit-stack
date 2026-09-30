#!/usr/bin/env python3
"""Verify the exact Scene/Anima v2 hosted reference execution contract."""

from __future__ import annotations

import copy
import json
import subprocess
import tempfile
from pathlib import Path

from rabbit_scene import (
    CATALOG_PATH,
    MERGE_PATH,
    ROOT,
    SceneError,
    execute,
    load_json,
    load_reviewed_creation,
    render_rgb,
    run_ticks,
    sha256_hex,
)


EXPECTED_TRACE_SHA256 = "1cfa264a561935ffe591184400ddf66dc0482f94be16a5f188a8dd499b9d62ab"
EXPECTED_FINAL_RGB_SHA256 = "39959b325ca7b419e022993ccc54c6131ef41caad35815a9415526832ad31ce7"
EXPECTED_CONTRACT_SHA256 = "7e6bc4af52f21da5001ed9be6068347799b312fe16021babab94b938530dd2cb"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rejected(label: str, action: object) -> None:
    try:
        action()  # type: ignore[operator]
    except SceneError as error:
        print(f"PASS: rejected {label}: {error}")
        return
    raise AssertionError(f"did not reject {label}")


def no_floats(value: object) -> bool:
    if isinstance(value, float):
        return False
    if isinstance(value, dict):
        return all(no_floats(item) for item in value.values())
    if isinstance(value, list):
        return all(no_floats(item) for item in value)
    return True


def main() -> int:
    result = execute(240)
    contract = result["contract"]
    trace = result["trace"]
    require(result["trace_sha256"] == EXPECTED_TRACE_SHA256, "deterministic trace identity changed")
    require(result["final_rgb_sha256"] == EXPECTED_FINAL_RGB_SHA256, "final raster identity changed")
    from rabbit_scene import canonical_bytes
    require(sha256_hex(canonical_bytes(contract)) == EXPECTED_CONTRACT_SHA256, "runner contract identity changed")
    require(len(trace) == 241 and trace[0]["tick"] == 0 and trace[-1]["tick"] == 240, "tick boundary changed")
    require(no_floats(trace), "trace contains non-deterministic floating point values")
    states = {state["cat_state"] for state in trace}
    require(states == {"look", "chase", "pounce", "bat", "wait"}, "Cat Anima state coverage changed")
    require(max(state["bat_count"] for state in trace) == 5, "cat/ball collision count changed")
    require(max(state["edge_bounce_count"] for state in trace) == 12, "ball edge collision count changed")
    require({state["cat_frame"] for state in trace} == {0, 1}, "cat frame animation did not advance")
    require(all(0 <= state[entity]["x"] <= 152 and 0 <= state[entity]["y"] <= 82 for state in trace for entity in ("cat", "ball")), "entity escaped scene bounds")
    repeated = execute(240)
    require(repeated["trace_sha256"] == result["trace_sha256"] and repeated["final_rgb"] == result["final_rgb"], "second execution was not identical")

    with tempfile.TemporaryDirectory(prefix="rabbit-scene-v2-") as directory:
        temporary = Path(directory)
        output = temporary / "output"
        completed = subprocess.run(
            ["python3", str(ROOT / "run_hosted.py"), "--output", str(output), "--ticks", "240"],
            check=False,
            capture_output=True,
            text=True,
        )
        require(completed.returncode == 0, f"hosted CLI failed: {completed.stdout}{completed.stderr}")
        report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        require(report["trace_sha256"] == EXPECTED_TRACE_SHA256, "CLI trace differs from API trace")
        require(report["status"] == "HOSTED-SCENE-EXECUTED-NOT-PHYSICALLY-DEPLOYED", "CLI overclaimed physical execution")
        require(report["physical_deployments"] == [], "CLI claimed a physical deployment")
        require((output / "preview.html").read_text(encoding="utf-8").count("https://") == 0, "preview has an external dependency")
        frame = (output / "final.ppm").read_bytes()
        require(frame.startswith(b"P6\n480 270\n255\n") and len(frame) == len(b"P6\n480 270\n255\n") + 480 * 270 * 3, "scaled PPM is malformed")

        changed_merge = copy.deepcopy(load_json(MERGE_PATH))
        changed_merge["creation"]["summary"] += " Changed."
        changed_merge_path = temporary / "changed.merge.json"
        changed_merge_path.write_text(json.dumps(changed_merge), encoding="utf-8")
        rejected("an unreviewed Creation revision", lambda: load_reviewed_creation(merge_path=changed_merge_path))

        changed_catalog = copy.deepcopy(load_json(CATALOG_PATH))
        for component in changed_catalog["components"]:
            if component["component_id"] == "rabbit.asset.cat-pixel":
                component["implementation"]["palette"]["O"] = "00FF00"
        changed_catalog_path = temporary / "changed.catalog.json"
        changed_catalog_path.write_text(json.dumps(changed_catalog), encoding="utf-8")
        rejected("a substituted cat asset", lambda: load_reviewed_creation(catalog_path=changed_catalog_path))

        changed_contract = copy.deepcopy(contract)
        changed_contract["max_ticks"] = 601
        changed_contract_path = temporary / "changed.runner.json"
        changed_contract_path.write_text(json.dumps(changed_contract), encoding="utf-8")
        rejected("an enlarged runner budget", lambda: load_reviewed_creation(contract_path=changed_contract_path))

        ambiguous_path = temporary / "ambiguous.runner.json"
        ambiguous_path.write_text('{"schema_version":1,"schema_version":2}', encoding="utf-8")
        rejected("ambiguous runner JSON", lambda: load_reviewed_creation(contract_path=ambiguous_path))

    rejected("zero ticks", lambda: run_ticks(0, contract))
    rejected("execution beyond the tick budget", lambda: run_ticks(601, contract))
    outside = copy.deepcopy(trace[-1])
    outside["cat"]["x"] = -1
    rejected("an out-of-bounds sprite write", lambda: render_rgb(outside, contract, result["components"]))
    print("PASS: exact Inventory v1 Creation is accepted without target-specific facts")
    print("PASS: integer-only Scene/Anima covers look, chase, pounce, bat, wait, animation, physics, and collision")
    print("PASS: two executions produce the exact same 240-tick trace and final raster")
    print("PASS: hosted artifacts include an offline visual preview and make no physical claim")
    print(f"PASS: contract={EXPECTED_CONTRACT_SHA256}, trace={EXPECTED_TRACE_SHA256}, final={EXPECTED_FINAL_RGB_SHA256}")
    print("PASS: SCENE-ANIMA-V2-HOSTED-EXECUTED-NOT-PHYSICALLY-DEPLOYED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
