#!/usr/bin/env python3
"""UEFI RAM lifetime/ABI gates on Yukabox; no physical chip or owner key."""
import hashlib,json,os,re,subprocess
from pathlib import Path
from verify_port import CC,NETWORK
ROOT=Path(__file__).resolve().parent
EXP=ROOT.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    fixtures=ROOT/'runs/firmware-chunks';base=json.loads((fixtures/'report.json').read_text())
    if base['status']!='SIGNED-RAM-CHUNKS-HOST-SANITIZERS-COFF-PASS':raise ValueError('RAM core gate required')
    for name,expected in base['source_sha256'].items():
        if sha((EXP.parent/name).read_bytes())!=expected:raise ValueError('RAM gate source changed')
    channel=ROOT/'runs/firmware-channel/report.json';binding=json.loads(channel.read_text())
    if binding['status']!='SIGNED-RAM-CHUNK-ATT-CHANNEL-HOST-COFF-PASS' or binding.get('handle_bases')!=[11,13]:raise ValueError('legacy and relocated channel gates required')
    for name,expected in binding['source_sha256'].items():
        if sha((EXP.parent/name).read_bytes())!=expected:raise ValueError('channel gate source changed')
    out=ROOT/'runs/firmware-port';out.mkdir(parents=True,exist_ok=True)
    inc=['-I'+str(p) for p in (ROOT,fixtures,EXP/'x86-64-uefi-runtime-supervisor-v1',EXP/'x86-64-uefi-wireless-supervisor-v1')]
    names=('firmware_port.c','firmware_port_test.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c')
    sources=[ROOT/n for n in names]+[EXP/'x86-64-uefi-runtime-supervisor-v1/sha256.c',fixtures/'monocypher.c',fixtures/'monocypher-ed25519.c']
    exe=out/'test';subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,*map(str,sources),'-o',str(exe)],check=True)
    log=''
    for scenario in range(11):
        result=subprocess.run([str(exe),str(scenario),str(fixtures/'reviewed-container')],capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
        log+=result.stdout+result.stderr
    setup_sources=[ROOT/'firmware_setup_test.c' if p.name=='firmware_port_test.c' else p for p in sources]
    setup_exe=out/'setup-test'
    subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,*map(str,setup_sources),'-o',str(setup_exe)],check=True)
    result=subprocess.run([str(setup_exe)],capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
    log+=result.stdout+result.stderr
    fresh_rejections=int(re.search(r'FRESH SETUP RAM GATE PASS rejected=(\d+)',result.stdout).group(1))
    assert fresh_rejections==143,'fresh gate fault coverage changed'
    subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*inc,'-c',str(ROOT/'firmware_port.c'),'-o',str(out/'firmware_port.obj')],check=True)
    layout=out/'layout.c';layout.write_text('#define FILE_LICENCE(x)\n#define FILE_SECBOOT(x)\n#include <stddef.h>\n#include <ipxe/efi/Uefi.h>\n_Static_assert(offsetof(EFI_BOOT_SERVICES,AllocatePool)==64,"AllocatePool");\n_Static_assert(offsetof(EFI_BOOT_SERVICES,FreePool)==72,"FreePool");\n_Static_assert(EfiBootServicesData==4,"pool memory type");\n_Static_assert(sizeof(EFI_SYSTEM_TABLE)==120,"system table");\n')
    subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-idirafter',str(NETWORK/'vendor/ipxe/src/include'),'-I'+str(NETWORK/'vendor/ipxe/src/include/ipxe/efi/X64'),'-c',str(layout),'-o',str(out/'layout.obj')],check=True)
    (out/'host.log').write_text(log)
    paths=[ROOT/n for n in (*names,'firmware_port.h','firmware_setup_test.c','verify_firmware_port.py','config_setup.h','config_read.h','full_read.h','init_adapter.h','bmi_transport.h','diag_ce.h','boot_irq.h','uefi_port.h')]+[EXP/'x86-64-uefi-runtime-supervisor-v1/abi.h',EXP/'x86-64-uefi-wireless-supervisor-v1/scene_abi.h']
    paths=sorted(set(paths)|set(ROOT.glob('*.h')))
    report={'status':'FIRMWARE-UEFI-RAM-PORT-HOST-COFF-ABI-PASS','build_host':'yukabox','source_sha256':{str(p.relative_to(EXP.parent)):sha(p.read_bytes()) for p in paths},'host_log_sha256':sha((out/'host.log').read_bytes()),'ram_gate_sha256':sha((fixtures/'report.json').read_bytes()),'channel_gate_sha256':sha(channel.read_bytes()),'scenarios':11,'fresh_setup_gate':True,'fresh_setup_rejections':fresh_rejections,'freed_dma_not_dereferenced':True,'physical_bmi_identity':False,'physical_allocation':False,'native_driver_integrated':False,'firmware_upload':False,'wifi_association':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status']);print(log,end='')
if __name__=='__main__':main()
