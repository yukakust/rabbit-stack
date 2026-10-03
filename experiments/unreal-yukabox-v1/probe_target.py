#!/usr/bin/env python3
"""Read-only Linux executor probe. Never installs, downloads or launches Unreal."""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def command(argv):
    try:
        p = subprocess.run(argv, text=True, capture_output=True, timeout=30)
        return {"exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": None, "stdout": "", "stderr": str(exc)}


def probe(root):
    if platform.system() != "Linux":
        raise SystemExit("Run this probe on Yukabox/Linux, not the command Mac.")
    memory = dict(re.findall(r"^(\w+):\s+(\d+)", Path("/proc/meminfo").read_text(), re.M))
    vulkan = command(["vulkaninfo", "--summary"])
    devices = []
    for block in re.split(r"GPU\d+:\n", vulkan["stdout"])[1:]:
        fields = dict(re.findall(r"^\s*(\w+)\s*=\s*(.+)$", block, re.M))
        devices.append(fields)
    hardware = [d for d in devices if d.get("deviceType") in (
        "PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU", "PHYSICAL_DEVICE_TYPE_DISCRETE_GPU")]
    editor = root / "engine/Engine/Binaries/Linux/UnrealEditor"
    free = shutil.disk_usage(root).free
    gaps = []
    if vulkan["exit_code"] != 0 or not hardware:
        gaps.append("No successful Vulkan hardware-device enumeration")
    if int(memory["MemTotal"]) * 1024 < 32 * 1024**3:
        gaps.append("Less than 32 GiB system memory")
    if free < 100 * 1024**3:
        gaps.append("Less than 100 GiB free for initial engine/project/cache")
    if not editor.is_file():
        gaps.append("Official Unreal Linux build not installed")
    return {
        "schema_version": 1,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "target": "yukabox", "platform": platform.platform(),
        "os_release": Path("/etc/os-release").read_text(),
        "cpu": next((x.split(":", 1)[1].strip() for x in
                     Path("/proc/cpuinfo").read_text().splitlines()
                     if x.startswith("model name")), "unknown"),
        "memory_bytes": int(memory["MemTotal"]) * 1024,
        "memory_available_bytes": int(memory["MemAvailable"]) * 1024,
        "storage_free_bytes": free,
        "display_environment": os.environ.get("DISPLAY"),
        "vulkan": vulkan, "hardware_devices": hardware,
        "editor_present": editor.is_file(), "editor_path": str(editor),
        "preflight_gaps": gaps,
        "engine_launch_verified": False,
        "render_verified": False,
        "note": "Enumeration is not rendering. Xvfb does not prove Vulkan presentation. "
                "Require actual Unreal Vulkan/offscreen run and frame evidence next.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True,
                        help="Existing Yukabox experiment directory")
    args = parser.parse_args()
    print(json.dumps(probe(args.root.resolve()), ensure_ascii=False, indent=2))
