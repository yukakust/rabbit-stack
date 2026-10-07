"""ROOT-only observed-context recovery. Tests use copied state, no keys or radio.
Archives precede the single hardware-pending retirement. No reboot API/claim.
"""
import base64,contextlib,datetime,fcntl,hashlib,importlib.util,json,os,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
ORIGINAL=REPO/'experiments/native-wifi-qca9377-v1/reboot_recovery.py'
ORIGINAL_SHA='af2e403b2cad44103946e0c5cfdb47064b43840de2ad2b475d870f67ef49424f'
spec=importlib.util.spec_from_file_location('public_prefix57_helpers',REPO/'experiments/native-wifi-qca9377-prefix57-admission-v1/gate.py');pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
sha=pub.sha;read=pub.read;require=pub.require;loads=pub.loads
PAYLOAD='9c63e6622c10190a8a17de2ff01ee03f72de95e93fd7326ca4da6e2c429be161'
PLAIN='0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce'
WORLD19='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7'
def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
@contextlib.contextmanager
def locked(state):
 with (state.parent/'state.lock').open('a') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ValueError('another state/controller owner')
  yield

def blob(directory,name,data):
 p=directory/pub.rel(name);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 return sha(data)
def syncdir(path):
 fd=os.open(path,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def atomic(path,data):
 with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:f.write(data);f.flush();os.fsync(f.fileno());tmp=Path(f.name)
 try:os.replace(tmp,path);syncdir(path.parent)
 finally:tmp.unlink(missing_ok=True)
def when(value):
 if isinstance(value,str):return datetime.datetime.fromisoformat(value).timestamp()
 require(type(value) in (int,float),'actual observation timestamp');return value

def observed_empty(state_raw,observation_raw,log,photo,now=None,allowed_before=None):
 s=loads(state_raw);o=loads(observation_raw);now=time.time() if now is None else now
 require(o.get('format')=='OWNER-PHOTO-BOOTSTRAP-OBSERVATION-1' and o.get('owner_confirmed_manual_reboot') is False and o.get('reboot_command_sent') is False,'observed context only; no fabricated human reboot')
 t=when(o.get('observed_at'));require(0<=now-t<=300,'fresh actual EMPTY<=300s; no timestamp reset')
 require(type(o.get('writes')) is int and o['writes']==0 and o.get('fresh_read_code')==0 and o.get('fresh_read_log_sha256')==sha(log) and o.get('photo_sha256')==sha(photo),'exact actual query/photo bindings')
 require(o.get('peripheral')==pub.PEER,'ROOT actual known-peer observation field required')
 require(o.get('state_before_sha256') in {sha(state_raw),allowed_before},'observed state context differs')
 require(not any(o.get(k) for k in ('fixture_kind','synthetic_only','test_clock')),'host fixture cannot authorize physical action')
 # Exact new diagnostic reader JSON callbacks, not a fabricated sender receipt.
 rows=[loads(line.encode()) for line in log.decode().splitlines() if line.strip()]
 values=[r.get('stage','') for r in rows if r.get('stage','').startswith('value bytes:')]
 require(values==['value bytes:60 hex:'+pub.EMPTY] and any(r.get('stage')=='read callback:52414242-4954-4649-8000-000000000004' and r.get('code')==0 for r in rows),'actual exact60 EMPTY callback')
 require(s['engine']['native_counter']==57 and s['engine']['payload_sha256']==PAYLOAD and s['counter']==18 and s['world_sha256']==pub.WORLD and s['package_sha256']==pub.PACKAGE,'saved exact57/world18 context')
 for k in ('pending','native_pending','recovery_pending'):require(k in s and s[k] is None,'competing controller '+k)
 return {'receiver_bootstrap_observed':True,'manual_reboot_confirmed':False,'reset_cause':'NOT_ESTABLISHED','observed_at':t,'query_sha256':sha(log),'photo_sha256':sha(photo),'physical_admission':False,'actual_all14_owner_release_proved':False,'ROM_ready_proved':False}

def public57(s):
 native=pub.within(Path(s['engine']['last_release_report']).parent,REPO);assets=pub.within(s['hardware_trial_pending'],REPO)
 r=loads(read(native/'report.json'));a=loads(read(assets/'report.json'));packet=read(native/'native.rrt');payload=read(native/'payload.efi');session=loads(read(native/'session.json'))
 require(r.get('status')=='EXACT-APPLIED-RECEIPT' and r.get('receiver_reported_applied') is True and r.get('counter')==57 and r.get('payload_sha256')==PAYLOAD and r.get('world_package_sha256')==pub.PACKAGE and r.get('base_world_sha256')==pub.WORLD,'actual APPLIED57 report')
 require(len(packet)==len(payload)+256 and sha(payload)==PAYLOAD and r['package_sha256']==sha(packet) and r['session_sha256']==sha(read(native/'session.json')),'native57 immutable bytes/session')
 h=pub.RRT.unpack_from(packet);require(h[:8]==(b'RRT3',3,1,len(packet),len(payload),3,2,57) and h[8].hex()==pub.TARGET and h[10].hex()==PAYLOAD and h[11].hex()==pub.PACKAGE and h[12].hex()==pub.OWNER and packet[192:-64]==payload,'signed57 context')
 public=pub.Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub.OWNER));public.verify(packet[-64:],b'Rabbit trusted runtime update v3\0'+packet[:-64])
 stream=base64.b64decode(session['stream_base64'],validate=True);require(session['kind']==2 and session['counter']==57 and stream[:32].hex()==sha(packet) and stream[32:]==packet,'saved native57 signed session')
 require(a.get('native_counter')==57 and a.get('native_payload_sha256')==PAYLOAD and a.get('world_counter')==18 and a.get('world_sha256')==pub.WORLD and a.get('policy')==pub.POLICY and a.get('completed_chunks')==10 and len(a.get('packets',[]))==12,'partial57 actual10/full12 saved policy')
 receipt=a['last_receipt'];require(receipt.get('bitmap')==1023 and receipt.get('ready')==0 and receipt.get('error')==0 and receipt.get('peripheral')==pub.PEER and receipt.get('received')==receipt.get('length')==receipt.get('confirmed_floor')==65760,'last accepted10 context')
 data=[]
 for i,item in enumerate(a['packets']):
  require(item['file']==f'chunk-{i}.bin','ordered saved12');p=read(assets/item['file']);n=min(65536,751436-i*65536)
  require(len(p)==224+n and p[:8]==b'RABFW001' and p[8:40].hex()==pub.TARGET and p[40:72].hex()==pub.POLICY['digest'] and p[72:104].hex()==sha(p[224:]) and not any(p[140:160]),'asset envelope/hash')
  require(pub.struct.unpack_from('<IIIIQIII',p,104)==(751436,i*65536,n,65536,57,8,84017153,1) and item['packet_sha256']==sha(p),'asset generation/order/metadata')
  public.verify(p[160:224],p[:160]);data.append(p[224:])
 require(sha(b''.join(data))==pub.POLICY['digest'] and receipt['packet_sha256']==a['packets'][9]['packet_sha256'],'full saved firmware plus actual accepted10 receipt')
 pub.source_world18(loads(read(s['world'])),read(s['package']))
 return native,assets,{'native_packet_sha256':sha(packet),'asset_report_sha256':sha(read(assets/'report.json')),'completed_before_context_loss':10,'saved_public_packets_verified':12,'native_counter':57,'world_counter':18}

def retire(state_path,before,observation,query_log,photo,output):
 state_path,before,observation,query_log,photo,output=map(lambda p:Path(p).resolve(),(state_path,before,observation,query_log,photo,output))
 require(state_path!=before and not output.exists() and output.parent.is_dir(),'separate before/new archive')
 with locked(state_path):
  require(sha(read(ORIGINAL))==ORIGINAL_SHA,'original frozen source changed')
  raw=read(state_path);require(raw==read(before),'exact unchanged before-state');s=loads(raw);native,assets,bundle=public57(s)
  require(not output.is_relative_to(native) and not output.is_relative_to(assets),'preserve originals')
  journal=state_path.parent/'control/journal.json';jraw=read(journal);require(not loads(jraw).get('active'),'world journal active')
  obs,log,image=read(observation),read(query_log),read(photo,10_000_000);proof=observed_empty(raw,obs,log,image)
  require(not any(x.get('native_counter')==57 for x in s.get('retired_hardware_trials',[])),'already retired57')
  output.mkdir(exist_ok=False);manifest={}
  for name,data in [('before-state.json',raw),('before-journal.json',jraw),('observation.json',obs),('query.log',log),('owner-screen.png',image)]:manifest[name]=blob(output,name,data)
  for label,directory in [('native57',native),('assets57',assets)]:
   for p in sorted(directory.iterdir()):
    if p.is_file():manifest[label+'/'+p.name]=blob(output,label+'/'+p.name,read(p,10_000_000))
  for name,path in [('world18/world.json',s['world']),('world18/world.rup',s['package'])]:manifest[name]=blob(output,name,read(path))
  audit={'status':'PARTIAL57-RETIRED-AFTER-OBSERVED-BOOTSTRAP-EMPTY','native_counter':57,'original_state_path':str(state_path),'original_asset_session':str(assets),'original_native_session':str(native),'before_state_sha256':sha(raw),'archive_sha256':manifest,'proof':proof,'public_bundle':bundle,'manual_reboot_confirmed':False,'reset_cause':'NOT_ESTABLISHED','source_sha256':{str(ORIGINAL):sha(read(ORIGINAL)),str(ROOT/'route.py'):sha(read(ROOT/'route.py')),str(ROOT/'restore_observed.py'):sha(read(ROOT/'restore_observed.py')),str(pub.__file__):sha(read(pub.__file__))}}
  auditraw=encoded(audit);blob(output,'retirement.json',auditraw)
  after=loads(raw);after['hardware_trial_pending']=None;after.setdefault('retired_hardware_trials',[]).append({'session':str(assets),'native_counter':57,'reason':'observed-bootstrap-empty-partial57-retired-cause-unknown-NO-human-reboot','retirement_sha256':sha(auditraw),'retirement_report':str(output/'retirement.json')})
  afterraw=encoded(after);blob(output,'after-state.json',afterraw)
  for d in sorted([p for p in output.rglob('*') if p.is_dir()]+[output],key=lambda p:len(p.parts),reverse=True):syncdir(d)
  syncdir(output.parent);require(read(state_path)==raw and read(journal)==jraw,'state/journal changed during archive');observed_empty(raw,obs,log,image)
  atomic(state_path,afterraw);return audit

def verify_retirement(state_path,audit_path):
 raw=read(state_path);s=loads(raw);a=loads(read(audit_path));d=Path(audit_path).parent
 require(a['status']=='PARTIAL57-RETIRED-AFTER-OBSERVED-BOOTSTRAP-EMPTY' and a['manual_reboot_confirmed'] is False and a['original_state_path']==str(Path(state_path).resolve()),'exact observed retirement')
 for n,h in a['archive_sha256'].items():require(sha(read(d/pub.rel(n),10_000_000))==h,'archive changed '+n)
 for n,h in a['source_sha256'].items():require(sha(read(n))==h,'recovery source changed')
 require(sha(read(ORIGINAL))==ORIGINAL_SHA,'original recovery changed')
 expected=loads(read(d/'before-state.json'));expected['hardware_trial_pending']=None
 expected.setdefault('retired_hardware_trials',[]).append({'session':a['original_asset_session'],'native_counter':57,'reason':'observed-bootstrap-empty-partial57-retired-cause-unknown-NO-human-reboot','retirement_sha256':sha(read(audit_path)),'retirement_report':str(Path(audit_path).resolve())})
 require(s==expected and raw==read(d/'after-state.json'),'only intended atomic retirement transition; counters remain57/18')
 return a,d

def activation_proof(state_path,path):
 proof=loads(read(path));a,d=verify_retirement(state_path,Path(proof['retirement']))
 require(proof.get('retirement_sha256')==sha(read(proof['retirement'])),'exact activation retirement digest')
 require(proof.get('state_sha256')==sha(read(state_path)) and proof.get('receiver_bootstrap_observed') is True and proof.get('manual_reboot_confirmed') is False,'activation state/observed facts')
 observed_empty(read(state_path),read(proof['observation']),read(proof['query_log']),read(proof['photo'],10_000_000),allowed_before=a['before_state_sha256'])
 return proof

def resume_proof(report):
 path=Path(report['bootstrap_proof']);require(sha(read(path))==report['bootstrap_proof_sha256'],'saved activation proof changed')
 proof=loads(read(path));require(proof.get('manual_reboot_confirmed') is False and proof.get('receiver_bootstrap_observed') is True,'no fake human reboot on resume')
 audit=Path(proof['retirement']);require(sha(read(audit))==proof.get('retirement_sha256'),'saved retirement audit changed');a=loads(read(audit));require(a['manual_reboot_confirmed'] is False,'retirement human claim')
 for n,h in a['source_sha256'].items():require(sha(read(n))==h,'resume source changed')
 for n,h in a['archive_sha256'].items():require(sha(read(audit.parent/pub.rel(n),10_000_000))==h,'resume archive changed')

def guarded_prepare(state_path,checked,directory,private,bootstrap_proof,_recovery=None):
 require(sha(read(ORIGINAL))==ORIGINAL_SHA,'original prepare source changed')
 if _recovery is None:
  import sys;sys.path.insert(0,str(ORIGINAL.parent));import reboot_recovery as recovery
 else:recovery=_recovery
 oldgate=recovery.gate;oldload=recovery.engine.load_private
 def check():
  activation_proof(Path(state_path),bootstrap_proof)
  require(sha(read(ORIGINAL))==ORIGINAL_SHA,'original changed before key boundary')
 def boundgate(*args):
  check();payload,report=oldgate(*args)
  require(sha(payload)==PLAIN and report.get('restored_package_sha256')==WORLD19,'same proven plain city/world19 restoration')
  return payload,report
 def boundload(*args):check();return oldload(*args)
 recovery.gate=boundgate;recovery.engine.load_private=boundload
 try:
  check();return recovery.prepare(Path(state_path),Path(checked),Path(directory),private)
 finally:recovery.gate=oldgate;recovery.engine.load_private=oldload
