"""Read-only public proof checks. No native/hardware module import."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def checked():
 r=json.loads((ROOT/'runs/host/report.json').read_text());h=json.loads((ROOT/'runs/interop/report.json').read_text())
 assert r['status']=='STATION-OWNED-PRIMARY-ORACLE-ASAN-UBSAN-COFF-PASS' and r['checks']>=180000 and r['build_host']=='yukabox'
 for n in ['native_integrated','native_capabilities_proven','physical_verified','rf_admission_granted','controlled_port_is_actual_open']:assert r[n] is False
 for n,pin in r['source_sha256'].items():
  p=ROOT/n;assert not p.is_symlink() and sha(p)==pin,n
 for n,pin in json.loads((ROOT/'frozen-inputs.json').read_text()).items():
  p=ROOT.parent.parent/n;assert not p.is_symlink() and sha(p)==pin,n
 assert sha(ROOT/'runs/host/test')==r['executable_sha256'] and sha(ROOT/'runs/host/host.log')==r['host_log_sha256']
 assert sha(ROOT/'runs/host/oracle.c')==r['oracle_sha256']
 for n,pin in r['coff_sha256'].items():assert sha(ROOT/'runs/host'/n)==pin
 assert h['status']=='HOST-PATCHED-RSN-STATION-METADATA-JOIN-INTEROP-PASS' and h['physical_verified'] is False and h['native_deployment_admitted'] is False and h['credential_reads']==h['owner_key_reads']==h['state_operations']==0
 assert [x['mode'] for x in h['interop_scenarios']]==[0,1,2,3,4,9]
 assert sha(ROOT/'runs/interop/interop')==h['executable_sha256']
 for n,pin in h['local_sources'].items():assert sha(ROOT/n)==pin
 for n,v in h['compiled_fixture_sources_sha256'].items():assert sha(ROOT/'runs/interop'/n)==v['sha256']
 for v in h['interop_scenarios']:assert sha(ROOT/'runs/interop'/('mode-'+str(v['mode'])+'.log'))==v['log_sha256']
 return r,h
if __name__=='__main__':print(checked()[0]['status'])
