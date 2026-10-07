"""Copied-state HOST tests only. Synthetic auth/EMPTY never physical evidence."""
import copy,fcntl,importlib.util,json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import route
ROOT=route.ROOT;REPO=route.REPO;G=route.GATE
class KeyBoundaryReached(Exception):pass
class RouteTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'runs');self.d=Path(self.tmp.name);self.state=self.d/'state.json';self.before=self.d/'before-state.json';self.archive=self.d/'retirement'
  s=route.gate.read(G/'evidence/2026-10-07/root-before-recovery/before-state.json')
  def relocate(v):
   if isinstance(v,str) and v.startswith('/Users/yukakust/rabbit-stack/'):return str(route.reference(v))
   if isinstance(v,dict):return {k:relocate(x) for k,x in v.items()}
   if isinstance(v,list):return [relocate(x) for x in v]
   return v
  self.s=relocate(s);raw=route.encoded(self.s);self.state.write_bytes(raw);self.before.write_bytes(raw)
  pre=G/'evidence/2026-10-07/root-before-recovery'
  for name in ('boot55.json','boot55.decoded.json','passive-near55.json','public-bundle.json'):(self.d/name).write_bytes((pre/name).read_bytes())
  metadata=route.gate.read(pre/'root-preflight.json');metadata['before_state_sha256']=route.sha(raw);(self.d/'root-preflight.json').write_bytes(route.encoded(metadata))
  now=time.time();self.auth=self.d/'authorization.json';self.obs=self.d/'observation.json';self.log=self.d/'query.log';self.log.write_bytes(b'HOST MODEL SYNTHETIC QUERY - NOT A DELL OBSERVATION')
  a={'explicit_owner_authorization':True,'action':'controlled-dell-reboot-for-native55-recovery','native_counter':55,'state_before_sha256':route.sha(raw),'owner_message_reference':'SYNTHETIC HOST TEST ONLY','authorized_at':now-10};self.auth.write_bytes(route.encoded(a))
  self.o={'owner_confirmed_reboot':True,'authorization_sha256':route.sha(self.auth.read_bytes()),'observed_at':now-1,'reboot_confirmed_at':now-5,'peripheral':route.gate.PEER,'writes':0,'receiver':{'raw_hex':route.gate.EMPTY,'outcome':'idle','counter':0},'log_sha256':route.sha(self.log.read_bytes())};self.obs.write_bytes(route.encoded(self.o))
  (self.d/'control').mkdir();(self.d/'control/journal.json').write_text('{"active":null}')
  self.checked=G/'runs/plain-city56-retry1'
 def tearDown(self):self.tmp.cleanup()
 def retire(self):return route.retire(self.state,self.before,self.auth,self.obs,self.log,self.archive)
 def admit(self):return route.admission(self.state,self.archive/'retirement.json',self.checked)
 def test_actual_writer_only_intended_transition(self):
  raw=self.state.read_bytes();audit=self.retire();after=route.gate.read(self.state);expected=copy.deepcopy(self.s);expected['hardware_trial_pending']=None
  expected.setdefault('retired_hardware_trials',[]).append(after['retired_hardware_trials'][-1]);self.assertEqual(after,expected);self.assertEqual(raw,(self.archive/'before-state.json').read_bytes())
  self.assertFalse(audit['actual_all14_owner_release_proved']);self.assertFalse(audit['native56_reserved']);self.assertEqual(self.admit()['native_counter_candidate'],56)
  with self.assertRaises(ValueError):self.retire()
 def test_stale_and_wrong_receipt_no_state_write(self):
  raw=self.state.read_bytes()
  for k,v in [('observed_at',time.time()-301),('owner_confirmed_reboot',False),('peripheral','OTHER')]:
   o=copy.deepcopy(self.o);o[k]=v;self.obs.write_bytes(route.encoded(o))
   with self.assertRaises(ValueError):self.retire()
   self.assertEqual(raw,self.state.read_bytes());self.assertFalse(self.archive.exists())
 def test_changed_state_no_archive_or_write(self):
  self.state.write_bytes(self.state.read_bytes()+b' ');before=self.state.read_bytes()
  with self.assertRaises(ValueError):self.retire()
  self.assertEqual(before,self.state.read_bytes());self.assertFalse(self.archive.exists())
 def test_real_lock_contended(self):
  with (self.d/'state.lock').open('a') as f:
   fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   with self.assertRaises(ValueError):self.retire()
  self.assertIsNotNone(route.gate.read(self.state)['hardware_trial_pending'])
 def test_failure_during_archive_retains_pending(self):
  raw=self.state.read_bytes()
  with patch.object(route,'archive_blob',side_effect=OSError('HOST disk failure')):
   with self.assertRaises(OSError):self.retire()
  self.assertEqual(raw,self.state.read_bytes())
 def test_nested_fsync_failure_retains_pending(self):
  raw=self.state.read_bytes();original=route.fsync_directory;calls=[]
  def failed(path):
   calls.append(Path(path))
   if Path(path).name=='assets55':raise OSError('HOST injected nested-dir fsync failure')
   return original(path)
  with patch.object(route,'fsync_directory',side_effect=failed):
   with self.assertRaises(OSError):self.retire()
  self.assertEqual(raw,self.state.read_bytes());self.assertIn(self.archive/'assets55',calls)
 def test_all_archive_dirs_fsynced_before_commit(self):
  calls=[];original=route.fsync_directory;atomic=route.atomic
  def synced(path):calls.append(Path(path));return original(path)
  def commit(path,data):
   for name in ('native55','assets55','world17','checked55','root-before-recovery'):
    self.assertIn(self.archive/name,calls)
   self.assertIn(self.archive,calls);self.assertIn(self.archive.parent,calls)
   return atomic(path,data)
  with patch.object(route,'fsync_directory',side_effect=synced),patch.object(route,'atomic',side_effect=commit):self.retire()
 def test_archive_corruption_admission_rejected(self):
  self.retire();(self.archive/'assets55/chunk-11.bin').write_bytes(b'bad')
  with self.assertRaises(ValueError):self.admit()
 def test_post_retirement_state_and_freshness_guards(self):
  self.retire();raw=self.state.read_bytes();s=json.loads(raw);s['engine']['native_counter']=56;self.state.write_bytes(route.encoded(s))
  with self.assertRaises(ValueError):self.admit()
  self.state.write_bytes(raw)
  with patch('time.time',return_value=time.time()+400):
   with self.assertRaises(ValueError):self.admit()
 def load_original(self):
  p=REPO/'experiments/native-wifi-qca9377-v1/reboot_recovery.py';spec=importlib.util.spec_from_file_location('host_original_recovery',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 def test_original_prepare_reaches_mocked_key_boundary_only_after_checks(self):
  self.retire();self.admit();m=self.load_original();old=(m.reservation,m.gate,m.engine);private=self.d/'DUMMY-NO-KEY';private.with_suffix('.pub').write_bytes(route.gate.OWNER);calls=[];raw=self.state.read_bytes()
  def stop(path):calls.append(path);raise KeyBoundaryReached()
  with patch.object(m.engine,'load_private',side_effect=stop):
   with self.assertRaises(KeyBoundaryReached):route.guarded_prepare56(self.state,self.archive/'retirement.json',self.checked,self.d/'prepared',private,_recovery=m)
  self.assertEqual(len(calls),1);self.assertFalse(private.exists());self.assertEqual(raw,self.state.read_bytes());self.assertEqual((m.reservation,m.gate,m.engine),old)
 def test_inlock_journal_mutation_rejects_before_mocked_key(self):
  self.retire();self.admit();m=self.load_original();old=m.reservation;calls=[];private=self.d/'DUMMY-NO-KEY';private.with_suffix('.pub').write_bytes(route.gate.OWNER)
  def changed(*args):
   result=old(*args);(self.d/'control/journal.json').write_text('{"active":"HOST mutation"}');return result
  m.reservation=changed;before=(m.reservation,m.gate,m.engine)
  with patch.object(m.engine,'load_private',side_effect=lambda p:calls.append(p)):
   with self.assertRaises(ValueError):route.guarded_prepare56(self.state,self.archive/'retirement.json',self.checked,self.d/'refused',private,_recovery=m)
  self.assertFalse(calls);self.assertEqual((m.reservation,m.gate,m.engine),before)
 def test_inlock_counter_freshness_source_guards_before_key(self):
  self.retire();self.admit();raw=self.state.read_bytes();private=self.d/'DUMMY-NO-KEY';private.with_suffix('.pub').write_bytes(route.gate.OWNER)
  for scenario in ('counter','freshness','source'):
   self.state.write_bytes(raw);m=self.load_original();reservation=m.reservation;calls=[];changed=[False];original_sha=route.sha;original_time=time.time;source_bytes=(ROOT/'route.py').read_bytes()
   def reserved(*args):
    result=reservation(*args);changed[0]=True
    if scenario=='counter':
     st=route.gate.read(self.state);st['engine']['native_counter']=56;self.state.write_bytes(route.encoded(st))
    return result
   def clock():return original_time()+(400 if changed[0] and scenario=='freshness' else 0)
   def digest(data):return '0'*64 if changed[0] and scenario=='source' and data==source_bytes else original_sha(data)
   m.reservation=reserved;old=(m.reservation,m.gate,m.engine)
   with patch.object(m.engine,'load_private',side_effect=lambda p:calls.append(p)),patch('time.time',side_effect=clock),patch.object(route,'sha',side_effect=digest):
    with self.assertRaises(ValueError):route.guarded_prepare56(self.state,self.archive/'retirement.json',self.checked,self.d/('refused-'+scenario),private,_recovery=m)
   self.assertFalse(calls,scenario);self.assertEqual((m.reservation,m.gate,m.engine),old)
if __name__=='__main__':unittest.main()
