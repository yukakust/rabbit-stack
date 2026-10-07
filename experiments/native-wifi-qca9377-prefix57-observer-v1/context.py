"""Read-only public artifact verification. Explicit paths only, no state/key loads."""
import base64,struct,re
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from decode_prefix import need,pairs,sha
import json
OWNER='622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac'
TARGET='363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9'
WORLD='fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74'
PACKAGE='f306120fdd548b6d4cc1d3915a13ae8cbe7848b162caa78528add353b9cb3f32'
POLICY={'owner':OWNER,'target':TARGET,'digest':'8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01','total':751436,'type':8,'version':84017153,'kind':1,'generation':57}
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
PROFILE='BOOT-PREFIX57-REPEATED-EFI-QEMU-WORLD18-DIAGNOSTIC-PASS'
REPO=Path(__file__).resolve().parents[2]
def read(p,limit=2000000):
 p=Path(p);need(p.is_file() and p.stat().st_size<=limit,'bounded actual file '+str(p));return p.read_bytes()
def load(p):
 return json.loads(read(p),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def local(directory,name):
 p=Path(directory)/name;need(p.resolve().parent==Path(directory).resolve(),'saved file escaped directory');return p

def verify_session(p,packet,kind,counter):
 s=load(p);stream=base64.b64decode(s['stream_base64'],validate=True)
 need(s.get('kind')==kind and s.get('counter')==counter and s.get('sha256')==sha(packet) and s.get('package_bytes')==len(packet),'saved transport context')
 need(len(stream)==len(packet)+32 and stream[32:]==packet and s.get('session_base64')==base64.b64encode(stream[:8]).decode(),'saved exact stream/session ID')
 return s

def commit_logs(report,directory):
 steps=report.get('sender_steps');need(isinstance(steps,list) and 0<len(steps)<=1000,'sender step bounds');found=False
 for s in steps:
  if s.get('name')!='commit':continue
  need(type(s.get('exit_code')) is int and s['exit_code']==0,'commit failed');log=read(local(directory,Path(s['log']).name))
  need(sha(log)==s.get('log_sha256') and b'FILE APPLIED RECEIPT (NOT ATTESTATION): exact SHA256/session/counter matched' in log,'actual applied correlated commit log');found=True
 need(found,'missing correlated commit log')

def verify_context(path):
 c=load(path);need(c.get('format')=='PREFIX57-PUBLIC-CONTEXT-1','explicit context schema')
 keys={'native_report','candidate_report','policy','asset_report','world_report','world_session','world_packet'}
 need(set(c.get('inputs',{}))==keys,'exact public input set');paths={};bindings={}
 for n,x in c['inputs'].items():
  need(set(x)=={'path','sha256'} and isinstance(x['path'],str) and Path(x['path']).is_absolute(),'absolute immutable context path')
  p=Path(x['path']);allowed={'native_report':{'report.json'},'candidate_report':{'report.json'},'policy':{'receiver-policy.json'},'asset_report':{'report.json'},'world_report':{'report.json'},'world_session':{'session.json','world-session.json'},'world_packet':{'world.rup'}}
  need(p.name in allowed[n] and '.rabbit-owner' not in p.parts,'explicit public artifact filename only');b=read(p);need(sha(b)==x['sha256'],'public input changed '+n);paths[n]=p;bindings[n]=sha(b)
 policy=load(paths['policy']);need(policy==POLICY,'exact generation57 RAM firmware policy')
 cand=load(paths['candidate_report']);need(cand.get('status')==PROFILE and cand.get('build_host')=='yukabox' and cand.get('native_counter')==57 and cand.get('physical_verified') is False and cand.get('signing_admitted') is False,'future checked prefix57 profile')
 need(cand.get('receiver_policy')==POLICY and cand.get('receiver_policy_sha256')==bindings['policy'] and cand.get('world_package_sha256')==PACKAGE and cand.get('world_semantic_sha256')==WORLD,'candidate exact policy/world binding')
 source=cand.get('source_sha256');need(isinstance(source,dict) and 0<len(source)<=2000,'candidate source closure required')
 for n,h in source.items():
  p=(REPO/n).resolve();need(not Path(n).is_absolute() and p.is_relative_to(REPO),'source escaped repo');need(sha(read(p,4000000))==h,'candidate source changed '+n)
 r=load(paths['native_report']);d=paths['native_report'].parent
 need(r.get('kind')=='native-read-only-pci' and r.get('status')=='EXACT-APPLIED-RECEIPT' and r.get('counter')==57 and r.get('receiver_reported_applied') is True,'actual57 applied report')
 need(r.get('gate',{}).get('report_sha256')==bindings['candidate_report'] and r.get('gate',{}).get('profile_status')==PROFILE,'native candidate report binding')
 need(Path(r['checked_directory']).resolve()==paths['candidate_report'].parent.resolve(),'native checked directory')
 packet=read(d/'native.rrt',262144);payload=read(d/'payload.efi',262144);session=d/'session.json'
 need(sha(payload)==r.get('payload_sha256')==cand.get('payload_sha256') and sha(packet)==r.get('package_sha256') and sha(read(session))==r.get('session_sha256'),'native packet/payload/session digest closure')
 need(len(packet)==len(payload)+256,'native envelope length');h=struct.unpack_from('<4sHHIIIIQ32s32s32s32s32s',packet)
 need(h[:8]==(b'RRT3',3,1,len(packet),len(payload),3,2,57) and h[8].hex()==TARGET and h[9].hex()==r['base_runtime_sha256'] and h[10].hex()==sha(payload) and h[11].hex()==PACKAGE and h[12].hex()==OWNER and packet[192:-64]==payload,'signed native exact header/body')
 need(r.get('base_world_sha256')==WORLD and r.get('world_package_sha256')==PACKAGE,'native current world18')
 Ed25519PublicKey.from_public_bytes(bytes.fromhex(OWNER)).verify(packet[-64:],b'Rabbit trusted runtime update v3\0'+packet[:-64]);verify_session(session,packet,2,57);commit_logs(r,d)
 world=read(paths['world_packet']);wr=load(paths['world_report'])
 need(len(world)>=128 and world[:6]==b'RUP5\x05\x00' and struct.unpack_from('<H',world,6)[0]==len(world) and struct.unpack_from('<I',world,8)[0]==18,'signed world18 envelope')
 Ed25519PublicKey.from_public_bytes(bytes.fromhex(OWNER)).verify(world[-64:],world[:-64])
 need(sha(world)==PACKAGE and wr.get('status')=='EXACT-APPLIED-RECEIPT' and wr.get('counter')==18 and wr.get('world_sha256')==WORLD and wr.get('package_sha256')==PACKAGE and wr.get('receiver_reported_applied') is True,'actual world18 applied receipt')
 need(sha(read(paths['world_session']))==wr.get('session_sha256'),'world18 session receipt binding');verify_session(paths['world_session'],world,1,18);commit_logs(wr,paths['world_report'].parent)
 a=load(paths['asset_report']);ad=paths['asset_report'].parent
 need(a.get('status')=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and a.get('native_counter')==57 and a.get('native_payload_sha256')==sha(payload) and a.get('completed_chunks')==12 and a.get('world_counter')==18 and a.get('world_sha256')==WORLD and a.get('policy')==POLICY,'actual full generation57 firmware context')
 need(a.get('gate')==r.get('gate') and Path(a['checked_directory']).resolve()==paths['candidate_report'].parent.resolve(),'asset exact same native gate')
 pp=a.get('packets');need(isinstance(pp,list) and len(pp)==12,'all12 saved signed firmware packets');whole=b'';accepted=[]
 steps=a.get('sender_steps');need(isinstance(steps,list) and 0<len(steps)<=2000,'asset logs bounded')
 for i,item in enumerate(pp):
  offset=i*65536;n=min(65536,751436-offset);need(item.get('file')==f'chunk-{i}.bin','packet exact order');b=read(ad/item['file'],65760)
  need(len(b)==n+224 and b[:8]==b'RABFW001' and b[8:40].hex()==TARGET and b[40:72].hex()==POLICY['digest'] and sha(b)==item.get('packet_sha256') and sha(b[224:])==b[72:104].hex() and b[140:160]==bytes(20),'packet body/envelope hash')
  need(struct.unpack_from('<IIIIQIII',b,104)==(751436,offset,n,65536,57,8,84017153,1),'packet exact generation/type/length')
  for k,v in {'offset':offset,'generation':57,'asset_bytes':751436,'asset_sha256':POLICY['digest'],'target_type':8,'target_version':84017153,'kind':1}.items():need(item.get(k)==v,'packet manifest field '+k)
  Ed25519PublicKey.from_public_bytes(bytes.fromhex(OWNER)).verify(b[160:224],b[:160]);whole+=b[224:]
  found=[]
  for s in steps:
   if s.get('chunk')!=i or type(s.get('exit_code')) is not int or s['exit_code']!=0:continue
   log=read(local(ad,Path(s['log']).name))
   for line in log.decode('utf-8').splitlines():
    try:q=json.loads(line,object_pairs_hook=pairs)
    except (ValueError,TypeError):continue
    if isinstance(q,dict) and q.get('action')==4 and q.get('packet_sha256')==sha(b):
     need(q.get('peripheral')==PEER and q.get('state')==2 and q.get('error')==0 and q.get('length')==n+224 and q.get('received')==n+224 and q.get('confirmed_floor')==n+224 and type(q.get('bitmap')) is int and 0<=q['bitmap']<=4095 and q['bitmap']&(1<<i) and q.get('device_attestation') is False,'correlated actual accepted chunk log')
     found.append((q,sha(log)))
  need(found,'no exact successful real receipt for chunk '+str(i));accepted.append(found[-1])
 need(sha(whole)==POLICY['digest'],'whole firmware exact hash')
 final=a.get('last_receipt');need(final==accepted[-1][0] and final.get('bitmap')==4095 and final.get('ready')==1,'final all12 ready receipt')
 return {'status':'PUBLIC57-NATIVE-WORLD18-ALL12-FIRMWARE-CONTEXT-VERIFIED','input_sha256':bindings,'payload_sha256':sha(payload),'firmware_receipt_log_sha256':[x[1] for x in accepted],'device_attestation':False,'state_read_or_written':False}
