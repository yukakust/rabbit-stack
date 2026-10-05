#!/usr/bin/env python3
"""Retire host-RAM-only staging for a checked next driver; no device writes."""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native-wifi-qca9377-v1'))
import boot_asset_route as route
from decode_boot import decode
from send_firmware_chunk import validate
flow=route.flow

def retire(state_path,session,observation,next_dir,preflight=False):
 with flow.state_lock(state_path):
  state=flow.read_json(state_path)
  if state.get('hardware_trial_pending')!=str(session):raise ValueError('exact pending session required')
  r=flow.read_json(session/'report.json');policy,public,gate=route.current(state,Path(r['checked_directory']))
  if r['policy']!=policy or r['gate']!=gate or r['native_counter']!=state['engine']['native_counter'] or r['native_payload_sha256']!=state['engine']['payload_sha256'] or r['world_sha256']!=state['world_sha256']:raise ValueError('staging base changed')
  if time.time()-observation.stat().st_mtime>300:raise ValueError('fresh physical observation required')
  raw=flow.read_json(observation);d=decode(raw)
  if raw.get('writes')!=0 or raw.get('peripheral','').upper()!=route.PEER or d['boot_round'] or d['boot_attempted'] or d['asset_ready'] or d['asset_pinned'] or not d['all_loader_resources_released'] or d['native_error'] or d['phase'] or d['board_phase']:raise ValueError('only unstarted, unpinned, released host-RAM staging can retire')
  if d['asset_bitmap']!=(1<<r['completed_chunks'])-1 or not 0<r['completed_chunks']<12:raise ValueError('partial bitmap differs')
  for item in r['packets']:
   if validate((session/item['file']).read_bytes(),public)!={k:v for k,v in item.items() if k!='file'}:raise ValueError('saved signed packet changed')
  nr=flow.read_json(next_dir/'report.json');rep=flow.read_json(next_dir/'reproduction.json',8*1024*1024)
  if nr['status']!=route.native_route.BOOT_STATUS or nr['receiver_policy']!={**policy,'generation':policy['generation']+1} or nr.get('bt_usb_integrated') is not True or rep['status']!='CURRENT-SOURCES-TWO-REBUILDS-WORLD-C-CHECK-PASS' or nr['payload_sha256']!=rep['payload_sha256'] or flow.sha((next_dir/'payload.efi').read_bytes())!=rep['payload_sha256'] or rep['world_package_sha256']!=state['package_sha256']:raise ValueError('next replacement/current world proof required')
  candidates=ROOT.parent/'native-wifi-qca9377-v1'/'runs/candidate42-sources'
  changed={'experiments/native-wifi-qca9377-v1/'+n for n in ('boot_build.py','boot-receiver-policy.json','verify_boot_profile.py','native_route.py')}
  for n,h in rep['inputs'].items():
   rel=Path(n)
   if rel.is_absolute() or '..' in rel.parts:raise ValueError('unsafe source path')
   source=candidates/rel.name if n in changed else ROOT.parent.parent/rel
   if flow.sha(source.read_bytes())!=h:raise ValueError('next source snapshot changed: '+n)
  if flow.sha((next_dir/'host.log').read_bytes())!=nr['host_log_sha256']:raise ValueError('next host log changed')
  for q in nr['gates']:
   name='actors-empty-boot-qemu' if q['empty_boot'] else 'actors-qemu'
   if flow.sha((next_dir/name/'observed.log').read_bytes())!=q['observed_log_sha256'] or q['payload_sha256']!=nr['payload_sha256']:raise ValueError('next QEMU proof changed')
  if preflight:
   print('RETIREMENT PREFLIGHT PASS; no state, packet, source or device changes');return
  old_inputs=flow.read_json(Path(r['checked_directory'])/'reproduction.json',8*1024*1024)['inputs']
  archive=session/'frozen-source-before-replacement';archive.mkdir(exist_ok=True)
  for name,h in old_inputs.items():
   p=ROOT.parent.parent/name
   if flow.sha(p.read_bytes())!=h:raise ValueError('old source changed before retirement')
   dst=archive/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
  evidence={'status':'PARTIAL-HOST-RAM-STAGING-RETIRED-FOR-CHECKED-NATIVE-REPLACEMENT','native_counter':policy['generation'],'next_counter':nr['receiver_policy']['generation'],'next_payload_sha256':nr['payload_sha256'],'next_report_sha256':flow.sha((next_dir/'report.json').read_bytes()),'next_reproduction_sha256':flow.sha((next_dir/'reproduction.json').read_bytes()),'session':str(session),'observation_sha256':flow.sha(observation.read_bytes()),'observation':raw,'decoded':d,'original_report_sha256':flow.sha((session/'report.json').read_bytes()),'old_source_inputs':old_inputs,'signed_packets_preserved':True,'device_writes':0,'reboot':False,'world_sha256':state['world_sha256'],'wifi_connected':False}
  flow.save(session/'retirement.json',evidence)
  r['status']=evidence['status'];r['retirement_sha256']=flow.sha((session/'retirement.json').read_bytes());flow.save(session/'report.json',r)
  state.setdefault('retired_hardware_trials',[]).append({'session':str(session),'retirement_sha256':r['retirement_sha256'],'native_counter':policy['generation'],'next_counter':evidence['next_counter']})
  state['hardware_trial_pending']=None;flow.save(state_path,state)
  print('Partial staging retired in controller only; signed packets preserved. No device write.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--session',type=Path,required=True);p.add_argument('--observation',type=Path,required=True);p.add_argument('--next-checked',type=Path,required=True);p.add_argument('--preflight-only',action='store_true');a=p.parse_args();retire(a.state,a.session,a.observation,a.next_checked,a.preflight_only)
if __name__=='__main__':main()
