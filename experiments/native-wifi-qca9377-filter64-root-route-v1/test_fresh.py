"""Explicit synthetic reports/freshness rejected before any helper/key/BLE call."""
import hashlib,json,tempfile,time,types,unittest
from pathlib import Path
from unittest.mock import patch
import prior63 as p
class Tests(unittest.TestCase):
 def test_reports_reject_early(self):
  before=b'SYNTHETIC NOT STATE';base={'status':'ACTUAL63-RELEASE14-PRE64-OBSERVATION','observed_at':time.time(),'state_sha256':hashlib.sha256(before).hexdigest(),'writes':0,'observer_source_sha256':p.sha(p.ROOT/'observe63.py')}
  bads=[{**base,key:True} for key in ('fixture_kind','synthetic_only','model_capture','test_clock','synthetic_timing_only','synthesized')]+[{**base,'writes':False},{**base,'observed_at':time.time()-301},{**base,'observed_at':time.time()+30},{**base,'observer_source_sha256':'0'*64}]
  for value in bads:
   with self.subTest(value=value),tempfile.TemporaryDirectory() as folder:
    (Path(folder)/'report.json').write_text(json.dumps(value))
    with patch.object(p,'authority',lambda:types.SimpleNamespace(gate=types.SimpleNamespace())),self.assertRaises(ValueError):p.fresh(folder,before)
if __name__=='__main__':unittest.main()
