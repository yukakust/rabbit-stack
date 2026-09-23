#!/usr/bin/env python3
"""Run the exact reviewed macOS Rabbit BLE advertiser."""

from __future__ import annotations

import runpy
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "x86-64-uefi-bluetooth-beacon-rx-v0" / "run_mac_beacon.py"
namespace = runpy.run_path(str(SOURCE))
raise SystemExit(namespace["main"]())
