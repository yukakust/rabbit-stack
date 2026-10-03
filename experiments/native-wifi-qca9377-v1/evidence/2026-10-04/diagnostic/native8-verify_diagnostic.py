#!/usr/bin/env python3
"""Run on Yukabox. Actual city-family UEFI gates and host sanitizers."""
import hashlib,json,subprocess,sys
from pathlib import Path
import diagnostic_build as build
sys.path.insert(0,str(build.CITY))
import actors_gate
ROOT=Path(__file__).resolve().parent
def fixture(source):
 source=build.one(source,'static uint8_t incoming[260],last_att;',
     'static uint8_t diagnostic_reply[247];static size_t diagnostic_reply_size;\nstatic uint8_t incoming[260],last_att;')
 source=build.one(source,'last_att=p[8];completed_packets++;',
     'last_att=p[8];diagnostic_reply_size=*n-8;if(diagnostic_reply_size>247)return EFI_ERROR(2);copy(diagnostic_reply,p+8,diagnostic_reply_size);completed_packets++;')
 source=build.one(source,'say("CITY FULLSCREEN QEMU READY");',r'''
 uint8_t request_pci[3]={0x0a,9,0};
 if(att(request_pci,3,0x0b)||diagnostic_reply_size!=129||!same(diagnostic_reply+1,(const uint8_t*)"QPD\1",4))return 1;
 /* Actual OVMF enumerator, QCA absent: positive flags/count, no guessed device. */
 if(le32(diagnostic_reply+5)!=1||!le32(diagnostic_reply+17)||le32(diagnostic_reply+21))return 1;
 say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");
 say("CITY FULLSCREEN QEMU READY");
 ''')
 return source
def main():
 out=ROOT/'runs/diagnostic';out.mkdir(parents=True,exist_ok=False)
 public=bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7')
 # Public VM key only; private fixture keys are confined to existing VM gates.
 target,modules,crypto=build.actors.engine.prepare(out,public)
 payload=build.compile_driver(out,crypto)
 assert payload==build.compile_driver(out,crypto),'non-reproducible candidate'
 (out/'payload.efi').write_bytes(payload)
 includes=[out,build.actors.OLD,build.actors.NATIVE,build.actors.LINK]
 host=out/'diagnostic-test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
  *['-I'+str(p) for p in includes],str(ROOT/'diagnostic_test.c'),str(out/'pci_collect.c'),
  str(out/'pci_identity.c'),str(out/'diagnostic_gatt.c'),str(build.actors.LINK/'file_core.c'),
  str(build.actors.NATIVE/'sha256.c'),'-o',str(host)],check=True)
 result=subprocess.run([str(host)],capture_output=True,text=True,check=True)
 (out/'host.log').write_text(result.stdout+result.stderr)
 gates=[actors_gate.qemu_gate(out,payload,test_transform=fixture),actors_gate.qemu_gate(out,payload,True,test_transform=fixture)]
 sources={str(p.relative_to(ROOT.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
   for p in [ROOT/n for n in ('diagnostic_build.py','pci_collect.c','pci_collect.h','pci_identity.c','pci_identity.h','diagnostic_test.c','verify_diagnostic.py')]
   +[build.CITY/n for n in ('actors_build.py','city_core.c','city_core.h','city_display.c','actor_clock.c','actors_gate.py')]}
 report={'status':'READ-ONLY-PCI-CITY-PROFILE-GATES-PASS','payload_sha256':hashlib.sha256(payload).hexdigest(),
  'reproducible_builds':2,'source_sha256':sources,'host_log_sha256':hashlib.sha256((out/'host.log').read_bytes()).hexdigest(),
  'gates':gates,'physical_dell_verified':False,'pci_writes':0,'mmio':0,'dma':0,'wifi_radio':0}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
