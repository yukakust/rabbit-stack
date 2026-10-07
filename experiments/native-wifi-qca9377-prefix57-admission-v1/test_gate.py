"""Pure Python static/corruption tests; no clock override in actual CLI, no BLE."""
import copy,hashlib,json,pathlib,struct,tempfile,time
import gate
from cryptography.exceptions import InvalidSignature
ROOT=pathlib.Path(__file__).resolve().parent;checks=0
BASE=gate.REPO/'experiments/native-wifi-qca9377-reboot-recovery55-root-v1/evidence/2026-10-07'
PLAN=BASE/'actual-city56-world18/saved-plan'
LIVEPLAN=gate.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/native56-city-recovery-plan'
READ=gate.REPO/'experiments/native-wifi-qca9377-reboot-recovery55-root-v1/runs/current56-world18-read'
def reject(fn,*a):
 global checks
 try:fn(*a)
 except (ValueError,KeyError,TypeError,FileNotFoundError,InvalidSignature):checks+=1;return
 raise AssertionError('bad input accepted')
def enc(v):return json.dumps(v).encode()
def main():
 global checks
 b=gate.native_public56(PLAN);checks+=1
 state_raw=gate.read(BASE/'actual-city56-world18/after-state.json');s=gate.current_state(state_raw,LIVEPLAN,b);checks+=1
 retire=gate.retirement55(BASE/'actual-reboot-retirement/retirement.json',s,PLAN);assert retire['actual_all14_owner_release_claimed'] is False;checks+=1
 obs=gate.loads(gate.read(READ/'observation.json'));report=gate.loads(gate.read(READ/'report.json'));log=gate.read(READ/'query-0.log')
 # Function-level deterministic historical replay only. This is NOT fresh-now
 # or a physical admission; CLI has no test clock and ALWAYS physicalfalse.
 at=obs['observed_at'];valid=gate.fresh_world18(obs,report,log,b,at+59);assert valid['device_attestation'] is False;checks+=1
 for now in (at-1,at+301,float('nan'),float('inf'),True):reject(gate.fresh_world18,obs,report,log,b,now)
 for k,v in [('observed_at',at-301),('observed_at',True),('native_counter',55),('world_counter',17),('peripheral','other'),('writes',1),('writes',False),('fixture_kind','SYNTHETIC-HOST'),('test_clock',at),('synthetic_only',True)]:
  x=copy.deepcopy(obs);x[k]=v;reject(gate.fresh_world18,x,report,log,b,at)
 for k,v in [('outcome','idle'),('state',0),('error',1),('received',2127),('length',2129),('counter',17),('sha256','00'*32),('session_matches',1),('device_attestation',True)]:
  x=copy.deepcopy(obs);x['receiver'][k]=v;reject(gate.fresh_world18,x,report,log,b,at)
 for k,v in [('exit_code',1),('exit_code',False),('name','commit'),('log_sha256','f'*64)]:
  x=copy.deepcopy(report);x['sender_steps'][0][k]=v;reject(gate.fresh_world18,obs,x,log,b,at)
 for i in range(60):
  x=copy.deepcopy(obs);raw=bytearray.fromhex(x['receiver']['raw_hex']);raw[i]^=1;x['receiver']['raw_hex']=raw.hex();reject(gate.fresh_world18,x,report,log,b,at)
 for badlog in (b'',log+b'\nBEGIN: acknowledged write\n',log.replace(b'READ-ONLY CACHED CONNECT:',b'FAKE CACHED CONNECT:'),log.replace(b'RFS STATUS HEX=',b'RAW='),log+log):reject(gate.fresh_world18,obs,report,badlog,b,at)
 for k in ('pending','native_pending','recovery_pending','hardware_trial_pending'):
  x=copy.deepcopy(s);x[k]='active';reject(gate.current_state,enc(x),LIVEPLAN,b)
 for k,v in [('counter',17),('world_sha256','f'*64),('package_sha256','f'*64)]:x=copy.deepcopy(s);x[k]=v;reject(gate.current_state,enc(x),LIVEPLAN,b)
 for k,v in [('native_counter',55),('payload_sha256','f'*64),('last_release_report','/tmp/fake-report.json'),('installed_gate_sha256','f'*64)]:
  x=copy.deepcopy(s);x['engine'][k]=v;reject(gate.current_state,enc(x),LIVEPLAN,b)
 for records in ([],[{'native_counter':55,'retirement_sha256':'f'*64}],s['retired_hardware_trials']*2):
  x=copy.deepcopy(s);x['retired_hardware_trials']=records;reject(gate.retirement55,BASE/'actual-reboot-retirement/retirement.json',x,PLAN)
 for raw in (b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}',b' '*2000001):reject(gate.loads,raw)
 payload=gate.read(PLAN/'payload.efi');assert gate.pe_caps(payload)<=4*1024*1024;checks+=1
 for n in range(64):reject(gate.pe_caps,payload[:n])
 for mutation in (0,1,60):
  x=bytearray(payload);x[mutation]^=0xff;reject(gate.pe_caps,bytes(x))
 x=bytearray(payload);off=struct.unpack_from('<I',x,60)[0];struct.pack_into('<I',x,off+80,4*1024*1024+1);reject(gate.pe_caps,bytes(x))
 x=bytearray(payload);struct.pack_into('<I',x,60,len(x));reject(gate.pe_caps,bytes(x))
 # Independent unchanged public RFS parser oracle: exact byte layout and
 # reserved/length/state rejection. Pure source, no controller import.
 import importlib.util,base64
 oracle_path=gate.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/delivery_status.py'
 spec=importlib.util.spec_from_file_location('rfs_public_oracle',oracle_path);oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
 session=gate.loads(gate.read(PLAN/'world-session.json'))
 parsed=oracle.parse_status(log.decode(),session);decoded=gate.rfs(parsed['raw_hex'])
 for key in ('received','length','state','error','counter','sha256'):assert decoded[key]==parsed[key]
 assert decoded['session_id_hex']==base64.b64decode(session['session_base64']).hex();checks+=1
 for offset in (22,23):
  raw=bytearray.fromhex(obs['receiver']['raw_hex']);raw[offset]=1;reject(gate.rfs,raw.hex())
 # No key/signing loader exists in this module. public verification only.
 text=(ROOT/'gate.py').read_text();assert 'Ed25519PrivateKey' not in text and 'runtime.key' not in text and 'tools.' not in text;checks+=1
 tmp=ROOT/'runs/test';tmp.mkdir(parents=True,exist_ok=True);public=tmp/'source.c';public.write_text('public source fixture\n')
 relative=str(public.relative_to(gate.REPO));mapping={relative:gate.sha(public.read_bytes())};assert gate.source_closure(mapping,gate.REPO)==1;checks+=1
 reject(gate.source_closure,{relative:'f'*64},gate.REPO);reject(gate.source_closure,{'../outside':'f'*64},gate.REPO);reject(gate.source_closure,{},gate.REPO)
 # Actual saved56 proof has a private-key-free public verifier. Copying immutable
 # PUBLIC bytes into own test scope permits safe corruption of plan metadata.
 import shutil
 local=tmp/'public-plan56';shutil.copytree(PLAN,local,dirs_exist_ok=True)
 pr=gate.loads(gate.read(local/'report.json'))
 for k,v in [('status','PREPARED-NOT-SENT'),('counter',57),('world_counter',17),('engine_done',1),('world_done',False),('receiver_reported_applied',1)]:
  changed=copy.deepcopy(pr);changed[k]=v;(local/'report.json').write_bytes(enc(changed));reject(gate.native_public56,local)
 (local/'report.json').write_bytes(gate.read(PLAN/'report.json'))
 # Explicit SYNTHETIC report-schema fixture; never actual prefix57 proof.
 profile=tmp/'SYNTHETIC-profile57';cd=profile/'runs/checked-candidate';nd=profile/'runs/native-host';cd.mkdir(parents=True,exist_ok=True);nd.mkdir(parents=True,exist_ok=True)
 (profile/'receiver-policy.json').write_bytes(enc(gate.POLICY));(cd/'payload.efi').write_bytes(payload)
 (cd/'driver.c').write_bytes(b'SYNTHETIC generated compiler bytes\n');(nd/'fixture.c').write_bytes(b'SYNTHETIC model fixture bytes\n');(nd/'host.log').write_bytes(b'SYNTHETIC offline host-only log\n')
 model={'status':gate.NATIVE_STATUS,'scenarios':8,'scenario_ids':[0,1,2,3,4,5,6,9],'source_sha256':mapping,'compiled_fixture_sources_sha256':{'fixture.c':gate.sha((nd/'fixture.c').read_bytes())},'host_log_sha256':gate.sha((nd/'host.log').read_bytes()),'actual_driver_poll':True,'actual_native_PCI_CE_DMA_model':True,'actual_driver_overlay_canary_test':True,'mocked_USB_backend':True,'driver_attach_not_modelled':True,'full_authenticated_container':True,'max_MAIN_bytes':32984,'max_MAIN_descriptors':133,'BMI_DONE_commands':0,'HTC_INIT_scan_commands':0,'device_operations':0,'private_key_loads':0,'physical_verified':False}
 (nd/'report.json').write_bytes(enc(model))
 qp=[]
 for empty in (False,True):
  directory=cd/('actors-empty-boot-qemu' if empty else 'actors-qemu');directory.mkdir(exist_ok=True);(directory/'observed.log').write_bytes(b'SYNTHETIC fixture QEMUlog\n')
  q={'status':'EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS','payload_sha256':gate.sha(payload),'empty_boot':empty,'physical_verified':False,'bluetooth_verified':False,'observed_log_sha256':gate.sha((directory/'observed.log').read_bytes())};qp.append(q);(directory/'report.json').write_bytes(enc(q))
 candidate={'status':gate.PROFILE_STATUS,'build_host':'yukabox','native_counter':57,'physical_verified':False,'signing_admitted':False,'world_package_sha256':gate.PACKAGE,'world_semantic_sha256':gate.WORLD,'max_MAIN_bytes':32984,'max_MAIN_descriptors':133,'BMI_DONE_commands':0,'HTC_INIT_scan_commands':0,'deadline_us':600000000,'receiver_policy':gate.POLICY,'receiver_policy_sha256':gate.sha((profile/'receiver-policy.json').read_bytes()),'payload_bytes':len(payload),'payload_sha256':gate.sha(payload),'source_sha256':mapping,'generated_compiler_sources_sha256':{'driver.c':gate.sha((cd/'driver.c').read_bytes())},'native_report_sha256':gate.sha((nd/'report.json').read_bytes()),'gates':qp}
 candidate.update(mapped_bytes=gate.pe_caps(payload),exact_world18_QEMU=True,radio_backend='MOCK USB ONLY',wifi_connected=False,owner_private_key_loads=0,device_operations=0)
 (cd/'world18-source.json').write_bytes(gate.read(PLAN/'world.json'));(cd/'world18.rup').write_bytes(gate.read(PLAN/'world.rup'));candidate['world_source_sha256']=gate.sha((cd/'world18-source.json').read_bytes())
 reproduction={'status':'PREFIX57-THREE-BUILDS-IDENTICAL','inputs':mapping,'generated_compiler_sources_sha256':candidate['generated_compiler_sources_sha256'],'payload_sha256':candidate['payload_sha256'],'public_world_package_sha256':gate.PACKAGE,'world_source_sha256':candidate['world_source_sha256'],'dummy_fixture_signing_only':True,'owner_private_key_loads':0}
 (cd/'reproduction.json').write_bytes(enc(reproduction));candidate['reproduction_sha256']=gate.sha((cd/'reproduction.json').read_bytes())
 def set_candidate(c):
  (cd/'report.json').write_bytes(enc(c));gate.FROZEN_REPORT_SHA=gate.sha((cd/'report.json').read_bytes())
 oldpin=gate.FROZEN_REPORT_SHA
 try:
  set_candidate(candidate);result=gate.candidate57(profile);assert result['physical_admission'] is False;checks+=1
  gate.FROZEN_REPORT_SHA=None;reject(gate.candidate57,profile);set_candidate(candidate)
  # A mismatched report pin rejects even otherwise consistent fields.
  gate.FROZEN_REPORT_SHA='f'*64;reject(gate.candidate57,profile)
  for k,v in [('status','OTHER'),('build_host','mac'),('native_counter',56),('physical_verified',True),('signing_admitted',True),('world_package_sha256','f'*64),('world_semantic_sha256','f'*64),('max_MAIN_bytes',32985),('max_MAIN_descriptors',134),('BMI_DONE_commands',1),('HTC_INIT_scan_commands',1),('deadline_us',600000001),('payload_bytes',1),('payload_sha256','f'*64),('receiver_policy_sha256','f'*64),('native_report_sha256','f'*64),('generated_compiler_sources_sha256',{}),('source_sha256',{}),('gates',qp[:1])]:
   x=copy.deepcopy(candidate);x[k]=v;set_candidate(x);reject(gate.candidate57,profile)
  for k,v in [('generation',56),('owner','f'*64),('target','f'*64),('digest','f'*64),('total',1),('type',1),('version',1),('kind',2)]:
   x=copy.deepcopy(candidate);x['receiver_policy'][k]=v;set_candidate(x);reject(gate.candidate57,profile)
  for k,v in [('max_MAIN_descriptors',134),('BMI_DONE_commands',1),('HTC_INIT_scan_commands',1),('actual_driver_poll',False),('actual_driver_overlay_canary_test',False),('actual_native_PCI_CE_DMA_model',False),('device_operations',1),('private_key_loads',1),('physical_verified',True),('scenarios',7),('scenario_ids',[0]),('compiled_fixture_sources_sha256',{'fixture.c':'f'*64}),('host_log_sha256','f'*64)]:
   m=copy.deepcopy(model);m[k]=v;(nd/'report.json').write_bytes(enc(m));x=copy.deepcopy(candidate);x['native_report_sha256']=gate.sha((nd/'report.json').read_bytes());set_candidate(x);reject(gate.candidate57,profile)
  (nd/'report.json').write_bytes(enc(model));set_candidate(candidate)
  # Mutate source/log/file bytes while keeping original pin/report.
  for path in (cd/'driver.c',nd/'fixture.c',nd/'host.log',cd/'actors-qemu/observed.log'):
   prior=path.read_bytes();path.write_bytes(prior+b'tamper');reject(gate.candidate57,profile);path.write_bytes(prior)
  (cd/'payload.efi').write_bytes(payload[:-1]);reject(gate.candidate57,profile);(cd/'payload.efi').write_bytes(payload)
 finally:gate.FROZEN_REPORT_SHA=oldpin
 # Parent-confirmed actual frozen report pin and all retained bytes.
 actual_profile=gate.REPO/'experiments/native-wifi-qca9377-boot-prefix57-native-v1';actual=gate.candidate57(actual_profile);assert actual['physical_admission'] is False and actual['source_count']==417 and actual['mapped_bytes']==4083712;checks+=1
 # Source semantics include original names; packet's public development creator
 # differs from runtimeowner. No decode_scene import/default signer is used.
 source=gate.loads(gate.read(PLAN/'world.json'));packet18=gate.read(PLAN/'world.rup');worldproof=gate.source_world18(source,packet18);assert worldproof['world_creator_public']!=gate.OWNER and worldproof['byte_reproduction'];checks+=1
 from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
 reject(Ed25519PublicKey.from_public_bytes(bytes.fromhex(gate.OWNER)).verify,packet18[-64:],packet18[:-64])
 for field in ('world_id',):x=copy.deepcopy(source);x[field]+='changed';reject(gate.source_world18,x,packet18)
 x=copy.deepcopy(source);x['actors'][0]['name']+=' changed';reject(gate.source_world18,x,packet18)
 for i in (0,8,32,len(packet18)-1):x=bytearray(packet18);x[i]^=1;reject(gate.source_world18,source,bytes(x))
 # Safe copied REAL artifact corruption; frozen producer bytes untouched.
 clone=tmp/'actual57-copy';clone_cd=clone/'runs/checked-candidate';clone_nd=clone/'runs/native-host';clone_cd.mkdir(parents=True,exist_ok=True);clone_nd.mkdir(parents=True,exist_ok=True)
 actual_cd=actual_profile/'runs/checked-candidate';actual_nd=actual_profile/'runs/native-host';ar=gate.loads(gate.read(actual_cd/'report.json'));an=gate.loads(gate.read(actual_nd/'report.json'))
 copy_names=set(ar['generated_compiler_sources_sha256'])|{'report.json','payload.efi','reproduction.json','world18-source.json','world18.rup'}
 for folder in ('actors-qemu','actors-empty-boot-qemu'):
  for name in ('report.json','observed.log'):copy_names.add(folder+'/'+name)
 for name in copy_names:
  path=clone_cd/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(gate.read(actual_cd/name,4_000_000))
 for name in set(an['compiled_fixture_sources_sha256'])|{'report.json','host.log'}:(clone_nd/name).write_bytes(gate.read(actual_nd/name,4_000_000))
 (clone/'receiver-policy.json').write_bytes(gate.read(actual_profile/'receiver-policy.json'))
 assert gate.candidate57(clone)['payload_sha256']==actual['payload_sha256'];checks+=1
 for path in (clone_cd/'report.json',clone_cd/'payload.efi',clone/'receiver-policy.json',clone_nd/'report.json',clone_nd/'host.log',clone_cd/'driver.c',clone_cd/'reproduction.json',clone_cd/'world18-source.json',clone_cd/'world18.rup',clone_cd/'actors-qemu/observed.log',clone_cd/'actors-empty-boot-qemu/report.json'):
  previous=path.read_bytes();path.write_bytes(previous+b'tamper');reject(gate.candidate57,clone);path.write_bytes(previous)
 require_original=gate.read(actual_cd/'report.json');assert gate.sha(require_original)==gate.FROZEN_REPORT_SHA;checks+=1
 out=ROOT/'runs/verified';out.mkdir(parents=True,exist_ok=True)
 result={'status':'PREFIX57-PURE-PUBLIC-HISTORICAL-BINDINGS-NEGATIVES-PASS','checks':checks,'source_sha256':{n:gate.sha((ROOT/n).read_bytes()) for n in ('gate.py','test_gate.py')},'physical_admission':False,'actual_candidate57_tested':True,'actual_candidate':actual,'source_world18_creator_verified':True,'unsigned_source_reproduction':True,'test_clock_only_in_function_cases':True,'actual_cli_clock_override':False,'radio_operations':0,'private_key_loads':0,'signatures_created':0,'state_written':False,'conditional_candidate_contract_pending':gate.FROZEN_REPORT_SHA is None,'rfs_oracle_sha256':gate.sha(oracle_path.read_bytes())}
 (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],checks)
if __name__=='__main__':main()
