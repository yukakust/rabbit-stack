"""Mac fake callbacks and pure public bytes only; no real manager."""
import copy,json,struct,hashlib,subprocess,os,time
from pathlib import Path
import fixtures,decode_htt as d,native_binding,bindings
R=Path(__file__).resolve().parent;sha=native_binding.sha
checks=0
def reject(fn,*args):
 global checks
 try:fn(*args)
 except (ValueError,KeyError,TypeError):checks+=1;return
 raise AssertionError('accepted malformed input')
def compile_host(test=False):
 out=R/'runs/control';out.mkdir(parents=True,exist_ok=True);exe=out/('host-test' if test else 'read-htt62');p=R/('host_test.m' if test else 'read_htt.m');plist=R.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist';inputs={str(x):sha(x) for x in (R/'read_htt.m',p,plist)};env=os.environ.copy()
 for n in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):env.pop(n,None)
 subprocess.run(['xcrun','--sdk','macosx','clang','-x','objective-c','-fobjc-arc','-Wall','-Wextra','-Werror',str(p),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],env=env,check=True,timeout=60);assert inputs=={n:sha(Path(n)) for n in inputs};return exe,inputs
def main():
 global checks
 out=R/'runs'/('proof-'+str(time.time_ns()));out.mkdir(parents=True);container=fixtures.CONTAINER.read_bytes();binding=native_binding.check()
 for major in (2,3):assert d.decode_capture(fixtures.capture(major),container)['version_only_pass'];checks+=1
 c=fixtures.capture();(out/'fixture.json').write_text(json.dumps(c));b=bytes.fromhex(c['status_hex'][0])
 for n in range(320):reject(d.status,b[:n])
 for n in range(8):bad=bytearray(b);bad[n]^=1;reject(d.status,bytes(bad))
 for field in ('counter','actual_released','mappings','dma_users','pci','wake','link','irq','pin','bus','access_count','adapter_phase','cleanup_slot','life_phase','credit_total'):
  x=copy.deepcopy(c);bad=bytearray(b);struct.pack_into('<I',bad,8+4*d.FIELDS.index(field),0xffffffff);x['status_hex']=[bad.hex()]*3;reject(d.decode_capture,x,container)
 for page in range(30):
  x=copy.deepcopy(c);x['pages_hex'][1][page]='00';reject(d.decode_capture,x,container)
  x=copy.deepcopy(c);x['pages_hex'][0][page]=x['pages_hex'][1][page]=x['pages_hex'][0][page][:-2];reject(d.decode_capture,x,container)
 # Production rx.c records event=0 for HTT pipe1, WMI payloadword for pipe2.
 bad=copy.deepcopy(c)
 for pas in bad['pages_hex']:
  page=bytearray.fromhex(pas[0]);struct.pack_into('<I',page,48,0x30100);pas[0]=page.hex()
 reject(d.decode_capture,bad,container)
 wmi=copy.deepcopy(c);payload=struct.pack('<I',0x1d011);raw=bytes([1,0,4,0,0,0,0,0])+payload;record=b'QHTX0001'+struct.pack('<12I',1,1,1,12,1,0,1,2,4,12,0x1d011,0)+raw+bytes(2036)
 for pas in wmi['pages_hex']:pas[5:10]=[record[i:i+512].hex() for i in range(0,2104,512)]
 status=bytearray.fromhex(wmi['status_hex'][0]);struct.pack_into('<I',status,8+4*d.FIELDS.index('archive_count'),1);wmi['status_hex']=[status.hex()]*3;assert d.decode_capture(wmi,container)['version_only_pass'];checks+=1
 for pas in wmi['pages_hex']:
  page=bytearray.fromhex(pas[5]);struct.pack_into('<I',page,48,0);pas[5]=page.hex()
 reject(d.decode_capture,wmi,container)
 credit=copy.deepcopy(c);raw=bytes([1,0,0,0,0,0,0,0]);record=b'QHTX0001'+struct.pack('<12I',1,1,1,12,1,0,1,2,0,8,0,0)+raw+bytes(2040)
 for pas in credit['pages_hex']:pas[5:10]=[record[i:i+512].hex() for i in range(0,2104,512)]
 status=bytearray.fromhex(credit['status_hex'][0]);struct.pack_into('<I',status,8+4*d.FIELDS.index('archive_count'),1);credit['status_hex']=[status.hex()]*3;assert d.decode_capture(credit,container)['version_only_pass'];checks+=1
 for pas in credit['pages_hex']:
  page=bytearray.fromhex(pas[5]);struct.pack_into('<I',page,48,1);pas[5]=page.hex()
 reject(d.decode_capture,credit,container)
 for payload in (bytes([99,7,4,0]),b''):
  archive=copy.deepcopy(c);raw=bytes([2,0,len(payload),0,0,0,0,0])+payload;record=b'QHTX0001'+struct.pack('<12I',1,1,1,12,1,0,2,1,len(payload),len(raw),0,0)+raw+bytes(2048-len(raw))
  for pas in archive['pages_hex']:pas[5:10]=[record[i:i+512].hex() for i in range(0,2104,512)]
  status=bytearray.fromhex(archive['status_hex'][0]);struct.pack_into('<I',status,8+4*d.FIELDS.index('archive_count'),1);archive['status_hex']=[status.hex()]*3;got=d.decode_capture(archive,container);assert got['exports']['slots'][1]['raw_hex']==raw.hex() and got['version_only_pass'];checks+=1
 for offset,value in [(36,2),(32,3),(20,10)]:
  bad=copy.deepcopy(c)
  for pas in bad['pages_hex']:
   page=bytearray.fromhex(pas[0]);struct.pack_into('<I',page,offset,value);pas[0]=page.hex()
  reject(d.decode_capture,bad,container)
 for offset in (56+8,56+10,56+11):
  x=copy.deepcopy(c)
  for pas in x['pages_hex']:
   bad=bytearray.fromhex(pas[0]);bad[offset]^=1;pas[0]=bad.hex()
  reject(d.decode_capture,x,container)
 for field in ('major','minor','htt_op','htt_offset','main_offset','main_bytes'):
  x=copy.deepcopy(c);bad=bytearray(b);struct.pack_into('<I',bad,8+4*d.FIELDS.index(field),999);x['status_hex']=[bad.hex()]*3;reject(d.decode_capture,x,container)
 assert not d.decode_capture(c)['version_only_pass'];checks+=1
 # Released fault snapshots and rejected envelopes remain owned diagnostics.
 fault=copy.deepcopy(c);bad=bytearray(b)
 for key,value in [('phase',4),('error',7),('version_seen',0)]:struct.pack_into('<I',bad,8+4*d.FIELDS.index(key),value)
 fault['status_hex']=[bad.hex()]*3;got=d.decode_capture(fault,container);assert got['error']==7 and not got['version_only_pass'] and got['exports']['slots'][0]['present'];checks+=1
 badraw=bytes([15,255,0,0,0,0,0,0]);record=b'QHTX0001'+struct.pack('<12I',5,1,0,12,1,0,15,1,0,8,0,9)+badraw+bytes(2040)
 for pas in fault['pages_hex']:pas[25:30]=[record[i:i+512].hex() for i in range(0,2104,512)]
 got=d.decode_capture(fault,container);assert got['exports']['slots'][5]['rx_error']==9 and got['exports']['slots'][5]['raw_hex']==badraw.hex();checks+=1
 reject(bindings.native_public,b'',{});reject(bindings.installed_binding,{}, {},{},b'');reject(bindings.candidate_binding,{},b'{}',{},R)
 candidate=native_binding.C/'report.json';r=json.loads(candidate.read_text());pins={'generation':62,'status':r['status'],'payload_sha256':native_binding.PAYLOAD,'report_sha256':native_binding.REPORT};assert bindings.candidate_binding(r,candidate.read_bytes(),pins,native_binding.REPO)['physical_admission'] is False;checks+=1
 for k,v in [('generation',61),('report_sha256','0'*64),('payload_sha256','0'*64)]:reject(bindings.candidate_binding,r,candidate.read_bytes(),{**pins,k:v},native_binding.REPO)

 reject(d.firmware,container[:-1]);bad=bytearray(container);bad[-1]^=1;reject(d.firmware,bytes(bad))
 capture=copy.deepcopy(c);capture.pop('fixture_kind');common={'peripheral':d.PEER,'writes':0,'NSError_code':0,'NSError_domain':'','cached_value_possible':False};rows=[dict(common,stage=k) for k in ('services','characteristics','services','characteristics')]
 for stage in range(5):
  for page in range(30 if stage in (1,3) else 1):
   uuid=0x80+page if stage in (1,3) else 0x2f;h=capture['pages_hex'][stage//2][page] if stage in (1,3) else capture['status_hex'][stage//2];rows.append(dict(common,stage='read',capture_stage=stage,page=page,expected=f'52414242-4954-4649-8000-{uuid:012X}',raw_hex=h,raw_bytes=len(bytes.fromhex(h))))
 assert bindings.callback_join(capture,rows)['physical_admission'] is False;checks+=1
 for index,key,value in [(4,'peripheral','BAD'),(4,'NSError_code',6),(4,'cached_value_possible',True),(4,'expected','BAD'),(4,'raw_bytes',319),(4,'capture_stage',1),(5,'page',1),(4,'fixture_kind','fake'),(4,'writes',1),(0,'stage','read')]:
  bad=copy.deepcopy(rows);bad[index][key]=value;reject(bindings.callback_join,capture,bad)
 reader=(R/'read_htt.m').read_text()
 for old,new in [('uid(0x2f)','uid(0x30)'),('word(b+8+54*4)!=62','word(b+8+53*4)!=62'),('word(b+8+44*4)!=12','word(b+8+45*4)!=12')]:reject(native_binding.check,reader.replace(old,new))
 assert 'writeValueForCharacteristic' not in reader and 'scanForPeripherals' not in reader;checks+=1
 exe,inputs=compile_host();subprocess.run([str(exe),'--preflight'],check=True,timeout=5);test,testinputs=compile_host(True);p=subprocess.run([str(test),str(out/'callbacks'),str(out/'fixture.json')],capture_output=True,text=True,check=True,timeout=20);(out/'host.log').write_text(p.stdout+p.stderr)
 report={'status':'OFFLINE-HTT62-OBSERVER-RAW-VERSION-IE6-CALLBACK-PREFLIGHT-PASS','python_checks':checks,'host_result':p.stdout.splitlines()[-1],'reader_path':str(exe),'reader_executable_sha256':sha(exe),'compiler_input_sha256':inputs,'test_input_sha256':testinputs,'source_sha256':{n:sha(R/n) for n in ('read_htt.m','host_test.m','decode_htt.py','fixtures.py','native_binding.py','verify_host.py','bindings.py')},'public_firmware_fixture_sha256':sha(fixtures.CONTAINER),'native_binding':binding,'host_log_sha256':sha(out/'host.log'),'bluetooth_manager_started':False,'writes':0,'private_key_loads':0,'physical_admission':False,'actual_APPLIED62':'PENDING ROOT','association':False,'IP':False};e=R/'evidence';e.mkdir(exist_ok=True);(e/'host-proof.json').write_text(json.dumps(report,indent=2)+'\n');(e/'host.log').write_text(p.stdout+p.stderr);print(json.dumps({'python_checks':checks,'host_result':report['host_result'],'proof_sha256':sha(e/'host-proof.json')}))
if __name__=='__main__':main()
