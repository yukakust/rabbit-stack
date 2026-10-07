"""Exact saved59 assets with serialized host diagnostic reads; no timer fix."""
import argparse,json,subprocess,time,os
from pathlib import Path
import route
import boot_asset_route as original
from send_firmware_chunk import validate
flow,engine=route.flow,route.engine
ROOT=route.REPO/'experiments/native-wifi-qca9377-v1'
OBSERVER=route.REPO/'experiments/native-wifi-qca9377-asset-observer-v1'
PEER=route.PEER
OBSERVER_PROOF='18548e99bff3447b5df490bde84c882a2b51c809b095ece3950c3406b62651db'
def observer_gate():
 route.need(route.sha(OBSERVER/'evidence/host-proof.json')==OBSERVER_PROOF,'frozen observer proof')
 proof=flow.read_json(OBSERVER/'evidence/host-proof.json')
 route.need(proof['callback_checks']==41 and proof['python_checks']==260 and not proof['physical_trial'] and not proof['private_key_loads'],'host observer proof scope')
 for n,h in proof['source_sha256'].items():route.need(route.sha(route.REPO/route.safe(n))==h,'observer source changed '+n)
 subprocess.run(['python3',str(OBSERVER/'observer.py')],check=True,timeout=90)
 c=flow.read_json(OBSERVER/'runs/control/compile-report.json')
 route.need(c['source_sha256']==proof['compile_report']['source_sha256'] and route.sha(Path(c['executable_path']))==c['executable_sha256'] and not c['bluetooth_manager_started'],'observer executable exact inputs')
def current(state,checked):
 route.need(not any(state.get(k) for k in ('pending','native_pending','recovery_pending')),'competing world/native operation')
 flow.current(state)
 proof=route.gates(checked,(checked/'payload.efi').read_bytes(),Path(state['package']).read_bytes())
 policy=proof['receiver_policy'];public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes()
 installed=engine.gate_check(Path(state['engine']['installed_gate']))
 route.need(route.sha(state['engine']['installed_gate'])==state['engine']['installed_gate_sha256'],'installed gate identity')
 route.need(public.hex()==route.OWNER and flow.sha(public)==installed['owner_public_sha256'] and policy['target']==installed['target_sha256'],'actual owner/target')
 route.need(state['counter']==19 and state['world_sha256']==route.SEMANTIC and state['package_sha256']==route.WORLD and state['engine']['native_counter']==59 and state['engine']['payload_sha256']==route.PAYLOAD,'exact applied59/world19')
 applied=flow.read_json(Path(state['engine']['last_release_report']))
 route.need(applied['status']=='EXACT-APPLIED-RECEIPT' and applied['counter']==59 and applied['receiver_reported_applied'] and applied['payload_sha256']==route.PAYLOAD,'physical59 applied receipt')
 return policy,public,proof
def deliver(a,state):
 if state.get('hardware_trial_pending')!=str(a.session):raise ValueError('exact pending boot asset session required')
 report=flow.read_json(a.session/'report.json');checked=Path(report['checked_directory']);policy,public,gate=current(state,checked)
 if report['policy']!=policy or report['gate']!=gate or report['native_payload_sha256']!=state['engine']['payload_sha256'] or report['world_sha256']!=state['world_sha256']:raise ValueError('RAM session/native/world changed; no radio')
 # Compile Cocoa helper without radio, then keep ONE controller lock.
 observer_gate()
 # Retain exact immutable signed packets and checkpoints across every retry.
 for i,item in enumerate(report['packets']):
  path=a.session/item['file'];packet=path.read_bytes()
  if validate(packet,public)!={k:v for k,v in item.items() if k!='file'}:raise ValueError('saved signed chunk changed')
  if i<report['completed_chunks'] and not (report['completed_chunks']==len(report['packets']) and i==len(report['packets'])-1):continue
  for mode in ('--query-only','--send'):
   log=a.session/f'chunk-{i}-{len(report["sender_steps"])}.log'
   checkpoint=path.with_suffix(path.suffix+'.checkpoint.json')
   command=[str(OBSERVER/'runs/control/sender'),str(path),str(checkpoint),mode,'--prefix-log',str(a.session/f'prefix-{i}-{len(report["sender_steps"])}.jsonl')]
   # The helper does not acquire another lock; outer route owns it throughout.
   import os
   env=os.environ.copy();env['RABBIT_ASSET_PEER']=PEER
   if flow.LOCK_FD is not None:env['RABBIT_CONNECTED_LOCK_FD']=str(flow.LOCK_FD)
   entry={'chunk':i,'mode':mode,'exit_code':None,'log':str(log)}
   report['sender_steps'].append(entry);flow.save(a.session/'report.json',report)
   with log.open('w') as output:
    try:r=subprocess.run(command,stdout=output,stderr=subprocess.STDOUT,env=env,timeout=250,pass_fds=() if flow.LOCK_FD is None else (flow.LOCK_FD,))
    except subprocess.TimeoutExpired:
     output.write('OUTCOME UNKNOWN: keep exact packet/checkpoint; query before retry\n');r=subprocess.CompletedProcess(command,1)
   entry['exit_code']=r.returncode
   flow.save(a.session/'report.json',report)
   lines=[]
   for line in log.read_text().splitlines():
    try:value=json.loads(line)
    except json.JSONDecodeError:continue
    if 'action' in value:lines.append(value)
   receipt=lines[-1] if lines else None
   if r.returncode or not receipt or receipt.get('peripheral','').upper()!=PEER:
    report['status']='RAM-RECEIPT-NOT-CONFIRMED';flow.save(a.session/'report.json',report);print(f'Chunk{i} unconfirmed; preserve session and query before retry. Log: {log}',flush=True);return 1
   if receipt['action']==4:break  # QFS_DONE4, exact packet + asset bitmap checks in sender core.
   if mode=='--send':
    report['status']='RAM-RECEIPT-NOT-CONFIRMED';flow.save(a.session/'report.json',report);return 1
  if not receipt or receipt['action']!=4:raise ValueError('exact accepted chunk receipt required')
  report['completed_chunks']=i+1;report['last_receipt']=receipt;report['status']='RAM-STAGING';flow.save(a.session/'report.json',report);print(f'Confirmed RAM chunk{i+1}/{len(report["packets"])} bitmap={receipt["bitmap"]} ready={receipt["ready"]}',flush=True)
 if report['last_receipt']['bitmap']!=4095 or report['last_receipt']['ready']!=1:raise ValueError('full verified RAM asset receipt required')
 report['status']='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM';flow.save(a.session/'report.json',report);print('EXACT FULL RAM STAGING VERIFIED; BOOT TRIAL MAY BE ACTIVE; READ QWBT BEFORE ENGINE CHANGE',flush=True);return 0

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','deliver'));p.add_argument('--state',type=Path,required=True);p.add_argument('--checked',type=Path,default=route.CHECKED);p.add_argument('--diagnostic',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--session',type=Path);p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');a=p.parse_args()
 if a.action=='prepare' and not all((a.diagnostic,a.firmware)):p.error('fresh diagnostic and exact firmware required')
 if a.action=='deliver' and not a.session:p.error('exact saved session required')
 with flow.state_lock(a.state):
  state=flow.read_json(a.state)
  if a.action=='deliver':return deliver(a,state)
  observer_gate();current(state,a.checked)
  old=original.current;original.current=current
  try:return original.prepare(a,state)
  finally:original.current=old
if __name__=='__main__':raise SystemExit(main())
