from pathlib import Path
import json,sys,subprocess,os,time
repo=Path('/Users/yukakust/rabbit-stack');root=repo/'experiments/native-wifi-qca9377-service-start-v1'
sys.path.insert(0,str(root));import operating_route as route
state=repo/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
native_session=Path(sys.argv[1]).resolve();native_pid=int(sys.argv[2])
if native_session.parent!=state.parent or not native_session.name.startswith('pci-native-'):raise SystemExit('STOP saved native session path required')
started=time.monotonic()
while True:
 try:os.kill(native_pid,0)
 except ProcessLookupError:break
 if time.monotonic()-started>3600:raise SystemExit('STOP native controller timeout; preserve exact signed session')
 time.sleep(2)
s=json.loads(state.read_text());receipt=json.loads((native_session/'report.json').read_text())
if s.get('native_pending') or s.get('hardware_trial_pending') or s['engine']['native_counter']!=46 or s['engine']['payload_sha256']!='dd261ac34e720259bc5d199b5f9832ddf7cb9ead7d7b607d3974af6593f5fcfc' or receipt['status']!='EXACT-APPLIED-RECEIPT' or not receipt['receiver_reported_applied']:raise SystemExit('STOP exact46 APPLIED required')
print('EXACT46 APPLIED; BOUNDED READ-ONLY INITIAL PCI RETRIES',flush=True)
diagnostic=root/'runs/control/native46-initial-pci.json'
for attempt in range(8):
 with route.flow.state_lock(state):
  run=subprocess.run([str(repo/'experiments/native-wifi-qca9377-operating-v1/runs/control/read-pci43'),'--read'],capture_output=True,text=True,timeout=70)
  (root/'runs/control'/f'native46-initial-pci-{attempt}.log').write_text(run.stdout+run.stderr)
  if not run.returncode:
   raw=json.loads(run.stdout);route.flow.save(diagnostic,raw);break
 if 'probe still active; retry read-only after cleanup' not in run.stderr:raise SystemExit('STOP initial PCI read failed; no guard bypass')
 time.sleep(3)
else:raise SystemExit('STOP initial probe still active; no asset signing')
print('INITIAL PCI SAVED; ALL EXACT GATES BEFORE NEW46 ASSET SIGNING',flush=True)
run=subprocess.run([sys.executable,str(root/'operating_route.py'),'asset-prepare','--state',str(state),'--checked',str(root/'runs/checked-candidate'),'--diagnostic',str(diagnostic),'--firmware',str(repo/'experiments/native-wifi-qca9377-v1/runs/mac-control/firmware-6.bin')],cwd=repo)
if run.returncode:raise SystemExit(run.returncode)
s=json.loads(state.read_text());session=s.get('hardware_trial_pending')
if not session:raise SystemExit('STOP exact new45 asset session missing')
print('EXACT46 ASSET SESSION',session,flush=True)
run=subprocess.run([sys.executable,'-u',str(root/'runs/control/resume_asset46.py'),session],cwd=repo)
if run.returncode:raise SystemExit(run.returncode)
print('ALL12 ASSETS CONFIRMED; BOUNDED BOOT/CONTROL OBSERVATION',flush=True)
for attempt in range(120):
 out=root/'runs/control/native46-boot.json'
 run=subprocess.run([sys.executable,str(repo/'experiments/native-wifi-qca9377-v1/read_boot.py'),'--read','--output',str(out)],cwd=repo)
 if run.returncode:raise SystemExit(run.returncode)
 d=json.loads(out.with_suffix('.decoded.json').read_text())
 if d['all_loader_resources_released'] and d['boot_round']:
  run=subprocess.run([sys.executable,str(root/'read_diagnostic.py'),'--read','--output',str(root/'runs/control/native46-final-diagnostic.json')],cwd=repo)
  print('ACTUAL BOOT/CONTROL SNAPSHOTS SAVED; NO ASSOCIATION/IP CLAIM',flush=True);raise SystemExit(run.returncode)
 time.sleep(120)
raise SystemExit('STOP bounded observation limit; preserve hardware trial/owners')
