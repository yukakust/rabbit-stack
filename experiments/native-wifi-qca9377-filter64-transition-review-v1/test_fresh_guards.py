"""Pure fresh63 validation with mocked receipt parser; never actual observation."""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys,tempfile,time,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
SCOPE=ROOT.parent/'native-wifi-qca9377-filter64-root-route-v1'
spec=importlib.util.spec_from_file_location('_review64_prior',SCOPE/'prior63.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class Guards(unittest.TestCase):
 def test_synthetic_context_rejection(self):
  route=p.authority();g=route.gate;reader=g.REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt';proof=g.flow.read_json(g.base60.prior.ROOT/'evidence/root-proof.json')
  before=b'PURE-TEST-STATE';receipt=bytearray(60);receipt[:4]=b'RFS\1';receipt[20:24]=b'\2\0\0\0';receipt[24:28]=(63).to_bytes(4,'little');receipt[28:]=bytes.fromhex('55d2a292e08011dc4377d104f333e59f40cc4537d5906604f838f8beb193a90f')
  existing=[json.loads(line) for line in (p.EVIDENCE/'progress63.jsonl').read_text().splitlines()]
  rows=[next(v for v in reversed(existing) if v['stage']=='value-read' and v['index']==0),next(v for v in reversed(existing) if v['stage']=='value-read' and v['index']==1)]
  for case in ('baseline','expired','future','observer','reportbool','rowbool',*[f'{where}:{key}' for where in ('report','row') for key in ('fixture_kind','synthetic_only','test_clock','model_capture')]):
   with self.subTest(case=case),tempfile.TemporaryDirectory() as directory:
    folder=Path(directory);testrows=copy.deepcopy(rows);(folder/'receipt.log').write_text('PURE MOCK PARSER INPUT')
    report={'status':'ACTUAL63-RELEASE14-PRE64-OBSERVATION','writes':0,'observed_at':time.time(),'state_sha256':hashlib.sha256(before).hexdigest(),'observer_source_sha256':p.sha(SCOPE/'observe63.py'),'receipt_reader_sha256':proof['source_sha256'][str(reader.relative_to(g.REPO))],'monitor_sha256':p.sha(route.admission.monitor_gate.checked())}
    if ':' in case:
     where,key=case.split(':');(report if where=='report' else testrows[0])[key]=True
    if case=='expired':report['observed_at']-=301
    if case=='future':report['observed_at']+=60
    if case=='observer':report['observer_source_sha256']='0'*64
    if case=='reportbool':report['writes']=False
    if case=='rowbool':testrows[0]['writes']=False
    (folder/'monitor.jsonl').write_text('\n'.join(json.dumps(v) for v in testrows)+'\n');report['inputs']={n:p.sha(folder/n) for n in ('receipt.log','monitor.jsonl')};(folder/'report.json').write_text(json.dumps(report))
    with patch.object(p,'authority',lambda:route),patch.object(g.base60.t,'raw_callback',lambda *_:bytes(receipt)):
     if case=='baseline':self.assertEqual(p.fresh(folder,before)['physical_counter'],63)
     else:
      with self.assertRaises(ValueError):p.fresh(folder,before)
if __name__=='__main__':unittest.main()
