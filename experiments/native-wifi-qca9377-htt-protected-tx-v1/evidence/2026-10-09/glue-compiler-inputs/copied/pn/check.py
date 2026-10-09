import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
REPO=R.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 r=json.loads((R/'runs/host/report.json').read_text());assert r['status']=='OWNED-PN-METADATA-ASAN-COFF-PASS'
 for name,h in r['source_sha256'].items():assert sha(R/name)==h,name
 for name,h in json.loads((R/'frozen-inputs.json').read_text()).items():assert sha(REPO/name)==h,name
 assert sha(R/'runs/host/host.log')==r['host_log_sha256']
 assert sha(R/'runs/host/original_oracle.c')==r['original_oracle_sha256']
 for name,h in r['coff_sha256'].items():assert sha(R/'runs/host'/name)==h
 assert r['counter_metadata_only'] and not r['frame_authentication_proven'] and r['protected_quarantine_required'] and not r['physical_verified'] and not r['native_integrated']
 print('OWNED-PN-PUBLIC-CLOSURE-PASS checks='+str(r['checks']))
if __name__=='__main__':main()
