"""Exact frozen host/native63 proof. No state/private key/manager/compile APIs."""
from pathlib import Path
import hashlib,json,importlib.util
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
NATIVE=REPO/'experiments/native-wifi-qca9377-filter63-native-v1';CHECKED=NATIVE/'runs/checked-candidate'
PINS={'generation':63,'report_sha256':'ba46f2c04021b71744a45a0fc31769d93629062422b8a6fbf878e66d8767fe37','payload_sha256':'a636b40f10103a90879bad00a55de173fa36ab2b7a4fd4f38262825191bf4442'}
ABI='527f0337d41ee5167cbed8ef0510afefce128910a356b38e42be2ed2a8b3de0d'
HELPERS={
'native-wifi-qca9377-filter63-staging-observer-v1':('92321053ff59e9a52a6c166a3a2ea3e720107484007f04df39f55ba0cadf0a7d','61b647a58de8f5c41c7d3e0fd5a2ff7986901ea8efc7994e4ee13947244cfc2c','sender','64ee8eaebeafcccf4547e5b775f1b47626d8a2e8e88d3012af5f911448cfc72d','d58cbcdf5e00f5047acb5d84aaefc12d58cf6f680e18f9fae85dbbc32f9c3819'),
'native-wifi-qca9377-filter63-progress-monitor-v2':('ce28833b48b060489c2da1114de1122dca98797d165d0e56f3fe6a078de36c29','3925f22dd9e5fde7f91fc2fae957a50533b8f9270ca5c7c1ae8a33cc0be94ec0','collector','2390cc9887e64f53a7d86a645261f42e6fae20b0478f465efad2dbbdd9eca99a','fba2dd596a51bde37e115272fc0e7753d16bf0da4ca1682ba81b8c3641af0607'),
'native-wifi-qca9377-filter63-observer-v2':('fdbb11cd24e3a3bf399538e569a592f6295d25a8d9cbfabfb33506c608b1ba26','8e096a11163926d815b2104088ef4ae318ce2959490604ae801dc8c0b72ea9d7','read-filter63','fb701c5476ff5ddc3ec408c1f06872f1fbf1e4937b495ba7fbe8746d09057b9d','20e51d1d500da2c9a3c5d2cdd63df03cb1844666dc556b884a141eca358c7c4b')}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def safe(n):
 p=Path(n);need(not p.is_absolute() and '..' not in p.parts,'unsafe relative path');return p
def load(name,path):
 spec=importlib.util.spec_from_file_location('_root63_host_'+name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def input_hash(n,h,scope):
 p=Path(n)
 if not p.is_absolute():p=REPO/safe(n) if n.startswith('experiments/') else scope/safe(n)
 need(p.resolve().is_relative_to(REPO.resolve()),'external source/input path');need(sha(p)==h,'changed source/input '+n)
def checked():
 need(sha(CHECKED/'report.json')==PINS['report_sha256'] and sha(CHECKED/'payload.efi')==PINS['payload_sha256'] and sha(NATIVE/'native-abi.json')==ABI,'frozen63 candidate/nativeABI')
 r=json.loads((CHECKED/'report.json').read_text());need(r['status']=='FILTER63-REPEATED-EFI-QEMU-WORLD19-DIAGNOSTIC-PASS' and r['native_counter']==63 and r['world_package_sha256']=='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7','exact native63/world19')
 for n,h in r['source_sha256'].items():need(sha(REPO/safe(n))==h,'frozen source changed '+n)
 for n,h in r['generated_compiler_sources_sha256'].items():need(sha(CHECKED/safe(n))==h,'generated compiler input changed '+n)
 result={}
 for name,(proof,binding,exe_name,exe_hash,test_hash) in HELPERS.items():
  scope=REPO/'experiments'/name;need(sha(scope/'evidence/host-proof.json')==proof and sha(scope/'evidence/bindings.json')==binding,'pinned host proof/binding changed '+name);p=json.loads((scope/'evidence/host-proof.json').read_text());b=json.loads((scope/'evidence/bindings.json').read_text());need(p['bluetooth_manager_started'] is False and p['private_key_loads']==0 and b['physical_admission'] is False and b['actual_APPLIED63']=='PENDING ROOT' and b['native_report_sha256']==PINS['report_sha256'] and b['native_payload_sha256']==PINS['payload_sha256'] and b['native_abi_sha256']==ABI,'offline/native binding')
  for n,h in b['source_sha256'].items():need(sha(scope/safe(n))==h,'frozen helper source changed')
  for section in ('source_sha256','compiler_input_sha256','test_input_sha256','test_inputs'):
   for n,h in p.get(section,{}).items():input_hash(n,h,scope)
  exe=scope/'runs/control'/exe_name;need(sha(exe)==exe_hash and sha(scope/'runs/control/host-test')==test_hash and Path(b['executable']).resolve()==exe.resolve() and b['executable_sha256']==exe_hash,'exact executable/test binding')
  if 'staging' in name:
   need(p['status']=='HOST-OBJC-FILTER63-STAGING-QWBT-CALLBACKS-PREFLIGHT-PASS' and p['callback_checks']==41 and p['python_checks']==216 and p['DATA_cap']==240 and p['timer_intervals_unchanged'] and p['QFS_write_ACK_checkpoint_methods_byte_identical'] and p['existing_prefix_log_alias_tested'] and p['resource_release_verified'] is False and p['readiness_verified'] is False and p['signatures_created']==0,'exact QFS staging')
   need((scope/'sender.m').read_text()==(REPO/'experiments/native-wifi-qca9377-htt62-staging-observer-v1/sender.m').read_text().replace('generation!=62','generation!=63'),'staging diff only generation guard')
   cr=p['compile_report'];need(Path(cr['executable_path']).resolve()==exe.resolve() and cr['executable_sha256']==exe_hash and p['host_test_executable_sha256']==test_hash,'compile manifest identity')
   for n,h in cr['source_sha256'].items():input_hash(n,h,scope)
   need(sha(scope/'evidence/callbacks.log')==p['callback_log_sha256'],'fakecallback log')
  else:
   need(p['native_binding_frozen'] is True and p['writes']==0 and sha(scope/'evidence/host.log')==p['host_log_sha256'],'frozen native join/log/write0')
   m=load(name,scope/'native_binding.py');need(m.check(PINS)==p['native_binding'],'actual native field/GATT/source join changed')
   if 'progress' in name:
    need(p['host_result']=='PASS 100 HOST progress collector cases; NO REAL MANAGER/WRITE' and p['wrong_ABI_negatives']==3 and p['actual_final_JSON_checks']==4 and p['raw_read_requires_release14'] and p['test_executable_sha256']==test_hash and p['executable_sha256']==exe_hash and Path(p['executable']).resolve()==exe.resolve(),'release-only monitor semantics')
   else:need(p['status']=='OFFLINE-FILTER63-FROZEN-NATIVE-RAW-FORENSIC-CALLBACK-PREFLIGHT-PASS' and p['python_checks']==1189 and p['host_result']=='PASS 511 HOST FILTER63 callback cases; NO MANAGER/WRITES' and p['physical_admission'] is False and p['test_executable_sha256']==test_hash and p['reader_executable_sha256']==exe_hash and Path(p['reader_path']).resolve()==exe.resolve(),'raw forensic reader scope')
  if 'observer-v2' in name:
   need(p['actual_C_producer_oracle_report_sha256']=='535a1dc3898d2f6f2d615f3aec1804b62ff5ca641ebbba49c76196f9a626e4d3' and len(p['actual_C_producer_cases'])==3,'real C producer semantic join')
   oracle=REPO/'experiments/native-wifi-qca9377-native63-host-oracle-v1/evidence/2026-10-08';need(sha(oracle/'report.json')==p['actual_C_producer_oracle_report_sha256'],'actual C oracle changed')
   for case in p['actual_C_producer_cases']:need(sha(oracle/f"capture-scan0-filter{case['case']}.json")==case['capture_sha256'] and case['physical'] is False and case['decoded_pipeline_completed']==case['target_observed']==(case['case']!=2),'producer bytes/positive/failure semantics')
  result[name]=str(exe)
 return result
if __name__=='__main__':print(json.dumps({'status':'ROOT63-FROZEN-HOST-SOURCE-COMPILER-NATIVE-ABI-GATE-PASS','helpers':checked(),'physical_admission':False,'device_operations':0},indent=2))
