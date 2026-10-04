#!/usr/bin/env python3
"""Yukabox sanitizers/COFF and pinned helper ABI; no physical operation."""
import hashlib,json,subprocess,os
from pathlib import Path
from verify_port import CC
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/board-core';out.mkdir(parents=True,exist_ok=True)
 inc=['-I'+str(p) for p in (ROOT,ROOT.parent/'x86-64-uefi-wireless-supervisor-v1',ROOT.parent/'x86-64-uefi-runtime-supervisor-v1')]
 files=('bmi_loader.c','bmi_loader.h','bmi_loader_test.c','board_query.c','board_query.h','board_smbios.c','board_smbios.h','board_smbios_test.c','board-query-policy.json','verify_board_core.py')
 inputs={n:sha((ROOT/n).read_bytes()) for n in files};log=''
 native=ROOT.parent/'x86-64-uefi-runtime-supervisor-v1'
 for name,names,cases in (('bmi-loader',('bmi_loader.c','bmi_loader_test.c','bmi_transport.c','rom_ready.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','boot_irq.c','power_core.c','pci_identity.c'),range(10)),('smbios',('board_smbios.c','board_smbios_test.c'),(None,))):
  exe=out/name
  subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,*[str(ROOT/n) for n in names],'-o',str(exe)],check=True)
  for i in cases:
   r=subprocess.run([str(exe)]+([] if i is None else [str(i)]),capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'});log+=r.stdout+r.stderr
 for name in ('bmi_loader','board_query','board_smbios'):
  subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*inc,'-I'+str(native),'-c',str(ROOT/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 assert inputs=={n:sha((ROOT/n).read_bytes()) for n in files}
 (out/'host.log').write_text(log)
 policy=json.loads((ROOT/'board-query-policy.json').read_text())
 vendor=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/linux/drivers/net/wireless/ath/ath10k')
 for name,expected in policy['reference_sha256'].items():assert sha((vendor/name).read_bytes())==expected,name
 report={'status':'BOUNDED-BOARD-HELPER-BMI-SMBIOS-HOST-COFF-PASS','source_sha256':inputs,'reference_sha256':policy['reference_sha256'],'host_log_sha256':sha(log.encode()),'build_host':'yukabox','physical_verified':False,'permanent_otp_commands':False,'main_firmware_execution':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
