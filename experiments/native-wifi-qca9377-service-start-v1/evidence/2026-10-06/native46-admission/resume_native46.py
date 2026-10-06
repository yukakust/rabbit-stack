import sys,json,pathlib,subprocess,os
repo=pathlib.Path('/Users/yukakust/rabbit-stack')
state=repo/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
expected=str(repo/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/pci-native-z_yxuvwo')
last=-1;stalls=0
for attempt in range(6):
 s=json.loads(state.read_text())
 if s.get('native_pending')!=expected:
  r=json.loads((pathlib.Path(expected)/'report.json').read_text());print('STOP',r['status'],flush=True);break
 r=json.loads((pathlib.Path(expected)/'report.json').read_text());floor=r.get('confirmed_received',0)
 if floor==last:stalls+=1
 else:stalls=0
 if stalls>=2:print('STOP TWO NO-PROGRESS ATTEMPTS; EXACT SESSION RETAINED',flush=True);break
 last=floor;print('DELIVERY ATTEMPT',attempt+1,'CONFIRMED',floor,flush=True)
 subprocess.run([sys.executable,str(repo/'experiments/native-wifi-qca9377-service-start-v1/operating_route.py'),'deliver','--state',str(state)],cwd=repo,check=False)
else:print('BOUNDED LIMIT; EXACT SESSION RETAINED',flush=True)
