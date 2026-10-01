#!/usr/bin/env python3
"""Russian intent -> LLM candidate -> deterministic package checks -> optional BLE."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from compile_world import compile_world
from llm_world import WORLD_SCHEMA, parse_proposal, propose, strict_json, validate_schema
from package import PackageError, decode_package
from transport import decode_transfer, encode_transfer, fnv1a32

ROOT = Path(__file__).resolve().parent


def validate_world(path: Path, counter: int):
    value = strict_json(path.read_text(encoding="utf-8"))
    validate_schema(value, WORLD_SCHEMA, "world")
    if value["palette"][0] != "121826":
        raise PackageError("this resident Runtime has a fixed 121826 background")
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    package = compile_world(path, counter, private)
    public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    decoded = decode_package(package, public)
    # Mirror the resident C interpreter's stricter instruction-count bound.
    for program in decoded["programs"]:
        code = program["code"]
        cursor = steps = 0
        while cursor < len(code):
            opcode = code[cursor]; cursor += 1; steps += 1
            if opcode in (3, 4, 6):
                if code[cursor + 1] > 8:
                    raise PackageError("LLM behavior magnitude must stay within 1..8")
                cursor += 2
            elif opcode == 5:
                cursor += 1
        if steps > 16:
            raise PackageError("program exceeds resident VM's 16-instruction tick budget")
    frames = encode_transfer(package)
    if decode_transfer(frames) != package:
        raise PackageError("transport round trip differs from the signed package")
    return value, package, frames


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent", help="what should change, in Russian or another language")
    parser.add_argument("--counter", type=int, required=True, help="greater than last accepted counter this Dell boot")
    parser.add_argument("--base", type=Path, default=ROOT / "worlds/cat-chases-mouse.json")
    parser.add_argument("--model", default=os.environ.get("RABBIT_LLM_MODEL", "gpt-4.1-mini"))
    parser.add_argument("--candidate", type=Path, help="use a saved proposal instead of calling the API")
    parser.add_argument("--send", action="store_true", help="transmit validated world and await Dell ACK")
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "runs")
    args = parser.parse_args(argv)
    report = None
    report_path = None
    try:
        if not 1 <= args.counter <= 0xFFFFFFFF or not args.intent.strip() or len(args.intent) > 4000:
            raise PackageError("intent must be 1..4000 characters and counter a nonzero uint32")
        base, _, _ = validate_world(args.base, args.counter)
        if args.candidate:
            proposal = parse_proposal(args.candidate.read_text(encoding="utf-8"))
            response_id = None
            provider = "saved-candidate"
        else:
            print("LLM: creating a candidate world...", flush=True)
            proposal, response_id = propose(args.intent, base, model=args.model,
                                           api_key=os.environ.get("OPENAI_API_KEY", ""))
            provider = "openai-responses"
        args.runs_dir.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix="world-", dir=args.runs_dir)).resolve()
        (directory / "intent.txt").write_text(args.intent, encoding="utf-8")
        (directory / "proposal.json").write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        explanation = "".join(char if char.isprintable() else " " for char in proposal["explanation"])
        print(explanation)
        if proposal["status"] == "unsupported":
            print(f"UNSUPPORTED: no package sent. Proposal: {directory / 'proposal.json'}")
            return 2
        world_path = directory / "world.json"
        world_path.write_text(json.dumps(proposal["world"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _, package, frames = validate_world(world_path, args.counter)
        digest = hashlib.sha256(package).hexdigest()
        report = {"schema_version": 1, "status": "VALIDATED-NOT-SENT", "provider": provider,
                  "model": args.model if provider == "openai-responses" else None,
                  "response_id": response_id, "counter": args.counter,
                  "base_sha256": hashlib.sha256(json.dumps(base, sort_keys=True).encode()).hexdigest(),
                  "world_sha256": hashlib.sha256(world_path.read_bytes()).hexdigest(),
                  "package_sha256": digest, "package_fnv1a32": f"{fnv1a32(package):08X}",
                  "package_bytes": len(package), "frames": len(frames),
                  "physical_execution_verified": False, "sender_exit_status": None}
        report_path = directory / "report.json"
        def save_report():
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        save_report()
        print(f"VALIDATED: {len(package)} signed bytes; {len(frames)} frames; counter={args.counter}")
        print(f"WORLD: {world_path}")
        if not args.send:
            print("VALIDATED-NOT-SENT: add --send to transmit a candidate, or use send_package.py with this world path")
            return 0
        report["status"] = "SENDING"; save_report()
        result = subprocess.run([sys.executable, str(ROOT / "send_package.py"), str(world_path),
                                 "--counter", str(args.counter)], check=False)
        report["sender_exit_status"] = result.returncode
        report["status"] = "ACK-RECEIVED" if result.returncode == 0 else "ACK-NOT-CONFIRMED"
        # A correlated ACK proves receipt/commit reporting, not independent pixel observation.
        save_report()
        print(f"{report['status']}: {report_path}")
        return result.returncode if result.returncode >= 0 else 1
    except KeyboardInterrupt:
        if report is not None and report_path is not None:
            report["status"] = "INTERRUPTED-ACK-NOT-CONFIRMED"
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("Interrupted; Dell receipt is not confirmed.")
        return 130
    except (OSError, ValueError, KeyError, TypeError, RecursionError, OverflowError) as error:
        print(f"FAIL: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
