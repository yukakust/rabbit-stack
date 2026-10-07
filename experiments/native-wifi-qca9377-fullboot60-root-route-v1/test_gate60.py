"""Negative frozen candidate admission tests; no keys/device/state writes."""
from pathlib import Path
import unittest
from unittest.mock import patch
import launch as g
class Gate(unittest.TestCase):
 def setUp(self):
  self.s=g.flow.read_json(g.prior.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json');self.payload=(g.CHECKED/'payload.efi').read_bytes();self.world=Path(self.s['package']).read_bytes()
 def check(self):return g.gates(g.CHECKED,self.payload,self.world)
 def test_actual_frozen_candidate(self):self.assertEqual(self.check()['native_counter'],60)
 def test_payload_world_and_directory(self):
  for d,p,w in [(g.CHECKED,b'changed',self.world),(g.CHECKED,self.payload,b'changed'),(Path('/other'),self.payload,self.world)]:
   with self.assertRaises(ValueError):g.gates(d,p,w)
 def test_changed_actual_source(self):
  old=g.prior.sha
  def bad(p):return '0'*64 if str(p).endswith('/prefix.h') else old(p)
  with patch.object(g.prior,'sha',side_effect=bad),self.assertRaises(ValueError):self.check()
 def test_changed_generated_and_native_fixture(self):
  for suffix in ('checked-candidate/init_probe.c','native-host/fixture.c'):
   old=g.prior.sha
   def bad(p):return '0'*64 if str(p).endswith(suffix) else old(p)
   with patch.object(g.prior,'sha',side_effect=bad),self.assertRaises(ValueError):self.check()
 def test_policy_and_scope(self):
  old=g.flow.read_json
  for change in ('policy','deadline','scan'):
   def bad(p,*args):
    r=old(p,*args)
    if change=='policy' and str(p)==str(g.PROFILE/'receiver-policy.json'):r['generation']=59
    if str(p)==str(g.CHECKED/'report.json'):
     if change=='deadline':r['deadline_us']=600000000
     if change=='scan':r['scan_commands']=1
    return r
   with patch.object(g.flow,'read_json',side_effect=bad),self.assertRaises(ValueError):self.check()
if __name__=='__main__':unittest.main()
