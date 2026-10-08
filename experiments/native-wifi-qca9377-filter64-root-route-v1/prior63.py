"""Read-only frozen physical63 proof replay. No Bluetooth, key or state writes."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
OLD=REPO/'experiments/native-wifi-qca9377-filter63-root-route-v1'
EVIDENCE=OLD/'evidence/physical63-filter-timeout'
VERDICT_SHA='13c9fd8c3e735f520232d0efe61b3f9318d933f93c3db620daf80ba9d9ff702c'
STATE=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def need(value,message):
 if not value:raise ValueError(message)
def verify(state_path=STATE):
 state_path=Path(state_path);before=state_path.read_bytes()
 need(sha(EVIDENCE/'verdict.json')==VERDICT_SHA,'immutable physical63 verdict changed')
 verdict=json.loads((EVIDENCE/'verdict.json').read_text())
 for name,digest in verdict['inputs'].items():need(sha(EVIDENCE/name)==digest,'physical63 input changed: '+name)
 need(hashlib.sha256(before).hexdigest()==verdict['inputs']['state.json'],'current state differs from physically classified63; inspect before transition')
 with tempfile.TemporaryDirectory(prefix='rabbit-public63-') as folder:
  output=Path(folder)/'classification.json'
  result=subprocess.run([sys.executable,str(OLD/'classify_filter63.py'),'--state',str(state_path),'--capture-log',str(EVIDENCE/'raw63.log'),'--raw-log',str(EVIDENCE/'raw63.jsonl'),'--output',str(output)],capture_output=True,text=True,timeout=180)
  need(result.returncode==0,'frozen public63 classifier rejected: '+result.stderr[-1500:])
  need(output.read_bytes()==(EVIDENCE/'classification63.json').read_bytes(),'independent replay differs from physical63 classification')
  classification=json.loads(output.read_text())
 need(classification['status']=='PHYSICAL63-RELEASED-DIAGNOSTIC-FAILURE' and classification['all14_released'] and not classification['pipeline_completed'],'expected released bounded63 diagnostic fault')
 need(state_path.read_bytes()==before,'state changed during public replay')
 return {'status':'PUBLIC63-FULL12-BOOT-QUEUED-ECHO-RELEASE14-PASS','state_sha256':hashlib.sha256(before).hexdigest(),'classification_sha256':sha(EVIDENCE/'classification63.json'),'device_operations':0,'key_accesses':0,'state_mutations':0,'wifi_connected':False,'IP':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))

def authority():
 """Load frozen Root63 with isolated generic module names."""
 import importlib.util
 names=('gate','admission','host_gate','monitor_gate','oracle_gate','transition62','assets63')
 saved={n:sys.modules.get(n) for n in names};paths=list(sys.path)
 try:
  sys.path.insert(0,str(OLD))
  for n in names:sys.modules.pop(n,None)
  spec=importlib.util.spec_from_file_location('_root64_prior63_route',OLD/'root_route.py');route=importlib.util.module_from_spec(spec);spec.loader.exec_module(route)
  return route
 finally:
  sys.path[:]=paths
  for n,v in saved.items():
   if v is None:sys.modules.pop(n,None)
   else:sys.modules[n]=v

def fresh(folder,before):
 import time
 folder=Path(folder);r=json.loads((folder/'report.json').read_text());route=authority();g=route.gate
 markers=('fixture_kind','synthetic_only','model_capture','test_clock','synthetic_timing_only','synthesized')
 need(not any(k in r for k in markers),'synthetic fresh63 report forbidden')
 need(type(r.get('writes')) is int and r['writes']==0 and r['status']=='ACTUAL63-RELEASE14-PRE64-OBSERVATION' and r['state_sha256']==hashlib.sha256(before).hexdigest() and 0<=time.time()-r['observed_at']<=300,'fresh63 context required')
 need(r['observer_source_sha256']==sha(ROOT/'observe63.py'),'fresh63 observer source changed')
 need(set(r['inputs'])=={'receipt.log','monitor.jsonl'},'fresh63 exact callback files')
 reader=g.REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt'
 proof=g.flow.read_json(g.base60.prior.ROOT/'evidence/root-proof.json');expected=proof['source_sha256'][str(reader.relative_to(g.REPO))]
 need(sha(reader)==r['receipt_reader_sha256']==expected and sha(route.admission.monitor_gate.checked())==r['monitor_sha256'],'fresh63 exact frozen helper identities')
 for name,digest in r['inputs'].items():need(sha(folder/name)==digest,'fresh63 file changed')
 receipt=g.base60.t.raw_callback(folder/'receipt.log',60)
 need(receipt[:4]==b'RFS\1' and receipt[20:24]==b'\2\0\0\0' and int.from_bytes(receipt[24:28],'little')==63 and receipt[28:].hex()=='55d2a292e08011dc4377d104f333e59f40cc4537d5906604f838f8beb193a90f','exact63 applied receipt')
 rows=[json.loads(line) for line in (folder/'monitor.jsonl').read_text().splitlines() if line.startswith('{')]
 for row in rows:need(row['peripheral'].upper()==g.base60.prior.PEER and type(row['writes']) is int and row['writes']==0 and row['NSError_code']==0 and not row['NSError_domain'] and not row.get('cached_value_possible') and not any(k in row for k in markers),'fresh actual callback required')
 values=[row for row in rows if row['stage']=='value-read']
 need(len(values)==2 and [row['index'] for row in values]==[0,1],'two ordered quiescent values required')
 boot=bytes.fromhex(values[0]['raw_hex']);status=bytes.fromhex(values[1]['raw_hex'])
 retained=json.loads(next(line for line in (EVIDENCE/'raw63.log').read_text().splitlines() if line.startswith('{')))
 need(len(boot)==values[0]['raw_bytes']==160 and boot[:8]==b'QWBT0001' and int.from_bytes(boot[8:12],'little')==5 and not int.from_bytes(boot[12:16],'little'),'fresh chipboot success')
 need(len(status)==values[1]['raw_bytes']==448 and status.hex()==retained['pipeline_hex'][0],'fresh63 full448 status must match retained all-owner release')
 return {'physical_counter':63,'all14_released':True,'status_sha256':hashlib.sha256(status).hexdigest()}
