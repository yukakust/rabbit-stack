"""Pinned public-only host62 gate. Import never starts a manager or reads state/key.
Independent from Root gate.py so parallel admission preparation is import-safe.
"""
from pathlib import Path
import hashlib,json,importlib.util
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
NATIVE=REPO/'experiments/native-wifi-qca9377-htt62-native-v1/runs/checked-candidate'
REPORT='9345001639d4eda7d224a8b5d2a7571324ee481f7f3e4c14b33df7f4e8ae46ce'
PAYLOAD='22cde47acd97eec959522b720ebfb6b28fefd2581a32f790fe1f85f2a29d2b81'
WORLD='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7'
PINS={
'native-wifi-qca9377-htt62-staging-observer-v1':{'proof':'2399bb303f37225ca7cc5eea13d5ec39913ce7fd3d0372f97c212e94d8f4e2db','binding':'1423d8d13421713d1e6e005c8b0714d0fa61055a6c72578b5bc495ef9a9e1aa3','exe':'63a3a16c4a42ffb76f519a1f2199b7b3c84f2145d7eaf20721d148b99792395b','test':'79630518b0e0c757e3c501f6b01c3d91dd344ec5be87b59080e8d06ea643e3b0','status':'HOST-OBJC-HTT62-STAGING-QWBT-CALLBACKS-PREFLIGHT-PASS'},
'native-wifi-qca9377-htt62-observer-v2':{'proof':'ece549b036cc55e2c29cd66ae1ad16843b93e005308126145235f92be0822ce4','binding':'50d6cdd5ef8d2f2520b0b38ad14b9935975503b0c46c014e94ec97591181ab61','exe':'1ff8a6a94d855aad44a6f336dd29e89e8a7791c5676a63cb3922dfe7db1b0794','test':'f1d8294531ecf6acb8cd6e2a9767f86eac0f76fa9d629f8ade6cc820e18bedfe','status':'OFFLINE-HTT62-OBSERVER-RAW-VERSION-IE6-CALLBACK-PREFLIGHT-PASS'}}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(value,message):
 if not value:raise ValueError(message)
def safe(name):
 p=Path(name);need(not p.is_absolute() and '..' not in p.parts,'unsafe relative source');return p
def load_module(name,path):
 spec=importlib.util.spec_from_file_location('_htt62_public_gate_'+name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def hash_input(name,h,scope):
 p=Path(name)
 if not p.is_absolute():p=REPO/safe(name) if name.startswith('experiments/') else scope/safe(name)
 need(p.resolve().is_relative_to(REPO.resolve()),'compiler/source path outside repository');need(sha(p)==h,'changed input '+name)
def helper_metadata(r,pin,staging):
 need(r['status']==pin['status'] and r['bluetooth_manager_started'] is False and r['private_key_loads']==0,'host offline status')
 if staging:
  for k in ('physical_trial','signature_verified','native_source_changes','native_generation_verified','readiness_verified','resource_release_verified'):need(r[k] is False,'staging false proof '+k)
  need(r['callback_checks']==41 and r['python_checks']==216 and r['signatures_created']==0 and r['DATA_cap']==240 and r['timer_intervals_unchanged'] and r['QFS_write_ACK_checkpoint_methods_byte_identical'] and r['existing_prefix_log_alias_tested'],'exact staging mechanics')
 else:need(r['python_checks']==451 and r['host_result']=='PASS 175 HOST HTT62 callback cases; NO MANAGER/WRITES' and r['writes']==0 and r['physical_admission'] is False and r['association'] is False and r['IP'] is False and r['actual_APPLIED62']=='PENDING ROOT','observer offline scope')
def checked():
 need(sha(NATIVE/'report.json')==REPORT and sha(NATIVE/'payload.efi')==PAYLOAD,'exact unsigned candidate62')
 nr=json.loads((NATIVE/'report.json').read_text());need(nr['native_counter']==62 and nr['world_package_sha256']==WORLD,'candidate/world19')
 for n in ('profile_gatt.c','init_probe.c','boot_gatt.c','firmware_op.c','version.c','htt_native.c'):need(sha(NATIVE/n)==nr['generated_compiler_sources_sha256'][n],'native generated ABI changed')
 result={}
 for name,pin in PINS.items():
  scope=REPO/'experiments'/name;staging='staging' in name
  need(sha(scope/'evidence/host-proof.json')==pin['proof'] and sha(scope/'evidence/bindings.json')==pin['binding'],'pinned host proof/binding changed '+name)
  r=json.loads((scope/'evidence/host-proof.json').read_text());b=json.loads((scope/'evidence/bindings.json').read_text());helper_metadata(r,pin,staging)
  need(b['physical_admission'] is False and b['actual_APPLIED62']=='PENDING ROOT' and b['native_candidate_report_sha256']==REPORT and b['native_payload_sha256']==PAYLOAD and b['native_boot_gatt_sha256']==sha(NATIVE/'boot_gatt.c'),'public host binding')
  for n,h in b['source_sha256'].items():need(sha(scope/safe(n))==h,'changed frozen helper source')
  for n,h in r['source_sha256'].items():hash_input(n,h,scope)
  for section in ('compiler_input_sha256','test_input_sha256'):
   for n,h in r.get(section,{}).items():hash_input(n,h,scope)
  if staging:
   cr=r['compile_report'];need(cr['bluetooth_manager_started'] is False and cr['private_key_loads']==0 and cr['signatures_created']==0,'staging compile only')
   for n,h in cr['source_sha256'].items():hash_input(n,h,scope)
   exe=scope/'runs/control/sender';need(Path(cr['executable_path']).resolve()==exe.resolve() and cr['executable_sha256']==pin['exe'] and r['host_test_executable_sha256']==pin['test'],'exact compiled staging path')
   log=scope/'evidence/callbacks.log';lh=r['callback_log_sha256']
   baseline=REPO/'experiments/native-wifi-qca9377-scan61-staging-observer-v1/sender.m';need((scope/'sender.m').read_text()==baseline.read_text().replace('generation!=61','generation!=62'),'sender diff only generation guard')
  else:
   exe=scope/'runs/control/read-htt62';need(Path(r['reader_path']).resolve()==exe.resolve() and r['reader_executable_sha256']==pin['exe'],'exact compiled reader path');log=scope/'evidence/host.log';lh=r['host_log_sha256']
   binding=load_module('native_binding',scope/'native_binding.py').check();need(binding==r['native_binding'],'native UUID/status field join differs')
   decoder=load_module('decode_htt',scope/'decode_htt.py');container=scope/'runs/public-fixture/firmware-6.bin';need(sha(container)==r['public_firmware_fixture_sha256']=='8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01','exact public IE6 container');f=decoder.firmware(container.read_bytes());need(f['htt_op']==3 and f['main_bytes']==727125 and f['main_sha256']==decoder.MAIN,'actual IE6 authenticated op/MAIN')
  need(sha(exe)==pin['exe'] and sha(scope/'runs/control/host-test')==pin['test'] and sha(log)==lh,'host executable/test/log changed')
  need(Path(b['executable_path']).resolve()==exe.resolve() and b['executable_sha256']==pin['exe'],'frozen executable binding')
  result[name]=str(exe)
 return result
if __name__=='__main__':print(json.dumps({'status':'ROOT-HTT62-PINNED-HOST-NATIVE-ABI-IE6-GATE-PASS','helpers':checked(),'physical_admission':False,'device_operations':0,'key_accesses':0},indent=2))
