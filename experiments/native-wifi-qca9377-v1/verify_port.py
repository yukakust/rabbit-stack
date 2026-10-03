#!/usr/bin/env python3
"""Yukabox-only initial port check. No physical PCI/MMIO accesses."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXP=ROOT.parent
NETWORK=Path('/home/yuka/rabbit-world/dell-network-viewer-v1')
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
def main():
 out=ROOT/'runs/port';out.mkdir(parents=True,exist_ok=True)
 inc=['-I'+str(ROOT),'-I'+str(EXP/'x86-64-uefi-wireless-supervisor-v1'),'-I'+str(EXP/'x86-64-uefi-runtime-supervisor-v1')]
 logs=[]
 for name,sources in [('wake',['wake_core.c','wake_test.c']),('port',['wake_core.c','uefi_port.c','pci_identity.c','port_test.c'])]:
  exe=out/(name+'-test')
  subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
   *inc,*[str(ROOT/n) for n in sources],'-o',str(exe)],check=True)
  result=subprocess.run([str(exe)],capture_output=True,text=True,check=True);logs.append(result.stdout+result.stderr)
 for name in ('wake_core','uefi_port','pci_identity'):
  subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone',
   '-Os','-Wall','-Wextra','-Werror',*inc,'-c',str(ROOT/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 layout=out/'layout.c';layout.write_text('''
#define FILE_LICENCE(x)
#define FILE_SECBOOT(x)
#include <stddef.h>
#include <ipxe/efi/Uefi.h>
#include <ipxe/efi/Protocol/PciIo.h>
_Static_assert(offsetof(EFI_BOOT_SERVICES,OpenProtocol)==280,"OpenProtocol");
_Static_assert(offsetof(EFI_BOOT_SERVICES,CloseProtocol)==288,"CloseProtocol");
_Static_assert(offsetof(EFI_BOOT_SERVICES,FreePool)==72,"FreePool");
_Static_assert(offsetof(EFI_PCI_IO_PROTOCOL,Mem)==16,"Mem read/write");
_Static_assert(offsetof(EFI_PCI_IO_PROTOCOL,Pci)==48,"PCI read/write");
_Static_assert(offsetof(EFI_PCI_IO_PROTOCOL,Attributes)==120,"Attributes");
_Static_assert(offsetof(EFI_PCI_IO_PROTOCOL,GetBarAttributes)==128,"GetBarAttributes");
''')
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding',
  '-idirafter',str(NETWORK/'vendor/ipxe/src/include'),'-I'+str(NETWORK/'vendor/ipxe/src/include/ipxe/efi/X64'),
  '-c',str(layout),'-o',str(out/'layout.obj')],check=True)
 (out/'host.log').write_text(''.join(logs))
 names=('wake_core.c','wake_core.h','wake_test.c','wake-target.json','uefi_port.c','uefi_port.h','port_test.c','verify_port.py','pci_identity.c','pci_identity.h')
 report={'status':'INITIAL-UEFI-PCI-WAKE-PORT-HOST-MOCK-AND-COFF-ABI-PASS',
  'source_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names},
  'host_log_sha256':hashlib.sha256((out/'host.log').read_bytes()).hexdigest(),
  'efi_abi_reference':'pinned iPXE6262f1081fe185564e8ec8365a1d23597ec6e6f5 headers',
  'build_host':'yukabox','physical_activated':False,'actual_uefi_execution':False,
  'mmio':'mock only','dma_implemented':False,'bmi_implemented':False,'firmware_uploaded':False,'wifi_associated':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
