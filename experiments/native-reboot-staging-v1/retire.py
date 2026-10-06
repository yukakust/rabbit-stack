"""Retire lost RAM staging ONLY after human reboot + fresh empty bootstrap read."""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
sys.path.insert(0,str(REPO/'experiments/native-wifi-qca9377-v1'))
import reboot_recovery as recovery
from send_firmware_chunk import validate
flow=recovery.flow
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
def retire(state_path,observation,public_path,confirmed=False,preflight=False):
 state_path=state_path.resolve();observation=observation.resolve();public_path=public_path.resolve()
 if not confirmed:raise ValueError('human confirmation of actual Dell reboot required')
 with flow.state_lock(state_path):
  state=flow.read_json(state_path)
  if any(state.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('competing operation')
  saved=state.get('hardware_trial_pending')
  if not isinstance(saved,str) or not Path(saved).is_absolute():raise ValueError('exact pending RAM session required')
  session=Path(saved).resolve()
  if not session.is_absolute() or session.parent!=state_path.parent:raise ValueError('exact pending RAM session required')
  raw=flow.read_json(observation);receiver=raw.get('receiver',{})
  if (not raw.get('owner_confirmed_reboot') or raw.get('peripheral','').upper()!=PEER or raw.get('writes')!=0
   or receiver.get('raw_hex')!=recovery.EMPTY or receiver.get('outcome')!='idle'
   or not 0<=time.time()-raw.get('observed_at',0)<=300
   or flow.sha(observation.with_name('query.log').read_bytes())!=raw.get('log_sha256')):raise ValueError('fresh known-peer empty receipt/log required')
  public=public_path.read_bytes();installed=recovery.engine.gate_check(Path(state['engine']['installed_gate']))
  if flow.sha(public)!=installed['owner_public_sha256']:raise ValueError('public owner differs')
  recovery.completed_reservation(state,public,installed)
  report=flow.read_json(session/'report.json')
  if report.get('reboot_retirement_sha256'):raise ValueError('session already retired')
  policy=report['policy'];checked=Path(report['checked_directory'])
  proof=flow.read_json(checked/'reproduction.json',8*1024*1024)
  if (report['native_counter']!=state['engine']['native_counter'] or report['native_payload_sha256']!=state['engine']['payload_sha256']
   or report['world_sha256']!=state['world_sha256'] or policy['generation']!=report['native_counter']
   or policy['owner']!=public.hex() or policy['target']!=installed['target_sha256']
   or proof['payload_sha256']!=state['engine']['payload_sha256']
   or flow.sha((checked/'payload.efi').read_bytes())!=proof['payload_sha256']
   or not 0<=report['completed_chunks']<len(report['packets']) or report.get('firmware_started')):raise ValueError('partial staging/native/world binding differs')
  for name,h in proof['inputs'].items():
   p=Path(name)
   if p.is_absolute() or '..' in p.parts or flow.sha((REPO/p).read_bytes())!=h:raise ValueError('frozen source changed')
  files={}
  for item in report['packets']:
   p=Path(item['file'])
   if p.name!=str(p):raise ValueError('unsafe packet path')
   packet=(session/p).read_bytes()
   if validate(packet,public)!={k:v for k,v in item.items() if k!='file'} or packet[8:40].hex()!=policy['target']:raise ValueError('saved signed chunk changed')
   files[str(p)]=flow.sha(packet)
  if preflight:return {'status':'REBOOT-RETIREMENT-PREFLIGHT-PASS','device_writes':0,'private_key_loads':0}
  audit={'status':'PARTIAL-RAM-STAGING-RETIRED-AFTER-OWNER-REBOOT','session':str(session),'native_counter':report['native_counter'],
   'completed_chunks_before_reboot':report['completed_chunks'],'world_sha256':state['world_sha256'],'signed_packet_sha256':files,
   'report_before_sha256':flow.sha((session/'report.json').read_bytes()),'observation_sha256':flow.sha(observation.read_bytes()),
   'owner_confirmed_reboot':True,'fresh_empty_receiver':raw,'device_writes':0,'private_key_loads':0,'wifi_connected':False}
  flow.save(session/'before-reboot-retirement-state.json',state);flow.save(session/'before-reboot-retirement-report.json',report);flow.save(session/'reboot-retirement.json',audit)
  report['status']=audit['status'];report['reboot_retirement_sha256']=flow.sha((session/'reboot-retirement.json').read_bytes());flow.save(session/'report.json',report)
  state.setdefault('retired_hardware_trials',[]).append({'session':str(session),'native_counter':report['native_counter'],
   'reason':'owner-confirmed-reboot-and-fresh-empty-bootstrap','retirement_sha256':report['reboot_retirement_sha256']})
  state['hardware_trial_pending']=None;flow.save(state_path,state)
  return audit
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--observation',type=Path,required=True);p.add_argument('--owner-public',type=Path,required=True);p.add_argument('--dell-rebooted',action='store_true');p.add_argument('--preflight-only',action='store_true');a=p.parse_args()
 print(json.dumps(retire(a.state,a.observation,a.owner_public,a.dell_rebooted,a.preflight_only),ensure_ascii=False))
if __name__=='__main__':main()
