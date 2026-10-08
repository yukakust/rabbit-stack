"""Additional independent public/synthetic tests: no actual state/BLE/private keys."""
from pathlib import Path
import sys,types,json,hashlib,copy,tempfile,time
import transition62 as t
ROOT=Path(__file__).resolve().parent;checks=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original_open=Path.open
accesses=[]
def guarded(self,*args,**kwargs):
 s=str(self);assert not (self.name=='state.json' or self.name.endswith('.key') or 'credential' in s.lower()),'prohibited actual state/key/credential access';accesses.append(s);return original_open(self,*args,**kwargs)
Path.open=guarded
try:
 d,capture,callbacks=t.capture();assert d['version_only_pass'] and (d['major'],d['minor'])==(3,56);checks.append('actual public cached62 version/release decode PASS')
 scope=t.REPO/'experiments/native-wifi-qca9377-htt62-observer-v2';r=json.loads((scope/'evidence/host-proof.json').read_text());assert sha(scope/'bindings.py')==r['source_sha256']['bindings.py'];b=t.load('_review_pinned62_callbacks',scope/'bindings.py');assert b.callback_join(capture,callbacks)['physical_admission'] is False;checks.append('actual67 callbacks exact stage/UUID/raw join PASS')
 for index,key,value in [(4,'capture_stage',1),(4,'expected','BAD'),(4,'raw_hex','00'),(4,'raw_bytes',319),(4,'cached_value_possible',True),(4,'NSError_code',6),(4,'writes',1),(4,'peripheral','BAD'),(4,'fixture_kind','fake'),(0,'stage','read')]:
  rows=copy.deepcopy(callbacks);rows[index][key]=value
  try:b.callback_join(capture,rows)
  except ValueError:checks.append('cached callback '+key+' rejected')
  else:raise AssertionError(key)
 for extra in ('synthetic_only','test_clock','model_capture'):
  raw=copy.deepcopy(capture);raw[extra]=True
  try:b.callback_join(raw,callbacks)
  except ValueError:checks.append(extra+' cached marker rejected')
  else:raise AssertionError(extra)
 names=('gate','host_gate','monitor_gate','admission');saved={n:sys.modules.get(n) for n in names};paths=list(sys.path);sentinels={n:types.ModuleType('sentinel_'+n) for n in names}
 try:
  sys.modules.update(sentinels);route=t.prior();assert route.gate is not sentinels['gate'] and all(sys.modules[n] is v for n,v in sentinels.items()) and sys.path==paths;checks.append('all generic modules/path preserved on success')
  load=t.load
  def failure(name,path):
   if name.endswith('host_gate'):raise ValueError('injected public module loading failure')
   return load(name,path)
  t.load=failure
  try:t.prior()
  except ValueError:pass
  else:raise AssertionError('failure injection missed')
  finally:t.load=load
  assert all(sys.modules[n] is v for n,v in sentinels.items()) and sys.path==paths;checks.append('all generic modules/path restored after load failure')
 finally:
  sys.path[:]=paths
  for n,v in saved.items():
   if v is None:sys.modules.pop(n,None)
   else:sys.modules[n]=v
 # Fresh checker evaluated with isolated synthetic files/mocks, never actual state.
 before=b'INDEPENDENT SYNTHETIC BYTES NOT ACTUAL STATE';rawreceipt=bytearray(60);rawreceipt[:4]=b'RFS\1';rawreceipt[20:24]=b'\2\0\0\0';rawreceipt[24:28]=(62).to_bytes(4,'little');rawreceipt[28:]=bytes.fromhex(t.pins()['native_packet_sha256']);boot=bytearray(160);boot[:8]=b'QWBT0001';boot[8:12]=(5).to_bytes(4,'little');common={'peripheral':capture['peripheral'],'writes':0,'NSError_code':0,'NSError_domain':'','cached_value_possible':False};rows=[dict(common,stage='value-read',index=0,raw_hex=boot.hex(),raw_bytes=160),dict(common,stage='value-read',index=1,raw_hex=capture['status_hex'][0],raw_bytes=320)]
 tools={'receipt_reader_sha256':'a'*64,'monitor_sha256':'b'*64,'observer_source_sha256':'c'*64}
 with tempfile.TemporaryDirectory(prefix='filter63-independent-public-') as tmp:
  folder=Path(tmp);(folder/'receipt.log').write_text('SYNTHETIC NOT PHYSICAL');(folder/'monitor.jsonl').write_text('\n'.join(map(json.dumps,rows)));report={'status':'ACTUAL62-RELEASE14-PRE63-OBSERVATION','writes':0,'state_sha256':hashlib.sha256(before).hexdigest(),'observed_at':time.time(),**tools,'inputs':{n:sha(folder/n) for n in ('receipt.log','monitor.jsonl')}}
  fake=types.SimpleNamespace(gate=types.SimpleNamespace(flow=types.SimpleNamespace(read_json=lambda p:json.loads(Path(p).read_text()),sha=lambda x:hashlib.sha256(x).hexdigest()),base60=types.SimpleNamespace(t=types.SimpleNamespace(raw_callback=lambda *a:bytes(rawreceipt)),prior=types.SimpleNamespace(PEER=capture['peripheral']))))
  originals=(t.prior,t.observation_tools,t.capture);t.prior=lambda:fake;t.observation_tools=lambda:tools;t.capture=lambda:(d,capture,callbacks)
  try:
   def run(value):
    (folder/'report.json').write_text(json.dumps(value));return t.fresh(folder,before)
   assert run(report)['physical_counter']==62;checks.append('SYNTHETIC fresh contract positive; NOT PHYSICAL')
   for field,value in [('observed_at',time.time()-301),('observed_at',time.time()+100),('state_sha256','0'*64),('writes',1),('receipt_reader_sha256','0'*64),('monitor_sha256','0'*64),('observer_source_sha256','0'*64)]:
    bad=copy.deepcopy(report);bad[field]=value
    try:run(bad)
    except ValueError:checks.append('SYNTHETIC fresh '+field+' rejected')
    else:raise AssertionError(field)
   for index,field,value in [(0,'index',1),(0,'NSError_code',6),(0,'raw_bytes',159),(1,'raw_hex','00'),(1,'cached_value_possible',True)]:
    badrows=copy.deepcopy(rows);badrows[index][field]=value;(folder/'monitor.jsonl').write_text('\n'.join(map(json.dumps,badrows)));bad=copy.deepcopy(report);bad['inputs']['monitor.jsonl']=sha(folder/'monitor.jsonl')
    try:run(bad)
    except ValueError:checks.append('SYNTHETIC fresh monitor '+field+' rejected')
    else:raise AssertionError(field)
   (folder/'monitor.jsonl').write_text('\n'.join(map(json.dumps,rows)));report['inputs']['monitor.jsonl']=sha(folder/'monitor.jsonl')
   rawreceipt[24:28]=(61).to_bytes(4,'little')
   try:run(report)
   except ValueError:checks.append('SYNTHETIC wrong RFS counter rejected')
   else:raise AssertionError('wrong receipt')
  finally:t.prior,t.observation_tools,t.capture=originals
finally:Path.open=original_open
result={'status':'INDEPENDENT-PRIOR62-PUBLIC-CACHED-AND-SYNTHETIC-FRESHNESS-REVIEW-PASS','checks':checks,'source_sha256':{p.name:sha(p) for p in (Path(__file__),ROOT/'transition62.py',ROOT/'observe62.py',ROOT/'prior62-pins.json')},'actual_state_accesses':0,'private_key_accesses':0,'manager_started':False,'new_counter_reserved':False,'synthetic_fresh_cases_are_not_physical_evidence':True,'finding':'Root resolved missing callback join: capture() now verifies frozen bindings source and calls callback_join on exact67 cached callbacks. Current bytes and independently mutated callbacks rechecked.'};e=ROOT/'evidence';e.mkdir(exist_ok=True);p=e/'additional-prior62-review.json';p.write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(checks),'reviewSHA',sha(p))
