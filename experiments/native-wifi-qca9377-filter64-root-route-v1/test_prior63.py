"""Read-only replay + corruption tests in disposable copies; never actual state edits."""
import hashlib,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import prior63 as p
class Tests(unittest.TestCase):
 def test_actual_public_replay(self):self.assertEqual(p.verify()['status'],'PUBLIC63-FULL12-BOOT-QUEUED-ECHO-RELEASE14-PASS')
 def test_changed_state(self):
  with tempfile.TemporaryDirectory() as folder:
   state=Path(folder)/'state.json';state.write_bytes(p.STATE.read_bytes()+b' ')
   with self.assertRaisesRegex(ValueError,'current state differs'):p.verify(state)
 def test_corrupted_retained_evidence(self):
  for name in ('verdict.json',*json.loads((p.EVIDENCE/'verdict.json').read_text())['inputs']):
   with self.subTest(name=name),tempfile.TemporaryDirectory() as folder:
    evidence=Path(folder)/'evidence';shutil.copytree(p.EVIDENCE,evidence)
    with (evidence/name).open('ab') as f:f.write(b' ')
    with patch.object(p,'EVIDENCE',evidence),self.assertRaises(ValueError):p.verify()
if __name__=='__main__':unittest.main()
