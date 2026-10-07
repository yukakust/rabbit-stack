"""Public-only prior59 proof and durable exact-session retirement. No radio/key APIs."""
from pathlib import Path
import sys,json,time,shutil,os
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'native-wifi-qca9377-observation59-root-route-v1'))
import route as prior
import assets
flow,engine=prior.flow,prior.engine
ROOT=Path(__file__).resolve().parent
NATIVE_PACKET='5462ada06c7a1e2fb801c31f9f3ab35c3eecc286dc7fbba8b3c296c7d9ce62ad'
def need(ok,why):prior.need(ok,why)
def raw_callback(path,size):
 rows=[json.loads(x) for x in path.read_text().splitlines() if x.startswith('{')]
 for v in rows:need(v.get('code')==0 and not v.get('domain'),'read error')
 values=[x['stage'].split(' hex:')[1] for x in rows if x.get('stage','').startswith(f'value bytes:{size} hex:')]
 need(len(values)==1,'one exact complete callback')
 return bytes.fromhex(values[0])
def verify(s):
 policy,public,g=assets.current(s,prior.CHECKED)
 need(s.get('hardware_trial_pending'),'exact completed59 assets needed')
 d=Path(s['hardware_trial_pending']);r=flow.read_json(d/'report.json')
 need(r['status']=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and r['completed_chunks']==12 and r['policy']==policy and r['gate']==g and r['native_counter']==59 and r['world_counter']==19 and r['native_payload_sha256']==prior.PAYLOAD and r['world_sha256']==prior.SEMANTIC,'actual full59 signed session')
 need(r['last_receipt']['bitmap']==4095 and r['last_receipt']['ready']==1 and r['last_receipt']['action']==4 and r['last_receipt']['peripheral'].upper()==prior.PEER,'actual full59 accepted receipt')
 for item in r['packets']:
  p=d/prior.safe(item['file']);need(assets.validate(p.read_bytes(),public)=={k:v for k,v in item.items() if k!='file'},'immutable signed firmware changed')
 native=Path(s['engine']['last_release_report']).parent;packet=(native/'native.rrt').read_bytes()
 installed=engine.gate_check(Path(s['engine']['installed_gate']))
 verified=engine.verify(packet,target=bytes.fromhex(prior.TARGET),owner=public,base_runtime=bytes.fromhex(prior.PLAIN),world=Path(s['package']).read_bytes(),counter=58)
 need(verified.counter==59 and flow.sha(verified.payload)==prior.PAYLOAD and flow.sha(packet)==NATIVE_PACKET,'actual public59 signature')
 return d,native
def fresh(q,state):
 r=flow.read_json(q/'report.json');need(type(r['writes']) is int and r['writes']==0 and r['state_sha256']==flow.sha(state) and 0<=time.time()-r['observed_at']<=300,'fresh actual59 context')
 for n in ('receipt.log','prefix.log'):need(prior.sha(q/n)==r['inputs'][n],'raw callback hash')
 raw=raw_callback(q/'receipt.log',60)
 need(raw[:4]==b'RFS\1' and raw[20:24]==b'\2\0\0\0' and int.from_bytes(raw[24:28],'little')==59 and raw[28:].hex()==NATIVE_PACKET,'physical59 still applied; no reset')
 raw=raw_callback(q/'prefix.log',240)
 import struct
 values=struct.unpack('<58I',raw[8:]);fields=dict(zip('''generation prefix_phase prefix_reason stop_calls prefix_released stop_offset stop_submitted stop_completed stop_plan stop_io boot_phase boot_error plan_phase plan_error plan_offset plan_submitted plan_completed io_phase stage failed adapter_phase cleanup_slot held dma_users claimed access_count bus_owned boot_owns_pin asset_pinned irq_owned link_owned wake_owned reset_owned ble_state pending connected credits inflight stream_used stream_goal usb_polls usb_reads usb_timeouts usb_observation last_usb_status_lo last_usb_status_hi last_usb_result last_usb_bytes raw_count raw_overflow usb_fault frames max_poll_us max_qca_us started_lo started_hi last_lo last_hi'''.split(),values))
 need(raw[:8]==b'QPFX0001' and fields['generation']==59 and fields['prefix_phase']==3 and fields['prefix_reason']==0 and fields['prefix_released']==1 and fields['stop_offset']==32984 and fields['stop_submitted']==fields['stop_completed'] and fields['cleanup_slot']==14 and fields['adapter_phase']==12,'actual checked59 prefix release')
 need(not any(fields[k] for k in ('held','dma_users','claimed','access_count','bus_owned','boot_owns_pin','asset_pinned','irq_owned','link_owned','wake_owned','reset_owned','raw_overflow','usb_fault')),'actual remaining owner/transport fault')
 return fields
def inventory(d):
 paths={}
 for p in d.rglob('*'):
  need(not p.is_symlink(),'session symlink forbidden')
  if p.is_file():paths[str(p.relative_to(d))]=prior.sha(p)
 return paths
def retire(state_path,s,q,candidate_admission):
 # Caller must independently validate exact new60 proof before this state transition.
 need(candidate_admission.get('native_counter')==60 and candidate_admission.get('world_package_sha256')==prior.WORLD and candidate_admission.get('source_model_verified') is True,'independent root60 candidate gate required')
 before=state_path.read_bytes();need(flow.read_json(state_path)==s,'unchanged actual state')
 assets_dir,native_dir=verify(s);fields=fresh(q,before)
 directory=ROOT/'runs/retired59';need(not directory.exists(),'retirement exists; inspect saved manifest, never overwrite')
 directory.mkdir(parents=True)
 manifests={}
 for name,source in (('assets',assets_dir),('native',native_dir)):
  expected=inventory(source);target=directory/name;shutil.copytree(source,target);need(inventory(target)==expected and inventory(source)==expected,'durable archive changed');manifests[name]=expected
  for p in target.rglob('*'):
   if p.is_file():
    with p.open('rb') as f:os.fsync(f.fileno())
 shutil.copytree(q,directory/'fresh-observation');(directory/'before-state.json').write_bytes(before)
 report={'status':'ACTUAL59-FULL-ASSET-CHECKED-RELEASE-ARCHIVED','native_counter':59,'world_counter':19,'session':str(assets_dir),'inventory':manifests,'prior_state_sha256':flow.sha(before),'fields':fields,'new_candidate':candidate_admission,'reboot_command':False,'new_signatures':0}
 flow.save(directory/'retirement.json',report)
 with (directory/'retirement.json').open('rb') as f:os.fsync(f.fileno())
 fd=os.open(directory,os.O_RDONLY);os.fsync(fd);os.close(fd)
 need(state_path.read_bytes()==before,'state changed before retirement')
 after=dict(s);after['hardware_trial_pending']=None;after['last_hardware_trial_retirement']=str(directory/'retirement.json');flow.save(state_path,after)
 return after,directory
