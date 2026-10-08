"""Durable63 retirement only after exact64 technical+independent admission."""
from pathlib import Path
import shutil
import prior63
ROOT=Path(__file__).resolve().parent
sha=prior63.sha
need=prior63.need
def inventory(directory):
 directory=Path(directory);need(directory.is_dir() and not directory.is_symlink(),'real archive source required');out={}
 for p in directory.rglob('*'):
  need(not p.is_symlink(),'archive symlink forbidden')
  if p.is_file():out[str(p.relative_to(directory))]=sha(p)
 return out

def sync_tree(directory):
 import os
 for p in directory.rglob('*'):
  if p.is_file():
   with p.open('rb') as handle:os.fsync(handle.fileno())
 for p in sorted([directory,*[p for p in directory.rglob('*') if p.is_dir()]],key=lambda p:len(p.parts),reverse=True):
  fd=os.open(p,os.O_RDONLY)
  try:os.fsync(fd)
  finally:os.close(fd)
 fd=os.open(directory.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)

def require_lock(flow,state_path):
 import os,stat,fcntl
 fd=getattr(flow,'LOCK_FD',None)
 need(type(fd) is int and fd>=0,'sole state lock required for retirement')
 actual=os.fstat(fd);expected=(Path(state_path).parent/'state.lock').stat()
 need(stat.S_ISREG(actual.st_mode) and (actual.st_dev,actual.st_ino)==(expected.st_dev,expected.st_ino),'held lock must match selected state directory')
 fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)

def retire(state_path,state,observation,candidate_admission):
 import root_route as candidate
 g=candidate.gate;actual=candidate.gates(g.CHECKED,(g.CHECKED/'payload.efi').read_bytes(),Path(state['package']).read_bytes())
 need(actual['native_counter']==64 and actual.get('source_model_verified') is True and actual==candidate_admission,'exact independent64 admission required')
 state_path=Path(state_path);flow=g.flow;require_lock(flow,state_path);before=state_path.read_bytes()
 need(flow.read_json(state_path)==state,'state changed before63 retirement')
 prior63.verify(state_path);fields=prior63.fresh(observation,before)
 directory=ROOT/'runs/retired63';need(not directory.exists(),'retirement exists; inspect instead of recreating');directory.mkdir(parents=True)
 sources={'native':Path(state['engine']['last_release_report']).parent,'assets':Path(state['hardware_trial_pending']),'fresh-observation':Path(observation),'physical63-evidence':prior63.EVIDENCE};manifests={}
 for name,source in sources.items():
  expected=inventory(source);shutil.copytree(source,directory/name);need(inventory(source)==expected and inventory(directory/name)==expected,'archive changed '+name);manifests[name]=expected
 (directory/'before-state.json').write_bytes(before)
 flow.save(directory/'retirement.json',{'status':'ACTUAL63-FULL12-BOOT-QUEUED-ECHO-RELEASE14-DURABLY-ARCHIVED','native_counter':63,'world_counter':19,'inventory':manifests,'prior_state_sha256':flow.sha(before),'fresh':fields,'candidate':candidate_admission,'new_signatures':0,'reboot_command':False})
 sync_tree(directory);prior63.fresh(observation,before);need(state_path.read_bytes()==before,'state changed before durable63 transition')
 for name,source in sources.items():need(inventory(source)==manifests[name] and inventory(directory/name)==manifests[name],'source/archive changed '+name)
 after=dict(state);after['hardware_trial_pending']=None;after['last_hardware_trial_retirement']=str(directory/'retirement.json');flow.save(state_path,after)
 return after,directory
