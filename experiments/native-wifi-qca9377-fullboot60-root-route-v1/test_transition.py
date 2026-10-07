"""Copied actual59 proof fault tests; no private material or device operations."""
import copy,json,tempfile,unittest,time
from pathlib import Path
from unittest.mock import patch
import transition59 as t
class Transition(unittest.TestCase):
 def setUp(self):
  self.s=t.flow.read_json(t.prior.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json')
 def test_actual_signed_packets(self):t.verify(self.s)
 def test_wrong_counter_and_pending(self):
  for k,v in [('counter',18),('native_pending','other'),('hardware_trial_pending',None)]:
   s=copy.deepcopy(self.s);s[k]=v
   with self.assertRaises(ValueError):t.verify(s)
 def test_rejected_ready(self):
  orig=t.flow.read_json
  def bad(p,*args):
   r=orig(p,*args)
   if str(p).endswith('/firmware-ram-e66kaqfm/report.json'):r['last_receipt']['ready']=0
   return r
  with patch.object(t.flow,'read_json',side_effect=bad),self.assertRaises(ValueError):t.verify(self.s)
 def test_physical_context_release(self):
  control=t.prior.ROOT/'runs/control'
  with tempfile.TemporaryDirectory() as td:
   q=Path(td);raw=json.dumps(self.s).encode()
   (q/'receipt.log').write_bytes((t.prior.ROOT/'runs/post-applied59/receipt.log').read_bytes());(q/'prefix.log').write_bytes((control/'final-prefix59-resume.log').read_bytes())
   r={'writes':0,'observed_at':time.time(),'state_sha256':t.flow.sha(raw),'inputs':{n:t.prior.sha(q/n) for n in ('receipt.log','prefix.log')}};(q/'report.json').write_text(json.dumps(r));t.fresh(q,raw)
   for k,v in [('writes',1),('observed_at',time.time()-301),('state_sha256','0'*64)]:
    b=dict(r);b[k]=v;(q/'report.json').write_text(json.dumps(b))
    with self.assertRaises(ValueError):t.fresh(q,raw)
   (q/'report.json').write_text(json.dumps(r));old=t.raw_callback
   def held(p,n):
    v=bytearray(old(p,n))
    if n==240:v[8+22*4]=1
    return bytes(v)
   with patch.object(t,'raw_callback',side_effect=held),self.assertRaises(ValueError):t.fresh(q,raw)
 def test_copied_retirement_archive_and_failure(self):
  original_state=t.prior.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json';original=original_state.read_bytes()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);state=root/'state.json';state.write_bytes(original);q=root/'read';q.mkdir()
   for n,p in [('receipt.log',t.prior.ROOT/'runs/post-applied59/receipt.log'),('prefix.log',t.prior.ROOT/'runs/control/final-prefix59-resume.log')]:(q/n).write_bytes(p.read_bytes())
   t.flow.save(q/'report.json',{'writes':0,'observed_at':time.time(),'state_sha256':t.flow.sha(original),'inputs':{n:t.prior.sha(q/n) for n in ('receipt.log','prefix.log')}})
   candidate={'native_counter':60,'world_package_sha256':t.prior.WORLD,'source_model_verified':True,'offline_fixture_only':True}
   with patch.object(t,'ROOT',root/'failed'),patch.object(t.shutil,'copytree',side_effect=OSError('fixture archive failure')):
    with self.assertRaises(OSError):t.retire(state,self.s,q,candidate)
   self.assertEqual(state.read_bytes(),original)
   with patch.object(t,'ROOT',root/'success'):
    after,d=t.retire(state,self.s,q,candidate)
   self.assertIsNone(after['hardware_trial_pending']);self.assertEqual(after['engine'],self.s['engine']);self.assertEqual(after['counter'],19)
   for n,h in t.flow.read_json(d/'retirement.json')['inventory']['assets'].items():self.assertEqual(t.prior.sha(d/'assets'/n),h)
  self.assertEqual(original_state.read_bytes(),original)
 def test_retirement_without60_candidate_rejected(self):
  with self.assertRaises(ValueError):t.retire(Path('/never-written'),self.s,Path('/never-read'),{})
if __name__=='__main__':unittest.main()
