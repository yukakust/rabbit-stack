#!/usr/bin/env python3
"""Run on Yukabox. Actual city-family UEFI gates and host sanitizers."""
import hashlib,json,subprocess,sys
from pathlib import Path
import power_build as build
sys.path.insert(0,str(build.CITY))
import actors_gate
ROOT=Path(__file__).resolve().parent
def fixture(source):
 source=build.one(source,'static uint8_t incoming[260],last_att;',
     'static uint8_t diagnostic_reply[247];static size_t diagnostic_reply_size;\nstatic uint8_t incoming[260],last_att;')
 source=build.one(source,'last_att=p[8];completed_packets++;',
     'last_att=p[8];diagnostic_reply_size=*n-8;if(diagnostic_reply_size>247)return EFI_ERROR(2);copy(diagnostic_reply,p+8,diagnostic_reply_size);completed_packets++;')
 source=build.one(source,'say("CITY FULLSCREEN QEMU READY");',r'''
 uint8_t request_pci[3]={0x0a,10,0};
 if(att(request_pci,3,0x0b)||diagnostic_reply_size!=145||!same(diagnostic_reply+1,(const uint8_t*)"QPD\3",4))return 1;
 /* Actual OVMF enumerator, QCA absent: positive flags/count, no guessed device. */
 if(le32(diagnostic_reply+5)!=1||!le32(diagnostic_reply+17)||le32(diagnostic_reply+21))return 1;
 say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");
 say("CITY FULLSCREEN QEMU READY");
 ''')
 return source
def main():
 out=ROOT/'runs/power';out.mkdir(parents=True,exist_ok=False)
 public=bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7')
 # Public VM key only; private fixture keys are confined to existing VM gates.
 target,modules,crypto=build.actors.engine.prepare(out,public)
 payload=build.compile_driver(out,crypto)
 assert payload==build.compile_driver(out,crypto),'non-reproducible candidate'
 (out/'payload.efi').write_bytes(payload)
 test=(ROOT/'diagnostic_test.c').read_text().replace('config[16]','config[64]').replace('count==16','count==64')
 for before,after in [('reconstructed[128]','reconstructed[144]'),('==129','==145'),('diagnostic,128','diagnostic,144'),('<=128','<=144'),('129-offset','145-offset'),('0,129,0','0,145,0'),('offset<128','offset<144')]:test=test.replace(before,after)
 test=test.replace(' qca_collect(&system);assert(get(4,4)==15', ' config[1]=0x00100100;config[13]=0x40;config[16]=0x00005001;config[17]=3;config[20]=0x10;config[24]=2;\n qca_collect(&system);assert(get(128,2)==0x40&&get(130,2)==3&&get(132,2)==0x50&&get(134,2)==2&&get(136,4)==1);assert(get(4,4)==15',1)
 (out/'power-test.c').write_text(test)
 includes=[out,build.actors.OLD,build.actors.NATIVE,build.actors.LINK]
 host=out/'diagnostic-test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
  *['-I'+str(p) for p in includes],str(out/'power-test.c'),str(out/'pci_collect.c'),
  str(out/'pci_identity.c'),str(out/'power_core.c'),str(out/'diagnostic_gatt.c'),str(build.actors.LINK/'file_core.c'),
  str(build.actors.NATIVE/'sha256.c'),'-o',str(host)],check=True)
 result=subprocess.run([str(host)],capture_output=True,text=True,check=True)
 pure=out/'power-parser-test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(ROOT),str(ROOT/'power_test.c'),str(ROOT/'power_core.c'),'-o',str(pure)],check=True)
 parser=subprocess.run([str(pure)],capture_output=True,text=True,check=True)
 (out/'host.log').write_text(result.stdout+result.stderr+parser.stdout+parser.stderr)
 gates=[actors_gate.qemu_gate(out,payload,test_transform=fixture),actors_gate.qemu_gate(out,payload,True,test_transform=fixture)]
 sources={str(p.relative_to(ROOT.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
   for p in [ROOT/n for n in ('power_build.py','power_core.c','power_core.h','power_test.c','verify_power.py','diagnostic_build.py','pci_collect.c','pci_collect.h','pci_identity.c','pci_identity.h','diagnostic_test.c','verify_diagnostic.py')]
   +[build.CITY/n for n in ('actors_build.py','city_core.c','city_core.h','city_display.c','actor_clock.c','actors_gate.py')]}
 report={'status':'READ-ONLY-PCI-POWER-CITY-PROFILE-GATES-PASS','payload_sha256':hashlib.sha256(payload).hexdigest(),
  'reproducible_builds':2,'source_sha256':sources,'host_log_sha256':hashlib.sha256((out/'host.log').read_bytes()).hexdigest(),
  'gates':gates,'physical_dell_verified':False,'pci_writes':0,'mmio':0,'dma':0,'wifi_radio':0}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
