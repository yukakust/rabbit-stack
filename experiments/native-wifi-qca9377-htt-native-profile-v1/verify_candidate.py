"""Equal wholeEFI builds, actual supervisor QEMU and exact world17 proof."""
import importlib.util,json,hashlib,shutil,time,sys
from pathlib import Path
import profile_build as build
spec=importlib.util.spec_from_file_location('checked_native52_qemu',build.checked.ROOT/'verify_candidate.py');checked=importlib.util.module_from_spec(spec);spec.loader.exec_module(checked)
ROOT=build.ROOT;REPO=ROOT.parent.parent;sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(text):
 s=checked.fixture(text)
 marker='say("WMI INIT SERVICE26..28 READ ONLY; ABSENT RADIO CLAIMS NO READY/MAC/IP");'
 code=r'''
 uint8_t hs[7]={0x10,29,0,255,255,0,0x28};
 if(att(hs,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=29||diagnostic_reply[4]!=31||diagnostic_reply[6]!=0x2e)return 1;
 uint8_t hr[5]={0x0a,31,0,0,0};
 if(att(hr,3,0x0b)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QHTT0001",8))return 1;
 for(unsigned j=9;j<247;j++)if(diagnostic_reply[j]!=(j==225?55:0))return 1;
 hr[0]=0x0c;hr[3]=246;if(att(hr,5,0x0d)||diagnostic_reply_size!=75)return 1;
 for(unsigned j=1;j<75;j++)if(diagnostic_reply[j])return 1;
 hr[3]=65;hr[4]=1;if(att(hr,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
 hs[1]=32;if(att(hs,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=32||diagnostic_reply[4]!=92||diagnostic_reply[6]!=0x30)return 1;
 for(unsigned slot=0;slot<6;slot++){
  hr[0]=0x0a;hr[1]=(uint8_t)(34+10*slot);hr[3]=hr[4]=0;
  if(att(hr,3,0x0b)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QHTX0001",8)||diagnostic_reply[9]!=slot)return 1;
  for(unsigned j=10;j<247;j++)if(diagnostic_reply[j])return 1;
  hr[0]=0x0c;hr[3]=0;hr[4]=2;if(att(hr,5,0x0d)||diagnostic_reply_size!=1)return 1;
  hr[3]=1;if(att(hr,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
  for(unsigned page=1;page<5;page++){hr[0]=0x0a;hr[1]=(uint8_t)(34+10*slot+2*page);
   if(att(hr,3,0x0b)||diagnostic_reply_size!=(page==4?57u:247u))return 1;
   for(unsigned j=1;j<diagnostic_reply_size;j++)if(diagnostic_reply[j])return 1;
   hr[0]=0x12;if(att(hr,3,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
  }
 }
 say("HTT55 READ-ONLY STATUS29..31 RAW32..92; ABSENT RADIO NO VERSION OR DATA-PLANE CLAIM");
'''+marker
 return build.one(s,marker,code)
def main():
 out=ROOT/'runs/checked-candidate';out.mkdir(parents=True,exist_ok=True)
 c=build.checked;n=build.native
 folders=(c.BASE,c.SESSION,c.AVAILABLE,c.LAYOUT,c.TXN,c.INIT,c.MEM,c.RES,c.ROOT,n.RX,n.BRIDGE,n.prior.prior.LIFE,n.ROOT,n.VERSION,build.PRIOR,build.SCAN,ROOT)
 inputs={str(p.relative_to(REPO)):sha(p.read_bytes()) for d in folders for p in d.iterdir() if p.is_file()}
 baseline=Path('/home/yuka/rabbit-world/wifi-bt42-v1/source/experiments/native-wifi-qca9377-wmi-native-v5/runs/operating-profile/reproduction.json')
 inherited=json.loads(baseline.read_text())['inputs'];shared=Path('/home/yuka/rabbit-world/wifi-bt42-v1/source')
 for name,h in inherited.items():
  p=Path(name)
  if p.is_absolute() or '..' in p.parts or not name.startswith('experiments/'):raise ValueError('invalid inherited path')
  src=shared/p;dst=REPO/p
  if sha(src.read_bytes())!=h:raise ValueError('frozen inherited source changed:'+name)
  if not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
  if sha(dst.read_bytes())!=h:raise ValueError('private source differs:'+name)
 inputs={**inherited,**inputs}
 _,_,crypto=c.prior.actors.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'))
 payload=build.compile_driver(out,crypto);assert payload==build.compile_driver(out,crypto)
 (out/'payload.efi').write_bytes(payload)
 for name in ('actors-qemu','actors-empty-boot-qemu'):
  p=out/name
  if p.exists():shutil.move(str(p),str(out/(name+'.previous-'+str(time.time_ns()))))
 gates=[checked.verify_init_profile.prior.actors_gate.qemu_gate(out,payload,test_transform=fixture),checked.verify_init_profile.prior.actors_gate.qemu_gate(out,payload,True,test_transform=fixture)]
 from actors_check import check_city
 world=Path('/home/yuka/rabbit-world/parallel-htt-native-profile-v1/world.rup');assert sha(world.read_bytes())=='47d63aa6e81b35fc355005cf65f889b9c43bc332443e37ddbba672b920c2fc2b'
 host=check_city(world,out/'current-world-check',sanitizers=True)
 assert inputs=={name:sha((REPO/name).read_bytes()) for name in inputs}
 closure=dict(inputs)
 for module in list(sys.modules.values()):
  f=getattr(module,'__file__',None)
  if f:
   p=Path(f).resolve()
   if p.is_file() and p.suffix=='.py' and p.is_relative_to(REPO):closure[str(p.relative_to(REPO))]=sha(p.read_bytes())
 for d in (c.prior.actors.OLD,c.prior.actors.NATIVE):
  for p in d.iterdir():
   if p.is_file():closure[str(p.relative_to(REPO))]=sha(p.read_bytes())
 generated={p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file() and p.suffix in ('.c','.h')}
 assert payload==build.compile_driver(out,crypto)==build.compile_driver(out,crypto)
 assert generated=={p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file() and p.suffix in ('.c','.h')}
 assert closure=={name:sha((REPO/name).read_bytes()) for name in closure}
 nrpath=ROOT/'runs/native-host/report.json';nr=json.loads(nrpath.read_text());assert nr['status']=='HTT55-PRODUCTION-AUTHENTICATED-IE6-RAW-EXPORT-ACTUAL-NATIVE-ASAN-COFF-PASS'
 for name,h in nr['source_sha256'].items():assert closure.get(name)==h,'native proof source differs:'+name
 assert sha(nrpath.with_name('host.log').read_bytes())==nr['host_log_sha256']
 report={'status':'HTT55-AUTHENTICATED-IE6-REPEATED-EFI-QEMU-WORLD17-RAW-PASS','build_host':'yukabox','payload_bytes':len(payload),'payload_sha256':sha(payload),'source_sha256':closure,'generated_compiler_sources_sha256':generated,'inherited_native52_closure_sha256':sha(baseline.read_bytes()),'gates':gates,'receiver_policy':build.policy(),'native_report_sha256':sha(nrpath.read_bytes()),'host_checks':host,'world_package_sha256':sha(world.read_bytes()),'world_semantic_sha256':'fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74','physical_verified':False,'signing_admitted':False,'rf_transmit':False,'htt_dataplane_ready':False,'bounded_us':3000000,'raw_slots':6,'raw_pages':30,'firmware_op_is_authenticated_ie':True}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(payload),sha(payload))
if __name__=='__main__':main()
