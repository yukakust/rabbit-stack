"""One bounded saved59 controller. No reset/reboot or automatic resign."""
from pathlib import Path
import sys,os,time,subprocess,json
import route
ROOT=route.ROOT;REPO=route.REPO
state=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
expected=Path(sys.argv[1]).resolve();control=ROOT/'runs/control';control.mkdir(parents=True,exist_ok=True)
s=route.flow.read_json(state)
if s.get('native_pending')!=str(expected):raise SystemExit('STOP exact signed59 session required')
r=subprocess.run([sys.executable,str(ROOT/'route.py'),'deliver','--state',str(state)],cwd=REPO)
if r.returncode:raise SystemExit('STOP native delivery unconfirmed; preserve exact session')
s=route.flow.read_json(state)
if s['engine']['native_counter']!=59 or s['engine']['payload_sha256']!=route.PAYLOAD or s['counter']!=19:raise SystemExit('STOP applied59/world19 required')
for attempt in range(8):
 with route.flow.state_lock(state):
  read=subprocess.run([str(REPO/'experiments/native-wifi-qca9377-operating-v1/runs/control/read-pci43'),'--read'],capture_output=True,text=True,timeout=70)
  (control/f'initial59-{attempt}.log').write_text(read.stdout+read.stderr)
  if read.returncode==0:
   route.flow.save(control/'initial59.json',json.loads(read.stdout));break
 if 'probe still active; retry read-only after cleanup' not in read.stderr:raise SystemExit('STOP initial59 diagnostic failed')
 time.sleep(3)
else:raise SystemExit('STOP setup59 not released')
subprocess.run([sys.executable,str(ROOT/'assets.py'),'prepare','--state',str(state),'--diagnostic',str(control/'initial59.json'),'--firmware',str(REPO/'experiments/native-wifi-qca9377-v1/runs/mac-control/firmware-6.bin')],cwd=REPO,check=True)
s=route.flow.read_json(state);assets=Path(s['hardware_trial_pending'])
r=subprocess.run([sys.executable,str(ROOT/'assets.py'),'deliver','--state',str(state),'--session',str(assets)],cwd=REPO)
if r.returncode:raise SystemExit('STOP observed asset failure; preserve exact packets/floors/diagnostics; no reconnect loop')
print('ALL12 ACCEPTED; quiet660s before final read, no reconnect polling',flush=True)
for _ in range(22):time.sleep(30)
with route.flow.state_lock(state):
 s=route.flow.read_json(state)
 if s.get('hardware_trial_pending')!=str(assets) or s['engine']['native_counter']!=59 or s['counter']!=19:raise SystemExit('STOP context changed')
 reader=REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt'
 env=os.environ.copy()
 if route.flow.LOCK_FD is not None:env['RABBIT_CONNECTED_LOCK_FD']=str(route.flow.LOCK_FD)
 with (control/'final-prefix59.log').open('w') as out:
  r=subprocess.run([str(reader),'prefix'],stdout=out,stderr=subprocess.STDOUT,env=env,timeout=70,pass_fds=() if route.flow.LOCK_FD is None else (route.flow.LOCK_FD,))
 if r.returncode:raise SystemExit('STOP final59 read failed; preserve exact raw callback')
print('PHYSICAL59 RAW CAPTURED; ROOT classification needed; no Wi-Fi/IP claim',flush=True)
