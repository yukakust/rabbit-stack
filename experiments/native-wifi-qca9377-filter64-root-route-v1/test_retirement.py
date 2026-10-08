"""Synthetic archive/ownership/race faults. Never actual state, gate, BLE or key."""
import hashlib,json,shutil,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import transition63 as t
class Tests(unittest.TestCase):
 def test_order_and_faults(self):
  for case in ('positive','wrong-candidate','gate-reject','false-model','source-corrupt','archive-corrupt','source-symlink','archive-exists','state-before-race','state-after-sync-race','sync-failed','freshness-expired-after-sync'):
   with self.subTest(case=case),tempfile.TemporaryDirectory() as folder:
    base=Path(folder);state_path=base/'state.json';world=base/'world';world.write_bytes(b'FIXTURE');checked=base/'checked';checked.mkdir();(checked/'payload.efi').write_bytes(b'FIXTURE');scope=base/'scope';scope.mkdir()
    folders={key:base/key for key in ('native','assets','observation','physical')}
    for path in folders.values():path.mkdir();(path/'data').write_bytes(b'FIXTURE')
    state={'package':str(world),'hardware_trial_pending':str(folders['assets']),'engine':{'last_release_report':str(folders['native']/'report.json')}};state_path.write_text(json.dumps(state));before=state_path.read_bytes();events=[]
    def save(path,value):
     events.append('state' if path==state_path else 'archive');Path(path).write_text(json.dumps(value))
    flow=types.SimpleNamespace(read_json=lambda p:json.loads(Path(p).read_text()),save=save,sha=lambda b:hashlib.sha256(b).hexdigest())
    candidate={'native_counter':64,'source_model_verified':True}
    supplied=dict(candidate)
    if case=='wrong-candidate':supplied['native_counter']=65
    if case=='false-model':candidate['source_model_verified']=False;supplied=dict(candidate)
    def gates(*args):
     if case=='gate-reject':raise ValueError('gate rejects')
     return candidate
    fake=types.SimpleNamespace(gate=types.SimpleNamespace(CHECKED=checked,flow=flow),gates=gates)
    sync=t.sync_tree;copytree=shutil.copytree
    def synced(directory):
     if case=='sync-failed':raise OSError('fsync fails')
     sync(directory);events.append('synced')
     if case=='state-after-sync-race':state_path.write_bytes(b'RACE')
    fresh_calls=[0]
    def fresh(*args):
     fresh_calls[0]+=1
     if case=='freshness-expired-after-sync' and fresh_calls[0]>1:raise ValueError('freshness expired')
     return {'fixture':True}
    def copied(source,dest):
     result=copytree(source,dest)
     if source==folders['native']:
      if case=='source-corrupt':(source/'data').write_bytes(b'RACE')
      if case=='archive-corrupt':(Path(dest)/'data').write_bytes(b'RACE')
     return result
    if case=='source-symlink':(folders['native']/'symlink').symlink_to(folders['native']/'data')
    if case=='archive-exists':(scope/'runs/retired63').mkdir(parents=True)
    if case=='state-before-race':state_path.write_bytes(b'{}')
    with patch.object(t,'require_lock',lambda *_:None),patch.dict(sys.modules,{'root_route':fake}),patch.object(t,'ROOT',scope),patch.object(t.prior63,'EVIDENCE',folders['physical']),patch.object(t.prior63,'verify',lambda *_:None),patch.object(t.prior63,'fresh',fresh),patch.object(t,'sync_tree',synced),patch.object(shutil,'copytree',copied):
     if case=='positive':
      after,directory=t.retire(state_path,state,folders['observation'],supplied)
      self.assertIsNone(after['hardware_trial_pending']);self.assertLess(events.index('archive'),events.index('synced'));self.assertLess(events.index('synced'),events.index('state'));self.assertEqual((directory/'before-state.json').read_bytes(),before)
     else:
      with self.assertRaises((ValueError,OSError)):t.retire(state_path,state,folders['observation'],supplied)
      self.assertNotIn('state',events)
 def test_lock_contract(self):
  with tempfile.TemporaryDirectory() as folder:
   state=Path(folder)/'state.json'
   with self.assertRaisesRegex(ValueError,'sole state lock'):t.require_lock(types.SimpleNamespace(LOCK_FD=None),state)
   with (Path(folder)/'state.lock').open('w') as handle:t.require_lock(types.SimpleNamespace(LOCK_FD=handle.fileno()),state)
   with (Path(folder)/'wrong.lock').open('w') as handle:
    with self.assertRaisesRegex(ValueError,'match selected'):t.require_lock(types.SimpleNamespace(LOCK_FD=handle.fileno()),state)
if __name__=='__main__':unittest.main()
