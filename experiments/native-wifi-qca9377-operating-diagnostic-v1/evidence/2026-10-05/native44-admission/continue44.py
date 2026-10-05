from pathlib import Path
import json,sys,subprocess,os,time
repo=Path('/Users/yukakust/rabbit-stack');root=repo/'experiments/native-wifi-qca9377-operating-diagnostic-v1'
sys.path.insert(0,str(root));import operating_route as route
state=repo/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
native_pid=26133
native_session=str(state.parent/'pci-native-7jesbhyh')
started=time.monotonic()
while True:
 try:os.kill(native_pid,0)
 except ProcessLookupError:break
 if time.monotonic()-started>3600:print('STOP native controller timeout; preserve session',flush=True);sys.exit(1)
 time.sleep(2)
s=json.loads(state.read_text());receipt=json.loads((Path(native_session)/'report.json').read_text())
if s.get('native_pending') or s.get('hardware_trial_pending') or s['engine']['native_counter']!=44 or s['engine']['payload_sha256']!='34126735c8c35f854d4a3cb1410e359e55999fef86298a5467cd9e6515dfab83' or receipt['status']!='EXACT-APPLIED-RECEIPT' or not receipt['receiver_reported_applied']:
 print('STOP native44 exact APPLIED missing; preserve all sessions',flush=True);sys.exit(1)
print('NATIVE44 EXACT APPLIED; READ-ONLY INITIAL DIAGNOSTIC NEXT',flush=True)
diagnostic=root/'runs/control/native44-initial-pci.json'
with route.flow.state_lock(state):
 run=subprocess.run([str(repo/'experiments/native-wifi-qca9377-operating-v1/runs/control/read-pci43'),'--read'],capture_output=True,text=True,timeout=70)
 diagnostic.with_suffix('.log').write_text(run.stdout+run.stderr)
 if run.returncode:print('STOP initial PCI read failed',flush=True);sys.exit(1)
 raw=json.loads(run.stdout);route.flow.save(diagnostic,raw)
print('INITIAL PCI SAVED; EXACT GATES/PIN RELEASE BEFORE ASSET SIGNING',flush=True)
cmd=[sys.executable,str(root/'operating_route.py'),'asset-prepare','--state',str(state),'--checked',str(root/'runs/checked-candidate'),'--diagnostic',str(diagnostic),'--firmware',str(repo/'experiments/native-wifi-qca9377-v1/runs/mac-control/firmware-6.bin')]
run=subprocess.run(cmd,cwd=repo)
if run.returncode:print('STOP asset preparation rejected; no bypass',flush=True);sys.exit(run.returncode)
s=json.loads(state.read_text());session=s.get('hardware_trial_pending')
if not session:print('STOP expected new44 asset session absent',flush=True);sys.exit(1)
print('EXACT44 ASSET SESSION',session,flush=True)
run=subprocess.run([sys.executable,'-u',str(root/'runs/control/resume_asset44.py'),session],cwd=repo)
if run.returncode:print('STOP asset delivery bounded controller; preserve exact session',flush=True);sys.exit(run.returncode)
print('ASSETS ACCEPTED; BOUNDED PHYSICAL BOOT OBSERVATION',flush=True)
for attempt in range(30):
 out=root/'runs/control/native44-boot.json'
 run=subprocess.run([sys.executable,str(repo/'experiments/native-wifi-qca9377-v1/read_boot.py'),'--read','--output',str(out)],cwd=repo)
 if run.returncode:print('STOP read failed; preserve ownership/session',flush=True);sys.exit(run.returncode)
 d=json.loads(out.with_suffix('.decoded.json').read_text())
 if d['all_loader_resources_released'] and d['boot_round']:
  run=subprocess.run([sys.executable,str(root/'read_diagnostic.py'),'--read','--output',str(root/'runs/control/native44-final-diagnostic.json')],cwd=repo)
  print('PHYSICAL DIAGNOSTIC SAVED; NEED EVIDENCE-SUPPORTED ANALYSIS; NO FORMAT BYPASS',flush=True);sys.exit(run.returncode)
 time.sleep(120)
print('STOP bounded boot observation limit; retain hardware trial and pin',flush=True);sys.exit(1)
