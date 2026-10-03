#!/usr/bin/env python3
"""ROM/BMI transport integration on Yukabox, not a physical BMI result."""
import hashlib,json,subprocess,os
from pathlib import Path
from verify_port import CC
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/bmi';out.mkdir(parents=True,exist_ok=True)
 inc=['-I'+str(ROOT),'-I'+str(ROOT.parent/'x86-64-uefi-wireless-supervisor-v1'),'-I'+str(ROOT.parent/'x86-64-uefi-runtime-supervisor-v1')]
 names=('rom_ready.c','bmi_transport.c','bmi_transport_test.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','boot_irq.c','power_core.c','pci_identity.c')
 exe=out/'test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,*[str(ROOT/n) for n in names],'-o',str(exe)],check=True)
 log=''
 for i in range(11):
  run=subprocess.run([str(exe),str(i)],capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=run.stdout+run.stderr
 (out/'host.log').write_text(log)
 for name in ('rom_ready','bmi_transport'):
  subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*inc,'-c',str(ROOT/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 sources=(*names,'bmi-target.json','rom_ready.h','bmi_transport.h','ce_ring.h','ce_hw.h','ce_uefi.h','ce_bus.h','dma_buffer.h','uefi_port.h','wake_core.h','boot_irq.h','power_core.h','pci_identity.h','verify_bmi.py')
 vendor=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/linux/drivers/net/wireless/ath/ath10k')
 target=json.loads((ROOT/'bmi-target.json').read_text())
 assert target['rom_indicator_address']==0x3a028 and target['bmi_get_target_info']==8 and target['response_bytes']==12
 for n,h in target['reference_sha256'].items():assert sha((vendor/n).read_bytes())==h,n
 report={'status':'ROM-BMI-CE0-CE1-INTEGRATION-HOST-COFF-PASS','source_sha256':{n:sha((ROOT/n).read_bytes()) for n in sources},'reference_sha256':{n:sha((vendor/n).read_bytes()) for n in ['pci.c','hw.c','hw.h','bmi.c','bmi.h']},'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','host_log_sha256':sha((out/'host.log').read_bytes()),'build_host':'yukabox','physical_rom_ready':False,'physical_bmi_response':False,'native_profile_integrated':False,'firmware_uploaded':False,'wifi_association':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
