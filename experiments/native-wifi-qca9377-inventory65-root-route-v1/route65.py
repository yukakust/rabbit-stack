"""Exact inventory65 admission/transition. One lock; immutable64/65 sources."""
from pathlib import Path
import argparse,base64,hashlib,importlib.util,json,os,shutil,struct,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
OLD=REPO/'experiments/native-wifi-qca9377-filter64-root-route-v1'
SCOPE=REPO/'experiments/native-wifi-qca9377-inventory65-native-v1'
CHECKED=SCOPE/'runs/checked-candidate'
STATE=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
sys.path.insert(0,str(OLD))
import root_route as prior
import transition63 as archive
import monitor_gate
g=prior.gate;flow=g.flow;engine=g.engine
sha=g.sha;need=g.need
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
software=module('_inventory65_software',SCOPE/'gate.py')
decoder=module('_inventory65_decode',SCOPE/'decode.py')
FREEZE='1e8d4c9492c371fc8297d829a8bcafe3485fdfa38ac90825e39031e61f37ee21'
CLASS='81569d0d9faa5ad84dd02ac9a9d5af0e402ff06ed3486ffe1d4722667fd9b825'
EVIDENCE=OLD/'evidence/native64-final'
PAYLOAD='84b28939af3774620ec57e19e3fd09fc4315edaeb69e572f7fa982c648284d20'
MARKERS=('fixture_kind','synthetic_only','model_capture','test_clock','synthetic_timing_only','synthesized')
def actual_callback(row):
 need(row['peripheral'].upper()==g.base60.prior.PEER and type(row['writes']) is int and row['writes']==0 and row['NSError_code']==0 and not row['NSError_domain'] and not row.get('cached_value_possible') and not any(k in row for k in MARKERS),'actual zero-write callback required')
 raw=bytes.fromhex(row['raw_hex']);need(type(row['raw_bytes']) is int and len(raw)==row['raw_bytes'],'actual callback bytes length');return raw
def applied_receipt(receipt,session):
 # RFS hashes the signed packet, not its inner EFI payload. Correlate every
 # field with the saved immutable transport session, including its nonce.
 wire_bytes=len(base64.b64decode(session['stream_base64']));need(wire_bytes==session['package_bytes']+32,'exact transport header size')
 need(len(receipt)==60 and receipt[:4]==b'RFS\1' and receipt[4:12]==base64.b64decode(session['session_base64']) and struct.unpack_from('<IIII',receipt,12)==(wire_bytes,wire_bytes,2,session['counter']) and receipt[28:].hex()==session['sha256'],'exact fresh APPLIED session/packet receipt')
def sync_file(path):
 with Path(path).open('rb') as h:os.fsync(h.fileno())
 fd=os.open(Path(path).parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def gates(directory,payload,world):
 need(Path(directory).resolve()==CHECKED.resolve(),'exact65 directory')
 need(sha(SCOPE/'evidence/freeze.json')==FREEZE,'reviewed65 freeze')
 frozen=flow.read_json(SCOPE/'evidence/freeze.json')
 for group,prefix in (('source_sha256',SCOPE),('evidence_sha256',SCOPE/'evidence')):
  for name,h in frozen[group].items():need(sha(prefix/g.safe(name))==h,'frozen65 '+name)
 result=software.checked()
 need(flow.sha(payload)==PAYLOAD and flow.sha(world)==g.WORLD,'exact payload/world19')
 pe=struct.unpack_from('<I',payload,60)[0]
 need(payload[:2]==b'MZ' and payload[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<I',payload,pe+80)[0]==result['mapped_bytes'],'actual mapped size')
 report=flow.read_json(CHECKED/'report.json')
 need(sha(CHECKED/'report.json')==sha(SCOPE/'evidence/native-report.json'),'actual report archive')
 for name,h in report['compiled_inputs_sha256'].items():
  marker='/runs/checked-candidate/'
  path=CHECKED/name.split(marker,1)[1] if marker in name else REPO/Path(name).relative_to('/home/yuka/rabbit-world/parallel-filter64-native-v1/source')
  need(sha(path)==h,'actual compiled input '+name)
 for name in ('reproduction.json','qemu-report.json'):need(sha(CHECKED/name)==sha(SCOPE/'evidence'/name),'actual archived '+name)
 need(sha(SCOPE/'runs/control/collector')==frozen['host_executable_sha256'] and sha(REPO/'experiments/x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist')==frozen['InfoPlist_sha256'],'exact host collector')
 installed=flow.read_json(g.base60.PROFILE/'receiver-policy.json')
 return {'report_sha256':sha(CHECKED/'report.json'),'payload_sha256':PAYLOAD,'profile_status':report['status'],'receiver_policy':{**installed,'generation':65},'native_counter':65,'world_package_sha256':g.WORLD,'source_model_verified':True,'inventory65_freeze_sha256':FREEZE,'entropy_approved':False}
def prior64(statepath):
 before=Path(statepath).read_bytes();s=json.loads(before)
 prior.current(s,g.CHECKED)
 need(sha(EVIDENCE/'classification64.json')==CLASS,'exact complete64 classification')
 c=flow.read_json(EVIDENCE/'classification64.json');closure=flow.read_json(EVIDENCE/'closure.json')
 for name,h in closure['files_sha256'].items():need(sha(EVIDENCE/name)==h,'public64 evidence '+name)
 need(flow.sha(before)==c['state_sha256'] and c['pipeline_completed'] and c['owned_filter_version_verified'] and c['all14_released'],'actual complete64 state/owners')
 need(s['hardware_trial_pending']==c['asset_session'],'exact64 firmware session')
 # Re-run the frozen independent classifier, including every firmware signature.
 out=ROOT/'runs'/('replay64-'+str(time.time_ns())+'.json');out.parent.mkdir(parents=True,exist_ok=True)
 p=subprocess.run([sys.executable,str(OLD/'classify_filter64.py'),'--state',str(statepath),'--capture-log',str(EVIDENCE/'raw64.log'),'--raw-log',str(EVIDENCE/'raw64.jsonl'),'--output',str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=180)
 need(p.returncode==0,'independent64 replay rejected: '+p.stderr[-1200:]);need(out.read_bytes()==(EVIDENCE/'classification64.json').read_bytes(),'actual64 replay mismatch')
 need(Path(statepath).read_bytes()==before,'state changed during replay');return s
def helpers():
 reader=REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt'
 proof=flow.read_json(g.base60.prior.ROOT/'evidence/root-proof.json');expected=proof['source_sha256'][str(reader.relative_to(REPO))]
 need(sha(reader)==expected,'frozen receipt reader');return reader,monitor_gate.checked()
def child(exe,args,out,timeout=135):
 env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(flow.LOCK_FD)
 with Path(out).open('x') as log:
  p=subprocess.run([str(exe),*map(str,args)],stdout=log,stderr=subprocess.STDOUT,env=env,pass_fds=(flow.LOCK_FD,),timeout=timeout)
 need(p.returncode==0,'physical operation failed; saved exact log '+str(out))
def fresh_validate(folder,before):
 folder=Path(folder);r=flow.read_json(folder/'report.json')
 need(r['status']=='ACTUAL64-FRESH-RELEASE14-PRE65' and r['state_sha256']==flow.sha(before) and 0<=time.time()-r['observed_at']<=300 and r['writes']==0,'fresh64 context')
 reader,monitor=helpers();need(r['reader_sha256']==sha(reader) and r['monitor_sha256']==sha(monitor) and r['source_sha256']==sha(__file__),'fresh observer identities')
 for name,h in r['inputs'].items():need(sha(folder/name)==h,'fresh file '+name)
 receipt=g.base60.t.raw_callback(folder/'receipt.log',60)
 prior_state=json.loads(before);native=Path(prior_state['engine']['last_release_report']).parent;session=flow.validate_session(flow.read_json(native/'session.json'));need(session['counter']==64 and session['sha256']==flow.read_json(EVIDENCE/'classification64.json')['native_packet_sha256'],'exact64 saved packet');applied_receipt(receipt,session)
 rows=[json.loads(line) for line in (folder/'monitor.jsonl').read_text().splitlines() if line.startswith('{')]
 for row in rows:actual_callback(row)
 values=[row for row in rows if row['stage']=='value-read'];need(len(values)==2 and [v['index'] for v in values]==[0,1],'two ordered64 values')
 boot=bytes.fromhex(values[0]['raw_hex']);status=bytes.fromhex(values[1]['raw_hex'])
 retained=json.loads(next(line for line in (EVIDENCE/'raw64.log').read_text().splitlines() if line.startswith('{')))
 need(len(boot)==values[0]['raw_bytes']==160 and boot[:8]==b'QWBT0001' and struct.unpack_from('<II',boot,8)==(5,0),'fresh completed chipboot')
 need(len(status)==values[1]['raw_bytes']==544 and status.hex()==retained['pipeline_hex'][0],'exact fresh64 all14 release')
 return {'counter':64,'all14_released':True,'status_sha256':flow.sha(status)}
def observe(statepath,s):
 before=Path(statepath).read_bytes();reader,monitor=helpers();out=ROOT/'runs'/('fresh64-'+str(time.time_ns()));out.mkdir(parents=True)
 child(reader,['receipt'],out/'receipt.log');child(monitor,['--monitor',out/'monitor.jsonl','--root-authorized-read'],out/'monitor.log')
 need(Path(statepath).read_bytes()==before,'state changed during fresh64 reads')
 flow.save(out/'report.json',{'status':'ACTUAL64-FRESH-RELEASE14-PRE65','observed_at':time.time(),'state_sha256':flow.sha(before),'reader_sha256':sha(reader),'monitor_sha256':sha(monitor),'source_sha256':sha(__file__),'writes':0,'inputs':{n:sha(out/n) for n in ('receipt.log','monitor.jsonl')}})
 fresh_validate(out,before);return out
def prepare(statepath,private):
 intent=ROOT/'runs/prepare65-intent.json';need(not intent.exists(),'65 signing intent exists; inspect saved session before any transition')
 need(not (ROOT/'runs/retired64').exists(),'64 retirement exists; inspect durable saved state before transition')
 s=prior64(statepath);candidate=gates(CHECKED,(CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes());observation=observe(statepath,s)
 archive.require_lock(flow,statepath);before=Path(statepath).read_bytes();fresh=fresh_validate(observation,before)
 dest=ROOT/'runs/retired64';need(not dest.exists(),'retirement already exists; inspect saved session');dest.mkdir(parents=True)
 sources={'native':Path(s['engine']['last_release_report']).parent,'assets':Path(s['hardware_trial_pending']),'fresh-observation':observation,'physical64-evidence':EVIDENCE};manifest={}
 for name,source in sources.items():
  expected=archive.inventory(source);shutil.copytree(source,dest/name);need(archive.inventory(source)==expected and archive.inventory(dest/name)==expected,'changed archive '+name);manifest[name]=expected
 (dest/'before-state.json').write_bytes(before)
 flow.save(dest/'retirement.json',{'status':'ACTUAL64-COMPLETED-ECHO-HTT-SCAN-RELEASE14-DURABLY-ARCHIVED','inventory':manifest,'prior_state_sha256':flow.sha(before),'fresh':fresh,'candidate':candidate,'new_signatures':0,'reboot':False})
 archive.sync_tree(dest);fresh_validate(observation,before);need(Path(statepath).read_bytes()==before,'state changed before retirement')
 for name,source in sources.items():need(archive.inventory(source)==manifest[name] and archive.inventory(dest/name)==manifest[name],'archive/source changed')
 s['hardware_trial_pending']=None;s['last_hardware_trial_retirement']=str(dest/'retirement.json');flow.save(statepath,s);sync_file(statepath);after=Path(statepath).read_bytes()
 need(not intent.exists(),'65 signing intent exists; never blindly sign again')
 with intent.open('x') as h:json.dump({'status':'ONE-PREPARE65-ATTEMPT-RESERVED','state_sha256':flow.sha(after),'candidate':candidate,'source_sha256':sha(__file__),'retirement_sha256':sha(dest/'retirement.json')},h,indent=2);h.flush();os.fsync(h.fileno())
 archive.sync_tree(intent.parent)
 old=g.primitive.gates;old_private=engine.load_private
 def guarded(path):
  need(Path(statepath).read_bytes()==after,'state changed before key access');fresh_validate(observation,before);need(gates(CHECKED,(CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes())==candidate,'candidate changed');return old_private(path)
 try:
  g.primitive.gates=gates;engine.load_private=guarded
  directory=g.primitive.prepare(Path(statepath),s,CHECKED,private)
  (directory/'root-before-state.json').write_bytes(after)
  flow.save(directory/'root-admission.json',{'candidate':candidate,'retirement':str(dest/'retirement.json'),'retirement_sha256':sha(dest/'retirement.json'),'before_state_sha256':flow.sha(after),'source_sha256':sha(__file__)})
  archive.sync_tree(directory);sync_file(statepath);return directory
 finally:g.primitive.gates=old;engine.load_private=old_private
def deliver(statepath,private):
 s=flow.read_json(statepath);need(s.get('native_pending'),'saved exact65 session required');d=Path(s['native_pending']);b=flow.read_json(d/'root-before-state.json');b['native_pending']=str(d);a=flow.read_json(d/'root-admission.json')
 need(s==b and a['candidate']==gates(CHECKED,(d/'payload.efi').read_bytes(),Path(s['package']).read_bytes()) and a['source_sha256']==sha(__file__) and a['before_state_sha256']==sha(d/'root-before-state.json') and a['retirement_sha256']==sha(a['retirement']),'saved65 exact admission')
 old=g.primitive.gates
 try:
  g.primitive.gates=gates;result=g.primitive.deliver(Path(statepath),s,private);sync_file(d/'report.json');sync_file(statepath);return result
 finally:g.primitive.gates=old
def collect(statepath):
 s=flow.read_json(statepath);flow.current(s);need(s['engine']['native_counter']==65 and s['engine']['payload_sha256']==PAYLOAD and not any(s.get(k) for k in ('pending','native_pending','hardware_trial_pending','recovery_pending')),'actual65 without live operation')
 r=flow.read_json(s['engine']['last_release_report']);need(r['status']=='EXACT-APPLIED-RECEIPT' and r['receiver_reported_applied'] and r['counter']==65 and r['gate']==gates(CHECKED,(CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes()),'exact65 applied gates')
 out=ROOT/'runs'/('physical65-'+str(time.time_ns()));out.mkdir(parents=True)
 before=Path(statepath).read_bytes();reader,_=helpers();child(reader,['receipt'],out/'receipt.log')
 receipt=g.base60.t.raw_callback(out/'receipt.log',60);session=flow.validate_session(flow.read_json(Path(s['engine']['last_release_report']).parent/'session.json'));need(session['counter']==65 and session['sha256']==r['package_sha256'],'exact65 signed packet');applied_receipt(receipt,session)
 child(SCOPE/'runs/control/collector',['--collect',out/'callbacks.jsonl','--root-authorized-read'],out/'collector.log')
 rows=[json.loads(line) for line in (out/'callbacks.jsonl').read_text().splitlines() if line.startswith('{')]
 for row in rows:actual_callback(row)
 values=[row for row in rows if row['stage']=='value-read'];need(len(values)==2 and [v['index'] for v in values]==[0,1],'two actual65 values')
 report=flow.read_json(CHECKED/'report.json');decoded=decoder.decode(bytes.fromhex(values[0]['raw_hex']),bytes.fromhex(values[1]['raw_hex']),report['rng_code_object_sha256'],sha(REPO/'experiments/native-wifi-qca9377-cpuid-inventory-v1/inventory.c'))
 need(Path(statepath).read_bytes()==before,'state changed during inventory')
 decoded.update(physical_observed=True,device_attestation=False,source_state_sha256=flow.sha(before),actual_inputs_sha256={n:sha(out/n) for n in ('receipt.log','collector.log','callbacks.jsonl')},collector_sha256=sha(SCOPE/'runs/control/collector'))
 flow.save(out/'decoded.json',decoded);archive.sync_tree(out);print(json.dumps(decoded,indent=2));return out
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('check','prepare','deliver','collect'));p.add_argument('--state',type=Path,default=STATE);p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');a=p.parse_args()
 with flow.state_lock(a.state):
  if a.action=='check':prior64(a.state);print(json.dumps(gates(CHECKED,(CHECKED/'payload.efi').read_bytes(),Path(flow.read_json(a.state)['package']).read_bytes()),indent=2));return 0
  if a.action=='prepare':print(prepare(a.state,a.private));return 0
  if a.action=='deliver':return deliver(a.state,a.private)
  print(collect(a.state));return 0
if __name__=='__main__':raise SystemExit(main())
