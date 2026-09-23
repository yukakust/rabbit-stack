#!/usr/bin/env python3
"""Reuse the already reviewed, pinned QCA firmware fetch boundary."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "x86-64-uefi-qca-ram-load-v0" / "fetch_firmware.py"
_SPEC = importlib.util.spec_from_file_location("rabbit_pinned_qca_firmware", _PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("could not load pinned QCA firmware boundary")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

FirmwareError = _MODULE.FirmwareError
MANIFEST_PATH = _MODULE.MANIFEST_PATH
fetch_all = _MODULE.fetch_all
load_manifest = _MODULE.load_manifest
