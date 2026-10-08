"""Exact63 public technical gate; separate Root admission required; no keys or device APIs."""
from pathlib import Path
import hashlib,struct,json
import transition62
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
prior62=transition62.prior().gate
flow,engine,primitive,base60=prior62.flow,prior62.engine,prior62.primitive,prior62.base60
PROFILE=REPO/'experiments/native-wifi-qca9377-filter63-native-v1';CHECKED=PROFILE/'runs/checked-candidate'
REPORT='ba46f2c04021b71744a45a0fc31769d93629062422b8a6fbf878e66d8767fe37';PAYLOAD='a636b40f10103a90879bad00a55de173fa36ab2b7a4fd4f38262825191bf4442';REPRODUCTION='931d3174122b73cc60a4856c5a165273e951528a684fd3ddf9e1dd7a4f08f4f0';NATIVE_REPORT='ca983db6fb2e9723a0f4371442307c2f3684cf5244fc6a22e1008167c9e543cc'
WORLD=prior62.WORLD;SEMANTIC=prior62.SEMANTIC
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def safe(name):
 p=Path(name);need(not p.is_absolute() and '..' not in p.parts,'unsafe proof path');return p

def gates(directory,payload,world):
 directory=Path(directory)
 need(all(len(h)==64 for h in (REPORT,PAYLOAD,REPRODUCTION,NATIVE_REPORT)),'candidate63 not frozen/reviewed')
 need(directory.resolve()==CHECKED.resolve(),'exact63 candidate directory')
 need(sha(directory/'report.json')==REPORT and flow.sha(payload)==PAYLOAD and flow.sha(world)==WORLD,'frozen63 report/payload/world19')
 r=flow.read_json(directory/'report.json');rep=flow.read_json(directory/'reproduction.json',8*1024*1024)
 need(r['status']=='FILTER63-REPEATED-EFI-QEMU-WORLD19-DIAGNOSTIC-PASS' and r['native_counter']==63 and r['build_host']=='yukabox','actual63 host/generation')
 need(len(payload)==r['payload_bytes']==202240 and r['mapped_bytes']==4194304,'immutable whole EFI mapped cap')
 pe=struct.unpack_from('<I',payload,60)[0]
 need(payload[:2]==b'MZ' and payload[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<I',payload,pe+80)[0]==r['mapped_bytes'],'actual PE mapped size')
 need(sha(directory/'reproduction.json')==r['reproduction_sha256']==REPRODUCTION and rep['inputs']==r['source_sha256'] and rep['generated_compiler_sources_sha256']==r['generated_compiler_sources_sha256'] and rep['payload_sha256']==PAYLOAD and rep['public_world_package_sha256']==WORLD and rep['dummy_fixture_signing_only'] is True and rep['owner_private_key_loads']==0,'three builds/current public world closure')
 need(len(r['source_sha256'])==473 and len(r['generated_compiler_sources_sha256'])==207,'complete source/compiler closure')
 for n,h in r['source_sha256'].items():need(sha(REPO/safe(n))==h,'source changed '+n)
 for n,h in r['generated_compiler_sources_sha256'].items():need(sha(directory/safe(n))==h,'compiler input changed '+n)
 np=PROFILE/'runs/native-host/report.json';n=flow.read_json(np)
 need(sha(np)==r['native_report_sha256']==NATIVE_REPORT and n['status']=='FILTER63-ACTUAL-PRODUCER-SYNTHETIC-ASAN-COFF-PASS' and n['scenarios']==16 and n['handover_checks']==92 and n['actual_driver_poll'] is True and n['actual_native_entrypoints'] is True and n['authenticated_firmware_ie6'] is True and sha(np.parent/'host.log')==n['host_log_sha256'],'actual native ASAN/COFF producers')
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
 policy=flow.read_json(PROFILE/'receiver-policy.json')
 need(sha(PROFILE/'receiver-policy.json')==r['receiver_policy_sha256'] and policy==r['receiver_policy'] and policy=={**flow.read_json(base60.PROFILE/'receiver-policy.json'),'generation':63},'same authenticated firmware/gen63')
 for name in ('driver.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c'):
  need((directory/name).read_bytes()==(prior62.CHECKED/name).read_bytes(),'protected transport changed '+name)
 return {'report_sha256':REPORT,'payload_sha256':PAYLOAD,'profile_status':r['status'],'receiver_policy':policy,'native_counter':63,'world_package_sha256':WORLD,'source_model_verified':True}
