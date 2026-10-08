"""Pure future63 observation bindings. Never authorizes physical operations."""
import hashlib,struct,json
from pathlib import Path
GENERATION=63;WORLD_COUNTER=19
WORLD_PACKAGE='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7'
TARGET='363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9'
OWNER='622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac'
WORLD_CREATOR='03a107bff3ce10be1d70dd18e74bc09967e4d6309ba50d5f1ddc8664125531b8'
RRT=struct.Struct('<4sHHIIIIQ32s32s32s32s32s')
sha=lambda b:hashlib.sha256(b).hexdigest()
def require(v,m):
 if not v:raise ValueError(m)
def digest(v):return type(v) is str and len(v)==64 and all(c in '0123456789abcdef' for c in v)
def candidate_binding(candidate,raw_report,pins,repo):
 # pins must come from Root's separately reviewed frozen admission, not candidate.
 require(pins.get('generation')==63 and digest(pins.get('report_sha256')) and digest(pins.get('payload_sha256')) and type(pins.get('status')) is str and pins['status'],'Root frozen63 pins pending')
 require(sha(raw_report)==pins['report_sha256'],'checked candidate report digest')
 require(candidate==json.loads(raw_report),'candidate object differs from hashed report bytes')
 require(candidate.get('status')==pins['status'] and candidate.get('native_counter')==63 and candidate.get('payload_sha256')==pins['payload_sha256'],'exact63 candidate identity')
 require(candidate.get('world_package_sha256')==WORLD_PACKAGE,'exact world19 package')
 sources=candidate.get('source_sha256');require(type(sources) is dict and bool(sources),'complete source closure missing')
 repo=Path(repo).resolve()
 for name,h in sources.items():
  require(type(name) is str and digest(h),'source entry')
  p=(repo/name).resolve();require(p.is_relative_to(repo),'source escaped repository');require(sha(p.read_bytes())==h,'frozen source changed')
 return {'generation':63,'candidate_report_sha256':pins['report_sha256'],'payload_sha256':pins['payload_sha256'],'world_counter':19,'world_package_sha256':WORLD_PACKAGE,'physical_admission':False,'root_controller_review_required':True}
def installed_binding(state,receipt,pins,world_packet):
 require(all(k in state and state[k] is None for k in ('pending','native_pending','recovery_pending')),'transport owner still active')
 e=state.get('engine',{});require((e.get('native_counter'),e.get('payload_sha256'))==(63,pins.get('payload_sha256')),'installed63 payload')
 require((state.get('counter'),state.get('package_sha256'))==(19,WORLD_PACKAGE),'current exact world19 state')
 require((receipt.get('status'),receipt.get('counter'),receipt.get('payload_sha256'),receipt.get('receiver_reported_applied'))==('EXACT-APPLIED-RECEIPT',63,pins.get('payload_sha256'),True) and receipt.get('receiver_reported_applied') is True,'actual63 APPLIED receipt')
 require(receipt.get('gate',{}).get('report_sha256')==pins.get('report_sha256'),'APPLIED/candidate report binding')
 require(sha(world_packet)==WORLD_PACKAGE and len(world_packet)>=128 and world_packet[:6]==b'RUP5\x05\x00' and struct.unpack_from('<I',world_packet,8)[0]==19,'exact world19 bytes/counter')
 from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
 Ed25519PublicKey.from_public_bytes(bytes.fromhex(WORLD_CREATOR)).verify(world_packet[-64:],world_packet[:-64])
 return {'physical_admission':False,'transport_owner_check_only':True,'hardware_trial_pending_not_cleared':True}
def native_public(packet,pins):
 require(len(packet)>=256,'native RRT bound');h=RRT.unpack_from(packet)
 require(h[:8]==(b'RRT3',3,1,len(packet),len(packet)-256,3,2,63),'exact native63 RRT header')
 require(digest(pins.get('runtime_identity_sha256')) and h[9].hex()==pins['runtime_identity_sha256'],'Root trusted runtime identity required')
 require(h[8].hex()==TARGET and h[10].hex()==pins.get('payload_sha256') and h[11].hex()==sha(b'') and h[12].hex()==OWNER and sha(packet[192:-64])==pins.get('payload_sha256'),'native63 target/owner/payload')
 from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
 Ed25519PublicKey.from_public_bytes(bytes.fromhex(OWNER)).verify(packet[-64:],b'Rabbit trusted runtime update v3\0'+packet[:-64])
 return {'signature_verified':True,'signing_performed':False,'physical_admission':False}
def callback_join(raw,rows):
 require(raw.get('format')=='QF631-QSCN1-QFEX1' and raw.get('peripheral','').upper()=='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF' and type(raw.get('writes')) is int and raw['writes']==0,'complete knownpeer capture')
 for value in [raw,*rows]:require(not any(k in value for k in ('fixture_kind','synthetic_only','test_clock','model_capture')),'fixture not physical evidence')
 for row in rows:require(row.get('peripheral','').upper()==raw['peripheral'].upper() and type(row.get('writes')) is int and row['writes']==0 and row.get('NSError_code')==0 and not row.get('NSError_domain') and not row.get('cached_value_possible'),'error/cached/write/wrongpeer')
 require(len(rows)==232 and [r['stage'] for r in rows[:6]]==['services','characteristics']*3 and all(r['stage']=='read' for r in rows[6:]),'6discoveries+226reads')
 require(len(raw['pipeline_hex'])==len(raw['status_hex'])==3 and len(raw['pages_hex'])==2 and all(len(p)==110 for p in raw['pages_hex']),'fullstatus/rawpasses')
 expected=[]
 for stage in range(5):
  if stage in (1,3):expected.extend((stage,0,page,0x80+page,h) for page,h in enumerate(raw['pages_hex'][stage//2]))
  else:expected.extend([(stage,0,0,0x2f,raw['pipeline_hex'][stage//2]),(stage,1,0,0x2b,raw['status_hex'][stage//2])])
 for row,(stage,part,page,uuid,h) in zip(rows[6:],expected):require(row['capture_stage']==stage and row['part']==part and (stage not in (1,3) or row['page']==page) and row['expected'].upper()==f'52414242-4954-4649-8000-{uuid:012X}' and row['raw_hex']==h and row['raw_bytes']==len(bytes.fromhex(h)),'raw callback stage/part/page/UUID join')
 return {'callback_join_verified':True,'physical_admission':False,'device_attestation':False}
