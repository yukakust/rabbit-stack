"""Sequential exact64 transition/sign/delivery; no unsigned or stale admission."""
from pathlib import Path
import argparse,os,json
import gate,admission
flow,engine=gate.flow,gate.engine
ROOT=Path(__file__).resolve().parent
def gates(directory,payload,world):
 g=gate.gates(directory,payload,world);g['filter_scan_trial_admission']=admission.checked();return g
def current(s,checked):
 gate.need(not any(s.get(k) for k in ('pending','native_pending','recovery_pending')),'competing operation')
 flow.current(s);g=gates(checked,(checked/'payload.efi').read_bytes(),Path(s['package']).read_bytes())
 public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes();installed=engine.gate_check(Path(s['engine']['installed_gate']))
 gate.need(public.hex()==gate.base60.prior.OWNER and flow.sha(public)==installed['owner_public_sha256'] and g['receiver_policy']['target']==installed['target_sha256'] and gate.sha(s['engine']['installed_gate'])==s['engine']['installed_gate_sha256'],'actual installation owner/target')
 gate.need(s['engine']['native_counter']==64 and s['engine']['payload_sha256']==gate.PAYLOAD and s['counter']==19 and s['world_sha256']==gate.SEMANTIC and s['package_sha256']==gate.WORLD,'actual64/world19')
 r=flow.read_json(Path(s['engine']['last_release_report']));gate.need(r['status']=='EXACT-APPLIED-RECEIPT' and r['receiver_reported_applied'] is True and r['counter']==64 and r['payload_sha256']==gate.PAYLOAD and r['gate']==g,'actual64 APPLIED exact gate')
 return g['receiver_policy'],public,g
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('check','prepare','deliver'));p.add_argument('--state',type=Path,required=True);p.add_argument('--observation',type=Path);p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');a=p.parse_args();a.state=a.state.resolve()
 import transition63 as transition
 with flow.state_lock(a.state):
  s=flow.read_json(a.state);g=gates(gate.CHECKED,(gate.CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes())
  if a.action=='check':__import__("prior63").verify(a.state);print('ROOT64-EXACT-PARTIAL-PASSIVE-CANDIDATE-PRIOR63-PUBLIC-PASS');return 0
  old=gate.primitive.gates;old_private=engine.load_private;gate.primitive.gates=gates
  try:
   if a.action=='prepare':
    # Do not change installed native until both its staging and final readers exist.
    import host_gate
    host_gate.checked()
    gate.need(a.observation is not None,'fresh actual63 release required')
    s,retired=transition.retire(a.state,s,a.observation,g);before=a.state.read_bytes()
    prior_before=(retired/'before-state.json').read_bytes()
    intent=ROOT/'runs/prepare64-intent.json'
    gate.need(not intent.exists(),'64 signing intent exists; inspect saved artifacts, never retry or re-sign blindly')
    with intent.open('x') as handle:
     json.dump({'status':'ONE-PREPARE64-ATTEMPT-RESERVED','state_sha256':flow.sha(before),'retirement_sha256':gate.sha(retired/'retirement.json'),'candidate':g},handle,indent=2);handle.flush();os.fsync(handle.fileno())
    fd=os.open(intent.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
    def guarded_private(path):
     gate.need(a.state.read_bytes()==before,'state changed immediately before key access')
     __import__('prior63').fresh(a.observation,prior_before)
     return old_private(path)
    engine.load_private=guarded_private
    directory=gate.primitive.prepare(a.state,s,gate.CHECKED,a.private)
    (directory/'root-before-state.json').write_bytes(before)
    flow.save(directory/'root-admission.json',{'candidate':g,'prior_state_sha256':flow.sha(before),'retirement':str(retired/'retirement.json'),'retirement_sha256':gate.sha(retired/'retirement.json')})
    print(directory);return 0
   directory=Path(s['native_pending']);b=flow.read_json(directory/'root-before-state.json');b['native_pending']=str(directory);r=flow.read_json(directory/'root-admission.json')
   gate.need(b==s and r['candidate']==g and r['prior_state_sha256']==gate.sha(directory/'root-before-state.json') and gate.sha(r['retirement'])==r['retirement_sha256'],'saved exact64 signed admission changed')
   return gate.primitive.deliver(a.state,s,a.private)
  finally:gate.primitive.gates=old;engine.load_private=old_private
if __name__=='__main__':raise SystemExit(main())
