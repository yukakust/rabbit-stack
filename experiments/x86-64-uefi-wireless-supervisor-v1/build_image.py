#!/usr/bin/env python3
"""Build resident Scene driver + actual QCA receive adapter. No installation."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
NATIVE=ROOT.parent/'x86-64-uefi-runtime-supervisor-v1'
V3=ROOT.parent/'x86-64-uefi-god-runtime-v3'
V1=ROOT.parent/'x86-64-uefi-god-runtime-v1'
TEST_OWNER=bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7')

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def digest(data): return hashlib.sha256(data).digest()
def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def c_bytes(name,data): return f'static const uint8_t {name}[{len(data)}]={{'+','.join(map(str,data))+'};\n'
def replace(source,old,new):
    if source.count(old)!=1: raise ValueError('upstream reviewed source marker changed: '+old[:80])
    return source.replace(old,new,1)

def verifier_source():
    source=(NATIVE/'verify_core.c').read_text()
    source=replace(source,'Rabbit trusted runtime update v1','Rabbit trusted runtime update v2')
    source=replace(source,'"RRT1",4)||u16(p+4)!=1','"RRT2",4)||u16(p+4)!=2')
    source=replace(source,'u32(p+16)!=1||u32(p+20)!=1','u32(p+16)!=2||u32(p+20)!=2')
    return source

def assembly_source():
    source=load('wireless_old_builder',V3/'build_image.py').transformed_source()
    source=replace(source,'    mov [rsp + 0x488], rdx       # preserve SystemTable for the chained receiver',
        '    mov [rsp + 0x488], rdx       # preserve SystemTable for the chained receiver\n'
        '    call rabbit_supervisor_entry\n    mov rdx, [rsp + 0x488]')
    source=replace(source,'    cmp r9d, 2                         # transport version 2\n    jne scan_scan_event_loop',
        '    cmp r9d, 2\n    je supervisor_transport_ok\n    cmp r9d, 3\n    jne scan_scan_event_loop\nsupervisor_transport_ok:')
    start=source.index('scan_frame_begin:');end=source.index('    # LE Set Advertising Data',start)
    # Print nothing to the physical viewport between tick/presentation and ACK.
    source=source[:start]+'''scan_frame_begin:
scan_frame_chunk:
scan_frame_commit:
    lea rcx, [rsp + 0x430]
    mov rdx, [rsp + 0x6f0]
    call rabbit_package_frame
    cmp eax, 4
    jne scan_scan_event_loop
    lea rcx, [rsp + 0x480]
    call rabbit_receipt_write
'''+source[end:]
    source=replace(source,'scan_return:\n    xor eax, eax','scan_return:\n    call rabbit_scene_shutdown\n    xor eax, eax')
    source=replace(source,'scan_health_failed:\n','scan_health_failed:\n    call scan_radio_cleanup_best_effort\n')
    # Replace legacy caller-frame scratch string conversion with one bounded
    # supervisor-owned ConOut adapter; no graphics module or radio is invoked.
    for label,next_label in [('print_ascii','write_hex')]:
        start=source.index('\n'+label+':\n');end=source.index('\n'+next_label+':\n',start)
        source=source[:start]+f'''\n{label}:
    mov rcx, rdx
    sub rsp, 0x28
    call rabbit_supervisor_print_ascii
    add rsp, 0x28
    ret
'''+source[end:]
    source=source.replace('RABBIT GOD RUNTIME v3.0','RABBIT WIRELESS SUPERVISOR v1.0')
    return source

def compile_efi(directory,name,sources,*,driver=False,definitions=()):
    compiler=shutil.which('x86_64-w64-mingw32-gcc')
    if not compiler: raise RuntimeError('MinGW GCC required')
    output=directory/(name+'.efi')
    command=[compiler,'-std=c11','-Os','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
             '-fno-stack-protector','-mno-red-zone','-nostdlib','-I',str(ROOT),'-I',str(NATIVE),'-I',str(V3),'-I',str(directory)]
    # Do not apply driver GC to the mixed assembly bootstrap with inline firmware
    # and chained code. Its separately observed linker profile is retained.
    if driver:command+=['-ffunction-sections','-fno-asynchronous-unwind-tables','-fno-unwind-tables']
    command += ['-D'+v for v in definitions]+list(map(str,sources))
    if driver:command+=['-Wl,--gc-sections','-Wl,--strip-all']
    command += [f'-Wl,--subsystem,{11 if driver else 10}',f"-Wl,--entry,{'module_entry' if driver else 'rabbit_entry'}",
                '-Wl,--no-insert-timestamp','-Wl,--image-base,0','-Wl,--file-alignment,512','-Wl,--section-alignment,4096','-o',str(output)]
    completed=subprocess.run(command,capture_output=True,text=True)
    if completed.returncode: raise RuntimeError(completed.stderr)
    dump=subprocess.check_output(['x86_64-w64-mingw32-objdump','-p',str(output)],text=True)
    if 'DLL Name:' in dump: raise RuntimeError('OS import forbidden')
    return output.read_bytes()

def prepare(directory,owner):
    sys.path.insert(0,str(ROOT.parent/'runtime-update-contract-v1'))
    from update import Policy
    target=digest(canonical(json.loads((ROOT/'target.json').read_text())))
    Policy(target,owner,2,2) # Includes rejection of the public world development key.
    load('wireless_crypto_builder',V1/'build_image.py').fetch_crypto(directory)
    crypto=[directory/'monocypher.c',directory/'monocypher-ed25519.c']
    (directory/'native_verify.c').write_text(verifier_source())
    modules={revision:compile_efi(directory,f'scene-{revision}',[ROOT/'scene_module.c',*crypto],driver=True,
                                definitions=(f'SCENE_REVISION={revision}',)) for revision in (1,2,3)}
    (directory/'bootstrap.h').write_text(c_bytes('bootstrap_module',modules[1])+c_bytes('bootstrap_target',target)+c_bytes('bootstrap_owner',owner))
    return target,modules,crypto

def build(owner,*,test_key=False):
    if owner==TEST_OWNER and not test_key:raise ValueError('public QEMU fixture key must never provision a physical bootstrap')
    ROOT.joinpath('runs').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='wireless-',dir=ROOT/'runs') as temporary:
        directory=Path(temporary);target,modules,crypto=prepare(directory,owner)
        source=assembly_source();(directory/'receiver.S').write_text(source)
        efi=compile_efi(directory,'bootstrap',[directory/'receiver.S',ROOT/'supervisor.c',directory/'native_verify.c',
                           NATIVE/'transport_core.c',NATIVE/'sha256.c',*crypto])
        efi=load('wireless_firmware_builder',V1/'build_image.py').inject_firmware(efi)
    image=load('wireless_media_builder',ROOT.parent/'x86-64-uefi-v0/build_image.py').build_image(efi)
    report={'status':'BUILT-NOT-INSTALLED','test_key_only':test_key,'physical_execution_verified':False,
        'bluetooth_physical_verified':False,'persistent_writes':0,'target_sha256':target.hex(),
        'owner_public_sha256':digest(owner).hex(),'efi_sha256':digest(efi).hex(),'image_sha256':digest(image).hex(),
        'baseline_runtime_sha256':digest(modules[1]).hex(),'module_hashes':{str(k):digest(v).hex() for k,v in modules.items()},
        'module_sizes':{str(k):len(v) for k,v in modules.items()},
        'generated_assembly_sha256':digest(source.encode()).hex(),'generated_verifier_sha256':digest(verifier_source().encode()).hex(),
        'source_hashes':{str(p.relative_to(REPO)):digest(p.read_bytes()).hex() for p in
            [ROOT/'scene_abi.h',ROOT/'scene_module.c',ROOT/'supervisor.c',ROOT/'build_image.py',ROOT/'release.py',ROOT/'target.json',
             ROOT/'sign_runtime.py',ROOT/'send_runtime.py',ROOT/'save_world.py',V3/'send_package.py',V3/'transport.py',
             ROOT.parent/'runtime-update-contract-v1/owner_key.py',ROOT.parent/'runtime-update-contract-v1/update.py',ROOT.parent/'runtime-update-contract-v1/transport.py',
             ROOT.parent/'x86-64-uefi-ble-program-loader-v0/mac_vm_program.m',ROOT.parent/'x86-64-uefi-ble-program-loader-v0/RabbitColorCommand-Info.plist',
             V3/'runtime_core.c',NATIVE/'abi.h',NATIVE/'verify_core.c',NATIVE/'verify_core.h',NATIVE/'transport_core.c',NATIVE/'transport_core.h',NATIVE/'sha256.c',NATIVE/'sha256.h',
             V1/'build_image.py',V3/'build_image.py',ROOT.parent/'x86-64-uefi-ble-program-loader-v0/program.S']}}
    return image,report,modules

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner-public',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--module-output',type=Path,required=True)
    args=parser.parse_args();owner=args.owner_public.read_bytes()
    if len(owner)!=32: parser.error('owner public key must be exactly 32 raw bytes')
    image,report,modules=build(owner)
    with args.output.open('xb') as out:out.write(image)
    with args.module_output.open('xb') as out:out.write(modules[2])
    with args.output.with_suffix('.json').open('x') as out:json.dump(report,out,indent=2,sort_keys=True)
    print(json.dumps(report,indent=2,sort_keys=True));print('STOP: no physical media write. Exact local QEMU and owner bootstrap provisioning required.')
if __name__=='__main__': main()
