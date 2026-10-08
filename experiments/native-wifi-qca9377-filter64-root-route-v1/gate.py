"""Exact64 public technical gate; separate Root admission required; no keys or device APIs."""
from pathlib import Path
import hashlib,struct,json
import prior63
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
prior62=prior63.authority().gate
flow,engine,primitive,base60=prior62.flow,prior62.engine,prior62.primitive,prior62.base60
PROFILE=REPO/'experiments/native-wifi-qca9377-filter64-native-v1';CHECKED=PROFILE/'runs/checked-candidate'
REPORT='37bde7009088c6a783940f642b3dfddbbe2fdeabea671fa17d7f498234f45866';PAYLOAD='d40efd8c0b08a9289f0caaa64d931519a253559c53ef732af8961ed91ad49965';REPRODUCTION='dc442f8d666ef387a651efdabd7f0db807643ce4910f222cba85b27ff32e647e';NATIVE_REPORT='1689fc687e78f23c752be7dd35a8b14e8c8ea6fa3e4f24ec7cabe3ac58bac86c'
WORLD=prior62.WORLD;SEMANTIC=prior62.SEMANTIC
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def safe(name):
 p=Path(name);need(not p.is_absolute() and '..' not in p.parts,'unsafe proof path');return p

def gates(directory,payload,world):
 directory=Path(directory)
 need(all(len(h)==64 for h in (REPORT,PAYLOAD,REPRODUCTION,NATIVE_REPORT)),'candidate64 not frozen/reviewed')
 need(directory.resolve()==CHECKED.resolve(),'exact64 candidate directory')
 need(sha(directory/'report.json')==REPORT and flow.sha(payload)==PAYLOAD and flow.sha(world)==WORLD,'frozen64 report/payload/world19')
 r=flow.read_json(directory/'report.json');rep=flow.read_json(directory/'reproduction.json',8*1024*1024)
 need(r['status']=='FILTER64-REPEATED-EFI-QEMU-WORLD19-DIAGNOSTIC-PASS' and r['native_counter']==64 and r['build_host']=='yukabox','actual64 host/generation')
 need(len(payload)==r['payload_bytes']<=262144 and r['mapped_bytes']<=4194304,'immutable whole EFI mapped cap')
 pe=struct.unpack_from('<I',payload,60)[0]
 need(payload[:2]==b'MZ' and payload[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<I',payload,pe+80)[0]==r['mapped_bytes'],'actual PE mapped size')
 need(sha(directory/'reproduction.json')==r['reproduction_sha256']==REPRODUCTION and rep['inputs']==r['source_sha256'] and rep['generated_compiler_sources_sha256']==r['generated_compiler_sources_sha256'] and rep['payload_sha256']==PAYLOAD and rep['public_world_package_sha256']==WORLD and rep['dummy_fixture_signing_only'] is True and rep['owner_private_key_loads']==0,'three builds/current public world closure')
 need(len(r['source_sha256'])==470 and len(r['generated_compiler_sources_sha256'])==207,'complete source/compiler closure')
 for n,h in r['source_sha256'].items():need(sha(REPO/safe(n))==h,'source changed '+n)
 for n,h in r['generated_compiler_sources_sha256'].items():need(sha(directory/safe(n))==h,'compiler input changed '+n)
 np=PROFILE/'runs/native-host/report.json';n=flow.read_json(np)
 need(sha(np)==r['native_report_sha256']==NATIVE_REPORT and n['status']=='FILTER64-ACTUAL-PRODUCER-SYNTHETIC-ASAN-COFF-PASS' and n['scenarios']==18 and n['handover_checks']==92 and n['actual_driver_poll'] is True and n['actual_native_entrypoints'] is True and n['authenticated_firmware_ie6'] is True and sha(np.parent/'host.log')==n['host_log_sha256'],'actual native ASAN/COFF producers')
 need(len(n['compiled_fixture_sources_sha256'])==161 and n['sanitizers']==['address','undefined'] and n['actual_native_PCI_CE_DMA_model'] is True and n['ready_before_dma_credit_ordering'] is True and n['actual_raw_union_export_preserves_trailers'] is True and n['actual_TX_handover'] is True,'actual model/fixture closure')
 need(len(n['coff_objects_sha256'])==15,'complete COFF coverage')
 for name,h in n['coff_objects_sha256'].items():need(sha(np.parent/safe(name))==h,'COFF object changed '+name)
 for key,name in (('native','test'),('handover','handover-test')):need(sha(np.parent/name)==n['test_executables_sha256'][key],'actual sanitizer executable changed '+name)
 for name,h in n['compiled_fixture_sources_sha256'].items():need(sha(np.parent/safe(name))==h,'native fixture changed '+name)
 for name,h in n['source_sha256'].items():need(r['source_sha256'].get(name)==h,'native sources joined whole closure '+name)
 for sub,empty in (('actors-qemu',False),('actors-empty-boot-qemu',True)):
  q=flow.read_json(directory/sub/'report.json')
  need(q in r['gates'] and q['empty_boot'] is empty and q['payload_sha256']==PAYLOAD and q['status']=='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS' and sha(directory/sub/'observed.log')==q['observed_log_sha256'],'normal/EMPTY actual whole EFI QEMU')
 h=r['host_checks'];need(h['sanitizers'] is True and h['roof_cat_timing'] is True and h['host_ticks']==120 and h['adversarial_camera_frames']==16 and sha(directory/'world19-source.json')==r['world_source_sha256'],'current city/cat timing')
 for proof in (r,n):
  for k in ('physical_verified','htt_dataplane_ready','credentials','association','wifi_connected'):need(proof[k] is False,'partial scan scope '+k)
  need(proof['scan'] is True and proof['raw_slots']==22 and proof['raw_pages']==110 and proof['device_operations']==0,'exact passive diagnostic scope')
 need(r['signing_admitted'] is False and r['passive_flags']==33 and r['channel_count']==13 and r['target_ssid_hex']=='6950686f6e6520283929' and r['rx_ring_cfg'] is False and r['aggregation_setup'] is False,'unsigned partial passive proof only')
 need(sha(np.parent/'handover_test.c')==sha(PROFILE/'handover_test.c'),'actual handover fixture matches source closure')
 need(r['partial_startup_no_rx_ring_no_aggregation'] is True and r['owner_private_key_loads']==0 and r['radio_backend']=='MOCK USB ONLY','whole software boundary')
 need(n['partial_startup_no_rx_ring_no_aggregation'] is True and n['private_key_loads']==0 and n['physical_admission'] is False,'partial startup software only')
 join_path=PROFILE/'evidence/2026-10-09/timing-production-join.json'
 need(sha(join_path)=='27eb67e3877b80c70e58c41f9aa9dd1d723151b5cb2038058eb669fda8b0a4df','timing production join changed')
 j=flow.read_json(join_path);component=REPO/'experiments/native-wifi-qca9377-filter64-barrier-v1';cp=component/'evidence/2026-10-09/report.json'
 need(j['status']=='FILTER64-TIMING-PRODUCTION-PROOF-JOIN-PASS' and j['candidate_report_sha256']==REPORT and j['native_report_sha256']==NATIVE_REPORT and j['reproduction_sha256']==REPRODUCTION and j['payload_sha256']==PAYLOAD,'exact timing/wholeproducer join')
 need(j['native_abi_sha256']==sha(PROFILE/'native-abi.json') and j['timing_component_report_sha256']==sha(cp)=='621c0470b158508b0305d521f20f8d536ce82e040aac3bcbfd5e1fc5e94911e8','timing component and ABI')
 c=flow.read_json(cp)
 need(c['status']=='FILTER64-STAGE3-ECHO3-OVERALL12-UNCHANGED-TX2-ASAN-COFF-PASS' and c['physical'] is False and c['device_operations']==0,'component software-only boundaries')
 for name,h in c['source_sha256'].items():need(sha(component/safe(name))==h,'timing component source changed '+name)
 need(sha(component/'runs/proof/host.log')==c['host_log_sha256'],'timing actual sanitizer log changed')
 for name,h in c['coff_objects_sha256'].items():need(sha(component/'runs/proof'/safe(name))==h,'timing COFF changed '+name)
 for name,h in j['protected63_byte_equality'].items():need(sha(directory/name)==h and (directory/name).read_bytes()==(prior62.CHECKED/name).read_bytes(),'protected63 producer input changed '+name)
 need(j['budgets_us']=={'per_command_stage':3000000,'echo_from_actual_post':3000000,'overall':12000000,'unchanged_TX':2000000} and n['slowpoll_actual_producer'] is True and n['missing_third_DMA_rejected'] is True and n['scenario_ids']==j['native_scenario_pairs'],'real slowpoll/missingDMA regression and exact budgets')
 policy=flow.read_json(PROFILE/'receiver-policy.json')
 need(sha(PROFILE/'receiver-policy.json')==r['receiver_policy_sha256'] and policy==r['receiver_policy'] and policy=={**flow.read_json(base60.PROFILE/'receiver-policy.json'),'generation':64},'same authenticated firmware/gen64')
 for name in ('driver.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c'):
  need((directory/name).read_bytes()==(prior62.CHECKED/name).read_bytes(),'protected transport changed '+name)
 return {'report_sha256':REPORT,'payload_sha256':PAYLOAD,'profile_status':r['status'],'receiver_policy':policy,'native_counter':64,'world_package_sha256':WORLD,'source_model_verified':True}
