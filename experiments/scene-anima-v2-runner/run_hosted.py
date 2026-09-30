#!/usr/bin/env python3
"""Run the exact Cat Plays With Ball Creation and write inspectable hosted artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rabbit_scene import canonical_bytes, execute, ppm_bytes, preview_html, scale_rgb, sha256_hex


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("/tmp/rabbit-cat-scene-v2"))
    parser.add_argument("--ticks", type=int, default=240)
    arguments = parser.parse_args()
    if arguments.output.exists() and any(arguments.output.iterdir()):
        raise SystemExit(f"refusing to replace nonempty output directory: {arguments.output}")
    result = execute(arguments.ticks)
    contract = result["contract"]
    arguments.output.mkdir(parents=True, exist_ok=True)
    trace_path = arguments.output / "trace.json"
    preview_path = arguments.output / "preview.html"
    frame_path = arguments.output / "final.ppm"
    trace_path.write_bytes(canonical_bytes(result["trace"]) + b"\n")
    preview_path.write_text(preview_html(result["trace"], result["components"], contract), encoding="utf-8")
    scaled = scale_rgb(
        result["final_rgb"], contract["logical_width"], contract["logical_height"], contract["pixel_scale"]
    )
    frame_path.write_bytes(ppm_bytes(
        scaled,
        contract["logical_width"] * contract["pixel_scale"],
        contract["logical_height"] * contract["pixel_scale"],
    ))
    report = {
        "schema_version": 1,
        "status": "HOSTED-SCENE-EXECUTED-NOT-PHYSICALLY-DEPLOYED",
        "creation_sha256": contract["accepted_creation_sha256"],
        "runner_contract_sha256": sha256_hex(canonical_bytes(contract)),
        "ticks_executed": arguments.ticks,
        "trace_sha256": result["trace_sha256"],
        "final_rgb_sha256": result["final_rgb_sha256"],
        "physical_deployments": [],
    }
    report_path = arguments.output / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"HOSTED SCENE EXECUTED: {arguments.ticks} ticks")
    print(f"TRACE SHA256: {result['trace_sha256']}")
    print(f"FINAL RGB SHA256: {result['final_rgb_sha256']}")
    print(f"PREVIEW: {preview_path}")
    print("STATUS: HOSTED-SCENE-EXECUTED-NOT-PHYSICALLY-DEPLOYED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
