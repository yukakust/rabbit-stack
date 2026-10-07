#!/usr/bin/env python3
"""Whole EFI repeat builds, real supervisor QEMU and frozen world17 C gates."""
import importlib.util,json,hashlib,shutil,time
from pathlib import Path
import profile_build as build
spec=importlib.util.spec_from_file_location('checked_qemu_verifier',build.checked.ROOT/'verify_candidate.py')
checked=importlib.util.module_from_spec(spec);spec.loader.exec_module(checked)
ROOT=build.ROOT;REPO=ROOT.parent.parent;sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(text):
 s=checked.fixture(text)
 marker='say("WMI INIT SERVICE26..28 READ ONLY; ABSENT RADIO CLAIMS NO READY/MAC/IP");'
 code=r'''
 uint8_t prof_service[7]={0x10,29,0,255,255,0,0x28};
 if(att(prof_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=29||diagnostic_reply[4]!=31||diagnostic_reply[6]!=0x28)return 1;
 uint8_t prof_status[3]={0x0a,31,0};
 if(att(prof_status,3,0x0b)||diagnostic_reply_size!=193||!same(diagnostic_reply+1,(const uint8_t*)"QWRX0001",8))return 1;
 for(unsigned i=9;i<193;i++)if(diagnostic_reply[i]!=(i==185?53:0))return 1;
 uint8_t prof_write[4]={0x12,31,0,0};if(att(prof_write,4,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
 uint8_t prof_blob[5]={0x0c,31,0,192,0};if(att(prof_blob,5,0x0d)||diagnostic_reply_size!=1)return 1;
 prof_blob[3]=193;if(att(prof_blob,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
 say("BOUNDED RX SERVICE29..31 READ ONLY; ABSENT RADIO CLAIMS NO READY OR ACTIVE OWNERS");
'''+marker
 return build.one(s,marker,code)
def main():
 out=ROOT/'runs/checked-candidate';out.mkdir(parents=True,exist_ok=True)
 paths=[p for d in (build.checked.BASE,build.checked.SESSION,build.checked.AVAILABLE,build.checked.LAYOUT,build.checked.TXN,build.checked.INIT,build.checked.MEM,build.checked.RES,build.checked.ROOT,build.RX,build.rx.BRIDGE,build.rx.prior.LIFE,ROOT) for p in d.iterdir() if p.is_file()]
 inputs={str(p.relative_to(REPO)):sha(p.read_bytes()) for p in paths}
 baseline=Path('/home/yuka/rabbit-world/wifi-bt42-v1/source/experiments/native-wifi-qca9377-wmi-native-v5/runs/operating-profile/reproduction.json')
 inherited=json.loads(baseline.read_text())['inputs']
 shared=Path('/home/yuka/rabbit-world/wifi-bt42-v1/source')
 for n,h in inherited.items():
  p=Path(n)
  if p.is_absolute() or '..' in p.parts or not n.startswith('experiments/'):raise ValueError('invalid inherited source path')
  source=shared/p;destination=REPO/p
  if sha(source.read_bytes())!=h:raise ValueError('inherited source differs:'+n)
  if not destination.exists():destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,destination)
  if sha(destination.read_bytes())!=h:raise ValueError('isolated inherited source differs:'+n)
 inputs={**inherited,**inputs}
 _,_,crypto=build.checked.prior.actors.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'))
 payload=build.compile_driver(out,crypto);assert payload==build.compile_driver(out,crypto)
 (out/'payload.efi').write_bytes(payload)
 for n in ('actors-qemu','actors-empty-boot-qemu'):
  p=out/n
  if p.exists():shutil.move(str(p),str(out/(n+'.previous-'+str(time.time_ns()))))
 gates=[checked.verify_init_profile.prior.actors_gate.qemu_gate(out,payload,test_transform=fixture),checked.verify_init_profile.prior.actors_gate.qemu_gate(out,payload,True,test_transform=fixture)]
 from actors_check import check_city
 world=Path('/home/yuka/rabbit-world/parallel-persistent-profile-v1/world.rup');assert sha(world.read_bytes())=='47d63aa6e81b35fc355005cf65f889b9c43bc332443e37ddbba672b920c2fc2b'
 host=check_city(world,out/'current-world-check',sanitizers=True)
 assert inputs=={n:sha((REPO/n).read_bytes()) for n in inputs}
 # Include exact generated compiler inputs plus all imported Python and local
 # included headers. No physical release or admission proof is fabricated.
 closure=dict(inputs)
 import sys
 for module in list(sys.modules.values()):
  f=getattr(module,'__file__',None)
  if f:
   p=Path(f).resolve()
   if p.is_file() and p.suffix=='.py' and p.is_relative_to(REPO):closure[str(p.relative_to(REPO))]=sha(p.read_bytes())
 for parent in (build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE):
  for p in parent.iterdir():
   if p.is_file():closure[str(p.relative_to(REPO))]=sha(p.read_bytes())
 generated={p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file() and p.suffix in ('.c','.h')}
 assert payload==build.compile_driver(out,crypto)==build.compile_driver(out,crypto)
 assert generated=={p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file() and p.suffix in ('.c','.h')}
 assert closure=={n:sha((REPO/n).read_bytes()) for n in closure}
 npath=ROOT/'runs/native-host/report.json';nr=json.loads(npath.read_text());assert nr['status']=='BOUNDED-PERSISTENT-PROFILE-NATIVE-ASAN-COFF-PASS'
 for n,h in nr['source_sha256'].items():assert closure.get(n)==h,'native model source differs:'+n
 assert sha(npath.with_name('host.log').read_bytes())==nr['host_log_sha256']
 report={'status':'BOUNDED-PERSISTENT-PROFILE-REPEATED-EFI-QEMU-WORLD17-PASS','build_host':'yukabox','payload_sha256':sha(payload),'payload_bytes':len(payload),'source_sha256':closure,'inherited_native52_closure_sha256':sha(baseline.read_bytes()),'generated_compiler_sources_sha256':generated,'gates':gates,'receiver_policy':build.policy(),'native_report_sha256':sha(npath.read_bytes()),'host_checks':host,'world_package_sha256':sha(world.read_bytes()),'world_semantic_sha256':'fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74','physical_verified':False,'signing_admitted':False,'station_ready':False,'rf_transmit':False,'bounded_us':10000000,'physical_native52_success_assumed':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(payload),sha(payload))
if __name__=='__main__':main()
