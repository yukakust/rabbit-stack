"""Host-only regression: actual resume main reaches current guard then saved deliver."""
import json,tempfile,sys,subprocess,unittest
from pathlib import Path
from unittest.mock import patch
import resume_assets60_v2 as m
class Resume(unittest.TestCase):
 def test_guard_delivery_and_failure_stop(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);state=root/'state.json';session=root/'assets';session.mkdir();before=json.dumps({'hardware_trial_pending':str(session)}).encode();state.write_bytes(before)
   report={'completed_chunks':0,'sender_steps':[]};(session/'report.json').write_text(json.dumps(report));guards=[];calls=[]
   def guard(s,d):guards.append((s,d))
   def fake(cmd,**kwargs):calls.append(cmd);return subprocess.CompletedProcess(cmd,23)
   with patch.object(m,'STATE',state),patch.object(sys,'argv',['resume',str(session)]),patch.object(m.route,'current',side_effect=guard),patch.object(subprocess,'run',side_effect=fake):
    with self.assertRaisesRegex(ValueError,'nonordinary route failure; stop'):m.main()
   self.assertEqual(len(guards),1);self.assertEqual(len(calls),1);self.assertTrue(calls[0][1].endswith('/assets60.py'));self.assertEqual(calls[0][-1],str(session));self.assertEqual(state.read_bytes(),before)
if __name__=='__main__':unittest.main()
