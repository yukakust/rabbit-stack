#!/usr/bin/env python3
"""Yukabox exact one-shot probe gates. OVMF target absent, host MMIO fixtures."""
import hashlib,json,subprocess,sys,shutil,os
from pathlib import Path
import bmi_build as build
import verify_ce_hw,verify_bmi
import verify_reset
import verify_diagnostic as diagnostic
import verify_port
sys.path.insert(0,str(build.CITY))
import actors_gate
ROOT=build.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(source):
 source=diagnostic.fixture(source).replace('diagnostic_reply_size!=129','diagnostic_reply_size!=241').replace('"QPD\\1"','"QPD\\5"')
 return build.one(source,'say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");',
  'if(le32(diagnostic_reply+129)!=7||le32(diagnostic_reply+141)!=1)return 1;\n say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");\n say("ONE-SHOT WIFI RESET PROBE TARGET ABSENT; CLEAN CLOSE AND CITY RETAINED");')
def main():
 out=ROOT/'runs/bmi-profile';out.mkdir(parents=True,exist_ok=False)
 verify_port.main()
 verify_reset.main()
 verify_ce_hw.main()
 verify_bmi.main()
 for component,run in [("ce","ce-hw"),("bmi","bmi")]:
  shutil.copyfile(ROOT/("runs/"+run+"/report.json"),out/(component+"-report.json"))
  shutil.copyfile(ROOT/("runs/"+run+"/host.log"),out/(component+"-host.log"))
 shutil.copyfile(ROOT/'runs/reset-core/report.json',out/'reset-report.json')
 shutil.copyfile(ROOT/'runs/reset-core/host.log',out/'reset-host.log')
 shutil.copyfile(ROOT/'runs/port/report.json',out/'port-report.json')
 shutil.copyfile(ROOT/'runs/port/host.log',out/'port-host.log')
 public=bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7')
 _,_,crypto=build.actors.engine.prepare(out,public)
 payload=build.compile_driver(out,crypto);assert payload==build.compile_driver(out,crypto)
 (out/'payload.efi').write_bytes(payload)
 exe=out/'bringup-test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
  *['-I'+str(p) for p in (ROOT,out,build.actors.OLD,build.actors.NATIVE)],
  str(ROOT/'bmi_probe_test.c'),*[str(out/n) for n in ('bmi_probe.c','reset_core.c','power_core.c','uefi_port.c','wake_core.c','pci_identity.c','rom_ready.c','bmi_transport.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c')],'-o',str(exe)],check=True)
 log=''
 for scenario in range(17):
  result=subprocess.run([str(exe),str(scenario)],capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'});log+=result.stdout+result.stderr
 (out/'host.log').write_text(log)
 gates=[actors_gate.qemu_gate(out,payload,test_transform=fixture),actors_gate.qemu_gate(out,payload,True,test_transform=fixture)]
 files=('bmi_build.py','bringup.h','bmi_probe.c','bmi_probe_test.c','verify_bmi_profile.py','reset_core.c','reset_core.h','reset_test.c','reset-target.json','verify_reset.py','power_core.c','power_core.h',
  'diagnostic_build.py','verify_diagnostic.py','pci_collect.c','pci_collect.h','pci_identity.c','pci_identity.h',
  'uefi_port.c','uefi_port.h','wake_core.c','wake_core.h','port_test.c','verify_port.py','wake-target.json','wake_test.c','rom_ready.c','rom_ready.h','bmi_transport.c','bmi_transport.h','ce_ring.c','ce_ring.h','ce_hw.c','ce_hw.h','ce_uefi.c','ce_uefi.h','ce_bus.c','ce_bus.h','dma_buffer.c','dma_buffer.h','ce_hw_test.c','ce_uefi_test.c','ce_bus_test.c','bmi_transport_test.c','verify_ce_hw.py','verify_bmi.py','ce-target.json','bmi-target.json')
 paths=[ROOT/n for n in files]+[build.CITY/n for n in ('actors_build.py','city_core.c','city_core.h','city_display.c','actor_clock.c','actors_gate.py')]
 report={'status':'QCA-ROM-BMI-CITY-PROFILE-GATES-PASS','payload_sha256':sha(payload),
  'source_sha256':{str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in paths},
  'host_log_sha256':sha((out/'host.log').read_bytes()),'port_report_sha256':sha((out/'port-report.json').read_bytes()),
  'reset_report_sha256':sha((out/'reset-report.json').read_bytes()),'gates':gates,'physical_dell_verified':False,'dma':True,'ce_report_sha256':sha((out/'ce-report.json').read_bytes()),'bmi_report_sha256':sha((out/'bmi-report.json').read_bytes()),'firmware_upload':False,
  'physical_operation':'one-shot QCA reset + ROM-ready + four coherent DMA pages + CE0/1 BMI target-info; verified all-eight halt, bus-master-off/Flush/Unmap/Free/PCI restore; no firmware upload'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('BRINGUP GATES PASS payload='+sha(payload))
if __name__=='__main__':main()
