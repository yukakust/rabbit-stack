"""Read-only candidate corruption injection. No private/radio calls."""
from pathlib import Path
from unittest.mock import patch
import json,sys
import scan_route as r
C=r.PROFILE/'runs/checked-candidate';state=json.loads((r.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json').read_text());payload=(C/'payload.efi').read_bytes();world=Path(state['package']).read_bytes();read=Path.read_bytes;count=0
def reject(fn):
 global count
 try:fn()
 except (ValueError,KeyError,FileNotFoundError):count+=1;return
 raise AssertionError('corruption admitted')
with patch.object(r.engine,'load_private',side_effect=AssertionError('private touched')),patch.object(r.flow,'deliver_session',side_effect=AssertionError('radio touched')):
 r.gates(C,payload,world)
 reject(lambda:r.gates(C,payload+b'x',world));reject(lambda:r.gates(C,payload,world+b'x'));reject(lambda:r.gates(C.parent,payload,world))
 targets=[C/'report.json',C/'init_probe.c',C/'scan_native.c',C/'scan_policy.h',C/'actors-qemu/observed.log',C/'actors-empty-boot-qemu/observed.log',r.PROFILE/'receiver-policy.json',r.PROFILE/'runs/native-host/fixture.c',r.PROFILE/'evidence/2026-10-07/native-host.log',r.PROFILE/'runs/policy-binding/binding.json',r.PROFILE/'runs/policy-binding/report.json',r.PROFILE/'runs/policy-binding/host.log',r.PROFILE/'scan_policy.h',r.REPO/'experiments/native-wifi-qca9377-regulatory-policy-v1/evidence/2026-10-07/policy-proposal.json']
 for target in targets:
  def changed(self,t=target):
   b=read(self);return b+b' ' if self.resolve()==t.resolve() else b
  with patch.object(Path,'read_bytes',changed):reject(lambda:r.gates(C,payload,world))
 print(json.dumps({'status':'PASSIVE55-ADMISSION-CORRUPTION-NO-KEY-NO-RADIO-PASS','rejections':count}))
