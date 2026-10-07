"""Offline copied physical fixture corruption; never used to authorize signing."""
import json,copy,struct
from pathlib import Path
from unittest.mock import patch
import scan_route as r
S=r.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json';s=json.loads(S.read_text());e=r.REPO/'experiments/native-wifi-qca9377-scan-result-v1/evidence/2026-10-07'
raw={'boot':json.loads((e/'boot54.json').read_text()),'capture':json.loads((e/'capture54.json').read_text())};folder=r.ROOT/'runs/tests';folder.mkdir(parents=True,exist_ok=True);obs=folder/'SYNTHETIC-copy-not-admission.json';count=0
def rejected(state,data):
 global count
 r.flow.save(obs,data)
 try:r.fresh(state,obs)
 except (ValueError,KeyError):count+=1;return
 raise AssertionError('bad copied fixture accepted')
with patch.object(r.engine,'load_private',side_effect=AssertionError('private accessed')),patch.object(r.flow,'deliver_session',side_effect=AssertionError('radio accessed')):
 r.flow.save(obs,raw);r.fresh(s,obs)
 for i in range(30):
  bad=copy.deepcopy(raw);b=bytearray.fromhex(bad['boot']['raw_hex']);struct.pack_into('<I',b,8+4*i,struct.unpack_from('<I',b,8+4*i)[0]^1);bad['boot']['raw_hex']=b.hex();rejected(s,bad)
 for field in ('pending','native_pending','hardware_trial_pending','recovery_pending'):
  state=copy.deepcopy(s);state[field]='unexpected';rejected(state,raw)
 for k in ('boot','capture'):
  bad=copy.deepcopy(raw);bad[k]['writes']=1;rejected(s,bad)
 bad=copy.deepcopy(raw);bad['capture']['status_hex'][1]='00'+bad['capture']['status_hex'][1][2:];rejected(s,bad)
 bad=copy.deepcopy(raw);bad['capture']['pages_hex'][1][0]='00'+bad['capture']['pages_hex'][1][0][2:];rejected(s,bad)
obs.unlink()
print(json.dumps({'status':'PASSIVE55-FRESH-GATE-COPIED-FIXTURE-NO-KEY-NO-RADIO-PASS','rejections':count,'fixture_is_live_admission':False}))
