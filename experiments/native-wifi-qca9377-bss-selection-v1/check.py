"""Public read-only local closure verifier; never imports a hardware module."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def checked():
 r=json.loads((ROOT/'runs/host/report.json').read_text())
 assert r['status']=='OWNED-WMI-BSS-SELECTION-ASAN-UBSAN-COFF-PASS' and r['build_host']=='yukabox'
 assert r['checks']>=86000 and r['credential_reads']==0
 for n in ['native_integrated','native_capabilities_currently_proven','physical_verified','rf_admission_granted','association_authority']:assert r[n] is False
 for n,h in r['source_sha256'].items():
  p=ROOT/n;assert not p.is_symlink() and p.is_file() and sha(p)==h,n
 for n,h in json.loads((ROOT/'frozen-inputs.json').read_text()).items():
  p=ROOT.parent.parent/n;assert p.is_file() and not p.is_symlink() and sha(p)==h,n
 assert sha(ROOT/'runs/host/test')==r['executable_sha256']
 assert sha(ROOT/'runs/host/host.log')==r['host_log_sha256']
 for n,h in r['coff_sha256'].items():assert sha(ROOT/'runs/host'/n)==h
 assert len(r['coff_sha256'])==7
 return r
if __name__=='__main__':print(checked()['status'])
