"""Public/read-only prefix57 preparation gate. Never signs, writes state or uses BLE.
Every output remains conditional with physical_admission=False. ROOT must obtain
fresh real observation and recheck identical inputs under its operation lock.
"""
import base64,hashlib,json,math,re,struct,time
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
OWNER='622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac'
CREATOR_PUBLIC='03a107bff3ce10be1d70dd18e74bc09967e4d6309ba50d5f1ddc8664125531b8'
TARGET='363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9'
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
WORLD='fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74'
PACKAGE='f306120fdd548b6d4cc1d3915a13ae8cbe7848b162caa78528add353b9cb3f32'
PAYLOAD56='0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce'
PACKET56='dbb0c8b918c924386cbcf959a63cabd1c456c42f2121d23c43c333e5b685f09d'
POLICY={'owner':OWNER,'target':TARGET,'digest':'8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01','total':751436,'type':8,'version':84017153,'kind':1,'generation':57}
FROZEN_REPORT_SHA='c362eb73bdfa96cef85962db9d625d6aa9664476f8b47b44fb60756f6f5099d1'  # Parent-confirmed final actual proof.
PROFILE_STATUS='BOOT-PREFIX57-REPEATED-EFI-QEMU-WORLD18-DIAGNOSTIC-PASS'
NATIVE_STATUS='BOOT-PREFIX57-ACTUAL-DRIVER-PCI-CE-USB-OVERLAY-ASAN-COFF-PASS'
RRT=struct.Struct('<4sHHIIIIQ32s32s32s32s32s')
EMPTY='52465301'+'00'*56
sha=lambda b:hashlib.sha256(b).hexdigest()
def require(v,why):
 if not v:raise ValueError(why)
def pairs(items):
 d={}
 for k,v in items:require(k not in d,'duplicate JSON key');d[k]=v
 return d
def loads(raw):
 require(len(raw)<=2_000_000,'JSON budget');return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def read(path,max_bytes=2_000_000):
 p=Path(path).resolve();require(p.is_relative_to(REPO.resolve()),'public input escaped repository');require(p.stat().st_size<=max_bytes,'file budget');return p.read_bytes()
def within(path,scope):
 p=Path(path).resolve();require(p.is_relative_to(Path(scope).resolve()),'path escaped scope');return p
def rel(path):
 p=Path(path);require(not p.is_absolute() and '..' not in p.parts and p.parts,'unsafe relative path');return p
def digest(h):require(isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h),'digest shape');return h
def source_closure(mapping,repo):
 require(isinstance(mapping,dict) and 0<len(mapping)<=2000,'source closure budget')
 for n,h in mapping.items():require(sha(read(within(Path(repo)/rel(n),repo),4_000_000))==digest(h),'source hash differs: '+n)
 return len(mapping)
def pe_caps(payload):
 require(64<=len(payload)<=262144 and payload[:2]==b'MZ','EFI immutable file cap/MZ')
 off,=struct.unpack_from('<I',payload,60);require(off<=len(payload)-104,'PE header bounds')
 require(payload[off:off+4]==b'PE\0\0','PE signature')
 machine,sections=struct.unpack_from('<HH',payload,off+4);optional,=struct.unpack_from('<H',payload,off+20)
 require(machine==0x8664 and 1<=sections<=16 and optional>=112 and off+24+optional+40*sections<=len(payload),'exact bounded x86-64 EFI headers')
 require(struct.unpack_from('<H',payload,off+24)[0]==0x20b,'PE32+ ABI')
 mapped,=struct.unpack_from('<I',payload,off+80);require(0<mapped<=4*1024*1024,'mapped EFI cap')
 return mapped

def source_world18(world,packet):
 """Pure unsigned SOURCE encoder oracle, no parser-generated placeholder names,
 no importing flow/CREATOR and no signer. Layout matches pinned scene5/city_world.
 Existing public signature is verified then carried unchanged into reproduction.
 """
 require(isinstance(world,dict) and world.get('schema_version')==5,'source RUP5 schema')
 require(sha(json.dumps(world,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==WORLD,'exact source semantic hash, including names')
 require(128<=len(packet)<=6816 and packet[:6]==b'RUP5\x05\x00' and struct.unpack_from('<H',packet,6)[0]==len(packet) and struct.unpack_from('<I',packet,8)[0]==18,'exact RUP5 world18 envelope/counter')
 Ed25519PublicKey.from_public_bytes(bytes.fromhex(CREATOR_PUBLIC)).verify(packet[-64:],packet[:-64])
 buildings=world['buildings'];actors=world['actors'];require(1<=len(buildings)<=64 and len(actors)<=4 and sum(len(a['parts']) for a in actors)<=96,'bounded source geometry')
 body=bytearray(32+32*len(buildings));body[:5]=b'RUP5\x05';struct.pack_into('<I',body,8,18);body[12]=len(buildings);body[13]=len(actors);struct.pack_into('<H',body,14,32)
 c=world['camera'];struct.pack_into('<hHhB',body,16,c['x'],c['y'],c['z'],c['yaw']);struct.pack_into('<II',body,24,int(world['sky'],16),int(world['ground'],16))
 for i,b in enumerate(buildings):
  p=b['position'];z=b['size'];struct.pack_into('<HBBhhhHHHII',body,32+32*i,b['id'],['house','box','road'].index(b['kind'])+1,0,p['x'],p['y'],p['z'],z['width'],z['height'],z['depth'],int(b['wall'],16),int(b['roof'],16))
 for a in actors:
  p=a['position'];body+=struct.pack('<HBBhHh6x',a['id'],a['yaw'],len(a['parts']),p['x'],p['y'],p['z'])
  for part in a['parts']:
   p=part['position'];z=part['size'];m=part['motion'];v=part['visibility']
   body+=struct.pack('<BBHhhhHHHIhhhHHHHH12x',['ellipsoid','box','cone'].index(part['shape'])+1,['always','inside','outside'].index(v['mode']),0,p['x'],p['y'],p['z'],z['width'],z['height'],z['depth'],int(part['color'],16),m['x'],m['y'],m['z'],m['period_ms'],m['phase_ms'],v['period_ms'],v['duration_ms'],v['delay_ms'])
 struct.pack_into('<H',body,6,len(body)+64)
 reproduced=bytes(body)+packet[-64:];require(reproduced==packet,'exact source-to-world18 complete bytes reproduction without signing')
 return {'world_creator_public':CREATOR_PUBLIC,'source_semantic_sha256':WORLD,'packet_sha256':sha(packet),'counter':18,'byte_reproduction':True,'signing_performed':False}

def native_public56(plan):
 plan=Path(plan).resolve();report_bytes=read(plan/'report.json');r=loads(report_bytes);prepared=loads(read(plan/'plan.json'))
 require(r.get('status')=='APPLIED' and r.get('kind')=='owner-reboot-city-recovery' and r.get('counter')==56 and r.get('world_counter')==18,'actual56 APPLIED plan')
 for key in ('owner_confirmed_reboot','engine_done','world_done','receiver_reported_applied'):require(r.get(key) is True,'actual applied flag '+key)
 require(prepared.get('status')=='PREPARED-NOT-ACTIVATED' and prepared.get('counter')==56 and prepared.get('files')==r.get('files'),'same immutable prepared signed plan')
 require(set(r['files'])=={'before-state.json','world.json','world.rup','native.rrt','payload.efi','session.json','world-session.json'},'exact prepared file closure')
 for n,h in r['files'].items():require(sha(read(plan/rel(n)))==digest(h),'saved56 file changed '+n)
 packet=read(plan/'native.rrt');payload=read(plan/'payload.efi');world=read(plan/'world.rup');session=loads(read(plan/'session.json'))
 require(len(packet)==len(payload)+256 and len(packet)<=262144 and sha(packet)==PACKET56 and sha(payload)==PAYLOAD56 and sha(world)==PACKAGE,'exact56 immutable packet/payload/world18')
 h=RRT.unpack_from(packet);require(h[:8]==(b'RRT3',3,1,len(packet),len(payload),3,2,56),'RRT56 header')
 require(h[8].hex()==TARGET and h[10].hex()==PAYLOAD56 and h[9].hex()=='02e3a839f5c4320754a7afa6fecc6ca626475d36c360f3ed66cdd6db30e7b4c3' and h[11].hex()==sha(b'') and h[12].hex()==OWNER and packet[192:-64]==payload,'RRT56 target/body/owner/world')
 Ed25519PublicKey.from_public_bytes(bytes.fromhex(OWNER)).verify(packet[-64:],b'Rabbit trusted runtime update v3\0'+packet[:-64])
 stream=base64.b64decode(session['stream_base64'],validate=True)
 require(session.get('counter')==56 and session.get('kind')==2 and session.get('sha256')==PACKET56 and session.get('package_bytes')==len(packet) and len(stream)==len(packet)+32 and stream[32:]==packet,'exact56 saved signed session')
 sid=base64.b64decode(session['session_base64'],validate=True);require(len(sid)==8 and base64.b64encode(sid).decode()==session['session_base64'] and stream[:32].hex()==PACKET56,'native session identifier/hash prefix')
 wr=loads(read(plan/'restored-world/report.json'));ws=loads(read(plan/'world-session.json'))
 require(wr.get('status')=='EXACT-APPLIED-RECEIPT' and wr.get('counter')==18 and wr.get('world_sha256')==WORLD and wr.get('package_sha256')==PACKAGE and wr.get('receiver_reported_applied') is True,'actual18 applied world report')
 require(sha(read(plan/'restored-world/world.rup'))==PACKAGE and sha(read(plan/'restored-world/session.json'))==sha(read(plan/'world-session.json'))==wr['session_sha256'],'world18 exact saved package/session')
 require(ws.get('counter')==18 and ws.get('kind')==1 and ws.get('sha256')==PACKAGE,'world18 session context')
 worldstream=base64.b64decode(ws['stream_base64'],validate=True);require(len(worldstream)==len(world)+32 and worldstream[32:]==world and worldstream[:32].hex()==PACKAGE,'world18 transport session')
 worldsid=base64.b64decode(ws['session_base64'],validate=True);require(len(worldsid)==8 and base64.b64encode(worldsid).decode()==ws['session_base64'],'world18 exact session identifier');require(ws['package_bytes']==len(world),'world18 session length');source_world18(loads(read(plan/'world.json')),world)
 for directory,report in ((plan,r),(plan/'restored-world',wr)):
  steps=report.get('sender_steps',[]);require(any(s.get('name')=='commit' for s in steps),'actual commit log required')
  for s in steps:
   require(type(s.get('exit_code')) is int and s['exit_code']==0 and Path(s['log']).name.endswith('.log'),'successful sender step')
   blob=read(directory/Path(s['log']).name);require(sha(blob)==s['log_sha256'],'saved applied step log hash')
   if s['name']=='commit':require(b'FILE APPLIED RECEIPT (NOT ATTESTATION): exact SHA256/session/counter matched' in blob,'correlated applied log')
 return {'plan_path':str(plan),'plan_report_sha256':sha(report_bytes),'payload_sha256':PAYLOAD56,'packet_sha256':PACKET56,'world_session_id_hex':worldsid.hex(),'world_package_bytes':len(world),'world_stream_bytes':len(worldstream),'one_saved_signed_packet_verified':True,'signer_invocation_count_proved':False}

def rfs(raw_hex):
 require(isinstance(raw_hex,str) and re.fullmatch('[0-9a-f]{120}',raw_hex),'exact60-byte RFS hex')
 raw=bytes.fromhex(raw_hex);require(raw[:4]==b'RFS\x01','RFS version')
 sid,received,length=struct.unpack_from('<8sII',raw,4);state,error=raw[20:22];counter=struct.unpack_from('<I',raw,24)[0]
 require(raw[22:24]==b'\0\0' and state<=4 and received<=length<=262176,'RFS reserved/state/length envelope')
 return {'session_id_hex':sid.hex(),'received':received,'length':length,'state':state,'error':error,'counter':counter,'sha256':raw[28:].hex()}
def query_match(log,observation,expected,session_id=None):
 require(len(log)<=2_000_000 and len(log)>0,'bounded query log');text=log.decode('utf-8')
 require('READ-ONLY CACHED CONNECT: '+PEER+' (not identity authentication)' in text and 'READ-ONLY QUERY: no BEGIN, DATA, COMMIT or ABORT' in text,'actual known-peer read-only query markers')
 require(not any(x in text for x in ('BEGIN: acknowledged write','FILE APPLIED RECEIPT','DATA CHUNK LIMIT=')),'write trace not allowed as read-only evidence')
 matches=re.findall(r'^RFS STATUS HEX=([0-9a-f]+)$',text,re.M);require(len(matches)==1,'exact one raw query status')
 require(matches[0]==observation['receiver']['raw_hex'],'observation raw/log correlation')
 decoded=rfs(matches[0]);require({k:decoded[k] for k in expected}==expected,'raw receiver context')
 if session_id is not None:require(decoded['session_id_hex']==session_id,'exact world18 saved session identifier')
 for k in ('received','length','state','error','counter','sha256'):require(observation['receiver'].get(k)==decoded[k],'decoded observation field '+k)
 require(observation.get('peripheral')==PEER and type(observation.get('writes')) is int and observation['writes']==0,'exact known peer zero writes')
 require(observation['receiver'].get('device_attestation') is False,'receipt is not attestation')
 return decoded

def retirement55(audit_path,state,plan):
 audit_path=Path(audit_path).resolve();directory=audit_path.parent;raw=read(audit_path);a=loads(raw)
 require(a.get('status')=='FULL55-RAM-TRIAL-RETIRED-AFTER-AUTHORIZED-OWNER-REBOOT' and a.get('native_counter')==55 and a.get('completed_chunks_before_reboot')==12,'actual full55 retirement audit')
 require(a.get('actual_all14_owner_release_proved') is False and a.get('raw55_exports')=='NOT_CAPTURED-LOST-AFTER-OWNER-REBOOT','honest historical lost raw55, no false owner release')
 manifest=a.get('archive_sha256');require(isinstance(manifest,dict) and 1<=len(manifest)<=1000,'retirement archive bound')
 for n,h in manifest.items():require(sha(read(within(directory/rel(n),directory),4_000_000))==digest(h),'retirement archive changed '+n)
 for n,h in a['source_sha256'].items():require(sha(read(within(n,REPO),4_000_000))==digest(h),'retirement source changed')
 # Archived native55 and all12 public firmware signatures remain verifiable
 # after reboot, even though their actual RAM/raw observations are lost.
 oldpacket=read(directory/'native55/native.rrt');oldpayload=read(directory/'native55/payload.efi');oldreport=loads(read(directory/'native55/report.json'))
 require(len(oldpacket)==len(oldpayload)+256 and oldpacket[192:-64]==oldpayload and sha(oldpayload)==a.get('native_payload_sha256'),'archived55 exact payload')
 oldh=RRT.unpack_from(oldpacket);require(oldh[:8]==(b'RRT3',3,1,len(oldpacket),len(oldpayload),3,2,55) and oldh[8].hex()==TARGET and oldh[12].hex()==OWNER and oldh[10].hex()==sha(oldpayload),'archived55 signed native header')
 require(oldreport.get('status')=='EXACT-APPLIED-RECEIPT' and oldreport.get('receiver_reported_applied') is True and oldreport.get('counter')==55 and oldreport.get('package_sha256')==sha(oldpacket),'archived55 exact applied native report')
 public=Ed25519PublicKey.from_public_bytes(bytes.fromhex(OWNER));public.verify(oldpacket[-64:],b'Rabbit trusted runtime update v3\0'+oldpacket[:-64])
 assets=loads(read(directory/'assets55/report.json'));require(assets.get('status')=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and assets.get('completed_chunks')==12 and assets.get('policy')=={**POLICY,'generation':55},'archived55 exact full12 policy')
 parts=[]
 for i in range(12):
  part=read(directory/f'assets55/chunk-{i}.bin');nbytes=min(65536,751436-i*65536)
  require(len(part)==224+nbytes and part[:8]==b'RABFW001' and part[8:40].hex()==TARGET and part[40:72].hex()==POLICY['digest'] and part[72:104].hex()==sha(part[224:]) and not any(part[140:160]),'archived55 asset envelope/body')
  require(struct.unpack_from('<IIIIQIII',part,104)==(751436,i*65536,nbytes,65536,55,8,84017153,1),'archived55 asset generation/order')
  public.verify(part[160:224],part[:160]);parts.append(part[224:])
 require(sha(b''.join(parts))==POLICY['digest'],'archived55 whole verified firmware digest')
 before=read(directory/'before-state.json');require(sha(before)==a['before_state_sha256'],'retirement original state')
 original=loads(before);require(original['engine']['native_counter']==55 and original['hardware_trial_pending']==a['original_asset_session'],'retired actual55 owner context')
 authraw=read(directory/'authorization.json');auth=loads(authraw);obs=loads(read(directory/'observation.json'));log=read(directory/'query.log')
 require(auth.get('explicit_owner_authorization') is True and auth.get('action')=='controlled-dell-reboot-for-native55-recovery' and auth.get('native_counter')==55 and auth.get('state_before_sha256')==sha(before),'owner-authorized specific reboot')
 require(obs.get('owner_confirmed_reboot') is True and obs.get('authorization_sha256')==sha(authraw) and obs.get('log_sha256')==sha(log),'actual owner reboot/EMPTY correlation')
 t,rt,at=obs.get('observed_at'),obs.get('reboot_confirmed_at'),auth.get('authorized_at')
 require(all(type(x) in (int,float) and math.isfinite(x) for x in (t,rt,at)) and at<=rt<=t and t-rt<=300,'historical authorized reboot/EMPTY chronology (not fresh-now)')
 query_match(log,obs,{'received':0,'length':0,'state':0,'error':0,'counter':0,'sha256':'00'*32},'00'*8)
 require(obs['receiver'].get('outcome')=='idle' and obs['receiver']['raw_hex']==EMPTY,'historical exact EMPTY')
 conditional=a.get('conditional_evidence',{});require(conditional.get('status')=='CONDITIONAL-FULL55-REBOOT-RETIREMENT-EVIDENCE-PASS' and conditional.get('raw55_lost_after_reboot') is True and conditional.get('physical_admission') is False,'historical retirement evidence status')
 required={'before-state.json':sha(before),'authorization.json':sha(authraw),'observation.json':sha(read(directory/'observation.json')),'query.log':sha(log)}
 require(conditional.get('archive_required')==required,'historical exact evidence proof hashes')
 records=[r for r in state.get('retired_hardware_trials',[]) if r.get('native_counter')==55]
 require(len(records)==1 and records[0].get('retirement_sha256')==sha(raw) and records[0].get('session')==a['original_asset_session'] and Path(records[0]['retirement_report']).resolve()==audit_path,'current state exact55 retirement record')
 require(read(Path(plan)/'before-state.json')==read(directory/'after-state.json'),'native56 prepared from exact retired state')
 return {'retirement_sha256':sha(raw),'historical_reboot_empty_verified':True,'actual_all14_owner_release_claimed':False,'raw55_lost':True}

def current_state(raw,plan,baseline):
 s=loads(raw)
 for k in ('pending','native_pending','recovery_pending','hardware_trial_pending'):require(k in s and s[k] is None,'active/missing state owner '+k)
 require(s.get('counter')==18 and s.get('world_sha256')==WORLD and s.get('package_sha256')==PACKAGE,'exact current world18')
 e=s.get('engine',{});require(e.get('native_counter')==56 and e.get('payload_sha256')==PAYLOAD56,'exact current native56')
 require(Path(e['last_release_report']).resolve()==Path(plan).resolve()/'report.json','exact56 applied plan source')
 worldpath=within(s['world'],REPO);packagepath=within(s['package'],REPO)
 require(sha(read(packagepath))==PACKAGE,'current immutable world18 package')
 world=loads(read(worldpath));require(sha(json.dumps(world,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==WORLD,'current canonical semantic world')
 require(baseline['world_package_bytes']==len(read(packagepath)),'world18 file length');source_world18(world,read(packagepath))
 gate=within(e['installed_gate'],REPO);require(sha(read(gate))==e['installed_gate_sha256'],'installed public native gate hash')
 return s

def fresh_world18(observation,report,log,baseline,now):
 require(type(now) in (int,float) and math.isfinite(now),'real finite current clock')
 for forbidden in ('fixture_kind','synthetic_only','mocked','test_clock','host_fixture'):require(forbidden not in observation,'host fixture cannot supply physical freshness')
 t=observation.get('observed_at');require(type(t) in (int,float) and math.isfinite(t) and 0<=now-t<=300,'new actual world18 query must be fresh<=300s; no oldreceipt age reset')
 require(observation.get('native_counter')==56 and observation.get('world_counter')==18 and observation['receiver'].get('outcome')=='applied' and observation['receiver'].get('session_matches') is True,'current56/world18 correlated observation')
 decoded=query_match(log,observation,{'received':baseline['world_stream_bytes'],'length':baseline['world_stream_bytes'],'state':2,'error':0,'counter':18,'sha256':PACKAGE},baseline['world_session_id_hex'])
 steps=report.get('sender_steps',[]);require(len(steps)==1 and steps[0].get('name')=='query' and type(steps[0].get('exit_code')) is int and steps[0]['exit_code']==0 and steps[0].get('log_sha256')==sha(log),'actual fresh query report/log binding')
 return {'observation_age_seconds':now-t,'query_log_sha256':sha(log),'receiver_counter':decoded['counter'],'device_attestation':False}

def candidate57(profile,repo=REPO):
 profile=within(profile,repo);directory=profile/'runs/checked-candidate';raw=read(directory/'report.json');require(FROZEN_REPORT_SHA is not None and sha(raw)==FROZEN_REPORT_SHA,'actual frozen prefix57 report pin required');r=loads(raw)
 require(r.get('status')==PROFILE_STATUS and r.get('build_host')=='yukabox' and r.get('native_counter')==57,'frozen full prefix57 proof status/host/generation')
 for k in ('physical_verified','signing_admitted'):require(r.get(k) is False,'offline proof cannot claim physical/signing '+k)
 require(r.get('world_package_sha256')==PACKAGE and r.get('world_semantic_sha256')==WORLD,'exact preserved world18 proof')
 expected={'max_MAIN_bytes':32984,'max_MAIN_descriptors':133,'BMI_DONE_commands':0,'HTC_INIT_scan_commands':0,'deadline_us':600000000}
 for k,v in expected.items():require(type(r.get(k)) is int and r[k]==v,'bounded profile scope '+k)
 policy=loads(read(profile/'receiver-policy.json'));require(policy==POLICY and r.get('receiver_policy')==POLICY and r.get('receiver_policy_sha256')==sha(read(profile/'receiver-policy.json')),'explicit receiver57 owner/target/GEN/full firmware policy')
 payload=read(directory/'payload.efi',262144);require(len(payload)==r.get('payload_bytes') and sha(payload)==digest(r.get('payload_sha256')),'immutable complete EFI file')
 mapped=pe_caps(payload);require(type(r.get('mapped_bytes')) is int and mapped==r['mapped_bytes'],'actual mapped PE/report equality');count=source_closure(r.get('source_sha256'),repo)
 require(r.get('exact_world18_QEMU') is True and r.get('radio_backend')=='MOCK USB ONLY' and r.get('wifi_connected') is False,'honest exact world18 offline scope')
 for k in ('owner_private_key_loads','device_operations'):require(type(r.get(k)) is int and r[k]==0,'no candidate owner/hardware '+k)
 source_raw=read(directory/'world18-source.json');packet18=read(directory/'world18.rup')
 require(sha(source_raw)==r.get('world_source_sha256') and sha(packet18)==PACKAGE,'retained exact source/world18 bytes');source_world18(loads(source_raw),packet18)
 repraw=read(directory/'reproduction.json');rep=loads(repraw)
 require(sha(repraw)==r.get('reproduction_sha256') and rep.get('status')=='PREFIX57-THREE-BUILDS-IDENTICAL','three identical full EFI build proof')
 require(rep.get('inputs')==r['source_sha256'] and rep.get('generated_compiler_sources_sha256')==r.get('generated_compiler_sources_sha256') and rep.get('payload_sha256')==r['payload_sha256'] and rep.get('public_world_package_sha256')==PACKAGE and rep.get('world_source_sha256')==sha(source_raw) and rep.get('dummy_fixture_signing_only') is True and type(rep.get('owner_private_key_loads')) is int and rep['owner_private_key_loads']==0,'actual immutable compiler/reproduction/sourceworld bindings')
 native_path=profile/'runs/native-host/report.json';native_raw=read(native_path);n=loads(native_raw)
 require(sha(native_raw)==r.get('native_report_sha256') and n.get('status')==NATIVE_STATUS,'actual native prefix/USB/overlay proof binding')
 require(type(n.get('scenarios')) is int and n['scenarios']==8 and n.get('scenario_ids')==[0,1,2,3,4,5,6,9],'all actual bounded native scenarios')
 for k in ('actual_driver_poll','actual_native_PCI_CE_DMA_model','actual_driver_overlay_canary_test','mocked_USB_backend','driver_attach_not_modelled','full_authenticated_container'):require(n.get(k) is True,'actual source model boundary '+k)
 for k in ('max_MAIN_bytes','max_MAIN_descriptors','BMI_DONE_commands','HTC_INIT_scan_commands'):require(type(n.get(k)) is int and n[k]==expected[k],'actual prefix publication bound '+k)
 for k in ('device_operations','private_key_loads'):require(type(n.get(k)) is int and n[k]==0,'native model cannot access hardware/keys '+k)
 require(n.get('physical_verified') is False,'native model not physical')
 source_closure(n['source_sha256'],repo);require(sha(read(profile/'runs/native-host/host.log'))==n['host_log_sha256'],'actual ASAN/COFF run log')
 for name,h in n['compiled_fixture_sources_sha256'].items():require(sha(read(within(profile/'runs/native-host'/rel(name),profile/'runs/native-host'),4_000_000))==digest(h),'actual compiled fixture source bytes '+name)
 # Future final archive must retain these exact generated bytes, not regenerate
 # or execute any candidate Python inside this pure preflight.
 generated=r.get('generated_compiler_sources_sha256');require(isinstance(generated,dict) and len(generated)>0,'retained generated compiler closure required')
 for name,h in generated.items():require(sha(read(within(directory/rel(name),directory),4_000_000))==digest(h),'generated compiler source retained bytes '+name)
 gates=r.get('gates');require(isinstance(gates,list) and len(gates)==2,'two genuine fullEFI QEMU runs required')
 require(gates[0].get('empty_boot') is False and gates[1].get('empty_boot') is True,'normal/empty QEMU baseline pair')
 for i,g in enumerate(gates):
  require(g.get('status')=='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS' and g.get('payload_sha256')==r['payload_sha256'] and g.get('physical_verified') is False and g.get('bluetooth_verified') is False,'exact full EFI/world18 QEMU gate')
  # Archive paths explicit in final collector contract; refuse missing bindings.
  evidence=directory/('actors-empty-boot-qemu' if i else 'actors-qemu')
  require(loads(read(evidence/'report.json'))==g,'actual QEMU report file binding')
  require(sha(read(evidence/'observed.log'))==g['observed_log_sha256'],'actual QEMU observed log bytes')
 return {'candidate_report_sha256':sha(raw),'payload_sha256':r['payload_sha256'],'payload_bytes':len(payload),'mapped_bytes':mapped,'source_count':count,'native_report_sha256':sha(native_raw),'profile_status':PROFILE_STATUS,'counter_candidate':57,'private_key_loads':0,'physical_admission':False}

def evaluate(profile,state_bytes,plan,retirement,observation_bytes,query_report_bytes,query_log,now):
 baseline=native_public56(plan);state=current_state(state_bytes,plan,baseline);historical=retirement55(retirement,state,plan)
 offline=candidate57(profile);fresh=fresh_world18(loads(observation_bytes),loads(query_report_bytes),query_log,baseline,now)
 return {'status':'CONDITIONAL-PREFIX57-PUBLIC-PREPARATION-BINDINGS-PASS','candidate':offline,'baseline56':baseline,'retirement55':historical,'fresh_world18':fresh,'state_sha256':sha(state_bytes),'observation_sha256':sha(observation_bytes),'query_report_sha256':sha(query_report_bytes),'physical_admission':False,'operation_lock_review_required':True,'fresh_root_observation_required':True,'counter_reserved':False,'signed':False,'sent':False,'private_key_loads':0,'state_written':False,'device_operations':0,'station_ready':False,'wifi_connected':False}

def main():
 import argparse
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('profile','state','plan','retirement','observation','query-report','query-log'):p.add_argument('--'+n,type=Path,required=True)
 args=p.parse_args();paths=[within(getattr(args,n.replace('-','_')),REPO) for n in ('profile','state','plan','retirement','observation','query-report','query-log')]
 profile,state,plan,retirement,observation,query_report,query_log=paths
 blobs=[read(x) for x in (state,observation,query_report,query_log)];hashes={str(x):sha(read(x)) for x in (state,retirement,observation,query_report,query_log,plan/'report.json')}
 result=evaluate(profile,blobs[0],plan,retirement,blobs[1],blobs[2],blobs[3],time.time())
 require(hashes=={n:sha(read(n)) for n in hashes},'inputs changed during read-only preflight')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
