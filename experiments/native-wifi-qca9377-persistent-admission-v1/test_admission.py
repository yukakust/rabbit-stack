"""Read-only corruption injection, before any private-key/radio action."""
import json
from pathlib import Path
from unittest.mock import patch
import route
C=route.PROFILE/'runs/checked-candidate';S=route.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
s=json.loads(S.read_text());payload=(C/'payload.efi').read_bytes();world=Path(s['package']).read_bytes();read=Path.read_bytes
cases=0
def rejected(fn):
 global cases
 try:fn()
 except (ValueError,KeyError,FileNotFoundError):cases+=1;return
 raise AssertionError('bad admission accepted')
with patch.object(route.engine,'load_private',side_effect=AssertionError('private accessed')),patch.object(route.flow,'deliver_session',side_effect=AssertionError('radio accessed')):
 route.gates(C,payload,world)
 rejected(lambda:route.gates(C,payload[:-1]+bytes([payload[-1]^1]),world))
 rejected(lambda:route.gates(C,payload,world+b'x'))
 rejected(lambda:route.gates(C.parent,payload,world))
 report=json.loads((C/'report.json').read_text())
 paths=[C/'report.json',route.PROFILE/'receiver-policy.json',route.REPO/next(iter(report['source_sha256'])),C/'init_probe.c',C/'actors-qemu/observed.log',C/'actors-empty-boot-qemu/observed.log',route.PROFILE/'evidence/2026-10-07/host.log',route.PROFILE/'runs/native-host/init_probe.c',route.V5/'runs/checked-candidate/reproduction.json']
 for target in paths:
  def modified(self,t=target):
   b=read(self)
   return b+b' ' if self.resolve()==t.resolve() else b
  with patch.object(Path,'read_bytes',modified):rejected(lambda:route.gates(C,payload,world))
 # Fresh admission requires exact receipt and hardware52 tuple, not cached proof.
 raw={n:json.loads((route.V5/'runs/control'/f'{n}52.json').read_text()) for n in ('boot','operating','startup')}
 temp=route.ROOT/'runs/tests';temp.mkdir(parents=True,exist_ok=True);obs=temp/'combined.json';route.flow.save(obs,raw)
 route.fresh(s,obs)
 for name in ('boot','operating','startup'):
  bad=json.loads(json.dumps(raw));bad[name]['writes']=1;route.flow.save(obs,bad);rejected(lambda:route.fresh(s,obs))
 route.flow.save(obs,raw)
 for field in ('pending','native_pending','recovery_pending','hardware_trial_pending'):
  bad=dict(s);bad[field]='unexpected';rejected(lambda:route.fresh(bad,obs))
 bad=json.loads(json.dumps(s));bad['engine']['native_counter']=51;rejected(lambda:route.fresh(bad,obs))
 obs.unlink()
print(json.dumps({'status':'BOUNDED53-ADMISSION-CORRUPTION-NO-SECRET-NO-RADIO-PASS','rejections':cases}))
