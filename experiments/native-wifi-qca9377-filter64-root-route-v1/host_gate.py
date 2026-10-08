"""Root wrapper for independently frozen64 host proof; no device/key APIs."""
from pathlib import Path
import importlib.util,hashlib
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'native-wifi-qca9377-filter64-host-gates-v1'/'host_gate.py'
SOURCE_SHA='f122ed85fa93f7c7a7c9c675d138e3e9433f06c9878ee8b126ca237cc4ce41cf'
def checked():
 if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('frozen64 host_gate authority changed')
 spec=importlib.util.spec_from_file_location('_root64_frozen_host_gate',SOURCE);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module.checked()
