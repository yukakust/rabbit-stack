"""Strict additive admission; reuse unchanged native transport and baseline gates."""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
sys.path.insert(0,str(ROOT.parent/'native-wifi-qca9377-v1'))
import native_route as prior
from decode_boot import decode
flow,engine=prior.flow,prior.engine
BASE_GATES=prior.gates
STATUS='OPERATING-CANDIDATE-TWO-REBUILDS-UEFI-QEMU-PASS'
def gates(directory,payload,world):
 r=flow.read_json(directory/'report.json');v=flow.read_json(directory/'reproduction.json',8*1024*1024)
 if r.get('build_host')!='yukabox':raise ValueError('candidate build host required')
 if r['status']!=STATUS or r['payload_sha256']!=flow.sha(payload) or r['payload_bytes']!=len(payload) or len(payload)>262144:raise ValueError('exact operating payload required')
 # Original port/reset/allocation/USB/BMI/asset/boot gates remain mandatory.
 base=directory/'baseline';base_payload=(base/'payload.efi').read_bytes()
 base_gate=BASE_GATES(base,base_payload,world)
 if base_gate['profile_status']!=prior.BOOT_STATUS:raise ValueError('exact boot prerequisite required')
 if v['status']!='OPERATING-CURRENT-SOURCES-TWO-REBUILDS-WORLD-C-CHECK-PASS' or v['payload_sha256']!=flow.sha(payload) or v['world_package_sha256']!=flow.sha(world) or v['build_host']!='yukabox':raise ValueError('exact operating reproduction required')
 old_proof=ROOT.parent/'native-wifi-qca9377-service-start-v1/runs/checked-candidate/reproduction.json'
 if v.get('native46_reproduction_sha256')!=flow.sha(old_proof.read_bytes()):raise ValueError('exact native45 reproduction required')
 for n,h in flow.read_json(old_proof,8*1024*1024)['inputs'].items():
  if v['inputs'].get(n)!=h:raise ValueError('native45 closure differs:'+n)
 base_inputs=flow.read_json(base/'reproduction.json',8*1024*1024)['inputs']
 for n,h in base_inputs.items():
  if v['inputs'].get(n)!=h:raise ValueError('baseline closure differs:'+n)
 required={str(p.relative_to(REPO)) for p in ROOT.iterdir() if p.is_file() and p.suffix in ('.c','.h','.py','.json')}
 import operating_build
 required|={str((operating_build.SESSION/n).relative_to(REPO)) for n in operating_build.PROTOCOL}
 required|={str((operating_build.AVAILABLE/n).relative_to(REPO)) for n in ('available.c','available.h','verify_available.py')}
 if not required.issubset(r['source_sha256']) or not required.issubset(v['inputs']):raise ValueError('complete operating source closure required')
 for name,h in v['inputs'].items():
  p=Path(name)
  if p.is_absolute() or '..' in p.parts or flow.sha((REPO/p).read_bytes())!=h:raise ValueError('operating input differs:'+name)
 for n,h in r['source_sha256'].items():
  if v['inputs'].get(n)!=h:raise ValueError('profile source differs:'+n)
 for name,status,cases in [('operating','NATIVE-OPERATING-CE-HANDSHAKE-SERVICE-READY-ASAN-COFF-PASS',41),('initial','NATIVE-OPERATING-INITIAL-ENTRYPOINT-ASAN-PASS',65)]:
  p=directory/(name+'-report.json');h=flow.read_json(p)
  if h['status']!=status or h['scenarios']!=cases or h['build_host']!='yukabox' or h.get('actual_native_entrypoints') is not True:raise ValueError('operating entrypoint proof required:'+name)
  if flow.sha(p.read_bytes())!=r[name+'_report_sha256'] or flow.sha((directory/(name+'-host.log')).read_bytes())!=h['host_log_sha256']:raise ValueError('operating proof log differs')
  if name=='operating' and (any(h.get(k) is not True for k in ('fixture_owner_override_only','bounded_trial_teardown')) or any(h.get(k) is not False for k in ('persistent_operating_radio','scan','wifi_connected','physical_verified'))):raise ValueError('bounded operating scope required')
  for n,val in h['source_sha256'].items():
   if v['inputs'].get(n)!=val:raise ValueError('entrypoint source differs:'+n)
 layout=flow.read_json(directory/'layout-report.json')
 if layout['status']!='SERVICE-READY-COMMON-PREFIX-MEMORY-ASAN-COFF-PASS' or layout['checks']!=22244 or layout['build_host']!='yukabox' or layout['reference_sha256']!='16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9':raise ValueError('pinned common-prefix proof required')
 if flow.sha((directory/'layout-report.json').read_bytes())!=r['layout_report_sha256'] or flow.sha((directory/'layout-host.log').read_bytes())!=layout['host_log_sha256']:raise ValueError('layout proof/log changed')
 for n,h in layout['source_sha256'].items():
  if v['inputs'].get(n)!=h:raise ValueError('layout source differs:'+n)
 av=flow.read_json(directory/'available-report.json')
 if av['status']!='ACTUAL-SERVICE-AVAILABLE-PINNED-ENUM-ASAN-COFF-PASS' or av['checks']!=7198 or av['build_host']!='yukabox':raise ValueError('pinned available event proof required')
 if flow.sha((directory/'available-report.json').read_bytes())!=r['available_report_sha256'] or flow.sha((directory/'available-host.log').read_bytes())!=av['host_log_sha256']:raise ValueError('available proof/log differs')
 for n,h in av['source_sha256'].items():
  if v['inputs'].get(n)!=h:raise ValueError('available oracle source differs:'+n)
 response=flow.read_json(directory/'response-report.json')
 if response['status']!='ACTUAL-CONNECT-RESPONSE-PINNED-CORE-ASAN-COFF-PASS' or response['checks']!=5186 or response['build_host']!='yukabox' or response['reference_sha256']!='e2dc499ce2865b16456d436dc55db38da93282778d8cc86d03ed07a3c37c1963':raise ValueError('pinned actual response proof required')
 if flow.sha((directory/'response-report.json').read_bytes())!=r['response_report_sha256'] or flow.sha((directory/'response-host.log').read_bytes())!=response['host_log_sha256']:raise ValueError('actual response proof log binding changed')
 for n,h in response['source_sha256'].items():
  if v['inputs'].get(n)!=h:raise ValueError('response oracle source differs:'+n)
 checks=v['host_checks']
 if checks['sanitizers'] is not True or checks['host_ticks']!=120 or checks['adversarial_camera_frames']!=16:raise ValueError('current world C proof required')
 policy=flow.read_json(ROOT/'receiver-policy.json')
 if policy!=r['receiver_policy'] or flow.sha((ROOT/'receiver-policy.json').read_bytes())!=r['receiver_policy_sha256']:raise ValueError('exact generation policy required')
 old=flow.read_json(base/'report.json')['receiver_policy'];expected={**old,'generation':old['generation']+5}
 if policy!=expected:raise ValueError('only next-generation exact asset policy admitted')
 for sub,empty in [('actors-qemu',False),('actors-empty-boot-qemu',True)]:
  g=flow.read_json(directory/sub/'report.json');log=(directory/sub/'observed.log').read_bytes()
  if g not in r['gates'] or g['empty_boot'] is not empty or g['payload_sha256']!=flow.sha(payload) or g['status']!='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS' or flow.sha(log)!=g['observed_log_sha256']:raise ValueError('exact QEMU proof required')
  for marker in (b'OPERATING SERVICE23..25 READ ONLY; ABSENT TARGET DOES NOT CLAIM SERVICE READY OR WIFI',b'BOOT SERVICE20..22 READ ONLY; RAM SERVICE PRESERVED; CITY RETAINED',b'FRAGMENTED16+5 CONNECTION AND MATCHED DISCONNECTION VERIFIED THROUGH ACTUAL UEFI USB; NO ORPHAN GUESSING'):
   if marker not in log:raise ValueError('operating QEMU marker missing')
 return {'report_sha256':flow.sha((directory/'report.json').read_bytes()),'reproduction_sha256':flow.sha((directory/'reproduction.json').read_bytes()),'profile_status':STATUS,'baseline_gate':base_gate}
def fresh(path,observation):
 if not path or not observation or any(not 0<=time.time()-p.stat().st_mtime<=300 for p in (path,observation)):raise ValueError('fresh dual observations required')
 raw=flow.read_json(path);op=flow.read_json(observation)
 for value in (raw,op):
  if value.get('peripheral','').upper()!='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF' or value.get('writes')!=0:raise ValueError('known-peer read-only observation required')
 # Exact immutable recorded46 baseline; variable descriptor DMA address omitted.
 baseline=REPO/'experiments/native-wifi-qca9377-service-start-v1/evidence/2026-10-06/native46-control-result/native46-current-diagnostic.json'
 if flow.sha(baseline.read_bytes())!='787766d249d75dd3c0d8f51f5e5a1257ac33567176d1b5cfe928a16301e6b8a6':raise ValueError('recorded46 baseline changed')
 expected=bytes.fromhex(flow.read_json(baseline)['raw_hex']);wire=bytes.fromhex(op.get('raw_hex',''))
 if len(wire)!=488 or wire[:136]!=expected[:136] or wire[140:]!=expected[140:]:raise ValueError('exact observed46 READY format required')
 d=decode(raw);fields={'phase':5,'error':0,'plan_phase':20,'plan_error':0,'submitted':3114,'completed':3114,'ready_bytes':20,'boot_round':1,'native_stage':6,'native_error':8448,'adapter_phase':12,'cleanup_slots':14,'dma_users':0,'asset_pinned':0,'asset_bitmap':4095}
 if any(d.get(k)!=v for k,v in fields.items()) or not d['all_loader_resources_released']:raise ValueError('actual46 owner release required')
 return d
def binding(state,private):
 installed=engine.gate_check(Path(state['engine']['installed_gate']));public=private.with_suffix('.pub').read_bytes()
 p=flow.read_json(ROOT/'receiver-policy.json')
 if p['owner']!=public.hex() or flow.sha(public)!=installed['owner_public_sha256'] or p['target']!=installed['target_sha256'] or p['generation']!=state['engine']['native_counter']+1:raise ValueError('owner target next-counter binding required')
def current_assets(state,checked):
 if any(state.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('pending world/native operation')
 flow.current(state)
 payload=(checked/'payload.efi').read_bytes();gate=gates(checked,payload,Path(state['package']).read_bytes())
 installed=engine.gate_check(Path(state['engine']['installed_gate']));public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes()
 policy=flow.read_json(ROOT/'receiver-policy.json')
 if flow.sha(payload)!=state['engine']['payload_sha256'] or policy['generation']!=state['engine']['native_counter'] or policy['target']!=installed['target_sha256'] or policy['owner']!=public.hex() or flow.sha(public)!=installed['owner_public_sha256']:raise ValueError('current installed operating receiver binding required')
 applied=flow.read_json(Path(state['engine']['last_release_report']))
 if applied['status']!='EXACT-APPLIED-RECEIPT' or not applied['receiver_reported_applied'] or applied['counter']!=policy['generation'] or applied['payload_sha256']!=flow.sha(payload):raise ValueError('exact installed applied receipt required')
 return policy,public,gate
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('check','prepare','deliver','asset-prepare','asset-deliver'));p.add_argument('--state',type=Path,required=True);p.add_argument('--checked',type=Path);p.add_argument('--baseline',type=Path);p.add_argument('--operating-observation',type=Path);p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');p.add_argument('--diagnostic',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--session',type=Path);a=p.parse_args()
 with flow.state_lock(a.state):
  s=flow.read_json(a.state)
  if a.action=='check':print(json.dumps(gates(a.checked,(a.checked/'payload.efi').read_bytes(),Path(s['package']).read_bytes())));return 0
  if a.action.startswith('asset-'):
   import boot_asset_route as asset
   old=asset.current
   try:
    asset.current=current_assets
    return asset.prepare(a,s) if a.action=='asset-prepare' else asset.deliver(a,s)
   finally:asset.current=old
  binding(s,a.private)
  if a.action=='prepare':fresh(a.baseline,a.operating_observation)
  old=prior.gates
  try:
   prior.gates=gates
   if a.action=='prepare':print(prior.prepare(a.state,s,a.checked,a.private));return 0
   return prior.deliver(a.state,s,a.private)
  finally:prior.gates=old
if __name__=='__main__':raise SystemExit(main())
