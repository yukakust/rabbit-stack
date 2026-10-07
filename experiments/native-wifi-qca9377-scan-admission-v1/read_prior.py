"""Sequential known-peer zero-write prior53 reads before passive54 signing."""
import subprocess,json,sys
from pathlib import Path
import scan_route as r
S=r.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json';out=r.ROOT/'runs/control';out.mkdir(parents=True,exist_ok=True)
with r.flow.state_lock(S):
 s=r.flow.read_json(S)
 if any(s.get(k) for k in ('pending','native_pending','hardware_trial_pending','recovery_pending')) or s['engine']['native_counter']!=53:raise ValueError('idle exact53 required')
 run=subprocess.run([str(r.REPO/'experiments/native-wifi-qca9377-v1/runs/mac-control/boot-reader'),'--read'],capture_output=True,text=True,timeout=70);(out/'prior-boot.log').write_text(run.stderr)
 if run.returncode:raise RuntimeError(run.stderr)
 r.flow.save(out/'prior-boot.json',json.loads(run.stdout))
for kind in ('startup','profile'):
 subprocess.run([sys.executable,str(r.REPO/'experiments/native-wifi-qca9377-persistent-admission-v1/read_status.py'),kind,'--output',str(out/('prior-'+kind+'.json'))],cwd=r.REPO,check=True)
subprocess.run([sys.executable,str(r.REPO/'experiments/native-wifi-qca9377-service-layout-v1/read_diagnostic.py'),'--read','--output',str(out/'prior-operating.json')],cwd=r.REPO,check=True)
r.flow.save(out/'prior53.json',{k:r.flow.read_json(out/('prior-'+k+'.json')) for k in ('boot','startup','profile','operating')})
print(json.dumps(r.fresh(r.flow.read_json(S),out/'prior53.json')))
