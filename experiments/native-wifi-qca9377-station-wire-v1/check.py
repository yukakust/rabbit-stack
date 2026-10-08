from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def checked():
 r=json.loads((ROOT/'runs/host/report.json').read_text());assert r['status']=='STATION-WIRE-ORIGINAL-GENERATORS-ASAN-COFF-PASS' and r['checks']>=11000 and r['build_host']=='yukabox'
 assert r['physical_verified'] is False and r['native_integrated'] is False and r['rf_admission_granted'] is False and r['native_radio_capability']=='UNKNOWN' and r['credential_reads']==0
 for n,pin in r['source_sha256'].items():assert sha(ROOT/n)==pin,n
 for n,pin in json.loads((ROOT/'frozen-inputs.json').read_text()).items():assert sha(ROOT.parent.parent/n)==pin,n
 assert sha(ROOT/'runs/host/oracle.c')==r['oracle_sha256'] and sha(ROOT/'runs/host/host.log')==r['host_log_sha256']
 return r
if __name__=='__main__':print(checked()['status'])
