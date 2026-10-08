"""Offline actual-host callbacks and synthetic byte tests; never starts real manager."""
from pathlib import Path
import copy,json,hashlib,struct,subprocess,os,time
import decode_filter as d,fixtures,native_binding,bindings
R=Path(__file__).resolve().parent;sha=native_binding.sha;checks=0
def reject(fn,*args):
 global checks
 try:fn(*args)
 except (ValueError,TypeError,KeyError):checks+=1;return
 raise AssertionError('accepted malformed input')
def compile_host(test=False):
 out=R/'runs/control';out.mkdir(parents=True,exist_ok=True);exe=out/('host-test' if test else 'read-filter63');p=R/('host_test.m' if test else 'read_filter.m');plist=R.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist';inputs={str(x):sha(x) for x in (R/'read_filter.m',p,plist)};env=os.environ.copy()
 for n in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):env.pop(n,None)
 subprocess.run(['xcrun','--sdk','macosx','clang','-x','objective-c','-fobjc-arc','-Wall','-Wextra','-Werror',str(p),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],env=env,check=True,timeout=60);assert inputs=={n:sha(Path(n)) for n in inputs};return exe,inputs
def main():
 global checks
 pins={'generation':63,'report_sha256':'ba46f2c04021b71744a45a0fc31769d93629062422b8a6fbf878e66d8767fe37','payload_sha256':'a636b40f10103a90879bad00a55de173fa36ab2b7a4fd4f38262825191bf4442'};binding=native_binding.check(pins);c=fixtures.capture();p=bytes.fromhex(c['pipeline_hex'][0]);s=bytes.fromhex(c['status_hex'][0]);out=R/'runs'/('proof-'+str(time.time_ns()));out.mkdir(parents=True)
 got=d.decode_capture(c);assert got['pipeline']['filter_tx_count']==3 and got['pipeline']['filter_tx_completed']==1;assert got['owned_filter_version_verified'] and got['target_observed'] and got['exports']['slots'][2]['payload_bytes']==0 and got['exports']['slots'][2]['raw_bytes']==16 and not got['physical_admission'];checks+=1
 assert not d.decode_capture(fixtures.capture(False))['target_observed'];checks+=1
 bad=bytearray(p);struct.pack_into('<I',bad,8+d.FIELDS.index('filter_tx_completed')*4,3);reject(d.pipeline,bytes(bad))
 bad=copy.deepcopy(c);value=bytearray.fromhex(bad['pipeline_hex'][0]);struct.pack_into('<I',value,8+d.FIELDS.index('filter_tx_completed')*4,0);bad['pipeline_hex']=[value.hex()]*3;assert not d.decode_capture(bad)['owned_filter_version_verified'];checks+=1
 (out/'fixture.json').write_text(json.dumps(c))
 for n in range(448):reject(d.pipeline,p[:n])
 for n in range(416):reject(d.scan.decode_status,s[:n])
 for field in ['filter_tx_completed','actual_released',*d.OWNERS,'generation','adapter_phase','cleanup_slots','lifecycle_phase','service_count']:
  bad=bytearray(p);struct.pack_into('<I',bad,8+4*d.FIELDS.index(field),0xffffffff);reject(d.pipeline,bytes(bad))
 for at in [*range(8),*range(398,432),*range(440,448)]:bad=bytearray(p);bad[at]^=1;reject(d.pipeline,bytes(bad))
 for page in range(110):
  x=copy.deepcopy(c);x['pages_hex'][1][page]='00';reject(d.decode_capture,x)
  x=copy.deepcopy(c);x['pages_hex'][0][page]=x['pages_hex'][1][page]=x['pages_hex'][0][page][:-2];reject(d.decode_capture,x)
 for slot,offset,value in [(0,20,10),(0,48,0),(0,36,1),(1,48,0x33800),(1,20,11),(16,32,2),(16,20,20),(2,48,1)]:
  x=copy.deepcopy(c)
  for pas in x['pages_hex']:
   b=bytearray.fromhex(pas[slot*5]);struct.pack_into('<I',b,offset,value);pas[slot*5]=b.hex()
  reject(d.decode_capture,x)
 # Actual raw trailer preserved; mutations cannot hide behind normalized padding.
 x=copy.deepcopy(c)
 for pas in x['pages_hex']:
  b=bytearray.fromhex(pas[0]);b[56+4]=0;pas[0]=b.hex()
 reject(d.decode_capture,x)
 # Valid unknown HTT and credit-only frames stay owned, no false payload claims.
 x=copy.deepcopy(c);raw=fixtures.frame(2,bytes([99,1,4,0]),True);record=b'QFEX0001'+struct.pack('<12I',2,1,1,13,42,0,2,1,4,len(raw),0,0)+raw+bytes(2048-len(raw))
 for pas in x['pages_hex']:pas[10:15]=[record[i:i+512].hex() for i in range(0,2104,512)]
 assert d.decode_capture(x)['exports']['slots'][2]['raw_hex']==raw.hex();checks+=1
 # Rejected invalid header diagnostic may have producer completion; no authority.
 x=copy.deepcopy(c);raw=bytes([15,255,0,0,0,0,0,0]);record=b'QFEX0001'+struct.pack('<12I',17,1,0,41,42,0,15,1,0,8,0,9)+raw+bytes(2040)
 for pas in x['pages_hex']:pas[85:90]=[record[i:i+512].hex() for i in range(0,2104,512)]
 b=bytearray.fromhex(x['status_hex'][0]);struct.pack_into('<I',b,8+31*4,1);struct.pack_into('<I',b,8+d.scan.NAMES.index('rx_error')*4,9);x['status_hex']=[b.hex()]*3;b=bytearray.fromhex(x['pipeline_hex'][0]);struct.pack_into('<I',b,8+d.FIELDS.index('rx_error')*4,9);x['pipeline_hex']=[b.hex()]*3;assert not d.decode_capture(x)['exports']['slots'][17]['validated'];checks+=1
 # Unsupported real VERSION2 still remains forensic, never partial-pipeline pass.
 x=fixtures.capture(False);b=bytearray.fromhex(x['pipeline_hex'][0])
 for name,value in [('pipeline_phase',5),('pipeline_error',113),('major',2)]:struct.pack_into('<I',b,8+4*d.FIELDS.index(name),value)
 x['pipeline_hex']=[b.hex()]*3
 for pas in x['pages_hex']:
  b=bytearray.fromhex(pas[5]);b[56+10]=2;pas[5]=b.hex()
 got=d.decode_capture(x);assert got['pipeline']['owned_version_verified'] and not got['owned_filter_version_verified'] and not got['pipeline_completed'];checks+=1
 reject(native_binding.check,{})

 report_path=native_binding.PRODUCER/'runs/checked-candidate/report.json';candidate=json.loads(report_path.read_text());assert bindings.candidate_binding(candidate,report_path.read_bytes(),dict(pins,status=candidate['status']),native_binding.REPO)['physical_admission'] is False;checks+=1
 reader=(R/'read_filter.m').read_text()
 for old,new in [('self.part?0x2b:0x2f','self.part?0x2b:0x30'),('word(b+8+59*4)!=63','word(b+8+58*4)!=63'),('word(b+8+55*4)!=12','word(b+8+54*4)!=12')]:reject(native_binding.check,None,reader.replace(old,new))
 reject(bindings.candidate_binding,{},b'{}',{},R);reject(bindings.native_public,b'',{});assert bindings.OWNER=='622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac' and bindings.TARGET=='363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9' and bindings.WORLD_PACKAGE=='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7';checks+=1
 raw=copy.deepcopy(c);raw.pop('fixture_kind');common={'peripheral':d.PEER,'writes':0,'NSError_code':0,'NSError_domain':'','cached_value_possible':False};rows=[dict(common,stage=k) for k in ('services','characteristics')*3]
 for stage in range(5):
  items=[(0,page,0x80+page,h) for page,h in enumerate(raw['pages_hex'][stage//2])] if stage in (1,3) else [(0,0,0x2f,raw['pipeline_hex'][stage//2]),(1,0,0x2b,raw['status_hex'][stage//2])]
  for part,page,uuid,h in items:rows.append(dict(common,stage='read',capture_stage=stage,part=part,page=page,expected=f'52414242-4954-4649-8000-{uuid:012X}',raw_hex=h,raw_bytes=len(bytes.fromhex(h))))
 assert bindings.callback_join(raw,rows)['physical_admission'] is False;checks+=1
 for index,key,value in [(6,'part',1),(6,'expected','BAD'),(6,'raw_bytes',447),(6,'capture_stage',1),(8,'page',1),(6,'NSError_code',6),(6,'cached_value_possible',True),(6,'peripheral','BAD'),(6,'fixture_kind','fake'),(6,'writes',1)]:
  bad=copy.deepcopy(rows);bad[index][key]=value;reject(bindings.callback_join,raw,bad)

 oracle_dir=native_binding.REPO/'experiments/native-wifi-qca9377-native63-host-oracle-v1/evidence/2026-10-08';oracle_pin='535a1dc3898d2f6f2d615f3aec1804b62ff5ca641ebbba49c76196f9a626e4d3';assert sha(oracle_dir/'report.json')==oracle_pin;oracle=json.loads((oracle_dir/'report.json').read_text());assert oracle['native_payload_sha256']==pins['payload_sha256'] and oracle['native_report_sha256']=='ca983db6fb2e9723a0f4371442307c2f3684cf5244fc6a22e1008167c9e543cc';producer=native_binding.PRODUCER/'runs/native-host'
 for n,h in oracle['unchanged_production_inputs_sha256'].items():assert sha(producer/n)==h,n
 actual_c=[]
 for case,h in [(0,'4a970b5b5db2f0231fe76c584050438f8ee98eaa236c7e5e2c2bcde91e6745bc'),(4,'81f1b52a020cad909d247f2c9fa451024ce7a1a0327a74d392ea33ad86f0f847'),(2,'ebd0dfe7c5ca821065e8430bdcdec4e976a326e7d94bd59fc00b0dfe4c8785aa')]:
  path=oracle_dir/f'capture-scan0-filter{case}.json';assert sha(path)==h;capture=json.loads(path.read_text());assert capture['fixture_kind']=='synthetic-actual-C-producer';got=d.decode_capture(capture);assert (got['pipeline']['filter_tx_count'],got['pipeline']['filter_tx_completed'])==(3,1);assert got['owned_filter_version_verified']==got['target_observed']==got['pipeline_completed']==(case!=2);checks+=1;actual_c.append({'case':case,'capture_sha256':h,'decoded_pipeline_completed':got['pipeline_completed'],'target_observed':got['target_observed'],'physical':False})
 exe,inputs=compile_host();subprocess.run([str(exe),'--preflight'],check=True,timeout=5);test,ti=compile_host(True);run=subprocess.run([str(test),str(out/'callbacks'),str(out/'fixture.json')],capture_output=True,text=True,check=True,timeout=20);(out/'host.log').write_text(run.stdout+run.stderr)
 r={'status':'OFFLINE-FILTER63-FROZEN-NATIVE-RAW-FORENSIC-CALLBACK-PREFLIGHT-PASS','python_checks':checks,'host_result':run.stdout.splitlines()[-1],'reader_path':str(exe),'reader_executable_sha256':sha(exe),'test_executable_sha256':sha(test),'compiler_input_sha256':inputs,'test_input_sha256':ti,'source_sha256':{n:sha(R/n) for n in ('read_filter.m','host_test.m','scan_decode.py','htc_codec.py','decode_filter.py','fixtures.py','native_binding.py','verify_host.py','bindings.py')},'native_binding':binding,'actual_C_producer_oracle_report_sha256':oracle_pin,'actual_C_producer_cases':actual_c,'host_log_sha256':sha(out/'host.log'),'native_binding_frozen':True,'bluetooth_manager_started':False,'writes':0,'private_key_loads':0,'physical_admission':False,'association':False,'IP':False};e=R/'evidence';e.mkdir(exist_ok=True);(e/'host-proof.json').write_text(json.dumps(r,indent=2)+'\n');(e/'host.log').write_text(run.stdout+run.stderr);print(json.dumps({'python_checks':checks,'host_result':r['host_result'],'proof_sha256':sha(e/'host-proof.json')}))
if __name__=='__main__':main()
