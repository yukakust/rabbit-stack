"""Root admission of exact reviewed, bounded generation53; frozen52 unchanged."""
import argparse,json,sys,time,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
PROFILE=ROOT.parent/'native-wifi-qca9377-persistent-profile-v1'
V5=ROOT.parent/'native-wifi-qca9377-wmi-native-v5'
sys.path.insert(0,str(V5));import startup_route as baseline
flow,engine,prior=baseline.flow,baseline.engine,baseline.prior
BASE_GATES=baseline.gates
STATUS='BOUNDED-PERSISTENT-PROFILE-REPEATED-EFI-QEMU-WORLD17-PASS'
REPORT_SHA='673b298b7ff1464c794985b1096c0745886b533464460b5eccc03cff69c1060e'
PAYLOAD_SHA='261649e8cd7ab2bd59621f8ee559c421c36cc5e54c5d19238b558e55dc55a522'
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
def hashes(mapping,base):
 for n,h in mapping.items():
  p=Path(n)
  if p.is_absolute() or '..' in p.parts or flow.sha((base/p).read_bytes())!=h:raise ValueError('exact source differs:'+n)
def gates(directory,payload,world):
 if directory.resolve()!=(PROFILE/'runs/checked-candidate').resolve():raise ValueError('reviewed directory required')
 path=directory/'report.json';r=flow.read_json(path,8*1024*1024)
 if flow.sha(path.read_bytes())!=REPORT_SHA or r['status']!=STATUS or r['build_host']!='yukabox' or flow.sha(payload)!=PAYLOAD_SHA or len(payload)!=163840:raise ValueError('reviewed exact candidate required')
 if r['world_package_sha256']!=flow.sha(world) or r['bounded_us']!=10000000 or any(r[k] is not False for k in ('physical_verified','signing_admitted','station_ready','rf_transmit','physical_native52_success_assumed')):raise ValueError('bounded no-RF current-world scope')
 hashes(r['source_sha256'],REPO);hashes(r['generated_compiler_sources_sha256'],directory)
 required={str(p.relative_to(REPO)) for p in PROFILE.iterdir() if p.is_file()}
 if not required.issubset(r['source_sha256']) or len(r['source_sha256'])!=565:raise ValueError('whole source closure required')
 old=V5/'runs/checked-candidate';bg=BASE_GATES(old,(old/'payload.efi').read_bytes(),world)
 closure=old/'reproduction.json'
 if flow.sha(closure.read_bytes())!=r['inherited_native52_closure_sha256']:raise ValueError('native52 inheritance required')
 for n,h in flow.read_json(closure,8*1024*1024)['inputs'].items():
  if r['source_sha256'].get(n)!=h:raise ValueError('native52 source omitted')
 ep=PROFILE/'evidence/2026-10-07';nr=flow.read_json(ep/'report.json')
 if flow.sha((ep/'report.json').read_bytes())!=r['native_report_sha256'] or nr['status']!='BOUNDED-PERSISTENT-PROFILE-NATIVE-ASAN-COFF-PASS' or nr['scenarios']!=24 or not nr['actual_native_entrypoints'] or nr['rf_transmit'] or nr['bounded_us']!=10000000 or nr['generation']!=53 or flow.sha((ep/'host.log').read_bytes())!=nr['host_log_sha256']:raise ValueError('actual entrypoint proof required')
 for n,h in nr['source_sha256'].items():
  if r['source_sha256'].get(n)!=h:raise ValueError('native model source omitted')
 hashes(nr['compiled_fixture_sources_sha256'],PROFILE/'runs/native-host')
 checks=r['host_checks']
 if not checks['sanitizers'] or checks['host_ticks']!=120 or checks['adversarial_camera_frames']!=16 or checks['physical_execution_verified']:raise ValueError('current city checks required')
 policy=flow.read_json(PROFILE/'receiver-policy.json')
 if policy!=r['receiver_policy'] or policy['generation']!=53:raise ValueError('exact policy required')
 for sub,empty in [('actors-qemu',False),('actors-empty-boot-qemu',True)]:
  g=flow.read_json(directory/sub/'report.json');log=(directory/sub/'observed.log').read_bytes()
  if g not in r['gates'] or g['empty_boot'] is not empty or g['payload_sha256']!=flow.sha(payload) or flow.sha(log)!=g['observed_log_sha256'] or g['status']!='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS':raise ValueError('exact QEMU required')
  for marker in [b'BOUNDED RX SERVICE29..31 READ ONLY; ABSENT RADIO CLAIMS NO READY OR ACTIVE OWNERS',b'WMI INIT SERVICE26..28 READ ONLY; ABSENT RADIO CLAIMS NO READY/MAC/IP',b'BOOT SERVICE20..22 READ ONLY; RAM SERVICE PRESERVED; CITY RETAINED']:
   if marker not in log:raise ValueError('scope marker required')
 return {'report_sha256':REPORT_SHA,'reproduction_sha256':REPORT_SHA,'profile_status':STATUS,'baseline_gate':bg,'admission_source_sha256':flow.sha(Path(__file__).read_bytes())}
def binding(state,private):
 public=private.with_suffix('.pub').read_bytes();installed=engine.gate_check(Path(state['engine']['installed_gate']));p=flow.read_json(PROFILE/'receiver-policy.json')
 if flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256']:raise ValueError('owner gate changed')
 if p['owner']!=public.hex() or flow.sha(public)!=installed['owner_public_sha256'] or p['target']!=installed['target_sha256'] or p['generation']!=state['engine']['native_counter']+1:raise ValueError('owner/target/next generation differs')
 return public,installed
def fresh(state,observation):
 if any(state.get(k) for k in ('pending','native_pending','recovery_pending','hardware_trial_pending')):raise ValueError('active owner')
 if state['engine']['native_counter']!=52 or state['engine']['payload_sha256']!='0b4dfbf03b12eef58cbaa4eabe965dda606ded3337a60708b22574b02edb52f6':raise ValueError('actual52 base required')
 release=flow.read_json(Path(state['engine']['last_release_report']))
 if release['status']!='EXACT-APPLIED-RECEIPT' or not release['receiver_reported_applied'] or release['counter']!=52 or release['payload_sha256']!=state['engine']['payload_sha256']:raise ValueError('exact52 receipt required')
 if not observation or not 0<=time.time()-observation.stat().st_mtime<=300:raise ValueError('fresh52 combined read required')
 raw=flow.read_json(observation)
 for name in ('boot','operating','startup'):
  if raw[name].get('peripheral','').upper()!=PEER or raw[name].get('writes')!=0:raise ValueError('known-peer read-only required')
 from decode_boot import decode
 d=decode(raw['boot'])
 expected={'phase':5,'error':0,'plan_phase':20,'plan_error':0,'submitted':3114,'completed':3114,'native_stage':5,'native_error':0,'adapter_phase':12,'cleanup_slots':14,'dma_users':0,'asset_pinned':0,'asset_bitmap':4095}
 if any(d.get(k)!=v for k,v in expected.items()) or not d['all_loader_resources_released']:raise ValueError('actual52 release required')
 b=bytes.fromhex(raw['operating']['raw_hex']);w=bytes.fromhex(raw['startup']['raw_hex'])
 if len(b)!=488 or b[:8]!=b'QWOP0003' or len(w)!=244 or w[:8]!=b'QWIN0002':raise ValueError('exact52 envelope required')
 if struct.unpack('<22I',b[8:96])[:15]!=(2,0,7,0,0,3,4,320,1,1,2,21,574,1,0) or struct.unpack('<12I',w[8:56])!=(2,0,4,0,1,2,1,1,574,2,0,0) or w[56:62].hex()!='c0b5d778c3fb' or struct.unpack('<5I',w[96:116])!=(0,68,68,1,60):raise ValueError('actual READY/TX/complete response required')
 return d
def current_assets(state,checked):
 if any(state.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('transport active')
 flow.current(state);p=flow.read_json(PROFILE/'receiver-policy.json');public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes();installed=engine.gate_check(Path(state['engine']['installed_gate']))
 payload=(checked/'payload.efi').read_bytes();g=gates(checked,payload,Path(state['package']).read_bytes());r=flow.read_json(Path(state['engine']['last_release_report']))
 if flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256'] or p['generation']!=state['engine']['native_counter'] or flow.sha(payload)!=state['engine']['payload_sha256'] or p['owner']!=public.hex() or p['target']!=installed['target_sha256'] or flow.sha(public)!=installed['owner_public_sha256'] or r['status']!='EXACT-APPLIED-RECEIPT' or not r['receiver_reported_applied'] or r['counter']!=53 or r['payload_sha256']!=PAYLOAD_SHA:raise ValueError('exact installed53 required')
 return p,public,g
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['check','prepare','deliver','asset-prepare','asset-deliver']);p.add_argument('--state',type=Path,required=True);p.add_argument('--checked',type=Path);p.add_argument('--observation',type=Path);p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');p.add_argument('--diagnostic',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--session',type=Path);a=p.parse_args();a.state=a.state.resolve()
 with flow.state_lock(a.state):
  s=flow.read_json(a.state)
  if a.action=='check':print(json.dumps(gates(a.checked,(a.checked/'payload.efi').read_bytes(),Path(s['package']).read_bytes())));return 0
  if a.action.startswith('asset-'):
   import boot_asset_route as asset
   old=asset.current
   try:asset.current=current_assets;return asset.prepare(a,s) if a.action=='asset-prepare' else asset.deliver(a,s)
   finally:asset.current=old
  binding(s,a.private)
  if a.action=='prepare':fresh(s,a.observation)
  old=prior.gates
  try:
   prior.gates=gates
   if a.action=='prepare':print(prior.prepare(a.state,s,a.checked,a.private));return 0
   return prior.deliver(a.state,s,a.private)
  finally:prior.gates=old
if __name__=='__main__':raise SystemExit(main())
