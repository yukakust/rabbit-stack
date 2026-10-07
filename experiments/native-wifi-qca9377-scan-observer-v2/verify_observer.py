#!/usr/bin/env python3
"""Static fixtures/corruptions and Mac compile/preflight; NEVER --read."""
import copy,hashlib,json,pathlib,struct
import decode_scan as d
import collect
ROOT=d.ROOT
checks=0
def reject(fn,*args):
 global checks
 try:fn(*args)
 except (ValueError,TypeError,KeyError):checks+=1;return
 raise AssertionError('invalid observation accepted')
def status(released=True,observation=False):
 f=[0]*64
 if released:
  for name,value in dict(native_phase=4,quiesce_requested=1,actual_owners_released=1,coordinator_phase=4,
                        tx_phase=8,pending_phase=8,pending_result=2,pending_started=1,start_floor=20,
                        live_frequency=2437,owned_stop_phase=6,terminal_seen=1,terminal_completion=40,
                        credit_available=2,credit_total=2,adapter_phase=12,cleanup_slots=14,
                        lifecycle_phase=4,startup_ready_seen=1,startup_tx_complete=1).items():f[d.NAMES.index(name)]=value
 f[60]=54;f[61]=13
 if observation:f[29]=f[30]=1
 b=bytearray(b'QSCN0001'+struct.pack('<64I',*f)+b''.join(bytes.fromhex(x) for x in d.POLICY)+bytes(56))
 if observation:b[360]=16;b[364:380]=b'SILK_56E35E_Plus';b[396:402]=bytes([2,4,6,8,10,12])
 assert len(b)==416;return bytes(b)
def beacon():
 f=bytearray(36);struct.pack_into('<H',f,0,0x80);f[4:10]=b'\xff'*6;f[10:16]=f[16:22]=bytes([2,4,6,8,10,12]);struct.pack_into('<HH',f,32,100,17)
 f+=bytes([0,16])+b'SILK_56E35E_Plus'+bytes([3,1,6])
 return struct.pack('<IHH10IHH',0x7001,40,44,6,31,54000,7,len(f),0,19,20,21,22,len(f),17)+f
def pages(observation=False):
 out=[]
 for i in range(8):
  payload=beacon() if observation and i==2 else b''
  fields=(i,int(bool(payload)),25 if payload else 0,42,0,1 if payload else 0,2 if payload else 0,len(payload),0x7001 if payload else 0)
  b=b'QEXP0001'+struct.pack('<9I',*fields)+payload+bytes(2040-len(payload))
  out.extend(b[j:j+512].hex() for j in range(0,2084,512))
 return out
def capture(observation=False):
 s=status(observation=observation).hex();p=pages(observation)
 return dict(peripheral=d.PEER,writes=0,status_hex=[s]*3,pages_hex=[p,p.copy()],fixture_kind='SYNTHETIC-HOST-NOT-PHYSICAL')
def main():
 global checks
 assert len(d.NAMES)==64
 # Full status reconstruction consistent with frozen real-QEMU ATT assertions:
 # all64 runtime fields zero except generation54/policy_count13; policy suffix.
 q=status(False);assert d.decode_status(q,False)['actual_owners_released']==0;checks+=1
 reject(d.decode_status,q)
 for seen in (False,True):
  c=capture(seen);r=d.decode_capture(c);assert r['raw_beacon_matches_status']==seen and not r['physical_ssid_discovered'];checks+=1
 # Frozen coordinator clears live_frequency at terminal, retaining raw BSS.
 terminal=capture(True);b=bytearray(status(observation=True))
 struct.pack_into('<I',b,8+24*4,0);struct.pack_into('<I',b,8+17*4,2)
 struct.pack_into('<I',b,8+19*4,0)
 terminal['status_hex']=[bytes(b).hex()]*3
 r=d.decode_capture(terminal)
 assert r['raw_beacon_matches_status'] and r['live_frequency']==0 and r['beacon']['frequency_mhz']==2437
 assert not r['physical_ssid_discovered'];checks+=1
 x=copy.deepcopy(terminal);b=bytearray.fromhex(x['status_hex'][0]);struct.pack_into('<I',b,8+24*4,2432);x['status_hex']=[bytes(b).hex()]*3;reject(d.decode_capture,x)
 x=copy.deepcopy(terminal);b=bytearray.fromhex(x['status_hex'][0]);struct.pack_into('<I',b,8+3*4,0);x['status_hex']=[bytes(b).hex()]*3;reject(d.decode_capture,x)
 x=copy.deepcopy(terminal);parts=[bytes.fromhex(v) for v in x['pages_hex'][0][10:15]];slot=bytearray(b''.join(parts))
 # Unsupported channel14 cannot become policy-approved by ending a scan.
 struct.pack_into('<I',slot,44+8,14);slot[44+52+56]=14
 changed=[slot[j:j+512].hex() for j in range(0,2084,512)]
 for p in x['pages_hex']:p[10:15]=changed
 reject(d.decode_capture,x)
 # Independently exercise the explicit policy-membership guard with a parser
 # test double; real parser remains strict channels1..13 (not widened).
 from unittest.mock import patch
 parsed=d.parse_raw_beacon(beacon());parsed['frequency_mhz']=2484
 with patch.object(d,'parse_raw_beacon',return_value=parsed):reject(d.decode_capture,terminal)
 # Raw is archived first even on failure, and a previous positive decoded
 # result cannot remain current under the new raw filename.
 archive=ROOT/'runs/archive-test/capture.json';archive.parent.mkdir(parents=True,exist_ok=True)
 collect.save(archive.with_suffix('.decoded.json'),{'stable_capture':True,'old_fixture':True})
 bad=copy.deepcopy(terminal);b=bytearray.fromhex(bad['status_hex'][0]);struct.pack_into('<I',b,8+24*4,2432);bad['status_hex']=[bytes(b).hex()]*3
 reject(collect.archive_and_decode,archive,bad)
 assert collect.load(archive)==bad
 assert collect.load(archive.with_suffix('.decoded.json'))['stable_capture'] is False
 assert collect.load(archive.with_suffix('.decode-error.json'))['raw_sha256']==collect.sha(archive);checks+=1
 assert list(archive.parent.glob('capture.decoded.json.previous-*'));checks+=1
 c=capture();base=status()
 for n in range(416):reject(d.decode_status,base[:n])
 for i in list(range(8))+list(range(264,360))+list(range(361,364))+list(range(402,416)):
  b=bytearray(base);b[i]^=1;reject(d.decode_status,bytes(b))
 for name in d.OWNERS:
  b=bytearray(base);struct.pack_into('<I',b,8+4*d.NAMES.index(name),1);reject(d.decode_status,bytes(b))
 for name,v in [('generation',53),('policy_count',12),('reserved0',1),('reserved1',1),('credit_available',3),('credit_total',65536),
                ('dispatcher_count',3),('archive_count',3),('rx_queue_count',3),('ssid_seen',1),('has_observation',1),('pending_started',2)]:
  b=bytearray(base);struct.pack_into('<I',b,8+4*d.NAMES.index(name),v)
  # has_observation without rawslot is a full-capture contradiction.
  if name=='has_observation':x=copy.deepcopy(c);x['status_hex']=[bytes(b).hex()]*3;reject(d.decode_capture,x)
  else:reject(d.decode_status,bytes(b))
 # A virtual credit reservation may remain after actual DMA release: conserved,
 # not falsely rejected as an active hardware owner.
 b=bytearray(base);struct.pack_into('<I',b,8+40*4,1);struct.pack_into('<I',b,8+42*4,1)
 assert d.decode_status(bytes(b))['credit_reserved']==1;checks+=1
 for i in range(2084):
  x=copy.deepcopy(c);parts=[bytes.fromhex(v) for v in x['pages_hex'][0][:5]];raw=bytearray(b''.join(parts));raw[i]^=1
  changed=[raw[j:j+512].hex() for j in range(0,2084,512)]
  for p in x['pages_hex']:p[:5]=changed
  reject(d.decode_capture,x)
 for i in range(40):
  x=copy.deepcopy(c);x['pages_hex'][1][i]='';reject(d.decode_capture,x)
 for seen in (False,True):
  x=capture(seen);x['status_hex'][1]='00'*416;reject(d.decode_capture,x)
 x=capture(True);x['status_hex']=[status(observation=True).hex()]*2;reject(d.decode_capture,x)
 x=capture(True);x['status_hex'][0]=status(False).hex();reject(d.decode_capture,x)
 x=capture(True);b=bytearray(status(observation=True));b[364]^=1;x['status_hex']=[bytes(b).hex()]*3;reject(d.decode_capture,x)
 x=capture(True);b=bytearray(status(observation=True));struct.pack_into('<I',b,8+16*4,0);x['status_hex']=[bytes(b).hex()]*3;reject(d.decode_capture,x)
 for field,value in [('writes',1),('writes',True),('peripheral','other')]:x=copy.deepcopy(c);x[field]=value;reject(d.decode_capture,x)
 # Real receipt/state/candidate gates, synthetic local values only.
 st={'engine':{'native_counter':54,'payload_sha256':d.PAYLOAD}}
 rc={'status':'EXACT-APPLIED-RECEIPT','counter':54,'payload_sha256':d.PAYLOAD,'receiver_reported_applied':True,'gate':{'report_sha256':'fixture'}}
 ca={'payload_sha256':d.PAYLOAD,'status':'SCAN54-REPEATED-FULL-EFI-QEMU-WORLD17-OWNED-EXPORT-PASS'}
 assert collect.admission(st,rc,ca,'fixture');checks+=1
 for k in ['pending','native_pending','recovery_pending']:x=copy.deepcopy(st);x[k]='live';reject(collect.admission,x,rc,ca,'fixture')
 for k,v in [('status','CHECKED-SIGNED-NOT-SENT'),('counter',53),('payload_sha256','wrong'),('receiver_reported_applied',1)]:x=copy.deepcopy(rc);x[k]=v;reject(collect.admission,st,x,ca,'fixture')
 reject(collect.admission,st,rc,ca,'wrong report')
 assets={'status':'EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM','native_counter':54,'native_payload_sha256':d.PAYLOAD,'completed_chunks':12,
  'last_receipt':{'bitmap':4095,'ready':1,'error':0,'peripheral':d.PEER,'action':4,'state':2,'packet_sha256':'f'*64,'length':30764,'received':30764,'confirmed_floor':30764},
  'packets':[{'file':f'chunk-{i}.bin','generation':54,'offset':i*65536,'asset_bytes':751436,'asset_sha256':'8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01','packet_sha256':'f'*64,'target_type':8,'target_version':84017153,'kind':1} for i in range(12)],
  'policy':{'generation':54,'target':'363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9',
   'owner':'622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac',
   'digest':'8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01','total':751436,'type':8,'version':84017153}}
 assert collect.asset_admission(assets);checks+=1
 for k,v in [('completed_chunks',11),('native_counter',53),('native_payload_sha256','wrong')]:x=copy.deepcopy(assets);x[k]=v;reject(collect.asset_admission,x)
 for k,v in [('bitmap',2047),('ready',0),('error',1),('peripheral','other')]:x=copy.deepcopy(assets);x['last_receipt'][k]=v;reject(collect.asset_admission,x)
 for k,v in [('generation',53),('target','other'),('owner','other'),('digest','other'),('total',1),('type',1),('version',1)]:x=copy.deepcopy(assets);x['policy'][k]=v;reject(collect.asset_admission,x)
 x=copy.deepcopy(assets);x['packets'][0]['generation']=53;reject(collect.asset_admission,x)
 x=copy.deepcopy(assets);x['packets'].pop();reject(collect.asset_admission,x)
 for k,v in [('packet_sha256','e'*64),('action',3),('state',1),('length',30763),('received',30763),('confirmed_floor',30763)]:x=copy.deepcopy(assets);x['last_receipt'][k]=v;reject(collect.asset_admission,x)
 for k,v in [('file','other.bin'),('offset',1),('asset_bytes',1),('asset_sha256','wrong'),('target_type',1),('target_version',1),('kind',2),('packet_sha256','not-a-digest')]:x=copy.deepcopy(assets);x['packets'][0][k]=v;reject(collect.asset_admission,x)
 # RFC8032 section7.1 public verification vector only. No private key/seed,
 # signing function or actual owner material is loaded during the test.
 import cryptography
 from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
 from cryptography.exceptions import InvalidSignature
 public=Ed25519PublicKey.from_public_bytes(bytes.fromhex('d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a'))
 sig=bytes.fromhex('e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b')
 public.verify(sig,b'');checks+=1
 try:public.verify(sig[:-1]+bytes([sig[-1]^1]),b'')
 except InvalidSignature:checks+=1
 else:raise AssertionError('invalid signature accepted')
 # Our lock filename and flags match actual flow.state_lock, without importing
 # its controller/signing code or touching its live lock/state.
 flow=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/ask_connected_world.py'
 text=flow.read_text();assert "with (path.parent / 'state.lock').open('a') as lock:" in text
 assert 'fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)' in text;checks+=1
 import fcntl
 temp=ROOT/'runs/lock-test';temp.mkdir(parents=True,exist_ok=True)
 original=collect.STATE;collect.STATE=temp/'state.json'
 try:
  with (temp/'state.lock').open('a') as first:
   fcntl.flock(first,fcntl.LOCK_EX|fcntl.LOCK_NB)
   reject(lambda:collect.lock().__enter__())
  with collect.lock():checks+=1
 finally:collect.STATE=original
 # No Bluetooth object is made: only compile and --preflight permitted here.
 exe=collect.compile_reader()
 import subprocess
 r=subprocess.run([str(exe),'--preflight'],text=True,capture_output=True,check=True,timeout=5)
 assert 'ZERO RADIO OPERATIONS' in r.stdout
 out=ROOT/'runs/verified';out.mkdir(parents=True,exist_ok=True)
 (out/'synthetic-release-capture.json').write_text(json.dumps(capture(True),indent=2)+'\n')
 (out/'qemu-uninitialized-contract.json').write_text(json.dumps({'raw_hex':q.hex(),'fixture_kind':'RECONSTRUCTED-FROZEN-QEMU-ATT-ASSERTION-CONTRACT-NOT-RAW-DUMP','physical_verified':False},indent=2)+'\n')
 v1=ROOT.parent/'native-wifi-qca9377-scan-observer-v1';old=json.loads((v1/'evidence/2026-10-07/report.json').read_text())
 for n,h in old['source_sha256'].items():assert collect.sha(v1/n)==h,'v1 proof source changed'
 coordinator=ROOT.parent/'native-wifi-qca9377-scan-coordinator-v1/coordinator.c'
 source=coordinator.read_text()
 assert 'else if(type==2||type==16||type==64||type==256)s->live_frequency=0;' in source
 assert 's->observation.epoch=s->epoch;s->has_observation=1;' in source
 report={'status':'SCAN54-OBSERVER-V2-TERMINAL-PROVENANCE-MAC-PREFLIGHT-PASS','checks':checks,'source_sha256':{n:collect.sha(ROOT/n) for n in ['decode_scan.py','collect.py','read_scan.m','verify_observer.py']},
  'frozen_exports_sha256':collect.sha(d.PROFILE/'decode_exports.py'),'frozen_qemu_verifier_sha256':collect.sha(d.PROFILE/'verify_candidate.py'),
  'qemu_record_sha256':collect.sha(d.PROFILE/'evidence/2026-10-07/actors-qemu/report.json'),
  'v1_preserved_report_sha256':collect.sha(v1/'evidence/2026-10-07/report.json'),
  'flow_state_lock_source_sha256':collect.sha(flow),'terminal_retained_frequency_tested':True,'raw_before_decode':True,
  'frozen_terminal_coordinator_sha256':collect.sha(coordinator),
  'public_verification_library':cryptography.__version__,'rfc8032_public_verification_vector':True,'private_keys_loaded':0,'signatures_created':0,
  'radio_reads':0,'radio_writes':0,'device_actions':0,'secret_loads':0,'physical_verified':False,'preflight':r.stdout.strip()}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],checks)
if __name__=='__main__':main()
