"""Counter50 CE3 INIT admission after exact native49 timeout and owner release."""
import argparse,json,sys,time
from pathlib import Path
import startup_build as build
ROOT=build.ROOT;REPO=ROOT.parent.parent
sys.path.insert(0,str(build.BASE));import native_route as prior
flow,engine=prior.flow,prior.engine
BASE_GATES=prior.gates
STATUS='WMI-INIT-CANDIDATE-TWO-REBUILDS-UEFI-QEMU-PASS'
PURE={
 'ready':('native-wifi-qca9377-wmi-native-v5','runs/ready-codec','READY-MINIMUM-PREFIX-PINNED-ASAN-COFF-PASS'),
 'init':('native-wifi-qca9377-wmi-init-v1','evidence/2026-10-05','WMI-INIT-PINNED-LAYOUT-PLAN-ASAN-COFF-PASS'),
 'memory':('native-wifi-qca9377-memory-v1','evidence/2026-10-05/memory-plan','WMI-MEMORY-PLAN-PINNED-ORACLE-ASAN-COFF-PASS'),
 'transaction':('native-wifi-qca9377-wmi-transaction-v1','evidence/2026-10-06','WMI-INIT-TRANSACTION-ORDER-CREDIT-ASAN-COFF-PASS'),
 'resources':('native-wifi-qca9377-resources-v1','evidence/2026-10-06','QCA9377-PCI-TLV-RESOURCE-REFERENCE-ASAN-COFF-PASS')}
def gates(directory,payload,world):
 r=flow.read_json(directory/'report.json');v=flow.read_json(directory/'reproduction.json',8*1024*1024)
 if r['status']!=STATUS or r.get('build_host')!='yukabox' or r['payload_sha256']!=flow.sha(payload) or r['payload_bytes']!=len(payload) or len(payload)>262144:raise ValueError('exact INIT profile required')
 if v['status']!='WMI-INIT-CURRENT-SOURCES-TWO-REBUILDS-WORLD-C-CHECK-PASS' or v['payload_sha256']!=flow.sha(payload) or v['world_package_sha256']!=flow.sha(world) or v['build_host']!='yukabox':raise ValueError('current world and source rebuild required')
 if any(r.get(k) is not False for k in ('physical_verified','scan','wifi_connected','station_profile_admitted','persistent_operating_radio')) or r.get('memory_requests_supported')!=0:raise ValueError('bounded INIT-only profile required')
 for n,h in v['inputs'].items():
  p=Path(n)
  if p.is_absolute() or '..' in p.parts or flow.sha((REPO/p).read_bytes())!=h:raise ValueError('source differs:'+n)
 for n,h in r['source_sha256'].items():
  if v['inputs'].get(n)!=h:raise ValueError('profile input differs:'+n)
 required={str(p.relative_to(REPO)) for p in ROOT.iterdir() if p.is_file()}
 if not required.issubset(v['inputs']) or not required.issubset(r['source_sha256']):raise ValueError('complete new scope required')
 # Legacy hardware/boot evidence remains unchanged and is checked with its
 # ORIGINAL world16 package. Native50 has separate current-world17 C/VM proof.
 base=directory/'baseline';baseproof=flow.read_json(base/'reproduction.json',8*1024*1024)
 legacy_world=(directory/'legacy-world.rup').read_bytes()
 if flow.sha(legacy_world)!='8254c70465eac5a04612e2e33f74be5afa078c2e71b9f00b5d5e13a8f02f0f5e':raise ValueError('legacy world bytes changed')
 bg=BASE_GATES(base,(base/'payload.efi').read_bytes(),legacy_world)
 for n,h in baseproof['inputs'].items():
  if v['inputs'].get(n)!=h:raise ValueError('legacy hardware source differs:'+n)
 old=build.LAYOUT/'runs/checked-candidate/reproduction.json'
 if v['native47_reproduction_sha256']!=flow.sha(old.read_bytes()):raise ValueError('native47 source closure required')
 for n,h in flow.read_json(old,8*1024*1024)['inputs'].items():
  if v['inputs'].get(n)!=h:raise ValueError('native47 dependency omitted')
 for name,status,count in [('operating','NATIVE-WMI-INIT-DMA-READY-OWNER-RELEASE-ASAN-COFF-PASS',23),('initial','NATIVE-OPERATING-INITIAL-ENTRYPOINT-ASAN-PASS',65),('layout','SERVICE-READY-COMMON-PREFIX-MEMORY-ASAN-COFF-PASS',22244),('available','ACTUAL-SERVICE-AVAILABLE-PINNED-ENUM-ASAN-COFF-PASS',7198),('response','ACTUAL-CONNECT-RESPONSE-PINNED-CORE-ASAN-COFF-PASS',5186)]:
  p=directory/(name+'-report.json');h=flow.read_json(p)
  if h['status']!=status or h['build_host']!='yukabox' or h.get('scenarios',h.get('checks'))!=count or flow.sha(p.read_bytes())!=r[name+'_report_sha256'] or flow.sha((directory/(name+'-host.log')).read_bytes())!=h['host_log_sha256']:raise ValueError('component proof differs:'+name)
  for n,digest in h['source_sha256'].items():
   if v['inputs'].get(n)!=digest:raise ValueError('component source differs')
  if name in ('operating','initial') and h.get('actual_native_entrypoints') is not True:raise ValueError('actual entrypoints required')
  if name=='operating' and (not h.get('ce3_route_pinned') or not h.get('old_ce0_route_rejected') or not h['bounded_trial_teardown'] or h['persistent_operating_radio'] or h['scan'] or h['wifi_connected'] or h['physical_verified']):raise ValueError('bounded zero-RF scope required')
 for name,(folder,relative,status) in PURE.items():
  p=REPO/'experiments'/folder/relative/'report.json';h=flow.read_json(p);log=p.with_name('host.log')
  if h['status']!=status or h['build_host']!='yukabox' or v['inputs'].get(str(p.relative_to(REPO)))!=flow.sha(p.read_bytes()) or v['inputs'].get(str(log.relative_to(REPO)))!=flow.sha(log.read_bytes()) or flow.sha(log.read_bytes())!=h['host_log_sha256']:raise ValueError('pure INIT proof differs:'+name)
  for n,digest in {**h['source_sha256'],**h.get('dependency_sha256',{})}.items():
   full=n if n.startswith('experiments/') else 'experiments/'+folder+'/'+n
   if v['inputs'].get(full)!=digest:raise ValueError('pure source omitted:'+full)
 checks=v['host_checks']
 if not checks['sanitizers'] or checks['host_ticks']!=120 or checks['adversarial_camera_frames']!=16:raise ValueError('current city checks required')
 p=flow.read_json(ROOT/'receiver-policy.json')
 if p!=r['receiver_policy'] or p['generation']!=52 or flow.sha((ROOT/'receiver-policy.json').read_bytes())!=r['receiver_policy_sha256']:raise ValueError('exact50 receiver policy required')
 for sub,empty in [('actors-qemu',False),('actors-empty-boot-qemu',True)]:
  g=flow.read_json(directory/sub/'report.json');log=(directory/sub/'observed.log').read_bytes()
  if g not in r['gates'] or g['empty_boot'] is not empty or g['payload_sha256']!=flow.sha(payload) or flow.sha(log)!=g['observed_log_sha256'] or g['status']!='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS':raise ValueError('exact QEMU proof required')
  for marker in [b'WMI INIT SERVICE26..28 READ ONLY; ABSENT RADIO CLAIMS NO READY/MAC/IP',b'BOOT SERVICE20..22 READ ONLY; RAM SERVICE PRESERVED; CITY RETAINED',b'FRAGMENTED16+5 CONNECTION AND MATCHED DISCONNECTION VERIFIED THROUGH ACTUAL UEFI USB; NO ORPHAN GUESSING']:
   if marker not in log:raise ValueError('native scope marker absent')
 return {'report_sha256':flow.sha((directory/'report.json').read_bytes()),'reproduction_sha256':flow.sha((directory/'reproduction.json').read_bytes()),'profile_status':STATUS,'baseline_gate':bg}
def binding(state,private):
 public=private.with_suffix('.pub').read_bytes();installed=engine.gate_check(Path(state['engine']['installed_gate']));p=flow.read_json(ROOT/'receiver-policy.json')
 if flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256']:raise ValueError('installed owner gate changed')
 if p['owner']!=public.hex() or flow.sha(public)!=installed['owner_public_sha256'] or p['target']!=installed['target_sha256'] or p['generation']!=state['engine']['native_counter']+1:raise ValueError('owner target next counter differs')
 return public,installed
def fresh_recovery(state,observation,public,installed):
 if any(state.get(k) for k in ('pending','native_pending','recovery_pending','hardware_trial_pending')):raise ValueError('active owner exists')
 if state['engine']['native_counter']!=51:raise ValueError('exact51 starting scope required')
 release=flow.read_json(Path(state['engine']['last_release_report']))
 if release['status']!='EXACT-APPLIED-RECEIPT' or not release['receiver_reported_applied'] or release['counter']!=51 or release['payload_sha256']!=state['engine']['payload_sha256']:raise ValueError('actual51 receipt required')
 if not observation or not 0<=time.time()-observation.stat().st_mtime<=300:raise ValueError('fresh combined51 observations required')
 raw=flow.read_json(observation)
 for name in ['boot','operating','startup']:
  item=raw[name]
  if item.get('peripheral','').upper()!='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF' or item.get('writes')!=0:raise ValueError('known-peer zero-write observation required')
 from decode_boot import decode
 d=decode(raw['boot'])
 expected={'phase':5,'error':0,'plan_phase':20,'plan_error':0,'submitted':3114,'completed':3114,'native_stage':6,'native_error':8448,'adapter_phase':12,'cleanup_slots':14,'dma_users':0,'asset_pinned':0,'asset_bitmap':4095}
 if any(d.get(k)!=v for k,v in expected.items()) or not d['all_loader_resources_released']:raise ValueError('actual51 all-owner release required')
 import struct
 b=bytes.fromhex(raw['operating']['raw_hex']);w=bytes.fromhex(raw['startup']['raw_hex'])
 if len(b)!=488 or b[:8]!=b'QWOP0003' or len(w)!=244 or w[:8]!=b'QWIN0002':raise ValueError('exact51 envelopes required')
 fields=struct.unpack('<22I',b[8:96]);init=struct.unpack('<12I',w[8:56])
 if fields[:15]!=(2,0,7,0,0,3,4,320,1,1,2,21,574,1,0) or init!=(3,8,6,228,1,1,0,0,0,2,0,0):raise ValueError('actual51 service/timeout baseline required')
 if struct.unpack('<5I',w[96:116])!=(4,68,68,1,60):raise ValueError('exact51 rejected READY frame required')
 return d
def current_assets(state,checked):
 if any(state.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('active transport owner')
 policy=flow.read_json(ROOT/'receiver-policy.json');public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes();installed=engine.gate_check(Path(state['engine']['installed_gate']))
 payload=(checked/'payload.efi').read_bytes();g=gates(checked,payload,Path(state['package']).read_bytes());r=flow.read_json(Path(state['engine']['last_release_report']))
 if flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256']:raise ValueError('installed owner gate changed')
 if policy['generation']!=state['engine']['native_counter'] or flow.sha(payload)!=state['engine']['payload_sha256'] or policy['owner']!=public.hex() or policy['target']!=installed['target_sha256'] or flow.sha(public)!=installed['owner_public_sha256'] or r['status']!='EXACT-APPLIED-RECEIPT' or not r['receiver_reported_applied'] or r['counter']!=52 or r['payload_sha256']!=flow.sha(payload):raise ValueError('exact installed50 asset receiver required')
 return policy,public,g
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
  public,installed=binding(s,a.private)
  if a.action=='prepare':fresh_recovery(s,a.observation,public,installed)
  old=prior.gates
  try:
   prior.gates=gates
   if a.action=='prepare':print(prior.prepare(a.state,s,a.checked,a.private));return 0
   return prior.deliver(a.state,s,a.private)
  finally:prior.gates=old
if __name__=='__main__':raise SystemExit(main())
