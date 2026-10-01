"""Subscription-backed local Codex proposals; never executes generated code."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from llm_world import INSTRUCTIONS, MAX_JSON_BYTES, PROPOSAL_SCHEMA, parse_proposal
from package import PackageError


def propose_codex(intent, base, *, model=None):
    executable = shutil.which("codex")
    if not executable:
        raise PackageError("Codex CLI not found; install it on this Mac, then run codex login")
    # An explicit ChatGPT-only policy prevents accidental API billing. Do not read
    # or copy auth.json: the CLI owns login, token storage, and refresh.
    environment = os.environ.copy()
    for name in ("OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN"):
        environment.pop(name, None)
    with tempfile.TemporaryDirectory(prefix="rabbit-codex-") as temporary:
        directory = Path(temporary)
        schema_path = directory / "schema.json"
        output_path = directory / "proposal.json"
        schema_path.write_text(json.dumps(PROPOSAL_SCHEMA), encoding="utf-8")
        command = [executable, "exec", "--ignore-user-config", "--ephemeral",
                   "--sandbox", "read-only", "--skip-git-repo-check",
                   "--cd", str(directory), "--color", "never",
                   "-c", 'forced_login_method="chatgpt"',
                   "-c", 'approval_policy="never"',
                   "-c", 'features.shell_tool=false',
                   "--output-schema", str(schema_path),
                   "--output-last-message", str(output_path)]
        if model:
            command.extend(["--model", model])
        command.append("-")
        prompt = INSTRUCTIONS + "\nReturn JSON only. Do not use tools.\n" + json.dumps(
            {"request": intent, "base_world": base}, ensure_ascii=False)
        try:
            result = subprocess.run(command, input=prompt, text=True,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    env=environment, timeout=180, check=False)
        except subprocess.TimeoutExpired:
            raise PackageError("Codex timed out after 180 seconds; no package sent") from None
        if result.returncode != 0:
            raise PackageError("Codex failed; check codex login status, subscription limits, "
                               "and CLI version. No API fallback or package sent")
        if not output_path.is_file() or output_path.stat().st_size > MAX_JSON_BYTES:
            raise PackageError("Codex final JSON is missing or exceeds the input budget")
        return parse_proposal(output_path.read_text(encoding="utf-8")), None
