#!/usr/bin/env python3
"""Actual CE core/PCI IO adapter in sanitizer mocks and freestanding COFF."""
import hashlib,json,subprocess,os
from pathlib import Path
from verify_port import CC
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 target=json.loads((ROOT/'ce-target.json').read_text())
 vendor=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/linux/drivers/net/wireless/ath/ath10k')
 assert sha((vendor/'hw.c').read_bytes())==target['hw_source_sha256']
 assert target['register_masks']['watermark_high']==65535 and target['register_masks']['watermark_low']==0xffff0000
 assert target['ce_base_addresses']==[0x34400+i*0x400 for i in range(8)]
 out=ROOT/'runs/ce-hw';out.mkdir(parents=True,exist_ok=True)
 inc=['-I'+str(ROOT),'-I'+str(ROOT.parent/'x86-64-uefi-wireless-supervisor-v1'),'-I'+str(ROOT.parent/'x86-64-uefi-runtime-supervisor-v1')]
 flags=['-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc]
 env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'};log=''
 for name,sources,scenarios in [('core',['ce_hw.c','ce_hw_test.c'],[[str(i)] for i in range(10)]),('uefi',['ce_hw.c','ce_uefi.c','ce_uefi_test.c','dma_buffer.c'],[[]]),('bus',['ce_hw.c','ce_uefi.c','ce_bus.c','ce_bus_test.c','dma_buffer.c'],[[str(i)] for i in range(10)])]:
  exe=out/name
  subprocess.run(['gcc',*flags,*[str(ROOT/n) for n in sources],'-o',str(exe)],check=True)
  for args in scenarios:
   run=subprocess.run([str(exe),*args],capture_output=True,text=True,check=True,env=env)
   log+=f'{name} {args} PASS\n'+run.stdout+run.stderr
 (out/'host.log').write_text(log)
 for name in ('ce_hw','ce_uefi','ce_bus'):
  subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*inc,'-c',str(ROOT/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 names=('ce_bus.c','ce_bus.h','ce_bus_test.c','ce-target.json','ce_hw.c','ce_hw.h','ce_hw_test.c','ce_uefi.c','ce_uefi.h','ce_uefi_test.c','dma_buffer.c','dma_buffer.h','uefi_port.h','wake_core.h','verify_ce_hw.py')
 report={'status':'CE-MMIO-UEFI-MAPPED-LIFETIME-HOST-COFF-PASS','source_sha256':{n:sha((ROOT/n).read_bytes()) for n in names},'host_log_sha256':sha((out/'host.log').read_bytes()),'build_host':'yukabox','linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','physical_ce_activation':False,'physical_dma_activation':False,'bus_master_lifecycle_implemented':True,'bmi_implemented':False,'firmware_uploaded':False,'wifi_association':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
