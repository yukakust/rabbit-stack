"""Read-only frozen Mac collector checks. No compile, manager, key or state APIs."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent.parent/'native-wifi-qca9377-fullboot60-collector-v1'
PROOF='0615819bee8531eb9a92d4eac8fb1a6a28812f0444ae14bd84bd250ddd240859'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,why):
 if not ok:raise ValueError(why)
def checked():
 p=ROOT/'evidence/host-proof.json';need(sha(p)==PROOF,'frozen44 collector report changed');r=json.loads(p.read_text())
 need(r['status']=='HOST-SEQUENTIAL-COLLECTOR-MONITOR-PREFLIGHT-PASS' and r['host_result']=='PASS 44 HOST collector cases; NO REAL MANAGER/WRITE' and not r['bluetooth_manager_started'] and r['writes']==0 and not r['private_key_loads'] and not r['physical_readiness_proven'],'actual host collector proof scope')
 for n,h in r['source_sha256'].items():need(Path(n).name==n and sha(ROOT/n)==h,'collector source changed '+n)
 for n,h in r['compiler_input_sha256'].items():need(sha(Path(n))==h,'collector compiler input changed '+n)
 need(sha(ROOT/'evidence/host.log')==r['host_log_sha256'],'collector callback log changed')
 exe=Path(r['executable']);need(exe.resolve()==(ROOT/'runs/control/collector').resolve() and sha(exe)==r['executable_sha256'],'collector exact executable changed');return exe
if __name__=='__main__':print('ROOT-FROZEN44-HOST-COLLECTOR-PASS',checked())
