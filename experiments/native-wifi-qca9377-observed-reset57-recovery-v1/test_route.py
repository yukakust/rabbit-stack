"""Copied-state HOST tests ONLY; no signing/key/radio/native compilation."""
import copy,json,pathlib,shutil,tempfile,time,types,unittest
from unittest.mock import patch
import route
ROOT=pathlib.Path(__file__).resolve().parent
BASE=route.REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/evidence/2026-10-07/user-screen-reset'
class KeyBoundary(Exception):pass
class Cases(unittest.TestCase):
 def setUp(self):
  (ROOT/'runs').mkdir(exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'runs');self.d=pathlib.Path(self.tmp.name)
  self.s=route.loads(route.read(BASE/'before-state.json'));native=pathlib.Path(self.s['engine']['last_release_report']).parent;assets=pathlib.Path(self.s['hardware_trial_pending'])
  shutil.copytree(native,self.d/'native57');shutil.copytree(assets,self.d/'assets57')
  self.s['engine']['last_release_report']=str(self.d/'native57/report.json');self.s['hardware_trial_pending']=str(self.d/'assets57')
  self.state=self.d/'state.json';self.before=self.d/'before-state.json';self.raw=route.encoded(self.s);self.state.write_bytes(self.raw);self.before.write_bytes(self.raw)
  (self.d/'control').mkdir();(self.d/'control/journal.json').write_text('{"active":null}')
  self.obs=self.d/'observation.json';self.log=self.d/'query.log';self.photo=self.d/'owner-screen.png';self.archive=self.d/'retirement'
  self.log.write_bytes(route.read(BASE/'fresh-receipt.log'));self.photo.write_bytes(route.read(BASE/'owner-screen.png',10_000_000))
  self.o=route.loads(route.read(BASE/'observation.json'));self.o.update(observed_at=time.time(),peripheral=route.pub.PEER,state_before_sha256=route.sha(self.raw));self.obs.write_bytes(route.encoded(self.o))
 def tearDown(self):self.tmp.cleanup()
 def retire(self):return route.retire(self.state,self.before,self.obs,self.log,self.photo,self.archive)
 def activate(self):
  self.retire();p=self.d/'activation.json';p.write_bytes(route.encoded({'state_sha256':route.sha(self.state.read_bytes()),'retirement':str(self.archive/'retirement.json'),'retirement_sha256':route.sha((self.archive/'retirement.json').read_bytes()),'observation':str(self.obs),'query_log':str(self.log),'photo':str(self.photo),'receiver_bootstrap_observed':True,'manual_reboot_confirmed':False}));return p
 def test_exact_copied_retirement(self):
  a=self.retire();after=route.loads(self.state.read_bytes());self.assertIsNone(after['hardware_trial_pending']);self.assertEqual((after['engine']['native_counter'],after['counter']),(57,18));self.assertFalse(a['manual_reboot_confirmed']);self.assertFalse(a['proof']['actual_all14_owner_release_proved']);self.assertEqual(a['public_bundle']['saved_public_packets_verified'],12)
  self.assertEqual(route.read(self.archive/'before-state.json'),self.raw);self.assertEqual(route.loads(route.read(self.archive/'assets57/report.json'))['completed_chunks'],10)
  route.verify_retirement(self.state,self.archive/'retirement.json')
 def test_stale_missing_peer_human_flags_no_writes(self):
  for key,value in [('observed_at',time.time()-301),('peripheral','other'),('owner_confirmed_manual_reboot',True),('reboot_command_sent',True),('state_before_sha256','f'*64),('photo_sha256','f'*64),('fresh_read_log_sha256','f'*64),('writes',False)]:
   with self.subTest(key=key):
    x=copy.deepcopy(self.o);x[key]=value;self.obs.write_bytes(route.encoded(x))
    with self.assertRaises(ValueError):self.retire()
    self.assertEqual(self.state.read_bytes(),self.raw);self.assertFalse(self.archive.exists())
  x=copy.deepcopy(self.o);x.pop('peripheral');self.obs.write_bytes(route.encoded(x))
  with self.assertRaises(ValueError):self.retire()
 def test_archive_before_atomic_failure(self):
  with patch.object(route,'atomic',side_effect=RuntimeError('injected before state commit')):
   with self.assertRaises(RuntimeError):self.retire()
  self.assertEqual(self.state.read_bytes(),self.raw);self.assertTrue((self.archive/'retirement.json').exists());self.assertTrue((self.archive/'assets57/chunk-11.bin').exists())
 def test_changed_state_journal_and_controller_lock(self):
  self.state.write_bytes(self.raw+b' ')
  with self.assertRaises(ValueError):self.retire()
  self.state.write_bytes(self.raw);(self.d/'control/journal.json').write_text('{"active":"worldwork"}')
  with self.assertRaises(ValueError):self.retire()
  (self.d/'control/journal.json').write_text('{"active":null}')
  with route.locked(self.state):
   with self.assertRaises(ValueError):self.retire()
 def test_asset_native_corruption(self):
  for path in (self.d/'assets57/chunk-11.bin',self.d/'native57/native.rrt'):
   path.chmod(0o600);original=path.read_bytes();path.write_bytes(original+b'x')
   with self.assertRaises(ValueError):self.retire()
   path.write_bytes(original)
  a=route.loads(route.read(self.d/'assets57/report.json'));a['completed_chunks']=12;(self.d/'assets57/report.json').write_bytes(route.encoded(a))
  with self.assertRaises(ValueError):self.retire()
 def test_activation_guarded_original_prepare_key_boundary(self):
  p=self.activate();route.activation_proof(self.state,p);calls=[]
  def key(*args):calls.append('key-boundary');raise KeyBoundary()
  def gate(*args):calls.append('originalgate');return b'notpayload',{'restored_package_sha256':route.WORLD19}
  module=types.SimpleNamespace(engine=types.SimpleNamespace(load_private=key),gate=gate)
  def prepare(*args):module.gate(None,None,None);module.engine.load_private(None)
  module.prepare=prepare
  # Wrong proven payload is denied BEFORE reaching mocked key boundary.
  with self.assertRaises(ValueError):route.guarded_prepare(self.state,self.d,self.d/'candidate',None,p,_recovery=module)
  self.assertEqual(calls,['originalgate'])
  module.gate=lambda *args:(route.read(route.REPO/'experiments/native-wifi-qca9377-reboot-recovery55-root-v1/evidence/2026-10-07/actual-city56-world18/saved-plan/payload.efi'),{'restored_package_sha256':route.WORLD19})
  with self.assertRaises(KeyBoundary):route.guarded_prepare(self.state,self.d,self.d/'candidate',None,p,_recovery=module)
  self.assertEqual(calls[-1],'key-boundary');self.assertIs(module.engine.load_private,key)
 def test_no_unguarded_duplicate_prepare_or_fake_human_claim(self):
  source=route.read(ROOT/'restore_observed.py').decode();self.assertNotIn('def prepare(',source);self.assertNotIn('engine.load_private',source);self.assertNotIn('owner_confirmed_reboot=True',source);self.assertNotIn('dell_rebooted',source);self.assertIn('manual_reboot_confirmed=False',source)
 def test_resume_proof_and_archival_corruption(self):
  p=self.activate();report={'bootstrap_proof':str(p),'bootstrap_proof_sha256':route.sha(p.read_bytes())};route.resume_proof(report)
  file=self.archive/'assets57/chunk-0.bin';file.write_bytes(file.read_bytes()+b'x')
  with self.assertRaises(ValueError):route.resume_proof(report)
if __name__=='__main__':unittest.main()
