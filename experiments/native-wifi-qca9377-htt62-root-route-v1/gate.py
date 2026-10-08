"""Exact62 public technical gate. No key, radio, state mutation or compilation."""
from pathlib import Path
import importlib.util,sys,json,hashlib,struct
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
# Load reviewed prior61 under a unique identity. Its legacy dependencies keep
# their own globals, but never replace a caller's generic gate/launch/route.
def _prior61():
 paths=list(sys.path);saved={n:sys.modules.get(n) for n in ('launch','transition59','assets','route')}
 try:
  for n in saved:sys.modules.pop(n,None)
  folder=REPO/'experiments/native-wifi-qca9377-scan61-root-route-v1'
  sys.path.insert(0,str(folder));spec=importlib.util.spec_from_file_location('_htt62_frozen_prior61_gate',folder/'gate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 finally:
  sys.path[:]=paths
  for n,v in saved.items():
   if v is None:sys.modules.pop(n,None)
   else:sys.modules[n]=v
prior61=_prior61();base60=prior61.base60
flow,engine,primitive=prior61.flow,prior61.engine,prior61.primitive
PROFILE=REPO/'experiments/native-wifi-qca9377-htt62-native-v1';CHECKED=PROFILE/'runs/checked-candidate'
REPORT='9345001639d4eda7d224a8b5d2a7571324ee481f7f3e4c14b33df7f4e8ae46ce'
PAYLOAD='22cde47acd97eec959522b720ebfb6b28fefd2581a32f790fe1f85f2a29d2b81'
WORLD=prior61.WORLD;SEMANTIC=prior61.SEMANTIC
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def safe(n):
 p=Path(n);need(not p.is_absolute() and '..' not in p.parts,'unsafe proof path');return p

def gates(directory,payload,world):
 directory=Path(directory);need(directory.resolve()==CHECKED.resolve(),'exact62 candidate directory')
 need(sha(directory/'report.json')==REPORT and flow.sha(payload)==PAYLOAD and flow.sha(world)==WORLD,'frozen62 report/payload/world19')
 r=flow.read_json(directory/'report.json');rep=flow.read_json(directory/'reproduction.json',8*1024*1024)
 need(r['status']=='HTT62-REPEATED-EFI-QEMU-WORLD19-DIAGNOSTIC-PASS' and r['native_counter']==62 and r['build_host']=='yukabox','actual62 host/generation')
 need(len(payload)==r['payload_bytes']==173568 and r['mapped_bytes']==4132864<=4194304,'whole EFI file/mapped caps')
 pe=struct.unpack_from('<I',payload,60)[0];need(payload[:2]==b'MZ' and payload[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<I',payload,pe+80)[0]==r['mapped_bytes'],'actual PE mapped size')
 need(sha(directory/'reproduction.json')==r['reproduction_sha256']=='36f23cac19bf35fa46d859d12824986ce67f29ef6a797be0e220ef48ea1f21f4' and rep['status']=='HTT62-THREE-BUILDS-IDENTICAL' and rep['inputs']==r['source_sha256'] and rep['generated_compiler_sources_sha256']==r['generated_compiler_sources_sha256'] and rep['payload_sha256']==PAYLOAD and rep['public_world_package_sha256']==WORLD and rep['dummy_fixture_signing_only'] is True and rep['owner_private_key_loads']==0,'three identical builds/current public world')
 need(len(r['source_sha256'])==433 and len(r['generated_compiler_sources_sha256'])==176,'complete source/compiled closure counts')
 for n,h in r['source_sha256'].items():need(sha(REPO/safe(n))==h,'source changed '+n)
 for n,h in r['generated_compiler_sources_sha256'].items():need(sha(directory/safe(n))==h,'generated source changed '+n)
 npath=PROFILE/'runs/native-host/report.json';n=flow.read_json(npath)
 need(sha(npath)==r['native_report_sha256']=='21d120ee9a4cf9702574cf71591c988f8729975dda0d90295fc731b0a0602c99' and n['status']=='HTT62-ACTUAL-PRODUCTION-AUTHENTICATED-IE6-VERSION-RAW-ASAN-COFF-PASS' and n['scenarios']==24 and n['actual_driver_poll'] is True and n['actual_native_entrypoints'] is True and n['authenticated_firmware_ie6'] is True and sha(npath.parent/'host.log')==n['host_log_sha256'],'actual24 native ASAN/COFF models')
 need(len(n['compiled_fixture_sources_sha256'])==130,'complete native fixture closure')
 for name,h in n['compiled_fixture_sources_sha256'].items():need(sha(npath.parent/safe(name))==h,'native fixture changed '+name)
 for name,h in n['source_sha256'].items():need(r['source_sha256'].get(name)==h,'native sources joined whole closure '+name)
 for sub,empty in (('actors-qemu',False),('actors-empty-boot-qemu',True)):
  q=flow.read_json(directory/sub/'report.json');need(q in r['gates'] and q['empty_boot'] is empty and q['payload_sha256']==PAYLOAD and q['status']=='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS' and sha(directory/sub/'observed.log')==q['observed_log_sha256'],'actual normal/EMPTY whole EFI QEMU')
 h=r['host_checks'];need(h['sanitizers'] is True and h['roof_cat_timing'] is True and h['host_ticks']==120 and h['adversarial_camera_frames']==16 and sha(directory/'world19-source.json')==r['world_source_sha256'],'current city/cat ASAN/timing')
 for key,value in {'MAIN_bytes':727128,'BMI_DONE_commands':1,'WMI_INIT_commands':1,'WMI_READY_required_before_success':True,'scan':False,'request_is_rf':False,'duplicate_HTT_CONNECT':False,'bootstrap_deadline_us':5400000000,'bounded_us':3000000,'raw_slots':6,'raw_pages':30,'authenticated_firmware_ie6':True,'htt_dataplane_ready':False,'physical_verified':False,'signing_admitted':False,'owner_private_key_loads':0,'device_operations':0,'wifi_connected':False,'radio_backend':'MOCK USB ONLY'}.items():need(r[key]==value,'exact diagnostic scope '+key)
 for key in ('request_is_rf','duplicate_HTT_CONNECT','physical_verified','physical_admission','htt_dataplane_ready','scan','credentials','association','wifi_connected'):need(n[key] is False,'native model scope '+key)
 policy=flow.read_json(PROFILE/'receiver-policy.json');need(sha(PROFILE/'receiver-policy.json')==r['receiver_policy_sha256'] and policy==r['receiver_policy'] and policy=={**flow.read_json(base60.PROFILE/'receiver-policy.json'),'generation':62},'same authenticated exact firmware/gen62')
 # Protected USB/HCI/resident production logic must remain exact frozen60/61.
 for name in ('driver.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c'):
  need((directory/name).read_bytes()==(prior61.CHECKED/name).read_bytes(),'protected transport changed '+name)
 return {'report_sha256':REPORT,'payload_sha256':PAYLOAD,'profile_status':r['status'],'receiver_policy':policy,'native_counter':62,'world_package_sha256':WORLD,'source_model_verified':True}
