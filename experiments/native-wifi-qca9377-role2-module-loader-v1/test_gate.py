"""Copied-proof negatives only; original/frozen sources are never modified."""
from pathlib import Path
import importlib.util,tempfile,shutil,json,hashlib
R=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('role2_checked',R/'check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def proof():
 t=tempfile.TemporaryDirectory();d=Path(t.name)
 for p in R.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts:continue
  q=d/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.symlink_to(p.resolve())
 return t,d
def mutate(d,name,change):
 p=d/name;b=p.read_bytes();p.unlink();p.write_bytes(change(b))
assert m.checked()['physical_admission'] is False
cases=[('artifact.c',lambda b:b+b'\n/*bad*/'),('runs/child/supplicant.efi',lambda b:b[:100]+bytes([b[100]^1])+b[101:]),('runs/qemu/debug.log',lambda b:b.replace(b'MODULE CHILD QEMU PASS',b'FAIL')),('parent-projection/runs/native-projection/payload.efi',lambda b:b[:-1]),('parent-projection/runs/native-projection/report.json',lambda b:b.replace(b'"physical_admission": false',b'"physical_admission": true')),('parent-projection/runs/native-projection/reproduction.json',lambda b:b.replace(b'516ea',b'00000')),('runs/checked/report.json',lambda b:b.replace(b'"coff_units": 6',b'"coff_units": 0'))]
for name,change in cases:
 t,d=proof()
 try:
  mutate(d,name,change)
  try:m.checked(d)
  except (ValueError,KeyError,AssertionError):pass
  else:raise AssertionError('accepted corruption '+name)
 finally:t.cleanup()
(R/'evidence/gate-negatives.json').write_text(json.dumps({'status':'ROLE2-READONLY-COPIED-PROOF-NEGATIVES-PASS','cases':len(cases),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'physical_calls':0,'key_reads':0},indent=2)+'\n')
print('PASS',len(cases),'copied-proof negatives')
