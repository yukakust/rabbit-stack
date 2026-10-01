#!/usr/bin/env python3
"""Offline boundary tests; no cloud request, BLE, or physical execution."""

import copy
import hashlib
import io
import json
import tempfile
import subprocess
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import ask_world
import codex_world
from llm_world import PackageError, parse_proposal, propose, response_text
from transport import fnv1a32


class TextWorldTests(unittest.TestCase):
    def setUp(self):
        self.base = json.loads((ask_world.ROOT / "worlds/cat-chases-mouse.json").read_text())
        self.proposal = {"status": "ready", "explanation": "Кот стал розовым и быстрее.",
                         "world": copy.deepcopy(self.base)}
        self.proposal["world"]["palette"][1] = "ff44aa"
        self.proposal["world"]["programs"][0]["code"][2] = 3
        self.temp = tempfile.TemporaryDirectory(prefix="rabbit-llm-test-", dir=ask_world.ROOT)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def invoke(self, proposal=None, send=False, sender_status=0):
        candidate = self.directory / "candidate.json"
        candidate.write_text(json.dumps(proposal if proposal is not None else self.proposal))
        args = ["Сделай кота розовым и быстрее", "--counter", "2", "--candidate", str(candidate),
                "--runs-dir", str(self.directory / "runs")]
        if send:
            args.append("--send")
        with patch.object(ask_world.subprocess, "run") as sender, redirect_stdout(io.StringIO()):
            sender.return_value.returncode = sender_status
            result = ask_world.main(args)
        return result, sender

    def test_valid_candidate_is_signed_roundtripped_and_not_sent_by_default(self):
        result, sender = self.invoke()
        self.assertEqual(result, 0); sender.assert_not_called()
        path = next((self.directory / "runs").glob("*/world.json"))
        world, package, frames = ask_world.validate_world(path, 2)
        self.assertEqual(world["palette"][1], "ff44aa")
        self.assertEqual(world["programs"][0]["code"][2], 3)
        self.assertEqual(len(frames), 54)
        report = json.loads(path.with_name("report.json").read_text())
        self.assertEqual(report["status"], "VALIDATED-NOT-SENT")
        self.assertFalse(report["physical_execution_verified"])

    def test_send_uses_validated_world_and_counter_and_records_ack(self):
        result, sender = self.invoke(send=True)
        self.assertEqual(result, 0); sender.assert_called_once()
        command = sender.call_args.args[0]
        self.assertEqual(command[-2:], ["--counter", "2"])
        self.assertEqual(Path(command[1]), ask_world.ROOT / "send_package.py")
        report = json.loads(Path(command[2]).with_name("report.json").read_text())
        self.assertEqual(report["status"], "ACK-RECEIVED")
        self.assertFalse(report["physical_execution_verified"])

    def test_sender_timeout_does_not_claim_ack(self):
        result, sender = self.invoke(send=True, sender_status=1)
        self.assertEqual(result, 1)
        report = next((self.directory / "runs").glob("*/report.json"))
        self.assertEqual(json.loads(report.read_text())["status"], "ACK-NOT-CONFIRMED")

    def test_bad_worlds_never_invoke_sender(self):
        for label, mutate in [
            ("opcode", lambda world: world["programs"][0]["code"].__setitem__(0, 127)),
            ("boolean", lambda world: world["objects"][0].__setitem__("x", True)),
            ("reference", lambda world: world["objects"][0].__setitem__("sprite", 99)),
            ("pixels", lambda world: world["sprites"][0]["frames"].__setitem__(0, "1")),
            ("budget", lambda world: world["palette"].extend(["ffffff"] * 16)),
            ("effect", lambda world: world.__setitem__("shell", "echo untrusted")),
            ("zero-id", lambda world: world["sprites"][0].__setitem__("id", 0)),
            ("tick-budget", lambda world: world["programs"][0].__setitem__("code", [1] * 16 + [0])),
            ("background", lambda world: world["palette"].__setitem__(0, "ffffff")),
            ("magnitude", lambda world: world["programs"][0]["code"].__setitem__(2, 255)),
        ]:
            with self.subTest(label=label):
                proposal = copy.deepcopy(self.proposal); mutate(proposal["world"])
                result, sender = self.invoke(proposal, send=True)
                self.assertEqual(result, 1); sender.assert_not_called()

    def test_unsupported_request_never_sends(self):
        result, sender = self.invoke({"status": "unsupported", "world": None,
                                     "explanation": "Микрофон пока не поддерживается."}, send=True)
        self.assertEqual(result, 2); sender.assert_not_called()

    def test_ambiguous_json_and_status_are_rejected(self):
        for value in ['{"status":"ready","status":"unsupported"}',
                      '{"status":"ready","world":null,"explanation":""}',
                      '{"status":"unsupported","world":null,"explanation":NaN}']:
            with self.assertRaises(PackageError):
                parse_proposal(value)

    def test_incomplete_refusal_missing_output_rejected(self):
        for response in [{"status": "incomplete", "output": []},
                         {"status": "completed", "output": []},
                         {"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal"}]}]}]:
            with self.assertRaises(PackageError):
                response_text(response)

    def test_api_request_is_structured_and_keeps_key_out_of_payload(self):
        response = {"status": "completed", "id": "test-only", "output": [{"type": "message",
                    "content": [{"type": "output_text", "text": json.dumps(self.proposal)}]}]}
        class Connection(io.BytesIO):
            pass
        with patch("llm_world.urllib.request.urlopen", return_value=Connection(json.dumps(response).encode())) as api:
            proposal, response_id = propose("Розовый кот", self.base, model="test-model", api_key="test-key")
        self.assertEqual(proposal, self.proposal); self.assertEqual(response_id, "test-only")
        request = api.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, "https://api.openai.com/v1/responses")
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertFalse(payload["store"])
        self.assertNotIn("test-key", request.data.decode())

    def test_missing_key_fails_before_network(self):
        with patch("llm_world.urllib.request.urlopen") as api, self.assertRaises(PackageError):
            propose("Кот", self.base, model="test-model", api_key="")
        api.assert_not_called()

    def test_archived_physical_receipt_binds_the_exact_baseline_package(self):
        evidence = json.loads((ask_world.ROOT / "evidence/dell-optiplex-3060-v2-world-observed.json").read_text())
        _, package, frames = ask_world.validate_world(ask_world.ROOT / evidence["bindings"]["world"], 1)
        self.assertEqual(hashlib.sha256(package).hexdigest(), evidence["bindings"]["package_sha256"])
        self.assertEqual(f"{fnv1a32(package):08X}", evidence["mac_receipt"]["hash_fnv1a32"])
        self.assertEqual(f"{frames[0][3]:02X}", evidence["mac_receipt"]["transfer"])
        self.assertEqual(len(frames), evidence["bindings"]["frames"])

    def test_codex_subscription_invocation_and_strict_output(self):
        def run(command, **kwargs):
            self.assertIn("--ignore-user-config", command)
            self.assertIn("--ephemeral", command)
            self.assertIn('forced_login_method="chatgpt"', command)
            self.assertIn('features.shell_tool=false', command)
            self.assertEqual(command[command.index("--sandbox") + 1], "read-only")
            self.assertEqual(command[-1], "-")
            self.assertNotIn("--model", command)
            self.assertNotIn("OPENAI_API_KEY", kwargs["env"])
            self.assertNotIn("CODEX_API_KEY", kwargs["env"])
            self.assertNotIn("CODEX_ACCESS_TOKEN", kwargs["env"])
            self.assertIn("Розовый кот", kwargs["input"])
            self.assertEqual(kwargs["timeout"], 180)
            schema = Path(command[command.index("--output-schema") + 1])
            self.assertEqual(json.loads(schema.read_text()), codex_world.PROPOSAL_SCHEMA)
            output = Path(command[command.index("--output-last-message") + 1])
            output.write_text(json.dumps(self.proposal))
            return subprocess.CompletedProcess(command, 0)
        with patch("codex_world.shutil.which", return_value="/test/codex"), \
             patch.dict("os.environ", {"OPENAI_API_KEY": "secret", "CODEX_API_KEY": "secret", "CODEX_ACCESS_TOKEN": "secret"}), \
             patch("codex_world.subprocess.run", side_effect=run):
            proposal, response_id = codex_world.propose_codex("Розовый кот", self.base)
        self.assertEqual(proposal, self.proposal)
        self.assertIsNone(response_id)

    def test_codex_failures_do_not_accept_or_fallback(self):
        for failure in ("missing", "exit", "timeout", "no-output", "malformed", "oversize"):
            def run(command, **kwargs):
                if failure == "timeout":
                    raise subprocess.TimeoutExpired(command, 180)
                output = Path(command[command.index("--output-last-message") + 1])
                if failure == "malformed":
                    output.write_text('{"status":"ready"}')
                elif failure == "oversize":
                    output.write_text(" " * (codex_world.MAX_JSON_BYTES + 1))
                return subprocess.CompletedProcess(command, 1 if failure == "exit" else 0)
            with self.subTest(failure=failure), \
                 patch("codex_world.shutil.which", return_value=None if failure == "missing" else "/test/codex"), \
                 patch("codex_world.subprocess.run", side_effect=run), \
                 self.assertRaises(PackageError):
                codex_world.propose_codex("Кот", self.base, model="test-model")

    def test_default_provider_codex_uses_same_send_gate(self):
        with patch.object(ask_world, "propose_codex", return_value=(self.proposal, None)) as codex, \
             patch.object(ask_world, "propose") as api, \
             patch.object(ask_world.subprocess, "run") as sender, redirect_stdout(io.StringIO()):
            result = ask_world.main(["Розовый кот", "--counter", "2", "--runs-dir", str(self.directory / "runs")])
        self.assertEqual(result, 0)
        codex.assert_called_once(); api.assert_not_called(); sender.assert_not_called()
        report = json.loads(next((self.directory / "runs").glob("*/report.json")).read_text())
        self.assertEqual(report["provider"], "codex-chatgpt")
        self.assertEqual(report["status"], "VALIDATED-NOT-SENT")

    def test_codex_failure_never_calls_api_or_sender(self):
        with patch.object(ask_world, "propose_codex", side_effect=PackageError("login required")), \
             patch.object(ask_world, "propose") as api, \
             patch.object(ask_world.subprocess, "run") as sender, redirect_stdout(io.StringIO()):
            result = ask_world.main(["Кот", "--counter", "2", "--send"])
        self.assertEqual(result, 1); api.assert_not_called(); sender.assert_not_called()

    def test_api_is_explicit_opt_in(self):
        with patch.object(ask_world, "propose", return_value=(self.proposal, "test")) as api, \
             patch.object(ask_world, "propose_codex") as codex, redirect_stdout(io.StringIO()):
            result = ask_world.main(["Кот", "--provider", "api", "--counter", "2",
                                     "--runs-dir", str(self.directory / "runs")])
        self.assertEqual(result, 0); codex.assert_not_called(); api.assert_called_once()
        self.assertEqual(api.call_args.kwargs["model"], "gpt-4.1-mini")


if __name__ == "__main__":
    unittest.main(verbosity=2)
