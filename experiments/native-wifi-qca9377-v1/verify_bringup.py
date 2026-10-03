#!/usr/bin/env python3
"""Yukabox exact one-shot probe gates. OVMF target absent, host MMIO fixtures."""
import hashlib,json,subprocess,sys,shutil
from pathlib import Path
import bringup_build as build
import verify_diagnostic as diagnostic
import verify_port
sys.path.insert(0,str(build.CITY))
import actors_gate
ROOT=build.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(source):
 source=diagnostic.fixture(source).replace('diagnostic_reply_size!=129','diagnostic_reply_size!=161').replace('"QPD\\1"','"QPD\\2"')
 return build.one(source,'say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");',
  'if(le32(diagnostic_reply+129)!=4||le32(diagnostic_reply+141)!=1)return 1;\n say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");\n say("ONE-SHOT WIFI PROBE TARGET ABSENT; CLEAN CLOSE AND CITY RETAINED");')
def main():
 out=ROOT/'runs/bringup';out.mkdir(parents=True,exist_ok=False)
 verify_port.main()
 shutil.copyfile(ROOT/'runs/port/report.json',out/'port-report.json')
 shutil.copyfile(ROOT/'runs/port/host.log',out/'port-host.log')
 public=bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7')
 _,_,crypto=build.actors.engine.prepare(out,public)
 payload=build.compile_driver(out,crypto);assert payload==build.compile_driver(out,crypto)
 (out/'payload.efi').write_bytes(payload)
 exe=out/'bringup-test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
  *['-I'+str(p) for p in (ROOT,out,build.actors.OLD,build.actors.NATIVE)],
  str(ROOT/'bringup_test.c'),*[str(out/n) for n in ('bringup.c','uefi_port.c','wake_core.c','pci_identity.c')],'-o',str(exe)],check=True)
 log=''
 for scenario in range(15):
  result=subprocess.run([str(exe),str(scenario)],capture_output=True,text=True,check=True);log+=result.stdout+result.stderr
 (out/'host.log').write_text(log)
 gates=[actors_gate.qemu_gate(out,payload,test_transform=fixture),actors_gate.qemu_gate(out,payload,True,test_transform=fixture)]
 files=('bringup_build.py','bringup.h','bringup.c','bringup_test.c','verify_bringup.py',
  'diagnostic_build.py','verify_diagnostic.py','pci_collect.c','pci_collect.h','pci_identity.c','pci_identity.h',
  'uefi_port.c','uefi_port.h','wake_core.c','wake_core.h','port_test.c','verify_port.py','wake-target.json','wake_test.c')
 paths=[ROOT/n for n in files]+[build.CITY/n for n in ('actors_build.py','city_core.c','city_core.h','city_display.c','actor_clock.c','actors_gate.py')]
 report={'status':'REVERSIBLE-PCI-WAKE-CITY-PROFILE-GATES-PASS','payload_sha256':sha(payload),
  'source_sha256':{str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in paths},
  'host_log_sha256':sha((out/'host.log').read_bytes()),'port_report_sha256':sha((out/'port-report.json').read_bytes()),
  'gates':gates,'physical_dell_verified':False,'dma':False,'firmware_upload':False,
  'physical_operation':'one-shot PCI memory decode + wake/chip-ID, then restore/close; no bus master/reset'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('BRINGUP GATES PASS payload='+sha(payload))
if __name__=='__main__':main()
