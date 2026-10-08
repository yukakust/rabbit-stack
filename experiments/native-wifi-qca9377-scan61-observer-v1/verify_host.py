#!/usr/bin/env python3
"""Offline pure tests and host ObjC fake callbacks/preflight only."""
import copy,json,hashlib,struct,subprocess,time,os
from pathlib import Path
import decode_scan as d,fixtures as f,bindings
R=d.ROOT;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=0
def reject(fn,*a):
 global checks
 try:fn(*a)
 except (ValueError,KeyError,TypeError):checks+=1;return
 raise AssertionError('accepted corruption')
def compile_host(test=False):
 out=R/'runs/control';out.mkdir(parents=True,exist_ok=True);exe=out/('host-test' if test else 'read-scan61');p=R/('host_test.m' if test else 'read_scan.m');plist=R.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist';inputs={str(x):sha(x) for x in (R/'read_scan.m',p,plist)};env=os.environ.copy()
 for name in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):env.pop(name,None)
 subprocess.run(['xcrun','--sdk','macosx','clang','-x','objective-c','-fobjc-arc','-Wall','-Wextra','-Werror',str(p),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],env=env,check=True,timeout=60)
 assert inputs=={n:sha(Path(n)) for n in inputs};return exe,inputs

def main():
 global checks
 out=R/'runs'/('proof-'+str(time.time_ns()));out.mkdir(parents=True)
 c=f.capture(True);b=bytearray.fromhex(c['status_hex'][0]);struct.pack_into('<I',b,8+24*4,0);c['status_hex']=[bytes(b).hex()]*3
 r=d.decode_capture(c);assert r['live_frequency']==0 and r['beacon']['frequency_mhz']==2437 and r['raw_beacon_matches_status'] and not r['physical_ssid_discovered'];checks+=1
 (out/'fixture.json').write_text(json.dumps(c))
 for n in range(416):reject(d.decode_status,bytes(b[:n]))
 for i in range(64):
  bad=bytearray(b);struct.pack_into('<I',bad,8+4*i,0xffffffff);reject(d.decode_status,bytes(bad)) if i in [d.NAMES.index(x) for x in ['generation','policy_count','reserved0','reserved1',*d.OWNERS,'archive_count','dispatcher_count','credit_total','ssid_seen','pending_started']] else None
 for i in list(range(8))+list(range(264,360))+list(range(361,364))+list(range(402,416)):
  bad=bytearray(b);bad[i]^=1;reject(d.decode_status,bytes(bad))
 for pos in range(110):
  x=copy.deepcopy(c);x['pages_hex'][1][pos]='00';reject(d.decode_capture,x)
  x=copy.deepcopy(c);x['pages_hex'][0][pos]=x['pages_hex'][1][pos]=x['pages_hex'][0][pos][:-2];reject(d.decode_capture,x)
 x=copy.deepcopy(c);bad=bytearray(b);struct.pack_into('<I',bad,8+24*4,2432);x['status_hex']=[bad.hex()]*3;reject(d.decode_capture,x)
 x=copy.deepcopy(c);bad=bytearray(b);struct.pack_into('<I',bad,8+3*4,0);x['status_hex']=[bad.hex()]*3;reject(d.decode_capture,x)
 for field,value in [('pending_started',0),('start_floor',25),('has_observation',0),('ssid_seen',0),('quiesce_requested',0)]:
  x=copy.deepcopy(c);bad=bytearray(b);struct.pack_into('<I',bad,8+4*d.NAMES.index(field),value);x['status_hex']=[bad.hex()]*3
  # ssid_seen false does not invalidate a supported raw observation: it must not
  # become physical discovery (only pure correlation). Test separately.
  if field=='ssid_seen':
   got=d.decode_capture(x);assert not got['physical_ssid_discovered'] and not got['ssid_seen'];checks+=1
  else:reject(d.decode_capture,x)
 x=copy.deepcopy(c);bad=bytearray(b);bad[364]^=1;x['status_hex']=[bad.hex()]*3;reject(d.decode_capture,x)
 x=copy.deepcopy(c)
 for pas in x['pages_hex']:
  for slot in range(22):
   page=bytearray.fromhex(pas[slot*5]);struct.pack_into('<II',page,20,0,0);pas[slot*5]=page.hex()
 reject(d.decode_capture,x)
 reject(bindings.native_public,b'',{})
 # No assigned candidate yet: fail closed on absent Root-pinned report/payload.
 reject(bindings.candidate_binding,{},b'{}',{},R.parent.parent)
 source=out/'dummy-source';source.write_bytes(b'host fixture')
 candidate={'status':'SYNTHETIC-HOST-NOT-PHYSICAL','native_counter':61,'payload_sha256':'a'*64,'world_package_sha256':bindings.WORLD_PACKAGE,'source_sha256':{'dummy-source':sha(source)}};raw=json.dumps(candidate).encode();pins={'status':candidate['status'],'generation':61,'payload_sha256':'a'*64,'report_sha256':hashlib.sha256(raw).hexdigest()}
 got=bindings.candidate_binding(candidate,raw,pins,out);assert got['physical_admission'] is False;checks+=1
 for field,value in [('generation',60),('payload_sha256','b'*64),('report_sha256','0'*64),('status','wrong')]:
  q={**pins,field:value};reject(bindings.candidate_binding,candidate,raw,q,out)
 source.write_bytes(b'changed');reject(bindings.candidate_binding,candidate,raw,pins,out)
 text=(R/'read_scan.m').read_text();assert 'writeValueForCharacteristic' not in text and 'scanForPeripherals' not in text;checks+=1
 exe,inputs=compile_host();subprocess.run([str(exe),'--preflight'],check=True,timeout=5)
 test,testinputs=compile_host(True);p=subprocess.run([str(test),str(out/'callbacks'),str(out/'fixture.json')],capture_output=True,text=True,check=True,timeout=20);(out/'host.log').write_text(p.stdout+p.stderr)
 report={'status':'OFFLINE-SCAN61-OBSERVER-DECODER-CALLBACK-PREFLIGHT-PASS','python_checks':checks,'host_result':p.stdout.splitlines()[-1],'source_sha256':{n:sha(R/n) for n in ('read_scan.m','host_test.m','decode_scan.py','fixtures.py','bindings.py','verify_host.py')},'reader_executable_sha256':sha(exe),'reader_path':str(exe),'compiler_input_sha256':inputs,'test_input_sha256':testinputs,'host_log_sha256':sha(out/'host.log'),'bluetooth_manager_started':False,'writes':0,'private_key_loads':0,'physical_admission':False,'physical_ssid_discovered':False,'candidate_pins':'PENDING ROOT FROZEN61','actual_APPLIED61_positive_test':'PENDING ACTUAL61','native_public_positive_test':'PENDING ACTUAL61'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');e=R/'evidence';e.mkdir(exist_ok=True);(e/'host-proof.json').write_text(json.dumps(report,indent=2)+'\n');(e/'host.log').write_text(p.stdout+p.stderr);print(json.dumps({'python_checks':checks,'host_result':report['host_result'],'report':str(out/'report.json')}))
if __name__=='__main__':main()
