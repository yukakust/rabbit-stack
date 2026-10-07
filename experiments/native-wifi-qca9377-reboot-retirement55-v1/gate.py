"""Read-only public-byte evidence gate. No state writer, radio, signing or key loader.

An eligible result is conditional evidence for ROOT's separately locked action;
it neither retires the pending trial nor authorizes a reboot or reserves counter56.
"""
import base64
import hashlib
import json
import math
import struct
import time
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
OWNER=bytes.fromhex('622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac')
TARGET='363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9'
PAYLOAD='cc8d7fec39a812273c1af5d52711fe6dc281b48873925aec2136cf3cb8533297'
WORLD='fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74'
NATIVE_REPORT='66f4c2756b40f43ed5f34b76be53f4df2a7546bdfc8bdc25ca09f309b6e6e77a'
ASSET_REPORT='652420aeb05bf34a9823658dee3e0dc833adc7479de512258c85ae7242afd1b6'
PACKAGE='47d63aa6e81b35fc355005cf65f889b9c43bc332443e37ddbba672b920c2fc2b'
ASSET='8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01'
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
EMPTY='52465301'+'00'*56
HEADER=struct.Struct('<4sHHIIIIQ32s32s32s32s32s')
sha=lambda b:hashlib.sha256(b).hexdigest()
def require(ok,why):
 if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_bytes())
def files(directory,names):return {n:sha((directory/n).read_bytes()) for n in names}
def safe(name):
 p=Path(name);require(not p.is_absolute() and '..' not in p.parts,'unsafe relative evidence path');return p

def public_bundle(repo,native,assets,checked,world):
 """Verify archived/public bytes only, including both signature domains."""
 repo,native,assets,checked=map(Path,(repo,native,assets,checked));world=Path(world).read_bytes()
 r=read(native/'report.json');s=read(native/'session.json');a=read(assets/'report.json');c=read(checked/'report.json')
 require(sha((native/'report.json').read_bytes())==NATIVE_REPORT and sha((assets/'report.json').read_bytes())==ASSET_REPORT,'pinned actual55 applied/full12 reports')
 payload=(native/'payload.efi').read_bytes();packet=(native/'native.rrt').read_bytes();h=HEADER.unpack_from(packet)
 require(len(packet)==len(payload)+256<=262144 and h[:8]==(b'RRT3',3,1,len(packet),len(payload),3,2,55),'native55 layout/counter')
 require(h[8].hex()==TARGET and h[9].hex()==r['base_runtime_sha256'] and h[10].hex()==PAYLOAD and h[11].hex()==sha(world) and h[12]==OWNER,'native55 owner/target/base/world')
 require(packet[192:-64]==payload and sha(payload)==PAYLOAD and sha(world)==PACKAGE,'native55 payload/world bytes')
 Ed25519PublicKey.from_public_bytes(OWNER).verify(packet[-64:],b'Rabbit trusted runtime update v3\0'+packet[:-64])
 require(r['status']=='EXACT-APPLIED-RECEIPT' and r['kind']=='native-read-only-pci' and r['counter']==55 and r['base_world_sha256']==WORLD and r['world_package_sha256']==PACKAGE,'native55 report')
 require(sha(packet)==r['package_sha256'] and sha((native/'session.json').read_bytes())==r['session_sha256'] and s['counter']==55 and s['kind']==2 and base64.b64decode(s['stream_base64'],validate=True)[32:]==packet,'native55 session')
 require(c['status']=='SCAN55-REPEATED-FULL-EFI-QEMU-WORLD17-OWNED-EXPORT-PASS' and c['payload_sha256']==PAYLOAD and len(c['source_sha256'])==642 and sha((checked/'payload.efi').read_bytes())==PAYLOAD,'native55 checked642')
 require(sha((checked/'report.json').read_bytes())==r['gate']['report_sha256']==a['gate']['report_sha256'],'native55 checked report hash')
 for n,v in c['source_sha256'].items():require(sha((repo/safe(n)).read_bytes())==v,'source changed: '+n)
 policy={'owner':OWNER.hex(),'target':TARGET,'digest':ASSET,'total':751436,'type':8,'version':84017153,'kind':1,'generation':55}
 require(a['policy']==policy and a['native_counter']==55 and a['native_payload_sha256']==PAYLOAD and a['world_counter']==17 and a['world_sha256']==WORLD,'asset policy/native/world')
 require(a['status']=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and a['completed_chunks']==12 and len(a['packets'])==12 and not a.get('reboot_retirement_sha256'),'full12 unretired assets')
 joined=bytearray();packet_hashes={}
 for i,item in enumerate(a['packets']):
  require(item['file']==f'chunk-{i}.bin','ordered exact12 names');p=(assets/item['file']).read_bytes()
  require(224<len(p)<=65760 and p[:8]==b'RABFW001' and p[8:40].hex()==TARGET and p[40:72].hex()==ASSET and not any(p[140:160]),'asset envelope')
  total,offset,length,chunk,gen,typ,ver,kind=struct.unpack_from('<IIIIQIII',p,104)
  require((total,offset,length,chunk,gen,typ,ver,kind)==(751436,i*65536,min(65536,751436-i*65536),65536,55,8,84017153,1) and len(p)==224+length and sha(p[224:])==p[72:104].hex(),'asset layout/body')
  Ed25519PublicKey.from_public_bytes(OWNER).verify(p[160:224],p[:160]);joined.extend(p[224:])
  expected={'packet_sha256':sha(p),'asset_sha256':ASSET,'offset':offset,'asset_bytes':total,'generation':55,'target_type':8,'target_version':84017153,'kind':1}
  require(expected=={k:v for k,v in item.items() if k!='file'},'saved asset metadata');packet_hashes[item['file']]=sha(p)
  checkpoint=read(assets/(item['file']+'.checkpoint.json'))
  require(checkpoint['packet_sha256']==sha(p) and checkpoint['floor']==len(p),'saved exact full12 checkpoint')
  packet_hashes[item['file']+'.checkpoint.json']=sha((assets/(item['file']+'.checkpoint.json')).read_bytes())
 require(sha(joined)==ASSET,'full firmware container digest')
 receipt=a['last_receipt'];require(receipt['peripheral']==PEER and receipt['error']==0 and receipt['bitmap']==4095 and receipt['ready']==1 and receipt['state']==2 and receipt['packet_sha256']==packet_hashes['chunk-11.bin'] and receipt['received']==receipt['length']==receipt['confirmed_floor']==30764,'actual final12 receipt')
 return {'native':files(native,('report.json','session.json','native.rrt','payload.efi')),'assets':{'report.json':sha((assets/'report.json').read_bytes()),**packet_hashes},'checked_report_sha256':sha((checked/'report.json').read_bytes()),'source_count':642,'world_package_sha256':PACKAGE,'world_semantic_sha256':WORLD,'native_counter':55,'next_native_counter_candidate':56,'physical_release_proved':False,'raw55_recovered':False,'state_written':False,'signing_admitted':False}

def archived_state(state_bytes,bundle,native_path,asset_path):
 require(bundle.get('native_counter')==55 and bundle.get('source_count')==642 and bundle.get('native',{}).get('report.json')==NATIVE_REPORT and bundle.get('assets',{}).get('report.json')==ASSET_REPORT,'verified exact public55 bundle required')
 s=json.loads(state_bytes);require(not any(s.get(k) for k in ('pending','native_pending','recovery_pending')),'competing state operation')
 e=s['engine'];require(e['native_counter']==55 and e['payload_sha256']==PAYLOAD and s['counter']==17 and s['world_sha256']==WORLD and s['package_sha256']==PACKAGE,'state native/world binding')
 require(s['hardware_trial_pending']==str(asset_path) and e['last_release_report']==str(Path(native_path)/'report.json'),'exact pending/completed paths')
 return sha(state_bytes)

def conditional_retirement(state_bytes,bundle,native_path,asset_path,authorization_bytes,observation_bytes,query_log,now=None):
 """No mutation. ROOT must archive inputs and recheck under its lock before action.
 now override is for deterministic HOST tests only; CLI uses wall clock.
 """
 state_hash=archived_state(state_bytes,bundle,native_path,asset_path);a=json.loads(authorization_bytes);o=json.loads(observation_bytes)
 require(a.get('explicit_owner_authorization') is True and a.get('action')=='controlled-dell-reboot-for-native55-recovery' and a.get('native_counter')==55 and a.get('state_before_sha256')==state_hash and isinstance(a.get('owner_message_reference'),str) and bool(a['owner_message_reference'].strip()),'explicit owner reboot authorization bound to state')
 require(o.get('owner_confirmed_reboot') is True and o.get('authorization_sha256')==sha(authorization_bytes),'actual reboot confirmation/auth binding')
 now=time.time() if now is None else now;t=o.get('observed_at');rt=o.get('reboot_confirmed_at')
 require(type(t) in (int,float) and type(rt) in (int,float) and math.isfinite(t) and math.isfinite(rt) and 0<=now-t<=300 and rt<=t and rt>=a.get('authorized_at',float('inf')),'fresh observation after authorized actual reboot')
 r=o.get('receiver',{});require(o.get('peripheral')==PEER and type(o.get('writes')) is int and o['writes']==0 and r.get('raw_hex')==EMPTY and r.get('outcome')=='idle' and type(r.get('counter')) is int and r['counter']==0,'fresh actual known-peer EMPTY/counter0')
 require(o.get('log_sha256')==sha(query_log) and bool(query_log),'exact nonempty query log')
 return {'status':'CONDITIONAL-FULL55-REBOOT-RETIREMENT-EVIDENCE-PASS','archive_required':{'before-state.json':state_hash,'authorization.json':sha(authorization_bytes),'observation.json':sha(observation_bytes),'query.log':sha(query_log)},'bundle':bundle,'next_native_counter_candidate':56,'pending_cleared':False,'device_writes':0,'private_key_loads':0,'reboot_performed_by_gate':False,'actual_all_owner_release_claimed':False,'physical_admission':False,'raw55_lost_after_reboot':True}

def main():
 import argparse
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('repo','native','assets','checked','world','archived-state'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--authorization',type=Path);p.add_argument('--observation',type=Path);p.add_argument('--query-log',type=Path)
 args=p.parse_args()
 # No implicit production-state path and no test clock override in CLI.
 require(args.archived_state.name=='before-state.json','explicit archived before-state.json required')
 require(args.archived_state.resolve()!=args.repo.resolve()/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json','production state prohibited')
 b=public_bundle(args.repo,args.native,args.assets,args.checked,args.world);s=args.archived_state.read_bytes()
 h=archived_state(s,b,args.native,args.assets)
 if any((args.authorization,args.observation,args.query_log)):
  require(all((args.authorization,args.observation,args.query_log)),'complete actual recovery evidence required')
  result=conditional_retirement(s,b,args.native,args.assets,args.authorization.read_bytes(),args.observation.read_bytes(),args.query_log.read_bytes())
 else:result={'status':'READ-ONLY-RECOVERY55-PLAN-BINDINGS-PASS','state_before_sha256':h,'bundle':b,'reboot_authorized':False,'pending_cleared':False,'physical_admission':False,'private_key_loads':0,'device_writes':0}
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
