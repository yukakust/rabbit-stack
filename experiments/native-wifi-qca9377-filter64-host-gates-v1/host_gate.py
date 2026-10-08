"""Exact frozen host/native63 proof. No state/private key/manager/compile APIs."""
from pathlib import Path
import hashlib,json,importlib.util
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
NATIVE=REPO/'experiments/native-wifi-qca9377-filter64-native-v1';CHECKED=NATIVE/'runs/checked-candidate'
PINS={'generation':64,'report_sha256':'37bde7009088c6a783940f642b3dfddbbe2fdeabea671fa17d7f498234f45866','payload_sha256':'d40efd8c0b08a9289f0caaa64d931519a253559c53ef732af8961ed91ad49965'}
ABI='3ce199a281689be068afc306c5b01c973787c028db006a27330a8fb3fdf44c94'
HELPERS={
'native-wifi-qca9377-filter64-staging-observer-v1':('efce3f5c1b46b8825f64ddfdf7983136d9d8c9b6212ae68a4a27f50395600f78','939c46ded5ae09c836a90e15769277c0517bfdb177088f626f894a8ecdee1cc7','sender','ab8daeed82768bd6163097a2cde54b0839948153edbcfde2482c49271fead5c6','964515f22152e68fe192dc0f047213f7130383341cbe44b0c5c4ce7764b4bba4'),
'native-wifi-qca9377-filter64-progress-monitor-v1':('64c13345a3eaf8f7b84810a1afa62b2ca0b03e76a64d40acfabc6db33dcf2f3f','03a541168e7cd85261d31a5b5a76690d5c7a153c6eae73b01ddb29f77370f3f1','collector','67ef3c8f8c52b3dabb21b5887203cc58da939ba45d3aec86793b19e53733f391','ceea5928d7a93f2df460715471e5b0c053fa3cf40dc42048b1799a53936f9941'),
'native-wifi-qca9377-filter64-observer-v1':('43dc726bad1b610bad373c8f1b06d3e8aba56b12b214bfc7bb3c8e261dd21510','28e42b3e286271088c4f46354406ee1591526b36250418e1fd3d939a8b43fca8','read-filter64','f988f256243e49e0e7850a55982c814fa1113a3049e6e2ef800905118c5ccfb0','c393293f30e3d4585fa09b42733f0388fe8258acdab4d2961508ead1a3e60f65')}
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
 r=json.loads((CHECKED/'report.json').read_text());need(r['status']=='FILTER64-REPEATED-EFI-QEMU-WORLD19-DIAGNOSTIC-PASS' and r['native_counter']==64 and r['world_package_sha256']=='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7','exact native63/world19')
 for n,h in r['source_sha256'].items():need(sha(REPO/safe(n))==h,'frozen source changed '+n)
 for n,h in r['generated_compiler_sources_sha256'].items():need(sha(CHECKED/safe(n))==h,'generated compiler input changed '+n)
 result={}
 for name,(proof,binding,exe_name,exe_hash,test_hash) in HELPERS.items():
  scope=REPO/'experiments'/name;need(sha(scope/'evidence/host-proof.json')==proof and sha(scope/'evidence/bindings.json')==binding,'pinned host proof/binding changed '+name);p=json.loads((scope/'evidence/host-proof.json').read_text());b=json.loads((scope/'evidence/bindings.json').read_text());need(p['bluetooth_manager_started'] is False and p['private_key_loads']==0 and b['physical_admission'] is False and b['actual_APPLIED64']=='PENDING ROOT' and b['native_report_sha256']==PINS['report_sha256'] and b['native_payload_sha256']==PINS['payload_sha256'] and b['native_abi_sha256']==ABI,'offline/native binding')
  for n,h in b['source_sha256'].items():need(sha(scope/safe(n))==h,'frozen helper source changed')
  for section in ('source_sha256','compiler_input_sha256','test_input_sha256','test_inputs'):
   for n,h in p.get(section,{}).items():input_hash(n,h,scope)
  exe=scope/'runs/control'/exe_name;need(sha(exe)==exe_hash and sha(scope/'runs/control/host-test')==test_hash and Path(b['executable']).resolve()==exe.resolve() and b['executable_sha256']==exe_hash,'exact executable/test binding')
  if 'staging' in name:
   need(p['status']=='HOST-OBJC-FILTER64-STAGING-QWBT-CALLBACKS-PREFLIGHT-PASS' and p['callback_checks']==41 and p['python_checks']==216 and p['DATA_cap']==240 and p['timer_intervals_unchanged'] and p['QFS_write_ACK_checkpoint_methods_byte_identical'] and p['existing_prefix_log_alias_tested'] and p['resource_release_verified'] is False and p['readiness_verified'] is False and p['signatures_created']==0,'exact QFS staging')
   need((scope/'sender.m').read_text()==(REPO/'experiments/native-wifi-qca9377-filter63-staging-observer-v1/sender.m').read_text().replace('generation!=63','generation!=64'),'staging diff only generation guard')
   cr=p['compile_report'];need(Path(cr['executable_path']).resolve()==exe.resolve() and cr['executable_sha256']==exe_hash and p['host_test_executable_sha256']==test_hash,'compile manifest identity')
   for n,h in cr['source_sha256'].items():input_hash(n,h,scope)
   need(sha(scope/'evidence/callbacks.log')==p['callback_log_sha256'],'fakecallback log')
  else:
   need(p['native_binding_frozen'] is True and p['writes']==0 and sha(scope/'evidence/host.log')==p['host_log_sha256'],'frozen native join/log/write0')
   m=load(name,scope/'native_binding.py');need(m.check(PINS)==p['native_binding'],'actual native field/GATT/source join changed')
   if 'progress' in name:
    need(p['host_result']=='PASS 100 HOST progress collector cases; NO REAL MANAGER/WRITE' and p['wrong_ABI_negatives']==3 and p['actual_final_JSON_checks']==4 and p['raw_read_requires_release14'] and p['test_executable_sha256']==test_hash and p['executable_sha256']==exe_hash and Path(p['executable']).resolve()==exe.resolve(),'release-only monitor semantics')
   else:need(p['status']=='OFFLINE-FILTER64-FROZEN-NATIVE-TIMING-RAW-CALLBACK-PREFLIGHT-PASS' and p['python_checks']==1296 and p['host_result']=='PASS 511 HOST FILTER64 callback cases; NO MANAGER/WRITES' and p['physical_admission'] is False and p['test_executable_sha256']==test_hash and p['reader_executable_sha256']==exe_hash and Path(p['reader_path']).resolve()==exe.resolve(),'raw forensic reader scope')
  if name=='native-wifi-qca9377-filter64-observer-v1':
   oracle=load('oracle',ROOT/'oracle_gate.py').checked();need(p['actual_C_producer_oracle_report_sha256']==oracle['report_sha256'] and p['actual_C_producer_cases']==oracle['cases'],'actual64 C/timing semantic join')
  result[name]=str(exe)
 return result
if __name__=='__main__':print(json.dumps({'status':'ROOT64-FROZEN-HOST-SOURCE-COMPILER-NATIVE-ABI-GATE-PASS','helpers':checked(),'physical_admission':False,'device_operations':0},indent=2))
