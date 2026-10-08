"""Public immutable prior62 proof; no key, Bluetooth or state mutation."""
from pathlib import Path
import importlib.util,sys,json,hashlib
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
PINS_SHA='42006ceba0e37181a616217e3831656d2bdae536561e8f967a7d16fab4f8cf7f'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def prior():
 old=REPO/'experiments/native-wifi-qca9377-htt62-root-route-v1';names=('gate','host_gate','monitor_gate','admission');saved={n:sys.modules.get(n) for n in names};paths=list(sys.path)
 try:
  sys.path.insert(0,str(old))
  for n in names:sys.modules[n]=load('_filter63_prior62_'+n,old/(n+'.py'))
  return load('_filter63_prior62_route',old/'root_route.py')
 finally:
  sys.path[:]=paths
  for n,v in saved.items():
   if v is None:sys.modules.pop(n,None)
   else:sys.modules[n]=v

def pins():
 p=ROOT/'prior62-pins.json';need(sha(p)==PINS_SHA,'immutable prior62 pins changed');return json.loads(p.read_text())
def capture():
 p=pins();old=REPO/'experiments/native-wifi-qca9377-htt62-root-route-v1';folder=old/'evidence/physical62-HTT-VERSION-CONF'
 for n,h in p['physical_evidence_sha256'].items():need(sha(folder/n)==h,'actual62 physical input changed '+n)
 decoder_path=REPO/'experiments/native-wifi-qca9377-htt62-observer-v2/decode_htt.py';need(sha(decoder_path)==p['decoder_sha256'],'prior62 codec changed');decoder=load('_filter63_owned62_decode',decoder_path)
 rows=[json.loads(x) for x in (folder/'raw.log').read_text().splitlines() if x.startswith('{')];need(len(rows)==1 and rows[0]['format']=='QHTT1-QHTX1' and 'fixture_kind' not in rows[0],'one actual62 complete capture')
 callbacks=[json.loads(x) for x in (folder/'raw.jsonl').read_text().splitlines() if x.startswith('{')];need(len(callbacks)==67,'actual67 callbacks required')
 for c in callbacks:need(c['peripheral'].upper()==decoder.PEER and c['writes']==0 and c['NSError_code']==0 and not c['NSError_domain'] and not c['cached_value_possible'] and 'fixture_kind' not in c,'error/cache/write/synthetic actual62 input')
 bindings_path=REPO/'experiments/native-wifi-qca9377-htt62-observer-v2/bindings.py';need(sha(bindings_path)=='b7e4e15b2fdc8fcdcbf15b2e4813c40dffdea9ddd92c58102cb988f44903f652','frozen62 callback join changed');bindings=load('_filter63_callback62_bindings',bindings_path);bindings.callback_join(rows[0],callbacks)
 body=(REPO/'experiments/native-wifi-qca9377-v1/runs/mac-control/firmware-6.bin').read_bytes();d=decoder.decode_capture(rows[0],container=body)
 need(d['version_only_pass'] and (d['major'],d['minor'])==(3,56),'owned actual62 VERSION3.56 required')
 c=json.loads((folder/'classification.json').read_text());need(c['status']=='PHYSICAL62-OWNED-HTT-VERSION-CONF-RELEASE14' and c['version_confirmed'] and c['all14_released'] and not c['htt_data_plane_ready'] and c['generation']==62 and c['native_packet_sha256']==p['native_packet_sha256'],'exact prior62 bounded verdict')
 return d,rows[0],callbacks

def verify(state):
 route=prior();g=route.gate;p=pins();policy,public,admitted=route.current(state,g.CHECKED)
 need(sha(g.ROOT/'gate.py')==p['prior_gate_sha256'] and sha(g.ROOT/'root_route.py')==p['prior_root_route_sha256'],'prior62 authority code changed')
 native=Path(state['engine']['last_release_report']).parent
 need(sha(native/'report.json')==p['native_report_sha256'] and sha(native/'root-admission.json')==p['native_root_admission_sha256'],'actual62 receipt/admission changed')
 b=(native/'native.rrt').read_bytes();v=g.engine.verify(b,target=bytes.fromhex(policy['target']),owner=public,base_runtime=bytes.fromhex('305d0171c3c2e296fdf00f82a01cc838d67c0a1f3ffa836a847f4f12770ce074'),world=Path(state['package']).read_bytes(),counter=61)
 need(v.counter==62 and g.flow.sha(v.payload)==p['native_payload_sha256'] and g.flow.sha(b)==p['native_packet_sha256'],'actual public62 signature on61/world19')
 need(state.get('hardware_trial_pending'),'completed62 firmware session required');assets=Path(state['hardware_trial_pending']);need(sha(assets/'report.json')==p['asset_report_sha256'],'completed62 asset report changed');r=g.flow.read_json(assets/'report.json')
 need(r['status']=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and r['completed_chunks']==12 and len(r['packets'])==12 and r['gate']==admitted and r['policy']==policy and r['native_counter']==62 and r['native_payload_sha256']==p['native_payload_sha256'],'actual62 firmware identity')
 need(r['last_receipt']['action']==4 and r['last_receipt']['bitmap']==4095 and r['last_receipt']['ready']==1 and r['last_receipt']['peripheral'].upper()==g.base60.prior.PEER,'actual all12 accepted')
 body=bytearray()
 for item in r['packets']:
  packet=(assets/g.safe(item['file'])).read_bytes();f=g.base60.t.assets.validate(packet,public)
  need(f=={k:x for k,x in item.items() if k!='file'} and f['generation']==62 and f['offset']==len(body),'all12 unchanged contiguous signatures');body.extend(packet[224:])
 need(len(body)==policy['total'] and g.flow.sha(body)==policy['digest'],'exact full signed62 firmware')
 c,_,_=capture();need(c['actual_released'] and c['adapter_phase']==12 and c['cleanup_slot']==14 and c['life_phase']==4,'actual retained62 cleanup proof')
 return {'status':'PUBLIC62-APPLIED-SIGNED-ASSETS-OWNED-VERSION3.56-RELEASE14-PASS','native_directory':str(native),'asset_directory':str(assets),'device_operations':0,'state_mutations':0,'key_accesses':0,'new_counter_reserved':False}
if __name__=='__main__':
 state=json.loads((REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json').read_text());print(json.dumps(verify(state),indent=2))

def observation_tools():
 route=prior();g=route.gate;reader=REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt';proof=g.flow.read_json(g.base60.prior.ROOT/'evidence/root-proof.json');expected=proof['source_sha256'][str(reader.relative_to(REPO))]
 need(sha(reader)==expected,'frozen receipt reader changed');monitor=route.admission.monitor_gate.checked()
 return {'receipt_reader_sha256':expected,'monitor_sha256':sha(monitor),'observer_source_sha256':sha(ROOT/'observe62.py')}

def fresh(folder,before):
 import time
 folder=Path(folder);route=prior();g=route.gate;r=g.flow.read_json(folder/'report.json')
 need(r['status']=='ACTUAL62-RELEASE14-PRE63-OBSERVATION' and type(r['writes']) is int and r['writes']==0 and r['state_sha256']==g.flow.sha(before) and 0<=time.time()-r['observed_at']<=300,'fresh unchanged62 context')
 need(all(r[k]==v for k,v in observation_tools().items()),'fresh62 source/helper identity')
 for n in ('receipt.log','monitor.jsonl'):need(sha(folder/n)==r['inputs'][n],'fresh callback input changed')
 raw=g.base60.t.raw_callback(folder/'receipt.log',60);need(raw[:4]==b'RFS\1' and raw[20:24]==b'\2\0\0\0' and int.from_bytes(raw[24:28],'little')==62 and raw[28:].hex()==pins()['native_packet_sha256'],'physical62 still exactly APPLIED')
 rows=[json.loads(x) for x in (folder/'monitor.jsonl').read_text().splitlines() if x.startswith('{')]
 for v in rows:need(v['peripheral'].upper()==g.base60.prior.PEER and v['writes']==0 and v['NSError_code']==0 and not v['NSError_domain'] and not v.get('cached_value_possible') and 'fixture_kind' not in v,'actual fresh62 peer/error/cache/write')
 values=[v for v in rows if v['stage']=='value-read'];need(len(values)==2 and values[0]['index']==0 and values[1]['index']==1,'two ordered immutable quiescent values')
 boot=bytes.fromhex(values[0]['raw_hex']);status=bytes.fromhex(values[1]['raw_hex'])
 need(len(boot)==values[0]['raw_bytes']==160 and boot[:8]==b'QWBT0001' and int.from_bytes(boot[8:12],'little')==5 and not int.from_bytes(boot[12:16],'little') and not int.from_bytes(boot[20:24],'little'),'fresh62 bootstrap completed without error')
 _,capture62,_=capture();need(len(status)==values[1]['raw_bytes']==320 and status.hex()==capture62['status_hex'][0],'fresh62 status differs from complete stable owned export')
 return {'status_sha256':g.flow.sha(status),'physical_counter':62,'all14_released':True}

def inventory(directory):
 directory=Path(directory);need(directory.is_dir() and not directory.is_symlink(),'real archive source required');out={}
 for p in directory.rglob('*'):
  need(not p.is_symlink(),'archive symlink forbidden')
  if p.is_file():out[str(p.relative_to(directory))]=sha(p)
 return out

def sync_tree(directory):
 import os
 for p in directory.rglob('*'):
  if p.is_file():
   with p.open('rb') as handle:os.fsync(handle.fileno())
 for p in sorted([directory,*[p for p in directory.rglob('*') if p.is_dir()]],key=lambda p:len(p.parts),reverse=True):
  fd=os.open(p,os.O_RDONLY)
  try:os.fsync(fd)
  finally:os.close(fd)
 fd=os.open(directory.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)

def retire(state_path,state,observation,candidate_admission):
 """Root sole-lock API; requires separately frozen actual63 gate to exist."""
 import shutil
 # Not available until Root implements/adopts the exact tested63 gate. Merely
 # supplying a dictionary with successful booleans cannot authorize retirement.
 g63=load('_filter63_exact_candidate_gate',ROOT/'gate.py')
 actual=g63.gates(g63.CHECKED,(g63.CHECKED/'payload.efi').read_bytes(),Path(state['package']).read_bytes())
 need(actual['native_counter']==63 and actual['source_model_verified'] is True and all(candidate_admission.get(k)==v for k,v in actual.items()),'independent exact63 source gate required')
 state_path=Path(state_path);before=state_path.read_bytes();route=prior();flow=route.gate.flow
 need(flow.read_json(state_path)==state,'state changed before retirement')
 verified=verify(state);fields=fresh(observation,before)
 directory=ROOT/'runs/retired62';need(not directory.exists(),'retirement already exists; inspect instead of overwriting');directory.mkdir(parents=True)
 sources={'native':Path(verified['native_directory']),'assets':Path(verified['asset_directory']),'fresh-observation':Path(observation),'physical62-evidence':REPO/'experiments/native-wifi-qca9377-htt62-root-route-v1/evidence/physical62-HTT-VERSION-CONF'};manifests={}
 for name,source in sources.items():
  expected=inventory(source);shutil.copytree(source,directory/name);need(inventory(source)==expected and inventory(directory/name)==expected,'archive changed '+name);manifests[name]=expected
 (directory/'before-state.json').write_bytes(before)
 flow.save(directory/'retirement.json',{'status':'ACTUAL62-HTT3.56-RELEASE14-DURABLY-ARCHIVED','native_counter':62,'world_counter':19,'inventory':manifests,'prior_state_sha256':flow.sha(before),'fresh':fields,'candidate':candidate_admission,'new_signatures':0,'reboot_command':False})
 sync_tree(directory);need(state_path.read_bytes()==before,'state changed before durable transition')
 for name,source in sources.items():need(inventory(source)==manifests[name] and inventory(directory/name)==manifests[name],'source/archive changed '+name)
 after=dict(state);after['hardware_trial_pending']=None;after['last_hardware_trial_retirement']=str(directory/'retirement.json');flow.save(state_path,after)
 return after,directory
