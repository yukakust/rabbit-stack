"""Pure public/fake-filesystem tests only. Never retire actual hardware state."""
from pathlib import Path
import importlib.util,sys,types,tempfile,json,time,hashlib,copy
import unittest
from unittest.mock import patch
R=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('test_htt62_transition',R/'transition61.py');t=importlib.util.module_from_spec(sp);sp.loader.exec_module(t);g=t.g
class PublicTests(unittest.TestCase):
 def test_import_collision_guard(self):
  sentinels={n:types.ModuleType(n) for n in ('gate','launch','transition59','assets','route')}
  saved={n:sys.modules.get(n) for n in sentinels};paths=list(sys.path)
  try:
   sys.modules.update(sentinels);sp=importlib.util.spec_from_file_location('new_gate_collision',R/'gate.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
   for n,s in sentinels.items():self.assertIs(sys.modules[n],s)
   self.assertEqual(sys.path,paths);self.assertEqual(m.PAYLOAD,g.PAYLOAD)
  finally:
   for n,v in saved.items():
    if v is None:sys.modules.pop(n,None)
    else:sys.modules[n]=v
 def test_exact62_public_gate(self):
  world=(g.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/world19.rwp')
  # Read public package path, not private or hardware state mutation.
  state=g.flow.read_json(g.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json')
  payload=(g.CHECKED/'payload.efi').read_bytes();package=Path(state['package']).read_bytes()
  self.assertEqual(g.gates(g.CHECKED,payload,package)['native_counter'],62)
  altered=bytearray(payload);altered[-1]^=1
  with self.assertRaises(ValueError):g.gates(g.CHECKED,altered,package)
  with self.assertRaises(ValueError):g.gates(g.CHECKED,payload,b'wrong-world')
 def test_report_pin_rejects_scope_empty_closure_duplicate_qemu(self):
  baseline=g.flow.read_json(g.CHECKED/'report.json')
  for kind in ('receiver_kind','empty_inputs','qemu_duplicate'):
   with tempfile.TemporaryDirectory() as folder:
    q=Path(folder);report=copy.deepcopy(baseline)
    if kind=='receiver_kind':report['receiver_policy']['kind']=99
    elif kind=='empty_inputs':report['source_sha256']={};report['generated_compiler_sources_sha256']={}
    else:report['gates']=[report['gates'][0],report['gates'][0]]
    (q/'report.json').write_text(json.dumps(report));payload=(g.CHECKED/'payload.efi').read_bytes()
    with patch.object(g,'CHECKED',q):
     with self.assertRaisesRegex(ValueError,'frozen62'):g.gates(q,payload,b'wrongworld')
 def fixture_observation(self,q,state):
  d,raw=t.physical();rfs=b'RFS\1'+b'\0'*16+b'\2\0\0\0'+(61).to_bytes(4,'little')+bytes.fromhex(t.PACKET61)
  (q/'receipt.log').write_text(json.dumps({'code':0,'stage':'value bytes:60 hex:'+rfs.hex()})+'\n')
  row={'stage':'diagnostic-status-read-untrusted-parent','peripheral':t.PEER,'writes':0,'NSError_code':0,'NSError_domain':'','info':{'parent_service':'52414242-4954-4649-8000-00000000002A','UUID':'52414242-4954-4649-8000-00000000002B','bytes':416,'cached_value_possible':0,'hex':raw.hex()}}
  (q/'inventory.jsonl').write_text(json.dumps(row)+'\n')
  proof=g.flow.read_json(g.REPO/'experiments/native-wifi-qca9377-observation59-root-route-v1/evidence/root-proof.json')
  r={'status':'ACTUAL61-RELEASE14-PRE62-OBSERVATION','writes':0,'state_sha256':g.flow.sha(state),'observed_at':time.time(),'inputs':{n:g.sha(q/n) for n in ('receipt.log','inventory.jsonl')},'receipt_reader_sha256':proof['source_sha256'][str(t.READER.relative_to(g.REPO))],'inventory_source_sha256':t.INVENTORY_SOURCE_SHA,'inventory_executable_sha256':t.INVENTORY_EXE_SHA,'observer_source_sha256':'f'*64}
  (q/'report.json').write_text(json.dumps(r));return r,row
 def test_fresh_fixture_and_parent_error_stale_negatives(self):
  with tempfile.TemporaryDirectory() as folder:
   q=Path(folder);state=b'public-test-state';r,row=self.fixture_observation(q,state);original=g.sha
   def sha(p):return 'f'*64 if Path(p)==R/'observe61.py' else original(p)
   with patch.object(g,'sha',side_effect=sha):
    self.assertEqual(t.fresh(q,state)['generation'],61)
    for kind in ('stale','wrong_parent','callback_error','wrong_receipt','wrong_tool'):
     r,row=self.fixture_observation(q,state)
     if kind=='stale':r['observed_at']-=301
     if kind=='wrong_tool':r['inventory_executable_sha256']='0'*64
     if kind=='wrong_parent':row['info']['parent_service']='52414242-4954-4649-8000-000000000040'
     if kind=='callback_error':row['NSError_code']=7
     if kind=='wrong_receipt':(q/'receipt.log').write_text(json.dumps({'code':0,'stage':'value bytes:60 hex:'+(b'RFS\1'+b'\0'*16+b'\2\0\0\0'+(60).to_bytes(4,'little')+bytes.fromhex(t.PACKET61)).hex()})+'\n')
     (q/'inventory.jsonl').write_text(json.dumps(row)+'\n');r['inputs']={n:original(q/n) for n in ('receipt.log','inventory.jsonl')};(q/'report.json').write_text(json.dumps(r))
     with self.assertRaises(ValueError):t.fresh(q,state)
class FakeRetirement(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.state=self.root/'fake-state.json';self.s={'engine':{'native_counter':61},'counter':19,'hardware_trial_pending':'fake-assets','pending':None,'native_pending':None,'recovery_pending':None};self.state.write_text(json.dumps(self.s));self.sources=[]
  for name in ('assets','native','fresh','physical'):
   p=self.root/name;(p/'nested').mkdir(parents=True);(p/'nested/data').write_bytes(name.encode());self.sources.append(p)
  self.admit={'native_counter':62,'payload_sha256':g.PAYLOAD,'report_sha256':g.REPORT,'world_package_sha256':g.WORLD,'source_model_verified':True}
 def tearDown(self):self.tmp.cleanup()
 def invoke(self):
  with patch.object(t,'ROOT',self.root/'route'),patch.object(t,'PHYSICAL',self.sources[3]),patch.object(t,'verify',return_value=tuple(self.sources[:2])),patch.object(t,'fresh',return_value={'generation':61}):return t.retire(self.state,self.s,self.sources[2],self.admit)
 def test_archive_durable_before_clear(self):
  before=self.state.read_bytes();sync=t.sync_tree;called=[]
  def checked(directory):self.assertEqual(self.state.read_bytes(),before);sync(directory);called.append(1)
  with patch.object(t,'sync_tree',side_effect=checked):after,d=self.invoke()
  self.assertEqual(called,[1]);self.assertIsNone(after['hardware_trial_pending']);expect=dict(self.s);expect['hardware_trial_pending']=None;expect['last_hardware_trial_retirement']=str(d/'retirement.json');self.assertEqual(after,expect)
  for name,p in zip(('assets','native','fresh-observation','physical61-evidence'),self.sources):self.assertEqual(t.inventory(p),t.inventory(d/name))
  self.assertEqual((d/'before-state.json').read_bytes(),before)
 def test_fsync_failure_no_state_clear(self):
  before=self.state.read_bytes()
  with patch.object(t,'sync_tree',side_effect=OSError('fake fsync')):
   with self.assertRaises(OSError):self.invoke()
  self.assertEqual(self.state.read_bytes(),before)
 def test_existing_archive_no_overwrite(self):
  d=self.root/'route/runs/retired61';d.mkdir(parents=True);(d/'sentinel').write_text('keep')
  with self.assertRaises(ValueError):self.invoke()
  self.assertEqual((d/'sentinel').read_text(),'keep')
 def test_wrong62_candidate_rejected(self):
  for n,v in [('native_counter',61),('payload_sha256','0'*64),('report_sha256','0'*64),('source_model_verified',False)]:
   old=self.admit[n];self.admit[n]=v
   with self.assertRaises(ValueError):self.invoke()
   self.admit[n]=old
  self.assertFalse((self.root/'route').exists())
 def test_symlink_rejected(self):
  (self.sources[0]/'link').symlink_to(self.sources[1]/'nested/data')
  before=self.state.read_bytes()
  with self.assertRaises(ValueError):self.invoke()
  self.assertEqual(self.state.read_bytes(),before)
 def test_state_race_rejected(self):
  def changed(_):self.state.write_text('{}')
  with patch.object(t,'sync_tree',side_effect=changed):
   with self.assertRaisesRegex(ValueError,'state changed'):self.invoke()
  self.assertEqual(self.state.read_text(),'{}')
if __name__=='__main__':unittest.main()
