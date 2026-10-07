#!/usr/bin/env python3
"""Offline repeated whole EFI + exact signed world19 normal/EMPTY QEMU proof.
Only Yukabox. Inherited QEMU uses deterministic public fixture signing keys;
never owner material, physical devices, controller state or radio operations.
"""
import argparse,hashlib,importlib.util,json,os,struct,sys,tempfile,shutil,time
from pathlib import Path
import fullboot_build as build
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
 # Native update counters are untouched; only current actor-world counter and
 # subsequent legacy restoration counter change for this exact world19 trial.
 s=build.one(s,'stage(city_stream,sizeof(city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=4','stage(city_stream,sizeof(city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=19')
 s=build.one(s,'before[36]!=5||le32(before+12)!=4','before[36]!=5||le32(before+12)!=19')
 s=build.one(s,'stage(restored_stream,sizeof(restored_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=5','stage(restored_stream,sizeof(restored_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=20')
 marker='say("WMI INIT SERVICE26..28 READ ONLY; ABSENT RADIO CLAIMS NO READY/MAC/IP");'
 extra=r'''
 uint8_t prefix_service[7]={0x10,29,0,255,255,0,0x28};
 if(att(prefix_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=29||diagnostic_reply[4]!=51||diagnostic_reply[6]!=0x40)return 1;
 uint8_t prefix_status[3]={10,31,0};
 if(att(prefix_status,3,11)||diagnostic_reply_size!=241||!same(diagnostic_reply+1,(const uint8_t*)"QPFX0001",8)||le32(diagnostic_reply+9)!=60||le32(diagnostic_reply+13)||le32(diagnostic_reply+25))return 1;
 uint8_t prefix_write[4]={0x12,31,0,0};if(att(prefix_write,4,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
 uint8_t raw_read[3]={10,33,0};if(att(raw_read,3,11)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QPHCI001",8)||le32(diagnostic_reply+9)!=60||le32(diagnostic_reply+21)||le32(diagnostic_reply+29)!=4672)return 1;
 uint8_t raw_blob[5]={12,33,0,246,0};if(att(raw_blob,5,13)||diagnostic_reply_size!=247)return 1;
 raw_blob[3]=236;raw_blob[4]=1;if(att(raw_blob,5,13)||diagnostic_reply_size!=21)return 1;
 raw_blob[3]=0;raw_blob[4]=2;if(att(raw_blob,5,13)||diagnostic_reply_size!=1)return 1;
 raw_blob[3]=1;if(att(raw_blob,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
 uint8_t last_read[3]={10,51,0};if(att(last_read,3,11)||diagnostic_reply_size!=65)return 1;
 for(unsigned i=1;i<65;i++)if(diagnostic_reply[i])return 1;
 say("FULLBOOT60 STATUS240 RAW4672 TEN READ-ONLY PAGES; ABSENT RADIO NO RELEASE OR WIFI CLAIMS");
 '''+marker
 return build.one(s,marker,extra)
spec=importlib.util.spec_from_file_location('fullboot60_inherited_fixture',build.CHECKED/'verify_candidate.py');checked=importlib.util.module_from_spec(spec);spec.loader.exec_module(checked)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--world',type=Path,required=True);ap.add_argument('--world-json',type=Path,required=True);ap.add_argument('--tmpdir',type=Path,required=True);a=ap.parse_args()
 need(sys.platform.startswith('linux'),'native C/COFF/QEMU only on Yukabox Linux')
 tmp=a.tmpdir.resolve();tmp.mkdir(parents=True,exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
 packet=a.world.read_bytes();need(sha(packet)==WORLD_PACKAGE,'exact immutable public world19 package')
 out=ROOT/'runs/checked-candidate'
 if out.exists():shutil.move(str(out),str(out.with_name('checked-candidate.previous-'+str(time.time_ns()))))
 out.mkdir(parents=True)
 native=ROOT/'runs/native-host/report.json';nr=load(native)
 need(nr['status']=='FULLBOOT60-ACTUAL-DRIVER-PCI-CE-USB-WMI-READY-ASAN-COFF-PASS' and nr['scenarios']==103,'actual103 native initial/boot/startup/transport model gates')
 need(digest(native.with_name('host.log'))==nr['host_log_sha256'],'native actual log hash')
 for n,h in nr['source_sha256'].items():need(digest(REPO/n)==h,'native model source changed '+n)
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
 closure=dict(nr['source_sha256']);folders={ROOT,build.BASE,build.CHECKED,actors.OLD,actors.LINK,actors.NATIVE,actors.V3}
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
 reproduction={'status':'FULLBOOT60-THREE-BUILDS-IDENTICAL','inputs':closure,'generated_compiler_sources_sha256':generated,'payload_sha256':sha(payload),'public_world_package_sha256':WORLD_PACKAGE,'world_source_sha256':digest(out/'world19-source.json'),'dummy_fixture_signing_only':True,'owner_private_key_loads':0}
 (out/'reproduction.json').write_text(json.dumps(reproduction,indent=2)+'\n')
 report={'status':'FULLBOOT60-REPEATED-EFI-QEMU-WORLD19-DIAGNOSTIC-PASS','build_host':'yukabox','native_counter':60,'payload_bytes':len(payload),'mapped_bytes':mapped,'payload_sha256':sha(payload),'source_sha256':closure,'generated_compiler_sources_sha256':generated,'gates':gates,'native_report_sha256':digest(native),'reproduction_sha256':digest(out/'reproduction.json'),'receiver_policy':build.policy(),'receiver_policy_sha256':digest(ROOT/'receiver-policy.json'),'host_checks':host,'world_package_sha256':WORLD_PACKAGE,'world_semantic_sha256':WORLD_SEMANTIC,'exact_world19_QEMU':True,'world_source_sha256':digest(out/'world19-source.json'),'MAIN_bytes':727128,'BMI_DONE_commands':1,'WMI_INIT_commands':1,'WMI_READY_required_before_success':True,'scan_commands':0,'scan':False,'deadline_us':5400000000,'physical_verified':False,'signing_admitted':False,'owner_private_key_loads':0,'device_operations':0,'wifi_connected':False,'radio_backend':'MOCK USB ONLY'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(payload),mapped,sha(payload),flush=True)
if __name__=='__main__':main()
