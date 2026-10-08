"""Offline retirement tests only; never open a key, BLE manager or real state."""
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('transition60', Path(__file__).with_name('transition60.py'))
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

class PublicRetirement(unittest.TestCase):
 def setUp(self):
  self.tmp = tempfile.TemporaryDirectory()
  self.root = Path(self.tmp.name)
  self.state = self.root / 'fake-state.json'
  self.s = {'hardware_trial_pending':'fake-assets','engine':{'native_counter':60},'counter':19,'pending':None,'native_pending':None,'recovery_pending':None}
  self.state.write_text(json.dumps(self.s))
  self.dirs = []
  for name in ('assets','native','fresh','physical'):
   d = self.root / name; (d/'nested').mkdir(parents=True); (d/'nested/data').write_bytes(name.encode());self.dirs.append(d)
  self.admission = {'native_counter':61,'world_package_sha256':t.prior.WORLD,'source_model_verified':True}
 def tearDown(self): self.tmp.cleanup()
 def invoke(self):
  with patch.object(t,'ROOT',self.root/'route'), patch.object(t,'PHYSICAL',self.dirs[3]), patch.object(t,'verify',return_value=tuple(self.dirs[:2])), patch.object(t,'fresh',return_value={'generation':60}):
   return t.retire(self.state,self.s,self.dirs[2],self.admission)
 def test_copies_durable_before_pending_clear(self):
  before = self.state.read_bytes(); original_sync=t._sync_tree; calls=[]
  def sync(directory):
   self.assertEqual(self.state.read_bytes(),before)
   for name,source in zip(('assets','native','fresh-observation','physical60-evidence'),self.dirs):self.assertEqual(t.inventory(directory/name),t.inventory(source))
   original_sync(directory);calls.append(directory)
  with patch.object(t,'_sync_tree',side_effect=sync):after,d=self.invoke()
  self.assertEqual(len(calls),1);self.assertIsNone(after['hardware_trial_pending'])
  expected=dict(self.s);expected['hardware_trial_pending']=None;expected['last_hardware_trial_retirement']=str(d/'retirement.json')
  self.assertEqual(after,expected);self.assertEqual(t.flow.read_json(self.state),expected)
  self.assertEqual((d/'before-state.json').read_bytes(),before)
  for source in self.dirs:self.assertTrue((source/'nested/data').is_file())
 def test_sync_failure_keeps_state(self):
  before=self.state.read_bytes()
  with patch.object(t,'_sync_tree',side_effect=OSError('fake fsync failure')):
   with self.assertRaises(OSError):self.invoke()
  self.assertEqual(self.state.read_bytes(),before)
 def test_existing_archive_not_overwritten(self):
  d=self.root/'route/runs/retired60';d.mkdir(parents=True);(d/'sentinel').write_text('keep')
  before=self.state.read_bytes()
  with self.assertRaises(ValueError):self.invoke()
  self.assertEqual(self.state.read_bytes(),before);self.assertEqual((d/'sentinel').read_text(),'keep')
 def test_wrong_generation_rejected(self):
  self.admission['native_counter']=60
  with self.assertRaises(ValueError):self.invoke()
  self.assertFalse((self.root/'route/runs').exists())
 def test_symlink_rejected(self):
  (self.dirs[0]/'link').symlink_to(self.dirs[1]/'nested/data')
  before=self.state.read_bytes()
  with self.assertRaises(ValueError):self.invoke()
  self.assertEqual(self.state.read_bytes(),before)
 def test_state_race_during_sync_rejected(self):
  def sync(_):self.state.write_text('{}')
  with patch.object(t,'_sync_tree',side_effect=sync):
   with self.assertRaisesRegex(ValueError,'state changed'):self.invoke()
  self.assertEqual(self.state.read_text(),'{}')
 def observation(self):
  # Synthetic bytes live only inside this host test; no physical admission is
  # exercised and no output is presented as a real hardware observation.
  q=self.root/'observation';q.mkdir()
  rfs=b'RFS\1'+b'\0'*16+b'\2\0\0\0'+(60).to_bytes(4,'little')+bytes.fromhex(t.NATIVE_PACKET)
  (q/'receipt.log').write_text(json.dumps({'code':0,'stage':'value bytes:60 hex:'+rfs.hex()})+'\n')
  rows=[]
  for name in ('QPFX','QWBT','QWOP','QWIN'):
   raw=bytes.fromhex((t.PHYSICAL/(name+'.hex')).read_text())
   rows.append({'writes':0,'peripheral':t.prior.PEER,'NSError_code':0,'NSError_domain':'','stage':'value-read','raw_bytes':len(raw),'raw_hex':raw.hex()})
  report={'status':'ACTUAL60-RELEASE14-PRE61-OBSERVATION','writes':0,'state_sha256':t.flow.sha(self.state.read_bytes()),'observed_at':time.time(),**t.observation_tools()}
  self.save_observation(q,report,rows)
  return q,report,rows
 def save_observation(self,q,report,rows):
  (q/'collector.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in rows))
  report['inputs']={n:t.prior.sha(q/n) for n in ('receipt.log','collector.jsonl')}
  (q/'report.json').write_text(json.dumps(report))
 def test_fresh_raw_format_pass_stale_wrong_peer_fail(self):
  q,report,rows=self.observation();self.assertEqual(t.fresh(q,self.state.read_bytes())['generation'],60)
  report['observed_at']-=301;self.save_observation(q,report,rows)
  with self.assertRaisesRegex(ValueError,'fresh'):t.fresh(q,self.state.read_bytes())
  report['observed_at']=time.time();rows[0]['peripheral']='OTHER';self.save_observation(q,report,rows)
  with self.assertRaisesRegex(ValueError,'wrong peer'):t.fresh(q,self.state.read_bytes())
 def test_status_and_explicit_synthetic_metadata_rejected(self):
  q,report,rows=self.observation()
  for key in ('fixture_kind','synthetic_only','mocked','test_clock','host_fixture'):
   report[key]='HOST';self.save_observation(q,report,rows)
   with self.assertRaisesRegex(ValueError,'synthetic'):t.fresh(q,self.state.read_bytes())
   report.pop(key)
  report['status']='SYNTHETIC-HOST';self.save_observation(q,report,rows)
  with self.assertRaisesRegex(ValueError,'status'):t.fresh(q,self.state.read_bytes())
  report['status']='ACTUAL60-RELEASE14-PRE61-OBSERVATION';rows[0]['fixture_kind']='HOST';self.save_observation(q,report,rows)
  with self.assertRaisesRegex(ValueError,'synthetic'):t.fresh(q,self.state.read_bytes())
 def test_exact_public_helper_provenance_required(self):
  q,report,rows=self.observation()
  for key in ('receipt_reader_sha256','collector_sha256','observer_source_sha256'):
   original=report[key];report[key]='0'*64;self.save_observation(q,report,rows)
   with self.assertRaisesRegex(ValueError,'provenance'):t.fresh(q,self.state.read_bytes())
   report[key]=original
 def test_four_exact_ordered_values_required(self):
  q,report,rows=self.observation()
  for altered in (rows[:1],rows[:3],rows+[rows[0]],[rows[1],rows[0],*rows[2:]]):
   self.save_observation(q,report,altered)
   with self.assertRaises(ValueError):t.fresh(q,self.state.read_bytes())
  for index in range(4):
   altered=[dict(row) for row in rows];altered[index]['raw_bytes']-=1;self.save_observation(q,report,altered)
   with self.assertRaisesRegex(ValueError,'envelope'):t.fresh(q,self.state.read_bytes())
 def test_fresh_boot_and_owned_ready_required(self):
  q,report,rows=self.observation()
  for index,offset in ((1,12),(1,16),(3,12),(3,116),(3,116+40)):
   altered=[dict(row) for row in rows];raw=bytearray.fromhex(altered[index]['raw_hex']);raw[offset]^=1;altered[index]['raw_hex']=raw.hex();self.save_observation(q,report,altered)
   with self.assertRaises(ValueError):t.fresh(q,self.state.read_bytes())
  # Other QWIN diagnostic counters may vary; exact owned READY frame still binds.
  altered=[dict(row) for row in rows];raw=bytearray.fromhex(altered[3]['raw_hex']);raw[64]^=1;altered[3]['raw_hex']=raw.hex();self.save_observation(q,report,altered)
  self.assertEqual(t.fresh(q,self.state.read_bytes())['generation'],60)

if __name__ == '__main__':unittest.main()
