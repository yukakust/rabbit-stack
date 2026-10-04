#!/usr/bin/env python3
"""Exact owner-signed firmware RAM staging. No chip upload/startup command."""
import argparse,json,subprocess,tempfile,time
from pathlib import Path
import native_route,receiver_build
from firmware_chunk_format import packets
from send_firmware_chunk import validate
from decode_diagnostic import decode
flow,engine=native_route.flow,native_route.engine
ROOT=Path(__file__).resolve().parent
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
sha=flow.sha
def current(state,checked):
 if any(state.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('world/native operation pending')
 flow.current(state)
 payload=(checked/'payload.efi').read_bytes();world=Path(state['package']).read_bytes()
 gate=native_route.gates(checked,payload,world)
 installed=engine.gate_check(Path(state['engine']['installed_gate']))
 policy=receiver_build.policy()
 public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes()
 if gate['profile_status']!=native_route.RECEIVER_STATUS or sha(payload)!=state['engine']['payload_sha256'] or policy['owner']!=public.hex() or sha(public)!=installed['owner_public_sha256'] or policy['target']!=installed['target_sha256'] or policy['generation']!=state['engine']['native_counter']:raise ValueError('current installed RAM-only native/owner/target/generation required')
 applied=flow.read_json(Path(state['engine']['last_release_report']))
 if applied['status']!='EXACT-APPLIED-RECEIPT' or applied['counter']!=policy['generation'] or not applied['receiver_reported_applied'] or applied['payload_sha256']!=sha(payload):raise ValueError('exact applied receiver native receipt required')
 return policy,public,gate

def prepare(a,state):
 policy,public,gate=current(state,a.checked)
 # This raw read is a live observation, NOT device attestation or write authority.
 if time.time()-a.diagnostic.stat().st_mtime>300:raise ValueError('fresh read-only observation required')
 observed=flow.read_json(a.diagnostic)
 if observed.get('format')!='QPD18' or observed.get('peripheral','').upper()!=PEER or observed.get('writes')!=0:raise ValueError('fresh known-peer read-only QPD18 required')
 decode(observed);raw=bytes.fromhex(observed['raw_hex']);u=lambda off:int.from_bytes(raw[off:off+4],'little')
 if len(raw)!=924 or u(128)!=5 or u(136) or u(280)!=4 or u(284) or u(288)!=10 or u(292)!=31 or u(296)!=31 or u(316)!=2 or u(320) or u(324)!=policy['version'] or u(328)!=policy['type'] or u(800)!=12 or u(832)!=6 or u(836)!=14 or u(840)!=14 or u(220) or u(232) or u(236) or raw[244] or raw[250]:raise ValueError('live completed setup/BMI/teardown observation required')
 data=a.firmware.read_bytes()
 if len(data)!=policy['total'] or sha(data)!=policy['digest']:raise ValueError('reviewed exact container required')
 # Private material first touched after all deterministic gates and live checks.
 private=engine.load_private(a.private)
 signed=packets(data,private,target=bytes.fromhex(policy['target']),generation=policy['generation'],target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])
 directory=Path(tempfile.mkdtemp(prefix='firmware-ram-',dir=a.state.parent))
 manifests=[]
 for i,packet in enumerate(signed):
  context=validate(packet,public);path=directory/f'chunk-{i}.bin';path.write_bytes(packet);path.chmod(0o400);manifests.append({'file':path.name,**context})
 report={'status':'CHECKED-SIGNED-NOT-SENT','checked_directory':str(a.checked),'native_counter':policy['generation'],'native_payload_sha256':state['engine']['payload_sha256'],'world_counter':state['counter'],'world_sha256':state['world_sha256'],'policy':policy,'gate':gate,'diagnostic_sha256':sha(a.diagnostic.read_bytes()),'packets':manifests,'completed_chunks':0,'sender_steps':[],'firmware_upload':False,'firmware_started':False,'wifi_association':False}
 flow.save(directory/'report.json',report);print(str(directory),flush=True)

def deliver(a,state):
 report=flow.read_json(a.session/'report.json');checked=Path(report['checked_directory']);policy,public,gate=current(state,checked)
 if report['policy']!=policy or report['gate']!=gate or report['native_payload_sha256']!=state['engine']['payload_sha256'] or report['world_sha256']!=state['world_sha256']:raise ValueError('RAM session/native/world changed; no radio')
 # Compile Cocoa helper without radio, then keep ONE controller lock.
 subprocess.run(['python3',str(ROOT/'send_firmware_chunk.py')],check=True)
 # Retain exact immutable signed packets and checkpoints across every retry.
 for i,item in enumerate(report['packets']):
  path=a.session/item['file'];packet=path.read_bytes()
  if validate(packet,public)!={k:v for k,v in item.items() if k!='file'}:raise ValueError('saved signed chunk changed')
  if i<report['completed_chunks'] and not (report['completed_chunks']==len(report['packets']) and i==len(report['packets'])-1):continue
  for mode in ('--query-only','--send'):
   log=a.session/f'chunk-{i}-{len(report["sender_steps"])}.log'
   checkpoint=path.with_suffix(path.suffix+'.checkpoint.json')
   command=[str(ROOT/'runs/mac-control/firmware-sender'),str(path),str(checkpoint),mode]
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
 report['status']='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM';flow.save(a.session/'report.json',report);print('EXACT FULL RAM STAGING VERIFIED; NO FIRMWARE EXECUTION',flush=True);return 0

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','deliver'));p.add_argument('--state',type=Path,required=True);p.add_argument('--checked',type=Path);p.add_argument('--diagnostic',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--session',type=Path);p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');a=p.parse_args()
 if a.action=='prepare' and not all((a.checked,a.diagnostic,a.firmware)):p.error('prepare requires checked profile, fresh diagnostic and reviewed firmware')
 if a.action=='deliver' and not a.session:p.error('deliver requires exact saved session')
 with flow.state_lock(a.state):
  state=flow.read_json(a.state)
  return prepare(a,state) if a.action=='prepare' else deliver(a,state)
if __name__=='__main__':raise SystemExit(main())
