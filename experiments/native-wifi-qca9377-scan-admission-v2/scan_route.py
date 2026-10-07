"""Root admission of exact reviewed, bounded generation53; frozen52 unchanged."""
import argparse,json,sys,time,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
PROFILE=ROOT.parent/'native-wifi-qca9377-scan-native-profile-v2'
V5=ROOT.parent/'native-wifi-qca9377-wmi-native-v5'
sys.path.insert(0,str(V5));import startup_route as baseline
flow,engine,prior=baseline.flow,baseline.engine,baseline.prior
BASE_GATES=baseline.gates
STATUS='SCAN55-REPEATED-FULL-EFI-QEMU-WORLD17-OWNED-EXPORT-PASS'
REPORT_SHA='688446530f8e573fb83d67ff141780926f49d7e0ac3a324ccf2dc56f0e523815'
PAYLOAD_SHA='cc8d7fec39a812273c1af5d52711fe6dc281b48873925aec2136cf3cb8533297'
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
def hashes(mapping,base):
 for n,h in mapping.items():
  p=Path(n)
  if p.is_absolute() or '..' in p.parts or flow.sha((base/p).read_bytes())!=h:raise ValueError('exact source differs:'+n)
def gates(directory,payload,world):
 if directory.resolve()!=(PROFILE/'runs/checked-candidate').resolve():raise ValueError('reviewed directory required')
 path=directory/'report.json';r=flow.read_json(path,8*1024*1024)
 if flow.sha(path.read_bytes())!=REPORT_SHA or r['status']!=STATUS or r['build_host']!='yukabox' or flow.sha(payload)!=PAYLOAD_SHA or len(payload)!=187392:raise ValueError('reviewed exact scan candidate required')
 if r['world_package_sha256']!=flow.sha(world) or r['bounded_us']!=25000000 or any(r[k] is not False for k in ('physical_verified','signing_admitted','station_ready','rf_admission_granted','physicalSSID_discovery','physical_native52_success_assumed')) or not r['rf_operation_candidate']:raise ValueError('exact bounded passive candidate scope required')
 hashes(r['source_sha256'],REPO);hashes(r['generated_compiler_sources_sha256'],directory)
 required={str(p.relative_to(REPO)) for p in PROFILE.iterdir() if p.is_file()}
 if not required.issubset(r['source_sha256']) or len(r['source_sha256'])!=642:raise ValueError('whole642-source closure required')
 old=V5/'runs/checked-candidate';bg=BASE_GATES(old,(old/'payload.efi').read_bytes(),world)
 closure=old/'reproduction.json'
 if flow.sha(closure.read_bytes())!=r['inherited_native52_closure_sha256']:raise ValueError('native52 inheritance required')
 for n,h in flow.read_json(closure,8*1024*1024)['inputs'].items():
  if r['source_sha256'].get(n)!=h:raise ValueError('inherited source omitted')
 ep=PROFILE/'evidence/2026-10-07';nr=flow.read_json(ep/'native-report.json')
 if flow.sha((ep/'native-report.json').read_bytes())!=r['native_report_sha256'] or nr['status']!='SCAN55-ACTUAL-PHYSICAL54-REGRESSION-PREFIX28-ARCHIVE16-ASAN-COFF-PASS' or nr['scenarios']!=19 or not nr['actual_native_entrypoints'] or not nr['lower_backend_mocked'] or nr['physical_verified'] or nr['credentials'] or nr['unknown_event_discards'] or nr['export_slots']!=22 or nr['export_pages']!=110 or flow.sha((ep/'native-host.log').read_bytes())!=nr['host_log_sha256']:raise ValueError('actual entrypoint export proof required')
 for n,h in nr['source_sha256'].items():
  if r['source_sha256'].get(n)!=h:raise ValueError('native model source omitted')
 hashes(nr['compiled_fixture_sources_sha256'],PROFILE/'runs/native-host')
 proof=PROFILE/'runs/policy-binding';pb=flow.read_json(proof/'binding.json');pr=flow.read_json(proof/'report.json')
 if flow.sha((proof/'binding.json').read_bytes())!=r['authenticated_policy_binding_sha256'] or pb['status']!='INDEPENDENT-SIGNED-REGDB-EXACT-GE-WORLD108-PROPOSAL-HEADER-PASS' or pb['rf_admission_granted'] or flow.sha((proof/'report.json').read_bytes())!=pb['report_sha256'] or flow.sha((proof/'host.log').read_bytes())!=pb['host_log_sha256'] or pr['status']!='SIGNED-REGDB-REBUILD-PURE-PASSIVE-FILTER-ASAN-COFF-PASS' or pr['checks']!=199278 or pr['device_action_count']:raise ValueError('independent signed-regdb proof required')
 proposal=REPO/'experiments/native-wifi-qca9377-regulatory-policy-v1/evidence/2026-10-07/policy-proposal.json';prop=flow.read_json(proposal)
 if flow.sha(proposal.read_bytes())!=pb['proposal_sha256'] or flow.sha((PROFILE/'scan_policy.h').read_bytes())!=pb['header_sha256'] or prop['rf_admission_granted'] or not prop['signature_verified'] or prop['country_or_board_override'] or prop['country_alpha2']!='GE' or prop['board_regdomain']!=108 or len(prop['candidate_channels'])!=13:raise ValueError('exact authenticated GE/world108 metadata required')
 for i,c in enumerate(prop['candidate_channels']):
  if any(c[k]!=v for k,v in {'frequency_mhz':2412+5*i,'centre1_mhz':2412+5*i,'centre2_mhz':0,'width_mhz':20,'flags':2 if i>=11 else 0,'passive':1,'mode':1,'max_power_dbm':20,'max_reg_power_dbm':20,'antenna_gain_db':0}.items()):raise ValueError('passive13-row policy differs')
 for n,h in pr['sources_sha256'].items():
  if flow.sha((REPO/'experiments/native-wifi-qca9377-regulatory-policy-v1'/n).read_bytes())!=h:raise ValueError('policy source differs')
 event_root=REPO/'experiments/native-wifi-qca9377-scan-event-v2';er=flow.read_json(event_root/'evidence/2026-10-07/report.json')
 if er['status']!='SCAN-EVENT-V2-PINNED-MIN-PREFIX-OPAQUE-REASON-ASAN-COFF-PASS' or er['checks']!=8967 or er['build_host']!='yukabox' or flow.sha((event_root/'evidence/2026-10-07/host.log').read_bytes())!=er['host_log_sha256']:raise ValueError('pinned event prefix proof required')
 for n,h in er['source_sha256'].items():
  q=Path(n);q=REPO/q if q.parts[0]=='experiments' else event_root/q
  if flow.sha(q.read_bytes())!=h:raise ValueError('event source differs')
 checks=r['host_checks']
 if not checks['sanitizers'] or checks['host_ticks']!=120 or checks['adversarial_camera_frames']!=16 or checks['physical_execution_verified']:raise ValueError('current city checks required')
 policy=flow.read_json(PROFILE/'receiver-policy.json')
 if policy!=r['receiver_policy'] or policy['generation']!=55 or prop['target_id']!=policy['target']:raise ValueError('exact54 policy/target required')
 for sub,empty in [('actors-qemu',False),('actors-empty-boot-qemu',True)]:
  g=flow.read_json(directory/sub/'report.json');log=(directory/sub/'observed.log').read_bytes()
  if g not in r['gates'] or g['empty_boot'] is not empty or g['payload_sha256']!=flow.sha(payload) or flow.sha(log)!=g['observed_log_sha256'] or g['status']!='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS':raise ValueError('exact QEMU proof required')
  if b'SCAN' not in log or b'EXPORT' not in log:raise ValueError('scan/export scope marker required')
 return {'report_sha256':REPORT_SHA,'reproduction_sha256':REPORT_SHA,'profile_status':STATUS,'baseline_gate':bg,'admission_source_sha256':flow.sha(Path(__file__).read_bytes()),'passive_policy_binding_sha256':r['authenticated_policy_binding_sha256']}
def binding(state,private):
 public=private.with_suffix('.pub').read_bytes();installed=engine.gate_check(Path(state['engine']['installed_gate']));p=flow.read_json(PROFILE/'receiver-policy.json')
 if flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256']:raise ValueError('owner gate changed')
 if p['owner']!=public.hex() or flow.sha(public)!=installed['owner_public_sha256'] or p['target']!=installed['target_sha256'] or p['generation']!=state['engine']['native_counter']+1:raise ValueError('owner/target/next generation differs')
 return public,installed
def fresh(state,observation):
 if any(state.get(k) for k in ('pending','native_pending','recovery_pending','hardware_trial_pending')):raise ValueError('active owner')
 if state['engine']['native_counter']!=54 or state['engine']['payload_sha256']!='3eefea77fbab35bca609216e4a418c2abad695f1a8a83da8aa2ee147bbfefca3':raise ValueError('actual54 base required')
 receipt=flow.read_json(Path(state['engine']['last_release_report']))
 if receipt['status']!='EXACT-APPLIED-RECEIPT' or not receipt['receiver_reported_applied'] or receipt['counter']!=54 or receipt['payload_sha256']!=state['engine']['payload_sha256']:raise ValueError('exact54 receipt required')
 if not observation or not 0<=time.time()-observation.stat().st_mtime<=300:raise ValueError('fresh54 combined read required')
 raw=flow.read_json(observation)
 sys.path.insert(0,str(REPO/'experiments/native-wifi-qca9377-scan-observer-v2'));import collect as collector;from decode_scan import decode_capture
 assets=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/firmware-ram-g9g89amj';collector.validate_saved_assets(flow.read_json(assets/'report.json'),assets)
 d=decode_capture(raw['capture'])
 archive=REPO/'experiments/native-wifi-qca9377-scan-result-v1/evidence/2026-10-07';old=flow.read_json(archive/'capture54.json')
 if raw['capture']['status_hex']!=old['status_hex'] or raw['capture']['pages_hex']!=old['pages_hex']:raise ValueError('stable same54 retained owner graph required')
 result=flow.read_json(archive/'result54.json');audit=flow.read_json(archive/'audit.json')
 if audit['result_sha256']!=flow.sha((archive/'result54.json').read_bytes()) or not result['all_raw_pages_saved_twice'] or not result['all_hardware_owners_released'] or not result['firmware_matching_started_observed'] or result['physical_ssid_discovered']:raise ValueError('exact54 failed dispatch/raw/actual release proof required')
 b=raw['boot']
 if b.get('peripheral','').upper()!=PEER or b.get('writes')!=0:raise ValueError('known-peer zero-write BOOT required')
 bb=bytes.fromhex(b['raw_hex'])
 if b.get('format')!='QWBT1' or len(bb)!=160 or bb[:8]!=b'QWBT0001' or bb[128:].hex()!='8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01' or struct.unpack('<30I',bb[8:128])!=(5,0,20,0,3114,3114,4202432,3,0,20,2,1792,4,1,0,0,0,0,6,8448,12,14,0,84017153,8,5,0,0,0,1):raise ValueError('actual54 all14/RAM release required')
 if not d['actual_owners_released'] or d['lifecycle_phase']!=4 or d['lifecycle_error'] or d['persistent_error'] or d['startup_ready_seen']!=1 or d['startup_tx_complete']!=1:raise ValueError('actual54 lifecycle/READY owner release required')
 if (d['native_error'],d['coordinator_error'],d['archive_count'],d['dispatcher_count'],d['rx_queue_count'],d['tx_completed'])!=(6,15,2,2,2,5):raise ValueError('exact54 failure baseline required')
 return {'prior_physical_trial':'FAILED-DISPATCH-WITH-GENUINE-STARTED','actual54_allowners_released':True,'prior_raw_pages_saved_twice':40,'prior_unknown_payloads_exported':True,'passive_rf_trial_authorized':True,'no_credentials':True,'prior_result_sha256':audit['result_sha256']}
def current_assets(state,checked):
 if any(state.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('transport active')
 flow.current(state);p=flow.read_json(PROFILE/'receiver-policy.json');public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes();installed=engine.gate_check(Path(state['engine']['installed_gate']))
 payload=(checked/'payload.efi').read_bytes();g=gates(checked,payload,Path(state['package']).read_bytes());r=flow.read_json(Path(state['engine']['last_release_report']))
 if flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256'] or p['generation']!=state['engine']['native_counter'] or flow.sha(payload)!=state['engine']['payload_sha256'] or p['owner']!=public.hex() or p['target']!=installed['target_sha256'] or flow.sha(public)!=installed['owner_public_sha256'] or r['status']!='EXACT-APPLIED-RECEIPT' or not r['receiver_reported_applied'] or r['counter']!=55 or r['payload_sha256']!=PAYLOAD_SHA:raise ValueError('exact installed53 required')
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
  admission=fresh(s,a.observation) if a.action=='prepare' else None
  if a.action=='deliver':
   saved=Path(s['native_pending']);rr=flow.read_json(saved/'report.json');proof=rr.get('passive_rf_admission')
   if not proof or not proof['passive_rf_trial_authorized'] or proof['no_credentials'] is not True or flow.sha((saved/'prior54-observation.json').read_bytes())!=proof['observation_sha256']:raise ValueError('saved passive admission binding required')
  old=prior.gates
  try:
   prior.gates=gates
   if a.action=='prepare':
    saved=prior.prepare(a.state,s,a.checked,a.private);raw=a.observation.read_bytes();(saved/'prior54-observation.json').write_bytes(raw)
    admission.update(observation_sha256=flow.sha(raw),proposal_sha256='a5ce1d3e2fdf8aefc2f862c77239cd2fbff1077371763c59c1b7a10d86ae3148',authorization='existing explicit owner Wi-Fi scan/connect instruction')
    rr=flow.read_json(saved/'report.json');rr['passive_rf_admission']=admission;flow.save(saved/'report.json',rr);print(saved);return 0
   return prior.deliver(a.state,s,a.private)
  finally:prior.gates=old
if __name__=='__main__':raise SystemExit(main())
