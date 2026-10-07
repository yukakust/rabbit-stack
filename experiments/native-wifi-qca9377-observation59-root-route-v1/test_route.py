"""Offline real-proof mutation guards; no keys, radio or state mutations."""
import copy,json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import route
class Guards(unittest.TestCase):
 def setUp(self):
  self.state=route.flow.read_json(route.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json')
 def test_real_proof(self):
  route.gates(route.CHECKED,(route.CHECKED/'payload.efi').read_bytes(),Path(self.state['package']).read_bytes());route.prior58(self.state)
 def test_altered_payload(self):
  b=bytearray((route.CHECKED/'payload.efi').read_bytes());b[-1]^=1
  with self.assertRaises(ValueError):route.gates(route.CHECKED,bytes(b),Path(self.state['package']).read_bytes())
 def test_other_world(self):
  with self.assertRaises(ValueError):route.gates(route.CHECKED,(route.CHECKED/'payload.efi').read_bytes(),b'other')
 def test_changed_source(self):
  old=route.sha
  def damaged(p):return '0'*64 if str(p).endswith('/init_probe.c') else old(p)
  with patch.object(route,'sha',damaged),self.assertRaises(ValueError):route.gates(route.CHECKED,(route.CHECKED/'payload.efi').read_bytes(),Path(self.state['package']).read_bytes())
 def test_counter_and_pending(self):
  for key,value in [('counter',18),('package_sha256','0'*64),('native_pending','other'),('hardware_trial_pending','other')]:
   s=copy.deepcopy(self.state);s[key]=value
   with self.assertRaises(ValueError):route.prior58(s)
 def test_model_proof_corrupted(self):
  old=route.sha
  def damaged(p):return '0'*64 if str(p).endswith('/native-host/report.json') else old(p)
  with patch.object(route,'sha',damaged),self.assertRaises(ValueError):route.gates(route.CHECKED,(route.CHECKED/'payload.efi').read_bytes(),Path(self.state['package']).read_bytes())
 def test_readback_age_and_binding(self):
  old=route.REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/pre-observation59-world19'
  r=route.flow.read_json(old/'report.json');state=(route.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json').read_bytes()
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);(d/'query.log').write_bytes((old/'query.log').read_bytes());r['observed_at']=time.time();(d/'report.json').write_text(json.dumps(r));route.fresh(d,state)
   for key,value in [('observed_at',time.time()-301),('writes',False),('writes',1),('state_sha256','0'*64),('query_sha256','0'*64)]:
    bad=dict(r);bad[key]=value;(d/'report.json').write_text(json.dumps(bad))
    with self.assertRaises(ValueError):route.fresh(d,state)
if __name__=='__main__':unittest.main()
