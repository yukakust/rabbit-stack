#!/usr/bin/env python3
"""Actual Yukabox host+UEFI VM test. Does not load a Wi-Fi driver on Dell."""
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
NETWORK=Path('/home/yuka/rabbit-world/dell-network-viewer-v1')
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
def main():
    out=ROOT/'runs/pci';out.mkdir(parents=True,exist_ok=True)
    subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
        str(ROOT/'pci_identity.c'),str(ROOT/'pci_identity_test.c'),'-o',str(out/'identity-test')],check=True)
    result=subprocess.run([str(out/'identity-test')],capture_output=True,text=True,check=True)
    (out/'host.log').write_text(result.stdout+result.stderr)
    objects=[]
    for name in ('pci_probe','pci_identity'):
        obj=out/(name+'.obj');objects.append(str(obj))
        subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fshort-wchar',
             '-fno-stack-protector','-mno-red-zone','-O2','-idirafter',str(NETWORK/'vendor/ipxe/src/include'),
             '-I'+str(NETWORK/'vendor/ipxe/src/include/ipxe/efi/X64'),
             '-c',str(ROOT/(name+'.c')),'-o',str(obj)],check=True)
    binary=out/'pci-probe.efi'
    subprocess.run([str(CC.with_name('lld')),'-flavor','link','/subsystem:efi_application',
             '/entry:efi_main','/nodefaultlib','/timestamp:0','/out:'+str(binary),*objects],check=True)
    subprocess.run(['python3',str(NETWORK/'run_probe.py'),'--efi',str(binary),'--output',str(out/'uefi')],check=True)
    log=(out/'uefi/serial.log').read_text(errors='replace')
    assert 'QCA PCI ENUM STATUS 0000000000000000' in log
    assert 'QCA PCI HANDLE COUNT 0000000000000000' not in log
    assert 'QCA PCI TARGET COUNT 0000000000000000' in log
    assert 'QCA PCI WRITES=0 MMIO=0 DMA=0 RADIO=0' in log
    report={'passed':True,'physical_dell':False,'uefi':'OVMF QEMU RTL8139, target absent',
       'positive_device_identity_test':'host fixtures only, not physical',
       'efi_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
       'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
         ('pci_probe.c','pci_identity.c','pci_identity.h','pci_identity_test.c','verify_pci.py')},
       'host_sanitizers':['address','undefined'],'pci_writes':0,'mmio':0,'dma':0,'radio':0}
    (out/'pci-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__':main()
