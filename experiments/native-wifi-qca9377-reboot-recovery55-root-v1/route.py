"""ROOT-only guarded recovery route. Writer tests use copied state exclusively.

No signing, private key load, Bluetooth query/send or reboot API exists here.
"""
import argparse,contextlib,fcntl,hashlib,importlib.util,json,os,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
GATE=REPO/'experiments/native-wifi-qca9377-reboot-retirement55-v1'
spec=importlib.util.spec_from_file_location('retirement55_checked_gate',GATE/'gate.py');gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
sha=gate.sha
@contextlib.contextmanager
def locked(state):
 with (state.parent/'state.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ValueError('another controller owns state.lock')
  yield

def atomic(path,data):
 with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
  name=Path(f.name)
  try:f.write(data);f.flush();os.fsync(f.fileno())
  except BaseException:name.unlink(missing_ok=True);raise
 try:os.replace(name,path)
 finally:name.unlink(missing_ok=True)
 fd=os.open(path.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def fsync_directory(path):
 fd=os.open(path,os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
 try:os.fsync(fd)
 finally:os.close(fd)
def durable_archive(output):
 # Every child directory entry and the output entry in its parent must persist
 # before the atomic state pointer can reference this archive.
 directories=[p for p in output.rglob('*') if p.is_dir()]+[output]
 for p in sorted(directories,key=lambda p:len(p.parts),reverse=True):fsync_directory(p)
 fsync_directory(output.parent)

def archive_blob(output,name,data):
 p=output/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 return sha(data)
def reference(path):
 p=Path(path);canonical=Path('/Users/yukakust/rabbit-stack')
 return REPO/p.relative_to(canonical) if p.is_relative_to(canonical) else p

def public(state):
 native=Path(state['engine']['last_release_report']).parent;assets=Path(state['hardware_trial_pending']);a=gate.read(assets/'report.json')
 return native,assets,gate.public_bundle(REPO,native,assets,reference(a['checked_directory']),Path(state['package']))

def retire(state_path,before_path,authorization,observation,query_log,output):
 """Guard, archive FIRST, then change exactly pending + append audit atomically."""
 state_path,before_path,authorization,observation,query_log,output=map(lambda p:Path(p).resolve(),(state_path,before_path,authorization,observation,query_log,output))
 gate.require(state_path!=before_path and before_path.name=='before-state.json','separate exact archived state required')
 gate.require(not output.exists() and output!=state_path.parent and output.parent.is_dir(),'NEW archive in existing parent required')
 with locked(state_path):
  original=state_path.read_bytes();before=before_path.read_bytes();gate.require(original==before,'live state changed since archive')
  preflight=gate.read(before_path.parent/'root-preflight.json')
  gate.require(preflight.get('status')=='EXACT-ACTUAL55-ARCHIVED-STATE-PUBLIC-BINDING-PASS' and preflight.get('before_state_sha256')==sha(before),'root pre-recovery archive hash binding')
  state=json.loads(original);native,assets,bundle=public(state)
  gate.require(not output.is_relative_to(native) and not output.is_relative_to(assets),'archive must not alter original signed55 directories')
  journal=state_path.parent/'control/journal.json';journal_bytes=journal.read_bytes();gate.require(not json.loads(journal_bytes).get('active'),'world journal active')
  auth=authorization.read_bytes();obs=observation.read_bytes();log=query_log.read_bytes()
  proof=gate.conditional_retirement(original,bundle,native,assets,auth,obs,log)
  gate.require(not any(r.get('native_counter')==55 for r in state.get('retired_hardware_trials',[])),'native55 already retired')
  output.mkdir(exist_ok=False);manifest={}
  for name,data in [('before-state.json',original),('authorization.json',auth),('observation.json',obs),('query.log',log),('before-journal.json',journal_bytes)]:manifest[name]=archive_blob(output,name,data)
  for name in ('before-state.json','root-preflight.json','boot55.json','boot55.decoded.json','passive-near55.json','public-bundle.json'):
   manifest['root-before-recovery/'+name]=archive_blob(output,'root-before-recovery/'+name,(before_path.parent/name).read_bytes())
  # Preserve all available raw reports/logs/signatures/sessions/checkpoints, not
  # only reconstructed JSON. No modifications to original signed55 directories.
  for label,directory in [('native55',native),('assets55',assets)]:
   for p in sorted(directory.iterdir()):
    if p.is_file():manifest[label+'/'+p.name]=archive_blob(output,label+'/'+p.name,p.read_bytes())
  for label,p in [('world17/world.json',Path(state['world'])),('world17/world.rup',Path(state['package']))]:manifest[label]=archive_blob(output,label,p.read_bytes())
  checked=reference(gate.read(assets/'report.json')['checked_directory'])
  for name in ('report.json','payload.efi'):manifest['checked55/'+name]=archive_blob(output,'checked55/'+name,(checked/name).read_bytes())
  audit={'status':'FULL55-RAM-TRIAL-RETIRED-AFTER-AUTHORIZED-OWNER-REBOOT','native_counter':55,'native_payload_sha256':gate.PAYLOAD,'completed_chunks_before_reboot':12,'before_state_sha256':sha(original),'original_asset_session':str(assets),'original_native_session':str(native),'original_state_path':str(state_path),'archive_sha256':manifest,'conditional_evidence':proof,'actual_all14_owner_release_proved':False,'raw55_exports':'NOT_CAPTURED-LOST-AFTER-OWNER-REBOOT','native56_reserved':False,'device_writes':0,'private_key_loads':0,'source_sha256':{str(ROOT/'route.py'):sha((ROOT/'route.py').read_bytes()),str(GATE/'gate.py'):sha((GATE/'gate.py').read_bytes())}}
  audit_bytes=encoded(audit);archive_blob(output,'retirement.json',audit_bytes)
  updated=json.loads(original);updated['hardware_trial_pending']=None
  updated.setdefault('retired_hardware_trials',[]).append({'session':str(assets),'native_counter':55,'reason':'authorized-owner-reboot-and-fresh-empty-bootstrap-full12-raw55-lost','retirement_sha256':sha(audit_bytes),'retirement_report':str(output/'retirement.json')})
  after=encoded(updated);archive_blob(output,'after-state.json',after)
  # Archive durability precedes the only operational state write. A crash here
  # leaves old pending intact, requiring review of the existing complete archive.
  durable_archive(output)
  gate.require(state_path.read_bytes()==original and journal.read_bytes()==journal_bytes,'state/journal changed inside lock')
  # Recheck actual freshness immediately before commit, never refresh receipt.
  gate.conditional_retirement(original,bundle,native,assets,auth,obs,log)
  atomic(state_path,after)
  return audit

def _admission_locked(state_path,retirement,checked):
 raw=state_path.read_bytes();s=json.loads(raw);a=gate.read(retirement);d=retirement.parent
 gate.require(a['status']=='FULL55-RAM-TRIAL-RETIRED-AFTER-AUTHORIZED-OWNER-REBOOT' and a['native_counter']==55 and a['original_state_path']==str(state_path),'exact applied retirement audit')
 for name,h in a['archive_sha256'].items():gate.require(sha((d/gate.safe(name)).read_bytes())==h,'retirement archive changed')
 for name,h in a['source_sha256'].items():gate.require(sha(Path(name).read_bytes())==h,'retirement source changed')
 gate.require(raw==(d/'after-state.json').read_bytes(),'retired state changed')
 before=(d/'before-state.json').read_bytes();expected=json.loads(before);expected['hardware_trial_pending']=None
 record={'session':a['original_asset_session'],'native_counter':55,'reason':'authorized-owner-reboot-and-fresh-empty-bootstrap-full12-raw55-lost','retirement_sha256':sha(retirement.read_bytes()),'retirement_report':str(retirement)}
 expected.setdefault('retired_hardware_trials',[]).append(record);gate.require(s==expected,'only intended retirement transition allowed')
 native=Path(a['original_native_session']);assets=Path(a['original_asset_session']);bundle=gate.public_bundle(REPO,native,assets,reference(gate.read(assets/'report.json')['checked_directory']),Path(s['package']))
 gate.conditional_retirement(before,bundle,native,assets,(d/'authorization.json').read_bytes(),(d/'observation.json').read_bytes(),(d/'query.log').read_bytes())
 # Use the original public-only native/gate checker, never prepare/restore.
 import sys
 sys.path.insert(0,str(REPO/'experiments/native-wifi-qca9377-v1'))
 import reboot_recovery as recovery
 installed=recovery.engine.gate_check(Path(s['engine']['installed_gate']))
 gate.require(sha(Path(s['engine']['installed_gate']).read_bytes())==s['engine']['installed_gate_sha256'],'installed gate hash')
 old,counter=recovery.completed_reservation(s,gate.OWNER,installed)
 world=recovery.flow.current(s);payload,proof=recovery.gate(checked,world,gate.OWNER)
 gate.require(counter==55 and s['counter']==17 and sha(payload)=='0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce' and proof['restored_package_sha256']=='f306120fdd548b6d4cc1d3915a13ae8cbe7848b162caa78528add353b9cb3f32','exact plain city56/world18 gate')
 journal=state_path.parent/'control/journal.json';j=recovery.flow.read_json(journal);gate.require(not j.get('active'),'world journal active')
 return {'status':'PLAINCITY56-OWNER-REBOOT-RECOVERY-READONLY-ADMISSION-PASS','state_sha256':sha(raw),'journal_sha256':sha(journal.read_bytes()),'checked_directory':str(checked),'gate_sha256':sha((checked/'recovery-gate.json').read_bytes()),'native_counter_candidate':56,'world_counter_candidate':18,'physical_admission':False,'signing_performed':False,'device_writes':0,'private_key_loads':0,'old_htt56_consumed':False,'next_action':'ROOT separately rechecks identical state/journal under original prepare lock, then existing reboot_recovery.prepare; never direct native55 replay'}

def admission(state_path,retirement,checked):
 state_path,retirement,checked=map(lambda p:Path(p).resolve(),(state_path,retirement,checked))
 with locked(state_path):return _admission_locked(state_path,retirement,checked)


def guarded_prepare56(state_path,retirement,checked,directory,private,*,_recovery=None):
 """Future ROOT-only signing wrapper; never invoked with a real key in tests.
 The original prepare owns the real lock. Recheck admission at its reservation,
 gate and immediately before private-key loading. No frozen function is edited.
 """
 state_path,retirement,checked,directory,private=map(lambda p:Path(p).resolve(),(state_path,retirement,checked,directory,private))
 approved=admission(state_path,retirement,checked)
 original_path=REPO/'experiments/native-wifi-qca9377-v1/reboot_recovery.py'
 original_hash=sha(original_path.read_bytes());route_hash=sha((ROOT/'route.py').read_bytes())
 if _recovery is None:
  spec=importlib.util.spec_from_file_location('isolated_original_recovery55',original_path)
  recovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(recovery)
 else:recovery=_recovery  # HOST-only dependency injection; CLI never exposes it.
 reservation=recovery.reservation;check_gate=recovery.gate;engine=recovery.engine
 def check():
  gate.require(sha(original_path.read_bytes())==original_hash and sha((ROOT/'route.py').read_bytes())==route_hash,'wrapper/original source changed')
  gate.require(_admission_locked(state_path,retirement,checked)==approved,'admitted state/journal/source/receipt changed')
 def guarded_reservation(state,owner,installed,kind):
  check();gate.require(kind=='completed' and state['engine']['native_counter']==55 and state['counter']==17 and owner==gate.OWNER,'exact completed55→56 world17→18 only')
  result=reservation(state,owner,installed,kind);gate.require(result[1]==55,'reservation differs');return result
 def guarded_gate(candidate,world,owner):
  check();gate.require(Path(candidate).resolve()==checked and owner==gate.OWNER,'exact checked candidate/owner')
  return check_gate(candidate,world,owner)
 class EngineProxy:
  def __getattr__(self,name):return getattr(engine,name)
  def load_private(self,path):
   check();gate.require(Path(path).resolve()==private,'exact private-key locator')
   return engine.load_private(path)
 recovery.reservation=guarded_reservation;recovery.gate=guarded_gate;recovery.engine=EngineProxy()
 try:
  plan=recovery.prepare(state_path,checked,directory,private)
  gate.require(plan['counter']==56 and plan['world_counter']==18 and plan['reserved_counter']==55,'unexpected original prepare counters')
  return plan
 finally:
  recovery.reservation=reservation;recovery.gate=check_gate;recovery.engine=engine

def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
 r=sub.add_parser('retire');r.add_argument('--apply',action='store_true',required=True)
 for name in ('state','before-state','authorization','observation','query-log','archive-output'):r.add_argument('--'+name,type=Path,required=True)
 a=sub.add_parser('admit')
 for name in ('state','retirement','checked'):a.add_argument('--'+name,type=Path,required=True)
 v=p.parse_args()
 result=retire(v.state,v.before_state,v.authorization,v.observation,v.query_log,v.archive_output) if v.command=='retire' else admission(v.state,v.retirement,v.checked)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
