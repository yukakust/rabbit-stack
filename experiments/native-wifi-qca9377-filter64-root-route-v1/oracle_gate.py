"""Root wrapper for independently frozen64 host proof; no device/key APIs."""
from pathlib import Path
import importlib.util,hashlib
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'native-wifi-qca9377-filter64-host-gates-v1'/'oracle_gate.py'
SOURCE_SHA='8b343d87b8167e5c177581d828ce7ea25aeb1daa81b7243fc933f3910b28e2e9'
def checked():
 if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('frozen64 oracle_gate authority changed')
 spec=importlib.util.spec_from_file_location('_root64_frozen_oracle_gate',SOURCE);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module.checked()
