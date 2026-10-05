from pathlib import Path
import json,sys,subprocess,time,os
repo=Path('/Users/yukakust/rabbit-stack');root=repo/'experiments/native-wifi-qca9377-operating-diagnostic-v1'
state=repo/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
session=state.parent/'firmware-ram-z9vgatek'
started=time.monotonic()
while True:
 try:os.kill(26884,0)
 except ProcessLookupError:break
 if time.monotonic()-started>7200:raise SystemExit('STOP controller wait timeout; preserve exact session')
 time.sleep(2)
s=json.loads(state.read_text());r=json.loads((session/'report.json').read_text())
if s['engine']['native_counter']!=44 or s.get('native_pending') or r['status']!='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' or r['completed_chunks']!=12:raise SystemExit('STOP all exact44 assets not confirmed; no radio')
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
