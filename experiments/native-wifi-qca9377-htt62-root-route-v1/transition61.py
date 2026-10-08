"""Public exact61 proof and durable retirement APIs only; no radio/key entrypoint."""
from pathlib import Path
import importlib.util,json,os,shutil,time,struct
ROOT=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('_htt62_transition_public_gate',ROOT/'gate.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
flow,engine=g.flow,g.engine;need=g.need
PRIOR=g.REPO/'experiments/native-wifi-qca9377-scan61-root-route-v1'
PHYSICAL=PRIOR/'evidence/physical61-complete-scan'
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
OWNER='622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac'
TARGET='363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9'
PAYLOAD61='305d0171c3c2e296fdf00f82a01cc838d67c0a1f3ffa836a847f4f12770ce074'
BASE60='3984d3f5d1c9a3c3540bf2ef00972bea52406a6f78edc56bd215507110668fd6'
PACKET61='ecd2703c73c1bc92e266542cf08241ef03c613ad4cfba75dcf6942ad0812d71c'
ASSET_REPORT='1df2b6b1f0499865c5a258f0a5654f4eb798bb635873434e92fe40bad22d8458'
NATIVE_REPORT='f56f47b4c05d9da5232a7ffebeabb59ed44074003867c8f29a5ff806d1da5a51'
ROOT_ADMISSION61='3574091eac39dac2ac5ae8e8580494df5f418b2f7bce654a9821cc5e078d15d3'
PHYSICAL_HASHES={'progress.jsonl':'599abcb66b9b9258198cd62d62a2dca65b8ef688922970d4e6c83173951c5652','hashes.json':'27e12d2a0d883b91edd1e0b1c0044bbfd8ac406b3991d89f19d789590eecfcb3','controller.json':'6fd6aec8d03dfccd29091f7965764fdd1148a86c69f765b4962f8d515d46d8f8','raw.log':'3ba18d953a08a69e34a8d7bf5be223240ea24aedd8b7fd1425862d80f614f132','archive-events.json':'f4b68eeb70eb12e93815a3e9c75e6c2669beb6eac3efb9eb61002bd2da702157','classification.json':'26338237712c60ae7fa24efbbc979afa28d496d03e1413439e6e34a11d607d8d','progress.log':'bd2c584c2ad666c1fe5b509254f374d376f8472a7d982e22c34f8b2595f008f3','raw.jsonl':'343ed990add705b596e77b73c08bbc3c6fcd883593dc82f10b6553c8b242cc5f'}
DECODE=g.REPO/'experiments/native-wifi-qca9377-scan61-observer-v1/decode_scan.py'
DECODE_SHA='abd638a1d3ea0a5d62d45cd9f66d93d6a1a21595dbf3bbae156e4ac7fc065775' # frozen public61 codec, never derive pin from mutable input
INVENTORY=g.REPO/'experiments/native-wifi-qca9377-scan61-inventory-v3'
READER=g.REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt'
INVENTORY_SOURCE_SHA='7e7a140eed173b8b1b2600830c2e44afa2c51b9eaf5d114e214f283d2d2a5dc7'
INVENTORY_EXE_SHA='a6a3489c856c58ee9d111cd0b7a7aa9463bea414cf97d83fea47ec0a68335d16'

def decoder():
 need(g.sha(DECODE)==DECODE_SHA,'frozen61 decoder changed')
 s=importlib.util.spec_from_file_location('_htt62_prior61_raw_decoder',DECODE);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def physical():
 for name,h in PHYSICAL_HASHES.items():need(g.sha(PHYSICAL/name)==h,'pinned actual61 evidence changed '+name)
 rows=[json.loads(line) for line in (PHYSICAL/'raw.log').read_text().splitlines() if line.startswith('{')]
 need(len(rows)==1 and rows[0].get('format')=='QSCN1-QEXP1' and 'fixture_kind' not in rows[0],'actual complete61 raw result')
 raw=rows[0];d=decoder().decode_capture(raw)
 callbacks=[json.loads(line) for line in (PHYSICAL/'raw.jsonl').read_text().splitlines() if line.startswith('{')]
 need(len(callbacks)==227 and [v['stage'] for v in callbacks[:4]]==['services','characteristics','services','characteristics'] and all(v['stage']=='read' for v in callbacks[4:]),'actual227 capture callbacks')
 for v in callbacks:need(v.get('peripheral','').upper()==PEER and v.get('writes')==0 and v.get('NSError_code')==0 and not v.get('NSError_domain') and not v.get('cached_value_possible') and 'fixture_kind' not in v,'actual61 callback error/cache/peer/write')
 expected=[(0,0x2b,raw['status_hex'][0])]
 expected.extend((1,0x80+i,h) for i,h in enumerate(raw['pages_hex'][0]));expected.append((2,0x2b,raw['status_hex'][1]));expected.extend((3,0x80+i,h) for i,h in enumerate(raw['pages_hex'][1]));expected.append((4,0x2b,raw['status_hex'][2]))
 for v,(stage,uuid,h) in zip(callbacks[4:],expected):need(v['capture_stage']==stage and v['expected'].upper()==f'52414242-4954-4649-8000-{uuid:012X}' and v['raw_hex']==h and v['raw_bytes']==len(bytes.fromhex(h)),'raw read/capture join')
 c=flow.read_json(PHYSICAL/'classification.json');need(c['status']=='PHYSICAL61-COMPLETE-SCAN-CAPTURE-NO-ACCEPTED-TARGET' and c['generation']==61 and c['payload_sha256']==PAYLOAD61 and c['native_packet_sha256']==PACKET61 and c['world_package_sha256']==g.WORLD and c['stable_statuses']==3 and c['stable_raw_passes']==2 and c['pages_per_pass']==110 and c['all14_released'] is True and c['target_SSID_observed'] is False,'exact complete physical61 classification; noSSID inference')
 release(d)
 return d,bytes.fromhex(raw['status_hex'][0])

def release(d):
 need(d['generation']==61 and d['policy_count']==13 and d['quiesce_requested']==d['actual_owners_released']==d['terminal_seen']==d['startup_ready_seen']==d['startup_tx_complete']==1 and d['adapter_phase']==12 and d['cleanup_slots']==14 and d['native_error']==0 and d['live_frequency']==0,'actual61 READY/terminal/all14 closure')
 need(not any(d[n] for n in decoder().OWNERS),'remaining61 DMA/pin/PCI owner')

def verify(s):
 need(not any(s.get(k) for k in ('pending','native_pending','recovery_pending')),'competing operation')
 flow.current(s)
 prior=g.prior61.gates(g.prior61.CHECKED,(g.prior61.CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes())
 need(s['engine']['native_counter']==61 and s['engine']['payload_sha256']==PAYLOAD61 and s['counter']==19 and s['world_sha256']==g.SEMANTIC and s['package_sha256']==g.WORLD,'actual61/world19')
 installed=engine.gate_check(Path(s['engine']['installed_gate']));public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes()
 need(public.hex()==OWNER and flow.sha(public)==installed['owner_public_sha256'] and installed['target_sha256']==TARGET and g.sha(s['engine']['installed_gate'])==s['engine']['installed_gate_sha256'],'public owner/target installation')
 native=Path(s['engine']['last_release_report']).parent
 need(g.sha(native/'report.json')==NATIVE_REPORT and g.sha(native/'root-admission.json')==ROOT_ADMISSION61,'immutable actual61 native admission/receipt')
 receipt=flow.read_json(native/'report.json');admission=flow.read_json(native/'root-admission.json');actual_gate=receipt['gate']
 need(receipt['status']=='EXACT-APPLIED-RECEIPT' and receipt['receiver_reported_applied'] is True and receipt['counter']==61 and receipt['payload_sha256']==PAYLOAD61 and admission['candidate']==actual_gate and all(actual_gate.get(k)==v for k,v in prior.items()),'actual61 admitted APPLIED gate')
 packet=(native/'native.rrt').read_bytes();v=engine.verify(packet,target=bytes.fromhex(TARGET),owner=public,base_runtime=bytes.fromhex(BASE60),world=Path(s['package']).read_bytes(),counter=60)
 need(v.counter==61 and flow.sha(v.payload)==PAYLOAD61 and flow.sha(packet)==PACKET61,'public61 signed on exact60/world19')
 need(s.get('hardware_trial_pending'),'completed actual61 assets required');assets=Path(s['hardware_trial_pending']);need(g.sha(assets/'report.json')==ASSET_REPORT,'actual complete61 asset report')
 r=flow.read_json(assets/'report.json');policy=prior['receiver_policy'];need(r['status']=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and r['completed_chunks']==12 and len(r['packets'])==12 and r['native_counter']==61 and r['native_payload_sha256']==PAYLOAD61 and r['world_counter']==19 and r['world_sha256']==g.SEMANTIC and r['policy']==policy and r['gate']==actual_gate,'actual full61 firmware session')
 end=r['last_receipt'];need(end['action']==4 and end['bitmap']==4095 and end['ready']==1 and end['peripheral'].upper()==PEER,'actual full accepted61 receipt')
 body=bytearray()
 for item in r['packets']:
  b=(assets/g.safe(item['file'])).read_bytes();val=g.base60.t.assets.validate(b,public)
  need(val=={k:x for k,x in item.items() if k!='file'} and val['generation']==61 and val['offset']==len(body) and b[8:40].hex()==TARGET,'exact61 signed asset ordering/target')
  body.extend(b[224:])
 need(len(body)==policy['total'] and flow.sha(body)==policy['digest'],'exact full61 firmware content')
 d,_=physical();need(flow.read_json(PHYSICAL/'classification.json')['asset_session']==str(assets),'actual61 classified asset session')
 return assets,native

def observation_tools():
 """Public host helper identities only; never compiles/starts a manager."""
 proof=flow.read_json(g.REPO/'experiments/native-wifi-qca9377-observation59-root-route-v1/evidence/root-proof.json')
 expected_reader=proof['source_sha256'][str(READER.relative_to(g.REPO))]
 need(g.sha(READER)==expected_reader and g.sha(INVENTORY/'inventory.m')==INVENTORY_SOURCE_SHA and g.sha(INVENTORY/'runs/inventory')==INVENTORY_EXE_SHA,'exact61 immutable read helpers')
 return {'receipt_reader_sha256':expected_reader,'inventory_source_sha256':INVENTORY_SOURCE_SHA,'inventory_executable_sha256':INVENTORY_EXE_SHA,'observer_source_sha256':g.sha(ROOT/'observe61.py')}

def fresh(q,state):
 q=Path(q);r=flow.read_json(q/'report.json');need(r.get('status')=='ACTUAL61-RELEASE14-PRE62-OBSERVATION' and type(r.get('writes')) is int and r['writes']==0 and r['state_sha256']==flow.sha(state) and 0<=time.time()-r['observed_at']<=300,'fresh actual61 unchanged context')
 for n in ('receipt.log','inventory.jsonl'):need(g.sha(q/n)==r['inputs'][n],'fresh callback changed '+n)
 tools=observation_tools();need(all(r.get(k)==v for k,v in tools.items()),'exact fresh61 read-only tools')
 raw=g.base60.t.raw_callback(q/'receipt.log',60)
 need(raw[:4]==b'RFS\1' and raw[20:24]==b'\2\0\0\0' and int.from_bytes(raw[24:28],'little')==61 and raw[28:].hex()==PACKET61,'physical61 still APPLIED; no reset')
 rows=[json.loads(line) for line in (q/'inventory.jsonl').read_text().splitlines() if line.startswith('{')];need(rows,'actual inventory callbacks absent')
 for v in rows:need(v.get('peripheral','').upper()==PEER and v.get('writes')==0 and v.get('NSError_code')==0 and not v.get('NSError_domain') and 'fixture_kind' not in v,'fresh61 inventory peer/error/write')
 found=[v for v in rows if v.get('stage')=='diagnostic-status-read-untrusted-parent'];need(len(found)==1,'one exact fresh61 QSCN callback')
 v=found[0]['info'];need(v['parent_service'].upper()=='52414242-4954-4649-8000-00000000002A' and v['UUID'].upper()=='52414242-4954-4649-8000-00000000002B' and v['bytes']==416 and not v.get('cached_value_possible'),'current61 actual status parent/UUID/error/size')
 status=bytes.fromhex(v['hex']);d=decoder().decode_status(status);release(d);_,previous=physical();need(status==previous,'fresh61 status differs from complete stable capture')
 return d

def inventory(d):
 d=Path(d);need(d.is_dir() and not d.is_symlink(),'real archive directory required');out={}
 for p in d.rglob('*'):
  need(not p.is_symlink(),'archive symlink forbidden')
  if p.is_file():out[str(p.relative_to(d))]=g.sha(p)
 return out

def sync_tree(directory):
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

def retire(state_path,s,q,candidate_admission):
 # Caller holds sole lock and independently admits exact new62/host tools.
 need(candidate_admission.get('native_counter')==62 and candidate_admission.get('payload_sha256')==g.PAYLOAD and candidate_admission.get('report_sha256')==g.REPORT and candidate_admission.get('world_package_sha256')==g.WORLD and candidate_admission.get('source_model_verified') is True,'independent exactRoot62 candidate gate required')
 state_path,q=Path(state_path),Path(q);before=state_path.read_bytes();need(flow.read_json(state_path)==s,'unchanged actual state')
 assets,native=verify(s);fields=fresh(q,before);directory=ROOT/'runs/retired61';need(not directory.exists(),'retirement exists; inspect manifest, never overwrite');directory.mkdir(parents=True)
 sources={'assets':assets,'native':native,'fresh-observation':q,'physical61-evidence':PHYSICAL};manifests={}
 for name,source in sources.items():
  expected=inventory(source);shutil.copytree(source,directory/name);need(inventory(directory/name)==expected and inventory(source)==expected,'archive/source changed '+name);manifests[name]=expected
 (directory/'before-state.json').write_bytes(before);report={'status':'ACTUAL61-FULL-SCAN-RELEASE14-ARCHIVED','native_counter':61,'world_counter':19,'session':str(assets),'inventory':manifests,'prior_state_sha256':flow.sha(before),'fields':fields,'new_candidate':candidate_admission,'native_packet_sha256':PACKET61,'physical_evidence_hashes':PHYSICAL_HASHES,'new_signatures':0,'reboot_command':False}
 flow.save(directory/'retirement.json',report);sync_tree(directory)
 need(state_path.read_bytes()==before,'state changed before retirement')
 for name,source in sources.items():need(inventory(source)==manifests[name] and inventory(directory/name)==manifests[name],'source/archive changed before transition')
 after=dict(s);after['hardware_trial_pending']=None;after['last_hardware_trial_retirement']=str(directory/'retirement.json');flow.save(state_path,after);return after,directory
