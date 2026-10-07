"""Resume only zero-write observations of exact already-applied53. No assets/key."""
from pathlib import Path
import subprocess,sys,json,time,hashlib
REPO=Path(__file__).resolve().parents[2];ROOT=Path(__file__).resolve().parent
CONTROL=REPO/'experiments/native-wifi-qca9377-persistent-admission-v1'
STATE=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
OUT=ROOT/'runs/control';OUT.mkdir(parents=True,exist_ok=True)
def exact():
 s=json.loads(STATE.read_text())
 if any(s.get(k) for k in ('pending','native_pending','recovery_pending')) or s['engine']['native_counter']!=53 or s['engine']['payload_sha256']!='261649e8cd7ab2bd59621f8ee559c421c36cc5e54c5d19238b558e55dc55a522':raise SystemExit('STOP exact53 state binding required')
 r=json.loads(Path(s['engine']['last_release_report']).read_text())
 if r['status']!='EXACT-APPLIED-RECEIPT' or r['counter']!=53 or not r['receiver_reported_applied'] or r['payload_sha256']!=s['engine']['payload_sha256']:raise SystemExit('STOP exact53 applied receipt required')
 if s.get('hardware_trial_pending') and Path(s['hardware_trial_pending']).name!='firmware-ram-8sztj97t':raise SystemExit('STOP hardware session changed')
 return s
def read(command):
 failures=0
 for attempt in range(8):
  exact();r=subprocess.run([sys.executable,*map(str,command)],cwd=REPO)
  if r.returncode==0:return
  failures+=1;print('READ-ONLY TRANSIENT FAILURE',failures,flush=True);time.sleep(10)
 raise SystemExit('STOP bounded read-only retries; preserve exact53 state')
for attempt in range(120):
 exact();read([REPO/'experiments/native-wifi-qca9377-v1/read_boot.py','--read','--output',CONTROL/'runs/control/boot53.json'])
 b=json.loads((CONTROL/'runs/control/boot53.decoded.json').read_text())
 if b['boot_round'] and b['all_loader_resources_released']:break
 time.sleep(30)
else:raise SystemExit('STOP bounded owner observation')
read([REPO/'experiments/native-wifi-qca9377-service-layout-v1/read_diagnostic.py','--read','--output',CONTROL/'runs/control/operating53.json'])
for kind in ('startup','profile'):read([CONTROL/'read_status.py',kind,'--output',CONTROL/'runs/control'/(kind+'53.json')])
p=json.loads((CONTROL/'runs/control/profile53.decoded.json').read_text());w=json.loads((CONTROL/'runs/control/startup53.decoded.json').read_text())
passed=bool(b['all_loader_resources_released'] and b['phase']==5 and not b['error'] and w['phase']==2 and not w['error'] and w['ready_seen']==1 and w['tx_complete']==1 and w['mac_hex']=='c0b5d778c3fb' and p.get('bounded_rx_trial_pass') and not p['rx_error'] and p['rx_phase'] in (1,3))
r={'status':'PHYSICAL53-BOUNDED-RX-READY-ALL-OWNER-RELEASE-PASS' if passed else 'PHYSICAL53-BOUNDED-RX-TRIAL-FAILED','native_counter':53,'pass':passed,'router_connected':False,'ip_verified':False,'device_attestation':False,'files_sha256':{n+ext:hashlib.sha256((CONTROL/'runs/control'/(n+ext)).read_bytes()).hexdigest() for n in ('boot53','operating53','startup53','profile53') for ext in ('.json','.decoded.json')}}
(OUT/'result53.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],flush=True)
raise SystemExit(0 if passed else 1)
