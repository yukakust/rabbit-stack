"""Synthetic retirement failure/order tests; no actual state/gate/key/BLE access."""
from pathlib import Path
import tempfile,json,types,hashlib,os,stat,shutil,copy
import transition62 as t
ROOT=Path(__file__).resolve().parent;checks=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
originals={n:getattr(t,n) for n in ('ROOT','REPO','prior','verify','fresh','sync_tree')};oldcopy=shutil.copytree;oldfsync=os.fsync;oldopen=Path.open
for case in ('missing-gate','dict-only','wrong-candidate','gate-failed','positive','source-corrupt','archive-corrupt','source-symlink','archive-exists','state-before-race','state-after-sync-race','fsync-failed'):
 with tempfile.TemporaryDirectory(prefix='synthetic-retire62-review-') as tmp:
  base=Path(tmp).resolve();scope=base/'scope';scope.mkdir();t.ROOT=scope;t.REPO=base/'fake-repo';t.REPO.mkdir();events=[];saves=[];state_path=base/'synthetic-state.json';world=base/'synthetic-world.rup';world.write_bytes(b'SYNTHETIC-NOT-SIGNED-WORLD');checked=base/'synthetic-candidate';checked.mkdir();(checked/'payload.efi').write_bytes(b'SYNTHETIC-NOT-EFI');candidate={'native_counter':63,'source_model_verified':True,'report_sha256':'FIXTURE-NOT-REAL-PROOF'}
  gate="from pathlib import Path\nCHECKED=Path("+repr(str(checked))+ ")\ndef gates(directory,payload,world):\n assert payload==b'SYNTHETIC-NOT-EFI' and world==b'SYNTHETIC-NOT-SIGNED-WORLD'\n return "+repr(candidate)+"\n"
  if case!='missing-gate':(scope/'gate.py').write_text(gate)
  native=base/'native';assets=base/'assets';obs=base/'fresh-observation';physical=t.REPO/'experiments/native-wifi-qca9377-htt62-root-route-v1/evidence/physical62-HTT-VERSION-CONF'
  for folder in (native,assets,obs,physical):folder.mkdir(parents=True);(folder/'fixture.bin').write_bytes(b'SYNTHETIC-NOT-PHYSICAL')
  state={'package':str(world),'hardware_trial_pending':str(assets),'counter':19,'engine':{'native_counter':62},'fixture_kind':'SYNTHETIC-STATE-NOT-ACTUAL'};state_path.write_text(json.dumps(state));before=state_path.read_bytes()
  def guarded(self,*a,**k):
   if not self.resolve().is_relative_to(base):raise AssertionError('actual path access forbidden '+str(self))
   if self.name.endswith('.key'):raise AssertionError('key access forbidden')
   return oldopen(self,*a,**k)
  Path.open=guarded
  def save(path,value):
   path=Path(path);assert path.resolve().is_relative_to(base),'actualstate write blocked';events.append('SAVE-STATE' if path==state_path else 'SAVE-ARCHIVE');saves.append(path);path.write_text(json.dumps(value))
  flow=types.SimpleNamespace(read_json=lambda p:json.loads(Path(p).read_text()),save=save,sha=lambda b:hashlib.sha256(b).hexdigest());t.prior=lambda:types.SimpleNamespace(gate=types.SimpleNamespace(flow=flow));t.verify=lambda _: {'native_directory':str(native),'asset_directory':str(assets)};t.fresh=lambda *_:{'fixture':'SYNTHETIC-NOT-PHYSICAL'}
  def fsync(fd):
   events.append('FSYNC-DIR' if stat.S_ISDIR(os.fstat(fd).st_mode) else 'FSYNC-FILE')
   if case=='fsync-failed':raise OSError('injected fsync failure')
   return oldfsync(fd)
  os.fsync=fsync
  def sync(directory):
   originals['sync_tree'](directory);events.append('SYNC-COMPLETE')
   if case=='state-after-sync-race':state_path.write_bytes(b'RACE-SYNTHETIC')
  t.sync_tree=sync
  def copytree(source,dest,*args,**kwargs):
   result=oldcopy(source,dest,*args,**kwargs)
   if Path(source)==native:
    if case=='source-corrupt':(native/'fixture.bin').write_bytes(b'SOURCE-RACE')
    if case=='archive-corrupt':(Path(dest)/'fixture.bin').write_bytes(b'ARCHIVE-CORRUPT')
   return result
  shutil.copytree=copytree
  supplied=dict(candidate)
  if case=='dict-only':supplied={'native_counter':63,'source_model_verified':True}
  if case=='wrong-candidate':supplied['report_sha256']='WRONG'
  if case=='gate-failed':candidate['source_model_verified']=False;(scope/'gate.py').write_text(gate.replace("'source_model_verified': True","'source_model_verified': False"));supplied=dict(candidate)
  if case=='source-symlink':(native/'link').symlink_to(native/'fixture.bin')
  if case=='archive-exists':(scope/'runs/retired62').mkdir(parents=True)
  if case=='state-before-race':state_path.write_text('{}')
  try:
   try:after,directory=t.retire(state_path,state,obs,supplied)
   except (ValueError,FileNotFoundError,OSError) as error:
    assert case!='positive',str(error);assert state_path not in saves,'failed retirement changed state';checks.append(case+' rejected without state save')
   else:
    assert case=='positive',case+' unexpectedly accepted';assert after['hardware_trial_pending'] is None and events.index('SYNC-COMPLETE')<events.index('SAVE-STATE') and events.index('SAVE-ARCHIVE')<events.index('SYNC-COMPLETE');assert events[:events.index('SAVE-STATE')].count('FSYNC-FILE')>=6 and events[:events.index('SAVE-STATE')].count('FSYNC-DIR')>=6;assert (directory/'before-state.json').read_bytes()==before
    retirement=json.loads((directory/'retirement.json').read_text());assert retirement['inventory'].keys()=={'native','assets','fresh-observation','physical62-evidence'} and retirement['new_signatures']==0;checks.append('synthetic archive+allfile/directoryfsync precede final syntheticstate save')
  finally:
   Path.open=oldopen;os.fsync=oldfsync;shutil.copytree=oldcopy
for n,v in originals.items():setattr(t,n,v)
e=ROOT/'evidence';e.mkdir(exist_ok=True);p=e/'independent-retirement-review.json';r={'status':'SYNTHETIC-RETIRE62-FS-SYNC-ORDER-FAILCLOSED-REVIEW-PASS','checks':checks,'source_sha256':{x.name:sha(x) for x in (Path(__file__),ROOT/'transition62.py')},'actual_gate_or_state_accessed':False,'real_state_writes':0,'BLE_operations':0,'private_key_accesses':0,'signatures_created':0,'synthetic_fixture_not_physical_retirement':True};p.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(checks),'SHA',sha(p))
