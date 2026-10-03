#!/usr/bin/env python3
"""Yukabox UEFI DMA host/COFF gates, no physical device/DMA activation."""
import hashlib,json,subprocess,os
from pathlib import Path
from verify_port import CC,NETWORK
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/dma';out.mkdir(parents=True,exist_ok=True)
 inc=['-I'+str(ROOT),'-I'+str(ROOT.parent/'x86-64-uefi-wireless-supervisor-v1'),'-I'+str(ROOT.parent/'x86-64-uefi-runtime-supervisor-v1')]
 exe=out/'test';names=('dma_buffer.c','dma_buffer_test.c','uefi_port.c','wake_core.c','pci_identity.c')
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,*[str(ROOT/n) for n in names],'-o',str(exe)],check=True)
 log=''
 for i in range(18):
  run=subprocess.run([str(exe),str(i)],capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=f'SCENARIO {i} PASS\n'+run.stdout+run.stderr
 (out/'host.log').write_text(log)
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*inc,'-c',str(ROOT/'dma_buffer.c'),'-o',str(out/'dma_buffer.obj')],check=True)
 layout=out/'layout.c';layout.write_text('#define FILE_LICENCE(x)\n#define FILE_SECBOOT(x)\n#include <stddef.h>\n#include <ipxe/efi/Uefi.h>\n#include <ipxe/efi/Protocol/PciIo.h>\n'+''.join(f'_Static_assert(offsetof(EFI_PCI_IO_PROTOCOL,{name})=={offset},"{name}");\n' for name,offset in [('Map',72),('Unmap',80),('AllocateBuffer',88),('FreeBuffer',96),('Flush',104)]))
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-idirafter',str(NETWORK/'vendor/ipxe/src/include'),'-I'+str(NETWORK/'vendor/ipxe/src/include/ipxe/efi/X64'),'-c',str(layout),'-o',str(out/'layout.obj')],check=True)
 sources=(*names,'dma_buffer.h','uefi_port.h','wake_core.h','pci_identity.h','verify_dma.py')
 report={'status':'UEFI-COMMON-DMA-LIFETIME-HOST-COFF-ABI-PASS','source_sha256':{n:sha((ROOT/n).read_bytes()) for n in sources},'host_log_sha256':sha((out/'host.log').read_bytes()),'build_host':'yukabox','efi_abi_reference':'pinned iPXE6262f1081fe185564e8ec8365a1d23597ec6e6f5 headers','physical_dma_activation':False,'ce_stop_callback':'mock only; physical CE halt adapter still required','ce_mmio_implemented':False,'bmi_implemented':False,'wifi_association':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
