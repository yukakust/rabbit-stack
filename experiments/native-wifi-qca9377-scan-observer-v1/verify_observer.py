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
  'last_receipt':{'bitmap':4095,'ready':1,'error':0,'peripheral':d.PEER},'packets':[{'generation':54} for _ in range(12)],
  'policy':{'generation':54,'target':'363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9',
   'owner':'622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac',
   'digest':'8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01','total':751436,'type':8,'version':84017153}}
 assert collect.asset_admission(assets);checks+=1
 for k,v in [('completed_chunks',11),('native_counter',53),('native_payload_sha256','wrong')]:x=copy.deepcopy(assets);x[k]=v;reject(collect.asset_admission,x)
 for k,v in [('bitmap',2047),('ready',0),('error',1),('peripheral','other')]:x=copy.deepcopy(assets);x['last_receipt'][k]=v;reject(collect.asset_admission,x)
 for k,v in [('generation',53),('target','other'),('owner','other'),('digest','other'),('total',1),('type',1),('version',1)]:x=copy.deepcopy(assets);x['policy'][k]=v;reject(collect.asset_admission,x)
 x=copy.deepcopy(assets);x['packets'][0]['generation']=53;reject(collect.asset_admission,x)
 x=copy.deepcopy(assets);x['packets'].pop();reject(collect.asset_admission,x)
 # No Bluetooth object is made: only compile and --preflight permitted here.
 exe=collect.compile_reader()
 import subprocess
 r=subprocess.run([str(exe),'--preflight'],text=True,capture_output=True,check=True,timeout=5)
 assert 'ZERO RADIO OPERATIONS' in r.stdout
 out=ROOT/'runs/verified';out.mkdir(parents=True,exist_ok=True)
 (out/'synthetic-release-capture.json').write_text(json.dumps(capture(True),indent=2)+'\n')
 (out/'qemu-uninitialized-contract.json').write_text(json.dumps({'raw_hex':q.hex(),'fixture_kind':'RECONSTRUCTED-FROZEN-QEMU-ATT-ASSERTION-CONTRACT-NOT-RAW-DUMP','physical_verified':False},indent=2)+'\n')
 report={'status':'SCAN54-OBSERVER-STATIC-CORRUPTION-MAC-PREFLIGHT-PASS','checks':checks,'source_sha256':{n:collect.sha(ROOT/n) for n in ['decode_scan.py','collect.py','read_scan.m','verify_observer.py']},
  'frozen_exports_sha256':collect.sha(d.PROFILE/'decode_exports.py'),'frozen_qemu_verifier_sha256':collect.sha(d.PROFILE/'verify_candidate.py'),
  'qemu_record_sha256':collect.sha(d.PROFILE/'evidence/2026-10-07/actors-qemu/report.json'),
  'radio_reads':0,'radio_writes':0,'device_actions':0,'secret_loads':0,'physical_verified':False,'preflight':r.stdout.strip()}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],checks)
if __name__=='__main__':main()
