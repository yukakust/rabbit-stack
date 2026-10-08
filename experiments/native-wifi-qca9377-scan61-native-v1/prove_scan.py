#!/usr/bin/env python3
"""Offline repeated whole EFI + exact signed world19 normal/EMPTY QEMU proof.
Only Yukabox. Inherited QEMU uses deterministic public fixture signing keys;
never owner material, physical devices, controller state or radio operations.
"""
import argparse,hashlib,importlib.util,json,os,struct,sys,tempfile,shutil,time
from pathlib import Path
import scan_build as build
ROOT=build.ROOT;REPO=ROOT.parent.parent
WORLD_PACKAGE='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7'
WORLD_SEMANTIC='fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74'
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(v,s):
 if not v:raise ValueError(s)
def load(p):return json.loads(Path(p).read_text())
def digest(p):return sha(Path(p).read_bytes())
def fixture(source):
 s=checked.fixture(source)
 s=build.one(s,'stage(city_stream,sizeof(city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=4','stage(city_stream,sizeof(city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=19')
 s=build.one(s,'before[36]!=5||le32(before+12)!=4','before[36]!=5||le32(before+12)!=19')
 s=build.one(s,'stage(restored_stream,sizeof(restored_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=5','stage(restored_stream,sizeof(restored_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=20')
 marker='say("WMI INIT SERVICE26..28 READ ONLY; ABSENT RADIO CLAIMS NO READY/MAC/IP");'
 d=load(ROOT.parent/'native-wifi-qca9377-regulatory-policy-v1/evidence/2026-10-07/policy-proposal.json')
 body='\n uint8_t scan_service[7]={0x10,32,0,255,255,0,0x28};\n if(att(scan_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=32||diagnostic_reply[4]!=34||diagnostic_reply[6]!=0x2a)return 1;\n uint8_t scan_read[3]={10,34,0};if(att(scan_read,3,11)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QSCN0001",8))return 1;\n for(unsigned i=9;i<247;i++)if(diagnostic_reply[i])return 1;\n uint8_t scan_blob[5]={12,34,0,246,0};if(att(scan_blob,5,13)||diagnostic_reply_size!=171)return 1;\n if(diagnostic_reply[3]!=61||diagnostic_reply[7]!=13)return 1;\n static const uint8_t policy_refs[96]={POLICY_BYTES};\n if(!same(diagnostic_reply+19,policy_refs,96))return 1;\n scan_blob[3]=160;scan_blob[4]=1;if(att(scan_blob,5,13)||diagnostic_reply_size!=1)return 1;\n scan_blob[3]++;if(att(scan_blob,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;\n uint8_t scan_write[4]={0x12,34,0,0};if(att(scan_write,4,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;\n uint8_t export_read[3]={10,37,0};if(att(export_read,3,11)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QEXP0001",8))return 1;\n for(unsigned i=9;i<247;i++)if(diagnostic_reply[i])return 1;\n uint8_t export_blob[5]={12,37,0,0,2};if(att(export_blob,5,13)||diagnostic_reply_size!=1)return 1;\n export_blob[3]=1;if(att(export_blob,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;\n for(unsigned slot=0;slot<22;slot++){export_read[1]=(uint8_t)(37+10*slot);\n  if(att(export_read,3,11)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QEXP0001",8)||diagnostic_reply[9]!=slot)return 1;\n  for(unsigned j=10;j<247;j++)if(diagnostic_reply[j])return 1;\n  for(unsigned page=1;page<5;page++){export_read[1]=(uint8_t)(37+10*slot+2*page);\n   if(att(export_read,3,11)||diagnostic_reply_size!=(page==4?37u:247u))return 1;\n   for(unsigned j=1;j<diagnostic_reply_size;j++)if(diagnostic_reply[j])return 1;\n  }\n }\n say("SCAN61 STATUS32..34 AND OWNED EXPORT35..255 READ ONLY; ABSENT RADIO NO RF CLAIMS");\n'
 policy_bytes=bytes.fromhex(digest(ROOT.parent/'native-wifi-qca9377-regulatory-policy-v1/evidence/2026-10-07/policy-proposal.json')+d['ruleset_signed_db_sha256']+d['location_sha256'])
 body=body.replace('POLICY_BYTES',','.join(str(n) for n in policy_bytes))
 body+='\n uint8_t gap[7]={0x10,29,0,255,0,0,0x28};if(att(gap,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=32||diagnostic_reply[4]!=34)return 1;gap[0]=8;gap[5]=3;if(att(gap,7,9)||diagnostic_reply_size!=23||diagnostic_reply[2]!=33||diagnostic_reply[5]!=34)return 1;gap[0]=4;if(att(gap,5,5)||diagnostic_reply_size!=6||diagnostic_reply[2]!=32)return 1;\n'
 return build.one(s,marker,body+marker)
spec=importlib.util.spec_from_file_location('scan61_inherited_fixture',build.CHECKED/'verify_candidate.py');checked=importlib.util.module_from_spec(spec);spec.loader.exec_module(checked)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--world',type=Path,required=True);ap.add_argument('--world-json',type=Path,required=True);ap.add_argument('--tmpdir',type=Path,required=True);a=ap.parse_args()
 need(sys.platform.startswith('linux'),'native C/COFF/QEMU only on Yukabox Linux')
 tmp=a.tmpdir.resolve();tmp.mkdir(parents=True,exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
 packet=a.world.read_bytes();need(sha(packet)==WORLD_PACKAGE,'exact immutable public world19 package')
 out=ROOT/'runs/checked-candidate'
 if out.exists():shutil.move(str(out),str(out.with_name('checked-candidate.previous-'+str(time.time_ns()))))
 out.mkdir(parents=True)
 native=ROOT/'runs/native-host/report.json';nr=load(native)
 need(nr['status']=='SCAN61-ACTUAL-PRODUCTION-DRIVER-PASSIVE-REGRESSION-ARCHIVE16-ASAN-COFF-PASS' and nr['scenarios']==19,'actual19 native scan/credit/fault/archive/stop model gates')
 need(digest(native.with_name('host.log'))==nr['host_log_sha256'],'native actual log hash')
 for n,h in nr['source_sha256'].items():need(digest(REPO/n)==h,'native model source changed '+n)
 binding=load(ROOT/'runs/policy-binding/binding.json');need(binding['status']=='INDEPENDENT-SIGNED-REGDB-EXACT-GE-WORLD108-PROPOSAL-HEADER-PASS' and binding['rf_admission_granted'] is False,'signed policy/header binding')
 actors=build.checked.prior.actors
 _,_,crypto=actors.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'))
 payload=build.compile_driver(out,crypto);need(payload==build.compile_driver(out,crypto),'two complete build bytes differ');(out/'payload.efi').write_bytes(payload)
 off=struct.unpack_from('<I',payload,60)[0];mapped=struct.unpack_from('<I',payload,off+80)[0]
 need(len(payload)<=262144 and mapped<=4194304,'immutable whole file/mapped cap')
 from actors_check import check_city
 from scene5 import decode_scene,compile_scene
 decoded,counter=decode_scene(packet);world_source=load(a.world_json)
 need(counter==19 and sha(json.dumps(world_source,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==WORLD_SEMANTIC,'actual source world19 canonical semantics')
 need(compile_scene(world_source,19)==packet,'exact signed source world19 reproduction with fixed public creator fixture key')
 (out/'world19-source.json').write_bytes(a.world_json.read_bytes());(out/'world19.rup').write_bytes(packet)
 host=check_city(a.world,out/'current-world-check',sanitizers=True,roof_cat_timing=True)
 qemu=checked.verify_init_profile.prior.actors_gate
 original_city=qemu.compile_scene;original_world=qemu.flow.compile_world;original_temp=tempfile.TemporaryDirectory
 def exact_city(world,counter,*args,**kwargs):
  need(counter==4,'unexpected fixture actor-city counter');return packet
 def later_restore(path,counter,*args,**kwargs):return original_world(path,20 if counter==5 else counter,*args,**kwargs)
 def bounded_temp(*args,**kwargs):
  if kwargs.get('dir')=='/tmp':kwargs['dir']=str(tmp)
  return original_temp(*args,**kwargs)
 try:
  qemu.compile_scene=exact_city;qemu.flow.compile_world=later_restore;tempfile.TemporaryDirectory=bounded_temp
  gates=[qemu.qemu_gate(out,payload,test_transform=fixture),qemu.qemu_gate(out,payload,True,test_transform=fixture)]
 finally:qemu.compile_scene=original_city;qemu.flow.compile_world=original_world;tempfile.TemporaryDirectory=original_temp
 # Full source closure from actual imported generators and direct compiler/header
 # dependency directories, plus the independent native proof's exact sources.
 closure=dict(nr['source_sha256']);
 policy_out=ROOT/'runs/policy-binding'
 for folder in (ROOT.parent/'native-wifi-qca9377-regulatory-policy-v1',ROOT.parent/'native-wifi-qca9377-regulatory-policy-v1/evidence/2026-10-07',ROOT.parent/'native-wifi-qca9377-wmi-native-v5/evidence/2026-10-07/native52-control-result'):
  for p in folder.iterdir():
   if p.is_file() and p.suffix in ('.json','.log','.c','.h','.py','.md'):closure[str(p.relative_to(REPO))]=digest(p)
 
 for p in policy_out.iterdir():
  if p.is_file() and p.suffix in ('.json','.log','.c','.h'):closure[str(p.relative_to(REPO))]=digest(p)
 folders={ROOT,build.COMPONENTS,build.BASE,build.CHECKED,actors.OLD,actors.LINK,actors.NATIVE,actors.V3}
 for module in list(sys.modules.values()):
  value=getattr(module,'__file__',None)
  if value:
   p=Path(value).resolve()
   if p.is_file() and p.is_relative_to(REPO) and p.suffix=='.py':folders.add(p.parent);closure[str(p.relative_to(REPO))]=digest(p)
 for folder in folders:
  for p in folder.iterdir():
   if p.is_file() and p.suffix in ('.c','.h','.py','.json','.S','.md'):closure[str(p.relative_to(REPO))]=digest(p)
 generated={str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file() and p.suffix in ('.c','.h')}
 need(payload==build.compile_driver(out,crypto),'post-QEMU repeat build differs')
 need(generated=={str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file() and p.suffix in ('.c','.h')},'post-QEMU compiler source bytes differ')
 for n,h in closure.items():need(digest(REPO/n)==h,'source changed during proof '+n)
 for g in gates:need(g['payload_sha256']==sha(payload) and g['physical_verified'] is False,'actual QEMU payload/model boundary')
 reproduction={'status':'SCAN61-THREE-BUILDS-IDENTICAL','inputs':closure,'generated_compiler_sources_sha256':generated,'payload_sha256':sha(payload),'public_world_package_sha256':WORLD_PACKAGE,'world_source_sha256':digest(out/'world19-source.json'),'dummy_fixture_signing_only':True,'owner_private_key_loads':0}
 (out/'reproduction.json').write_text(json.dumps(reproduction,indent=2)+'\n')
 report={'status':'SCAN61-REPEATED-EFI-QEMU-WORLD19-DIAGNOSTIC-PASS','build_host':'yukabox','native_counter':61,'payload_bytes':len(payload),'mapped_bytes':mapped,'payload_sha256':sha(payload),'source_sha256':closure,'generated_compiler_sources_sha256':generated,'gates':gates,'native_report_sha256':digest(native),'reproduction_sha256':digest(out/'reproduction.json'),'receiver_policy':build.policy(),'receiver_policy_sha256':digest(ROOT/'receiver-policy.json'),'host_checks':host,'world_package_sha256':WORLD_PACKAGE,'world_semantic_sha256':WORLD_SEMANTIC,'exact_world19_QEMU':True,'world_source_sha256':digest(out/'world19-source.json'),'MAIN_bytes':727128,'BMI_DONE_commands':1,'WMI_INIT_commands':1,'WMI_READY_required_before_success':True,'scan_commands_candidate':True,'bootstrap_deadline_us':5400000000,'scan_deadline_us':25000000,'rf_admission_granted':False,'physicalSSID_discovery':False,'raw_slots':22,'raw_pages':110,'physical_verified':False,'signing_admitted':False,'owner_private_key_loads':0,'device_operations':0,'wifi_connected':False,'radio_backend':'MOCK USB ONLY','authenticated_policy_binding_sha256':digest(ROOT/'runs/policy-binding/binding.json'),'legal_primary_GE_instrument_verified':False,'active_probe':False,'association':False,'credentials':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(payload),mapped,sha(payload),flush=True)
if __name__=='__main__':main()
