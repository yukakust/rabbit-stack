#!/usr/bin/env python3
"""Build on Yukabox only, using pinned iPXE headers/driver and UE's Clang."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import struct
import os

IPXE='6262f1081fe185564e8ec8365a1d23597ec6e6f5'
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
def main():
    p=argparse.ArgumentParser(); p.add_argument('--source',default='efi_probe.c')
    p.add_argument('--out',default='probe.efi'); a=p.parse_args()
    root=Path(__file__).resolve().parent; vendor=root/'vendor/ipxe'
    rev=subprocess.check_output(['git','-C',str(vendor),'rev-parse','HEAD'],text=True).strip()
    if rev!=IPXE: raise SystemExit('iPXE revision mismatch')
    subprocess.run(['python3',str(root/'patch_ipxe.py')],check=True)
    subprocess.run(['make','-j4','bin-x86_64-efi/10ec8168.efidrv'],cwd=vendor/'src',
                   env={**os.environ,'SOURCE_DATE_EPOCH':'0'},check=True,stdout=subprocess.DEVNULL)
    data=(vendor/'src/bin-x86_64-efi/10ec8168.efidrv').read_bytes()
    (root/'driver_bytes.h').write_text('static const unsigned char driver_bytes[]={'+','.join(str(x) for x in data)+'};\n')
    source=root/a.source; output=root/a.out
    sources=[source]
    if source.name=='efi_receiver.c':
        sources+=[root/x for x in ('frame_core.c','monocypher.c','monocypher-ed25519.c')]
    objects=[]
    for source in sources:
        obj=root/(source.stem+'.obj');objects.append(str(obj))
        subprocess.run([CC,'-target','x86_64-pc-win32-coff','-ffreestanding','-fshort-wchar',
                    '-fno-stack-protector','-mno-red-zone','-O2','-idirafter',str(vendor/'src/include'),
                    '-I'+str(vendor/'src/include/ipxe/efi/X64'),'-c',str(source),'-o',str(obj)],check=True)
    subprocess.run([str(Path(CC).with_name('lld')),'-flavor','link','/subsystem:efi_application',
                    '/entry:efi_main','/nodefaultlib','/timestamp:0','/out:'+str(output),*objects],check=True)
    binary=output.read_bytes(); pe=struct.unpack_from('<I',binary,60)[0]
    report={'efi_sha256':hashlib.sha256(binary).hexdigest(),
                      'ipxe_commit':rev,'driver_sha256':hashlib.sha256(data).hexdigest(),
                      'efi_file_bytes':len(binary),'efi_mapped_bytes':struct.unpack_from('<I',binary,pe+24+56)[0],
                      'source_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sources},
                      'installed_on_dell':False,'test_only':True}
    report['source_date_epoch']=0
    for name in ('efi_probe.c','frame_core.h','ipxe_rabbit_config.c','patch_ipxe.py','build_efi.py','fixture_public.h'):
        report['source_sha256'][name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
    output.with_suffix('.build.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__': main()
