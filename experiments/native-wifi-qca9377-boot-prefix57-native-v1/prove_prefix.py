#!/usr/bin/env python3
"""Offline repeated whole EFI + exact signed world18 normal/EMPTY QEMU proof.
Only Yukabox. Inherited QEMU uses deterministic public fixture signing keys;
never owner material, physical devices, controller state or radio operations.
"""
import argparse,hashlib,importlib.util,json,os,struct,sys,tempfile,shutil,time
from pathlib import Path
import prefix_build as build
ROOT=build.ROOT;REPO=ROOT.parent.parent
WORLD_PACKAGE='f306120fdd548b6d4cc1d3915a13ae8cbe7848b162caa78528add353b9cb3f32'
WORLD_SEMANTIC='fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74'
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(v,s):
 if not v:raise ValueError(s)
def load(p):return json.loads(Path(p).read_text())
def digest(p):return sha(Path(p).read_bytes())
def fixture(source):
 s=checked.fixture(source)
 # Native update counters are untouched; only current actor-world counter and
 # subsequent legacy restoration counter change for this exact world18 trial.
 s=build.one(s,'stage(city_stream,sizeof(city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=4','stage(city_stream,sizeof(city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=18')
 s=build.one(s,'before[36]!=5||le32(before+12)!=4','before[36]!=5||le32(before+12)!=18')
 s=build.one(s,'stage(restored_stream,sizeof(restored_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=5','stage(restored_stream,sizeof(restored_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=19')
 marker='say("WMI INIT SERVICE26..28 READ ONLY; ABSENT RADIO CLAIMS NO READY/MAC/IP");'
 extra=r'''
 uint8_t prefix_service[7]={0x10,29,0,255,255,0,0x28};
 if(att(prefix_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=29||diagnostic_reply[4]!=51||diagnostic_reply[6]!=0x40)return 1;
 uint8_t prefix_status[3]={10,31,0};
 if(att(prefix_status,3,11)||diagnostic_reply_size!=241||!same(diagnostic_reply+1,(const uint8_t*)"QPFX0001",8)||le32(diagnostic_reply+9)!=57||le32(diagnostic_reply+13)||le32(diagnostic_reply+25))return 1;
 uint8_t prefix_write[4]={0x12,31,0,0};if(att(prefix_write,4,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
 uint8_t raw_read[3]={10,33,0};if(att(raw_read,3,11)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QPHCI001",8)||le32(diagnostic_reply+9)!=57||le32(diagnostic_reply+21)||le32(diagnostic_reply+29)!=4672)return 1;
 uint8_t raw_blob[5]={12,33,0,246,0};if(att(raw_blob,5,13)||diagnostic_reply_size!=247)return 1;
 raw_blob[3]=236;raw_blob[4]=1;if(att(raw_blob,5,13)||diagnostic_reply_size!=21)return 1;
 raw_blob[3]=0;raw_blob[4]=2;if(att(raw_blob,5,13)||diagnostic_reply_size!=1)return 1;
 raw_blob[3]=1;if(att(raw_blob,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
 uint8_t last_read[3]={10,51,0};if(att(last_read,3,11)||diagnostic_reply_size!=65)return 1;
 for(unsigned i=1;i<65;i++)if(diagnostic_reply[i])return 1;
 say("PREFIX57 STATUS240 RAW4672 TEN READ-ONLY PAGES; ABSENT RADIO NO RELEASE OR WIFI CLAIMS");
 '''+marker
 return build.one(s,marker,extra)
spec=importlib.util.spec_from_file_location('prefix57_inherited_fixture',build.CHECKED/'verify_candidate.py');checked=importlib.util.module_from_spec(spec);spec.loader.exec_module(checked)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--world',type=Path,required=True);ap.add_argument('--world-json',type=Path,required=True);ap.add_argument('--tmpdir',type=Path,required=True);a=ap.parse_args()
 need(sys.platform.startswith('linux'),'native C/COFF/QEMU only on Yukabox Linux')
 tmp=a.tmpdir.resolve();tmp.mkdir(parents=True,exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
 packet=a.world.read_bytes();need(sha(packet)==WORLD_PACKAGE,'exact immutable public world18 package')
 out=ROOT/'runs/checked-candidate'
 if out.exists():shutil.move(str(out),str(out.with_name('checked-candidate.previous-'+str(time.time_ns()))))
 out.mkdir(parents=True)
 native=ROOT/'runs/native-host/report.json';nr=load(native)
 need(nr['status']=='BOOT-PREFIX57-ACTUAL-DRIVER-PCI-CE-USB-OVERLAY-ASAN-COFF-PASS' and nr['scenarios']==8,'actual eight native model gates')
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
 need(counter==18 and sha(json.dumps(world_source,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==WORLD_SEMANTIC,'actual source world18 canonical semantics')
 need(compile_scene(world_source,18)==packet,'exact signed source world18 reproduction with fixed public creator fixture key')
 (out/'world18-source.json').write_bytes(a.world_json.read_bytes());(out/'world18.rup').write_bytes(packet)
 host=check_city(a.world,out/'current-world-check',sanitizers=True,roof_cat_timing=True)
 qemu=checked.verify_init_profile.prior.actors_gate
 original_city=qemu.compile_scene;original_world=qemu.flow.compile_world;original_temp=tempfile.TemporaryDirectory
 def exact_city(world,counter,*args,**kwargs):
  need(counter==4,'unexpected fixture actor-city counter');return packet
 def later_restore(path,counter,*args,**kwargs):return original_world(path,19 if counter==5 else counter,*args,**kwargs)
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
 reproduction={'status':'PREFIX57-THREE-BUILDS-IDENTICAL','inputs':closure,'generated_compiler_sources_sha256':generated,'payload_sha256':sha(payload),'public_world_package_sha256':WORLD_PACKAGE,'world_source_sha256':digest(out/'world18-source.json'),'dummy_fixture_signing_only':True,'owner_private_key_loads':0}
 (out/'reproduction.json').write_text(json.dumps(reproduction,indent=2)+'\n')
 report={'status':'BOOT-PREFIX57-REPEATED-EFI-QEMU-WORLD18-DIAGNOSTIC-PASS','build_host':'yukabox','native_counter':57,'payload_bytes':len(payload),'mapped_bytes':mapped,'payload_sha256':sha(payload),'source_sha256':closure,'generated_compiler_sources_sha256':generated,'gates':gates,'native_report_sha256':digest(native),'reproduction_sha256':digest(out/'reproduction.json'),'receiver_policy':build.policy(),'receiver_policy_sha256':digest(ROOT/'receiver-policy.json'),'host_checks':host,'world_package_sha256':WORLD_PACKAGE,'world_semantic_sha256':WORLD_SEMANTIC,'exact_world18_QEMU':True,'world_source_sha256':digest(out/'world18-source.json'),'max_MAIN_bytes':32984,'max_MAIN_descriptors':133,'BMI_DONE_commands':0,'HTC_INIT_scan_commands':0,'deadline_us':600000000,'physical_verified':False,'signing_admitted':False,'owner_private_key_loads':0,'device_operations':0,'wifi_connected':False,'radio_backend':'MOCK USB ONLY'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(payload),mapped,sha(payload),flush=True)
if __name__=='__main__':main()
