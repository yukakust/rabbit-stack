"""One exact saved57 controller; foreground native sender must exit first."""
from pathlib import Path
import sys,os,time,subprocess,json,hashlib
REPO=Path('/Users/yukakust/rabbit-stack');ROOT=REPO/'experiments/native-wifi-qca9377-prefix57-root-route-v1'
sys.path.insert(0,str(ROOT));import route
state=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
expected=Path(sys.argv[1]).resolve();old_pid=int(sys.argv[2]);control=ROOT/'runs/control'
for _ in range(300):
 try:os.kill(old_pid,0)
 except ProcessLookupError:break
 time.sleep(2)
else:raise SystemExit('STOP prior native sender still live; no second radio operation')
for attempt in range(6):
 s=route.flow.read_json(state)
 if not s.get('native_pending'):break
 if s['native_pending']!=str(expected):raise SystemExit('STOP pending session changed')
 print('EXACT57 NATIVE RESUME',attempt+1,flush=True)
 r=subprocess.run([sys.executable,str(ROOT/'route.py'),'deliver','--state',str(state)],cwd=REPO)
 if r.returncode==0:break
 if r.returncode!=1:raise SystemExit(r.returncode)
else:raise SystemExit('STOP bounded native resume; preserve exact signature/session')
s=route.flow.read_json(state);r=route.flow.read_json(expected/'report.json')
if s.get('native_pending') or s['engine']['native_counter']!=57 or s['engine']['payload_sha256']!=route.PAYLOAD_SHA or r['status']!='EXACT-APPLIED-RECEIPT' or not r['receiver_reported_applied']:raise SystemExit('STOP exact57 applied required')
if not s.get('hardware_trial_pending'):
 for attempt in range(8):
  with route.flow.state_lock(state):
   read=subprocess.run([str(REPO/'experiments/native-wifi-qca9377-operating-v1/runs/control/read-pci43'),'--read'],capture_output=True,text=True,timeout=70)
   (control/f'initial57-{attempt}.log').write_text(read.stdout+read.stderr)
   if read.returncode==0:
    route.flow.save(control/'initial57.json',json.loads(read.stdout));break
  if 'probe still active; retry read-only after cleanup' not in read.stderr:raise SystemExit('STOP initial57 diagnostic failed')
  time.sleep(3)
 else:raise SystemExit('STOP initial57 not released')
 subprocess.run([sys.executable,str(ROOT/'route.py'),'asset-prepare','--state',str(state),'--diagnostic',str(control/'initial57.json'),'--firmware',str(REPO/'experiments/native-wifi-qca9377-v1/runs/mac-control/firmware-6.bin')],cwd=REPO,check=True)
s=route.flow.read_json(state);assets=Path(s['hardware_trial_pending']);last=-1;stalls=0
for attempt in range(30):
 r=route.flow.read_json(assets/'report.json')
 if r['completed_chunks']==12:break
 print('EXACT57 ASSET DELIVERY',attempt+1,flush=True)
 run=subprocess.run([sys.executable,str(ROOT/'route.py'),'asset-deliver','--state',str(state),'--session',str(assets)],cwd=REPO)
 r=route.flow.read_json(assets/'report.json');n=r['completed_chunks']
 if run.returncode==0 and n==12:break
 if run.returncode not in (0,1):raise SystemExit(run.returncode)
 floor=n*65536
 if n<12:
  for step in r['sender_steps']:
   if step.get('chunk')!=n:continue
   p=Path(step['log'])
   if not p.exists():continue
   for line in p.read_text().splitlines():
    try:v=json.loads(line)
    except ValueError:continue
    if v.get('packet_sha256')==r['packets'][n]['packet_sha256'] and v.get('error')==0 and v.get('peripheral','').upper()==route.PEER:
     floor=max(floor,n*65536+max(0,v.get('received',0)-224))
 stalls=stalls+1 if floor<=last else 0;last=floor
 if stalls>=2:raise SystemExit('STOP two no-progress attempts; preserve exact assets')
else:raise SystemExit('STOP bounded asset resume limit')
print('ALL12 ACCEPTED; bounded660s quiet observation before read, no reconnect polling',flush=True)
for _ in range(22):time.sleep(30)
with route.flow.state_lock(state):
 s=route.flow.read_json(state)
 if s.get('hardware_trial_pending')!=str(assets) or s['engine']['native_counter']!=57 or s['counter']!=18:raise SystemExit('STOP installed/pending context changed')
 worldplan=state.parent/'native56-city-recovery-plan';paths={'native_report':expected/'report.json','candidate_report':route.PROFILE/'runs/checked-candidate/report.json','policy':route.PROFILE/'receiver-policy.json','asset_report':assets/'report.json','world_report':worldplan/'restored-world/report.json','world_session':worldplan/'restored-world/session.json','world_packet':Path(s['package']),'world_source':Path(s['world'])}
 context={'format':'PREFIX57-PUBLIC-CONTEXT-2','inputs':{k:{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in paths.items()}}
 route.flow.save(control/'context57.json',context)
 subprocess.run([sys.executable,str(REPO/'experiments/native-wifi-qca9377-prefix57-observer-v2/collect.py'),'--read','--context',str(control/'context57.json'),'--output',str(control/'capture57')],cwd=REPO,check=True)
print('PHYSICAL57 OWNED RAW CAPTURED; ROOT classification required; no IP claim',flush=True)
