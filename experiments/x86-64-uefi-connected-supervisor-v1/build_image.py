#!/usr/bin/env python3
"""Build a connected owner supervisor CANDIDATE. Never install or send."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'x86-64-uefi-wireless-supervisor-v1'
LINK=ROOT.parent/'ble-connected-file-transfer-v1'
NATIVE=ROOT.parent/'x86-64-uefi-runtime-supervisor-v1'
V3=ROOT.parent/'x86-64-uefi-god-runtime-v3'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
old=load('connected_old_builder',OLD/'build_image.py')
digest=old.digest
c_bytes=old.c_bytes
replace=old.replace

def verifier_source():
    s=old.verifier_source().replace('Rabbit trusted runtime update v2','Rabbit trusted runtime update v3')
    s=replace(s,'"RRT2",4)||u16(p+4)!=2','"RRT3",4)||u16(p+4)!=3')
    s=replace(s,'u32(p+16)!=2||u32(p+20)!=2','u32(p+16)!=3||u32(p+20)!=2')
    return replace(s,'u64(p+24)<=policy->counter','u64(p+24)<=policy->counter||u64(p+24)>0xffffffffu')

def supervisor_source():
    s=(OLD/'supervisor.c').read_text()
    s=replace(s,'#include "scene_abi.h"','#include "connected_abi.h"\nstatic RfFile file_session;')
    s=s.replace('SceneRegistration','ConnectedRegistration').replace('SCENE_MAGIC','CONNECTED_MAGIC')
    s=replace(s,'*r=(ConnectedRegistration){CONNECTED_MAGIC,2,sizeof(*r),2,0,0,0,0,0,0};',
              '*r=(ConnectedRegistration){.magic=CONNECTED_MAGIC,.abi=3,.size=sizeof(*r),.state_abi=2};')
    s=replace(s,'r->abi!=2','r->abi!=3')
    marker='!code_pointer((uintptr_t)r->counter,image,pe))'
    s=replace(s,marker,'!code_pointer((uintptr_t)r->counter,image,pe)||\n'+
       '||\n'.join(' !code_pointer((uintptr_t)r->'+v+',image,pe)' for v in ('attach','poll','close','command','world'))+')')
    start=s.index(' else{\n  void*previous=active_handle;')
    end=s.index('\n if(guard(0)){fault=1;return 3;}',start)
    s=s[:start]+''' else{
  /* ATT has returned before entering this function. No callback stack from
   * the old driver remains. Confirm radio close before any unload. */
  if(active.close()){fault=1;return 3;}
  if(candidate.attach(system,&file_session)){
   if(candidate.close()||((UnloadImage)service(system,224))(child)||active.attach(system,&file_session)){fault=1;return 3;}
   failed=1;
  }else{
   void*previous=active_handle;active_handle=child;active=candidate;
   copy(pixels,trial_pixels,sizeof(pixels));copy(policy.base,p+96,32);
   if(previous&&((UnloadImage)service(system,224))(previous)){fault=1;return 3;}
   present();
  }
 }
'''+s[end:]
    return s+'\n#include "loop.c"\n'

def assembly_source():
    s=old.assembly_source()
    s=replace(s,'scan_entry:\n','scan_entry:\n    jmp rabbit_connected_run\n')
    return s.replace('RABBIT WIRELESS SUPERVISOR v1.0','RABBIT CONNECTED SUPERVISOR v1.0')

def compile_efi(directory,name,sources,driver=False,definitions=()):
    # Reuse the reviewed freestanding linker profile, extend include paths only.
    return old.compile_efi(directory,name,sources,driver=driver,definitions=definitions)

def prepare(directory,owner):
    if len(owner)!=32:raise ValueError('32-byte raw public owner key required')
    sys.path.insert(0,str(ROOT.parent/'runtime-update-contract-v1'))
    from update import Policy
    target=digest(old.canonical(json.loads((ROOT/'target.json').read_text())))
    Policy(target,owner,3,2)
    old.load('connected_crypto',old.V1/'build_image.py').fetch_crypto(directory)
    # Exact absolute forwarding includes keep old immutable helpers untouched.
    for name in ('connected_abi.h','loop.c'):
        (directory/name).write_text(f'#include "{ROOT/name}"\n')
    for name in ('file_core.h','gatt_core.h','hci_link.h','usb_port.h'):
        (directory/name).write_text(f'#include "{LINK/name}"\n')
    crypto=[directory/'monocypher.c',directory/'monocypher-ed25519.c']
    (directory/'native_verify.c').write_text(verifier_source())
    modules={r:compile_efi(directory,f'driver-{r}',[ROOT/'driver.c',LINK/'usb_port.c',LINK/'hci_link.c',
        LINK/'gatt_core.c',LINK/'file_core.c',NATIVE/'sha256.c',*crypto],driver=True,
        definitions=(f'SCENE_REVISION={r}',)) for r in (1,2,3)}
    (directory/'bootstrap.h').write_text(c_bytes('bootstrap_module',modules[1])+c_bytes('bootstrap_target',target)+c_bytes('bootstrap_owner',owner))
    return target,modules,crypto

def build(owner,test_key=False):
    if owner==old.TEST_OWNER and not test_key:raise ValueError('public fixture key forbidden for physical image')
    ROOT.joinpath('runs').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='connected-',dir=ROOT/'runs') as temporary:
        d=Path(temporary);target,modules,crypto=prepare(d,owner)
        assembly=assembly_source();supervisor=supervisor_source()
        (d/'receiver.S').write_text(assembly);(d/'supervisor.c').write_text(supervisor)
        efi=compile_efi(d,'bootstrap',[d/'receiver.S',d/'supervisor.c',d/'native_verify.c',
             NATIVE/'transport_core.c',NATIVE/'sha256.c',LINK/'file_core.c',*crypto])
        efi=old.load('connected_firmware',old.V1/'build_image.py').inject_firmware(efi)
    image=old.load('connected_media',ROOT.parent/'x86-64-uefi-v0/build_image.py').build_image(efi)
    report={'status':'CANDIDATE-NOT-INSTALLED','test_key_only':test_key,'persistent_writes':0,
      'physical_verified':False,'mac_sender_compile_verified':False,'qemu_verified':False,
      'owner_public_sha256':digest(owner).hex(),'target_sha256':target.hex(),
      'efi_sha256':digest(efi).hex(),'image_sha256':digest(image).hex(),
      'module_hashes':{str(r):digest(v).hex() for r,v in modules.items()},
      'module_sizes':{str(r):len(v) for r,v in modules.items()},
      'assembly_sha256':digest(assembly.encode()).hex(),'supervisor_sha256':digest(supervisor.encode()).hex(),
      'verifier_sha256':digest(verifier_source().encode()).hex(),
      'source_hashes':{str(p.relative_to(ROOT.parents[1])):digest(p.read_bytes()).hex() for p in
       sorted([*ROOT.glob('*.c'),*ROOT.glob('*.h'),*ROOT.glob('*.py'),ROOT/'target.json',ROOT/'FileSender-Info.plist',
       *LINK.glob('*.c'),*LINK.glob('*.h'),LINK/'mac_file_sender.m',
       OLD/'supervisor.c',OLD/'scene_module.c',OLD/'scene_abi.h',OLD/'build_image.py',
       V3/'runtime_core.c',V3/'build_image.py',old.V1/'build_image.py',
       NATIVE/'abi.h',NATIVE/'verify_core.c',NATIVE/'verify_core.h',NATIVE/'sha256.c',NATIVE/'sha256.h',
       NATIVE/'transport_core.c',NATIVE/'transport_core.h',
       ROOT.parent/'runtime-update-contract-v1/update.py',ROOT.parent/'runtime-update-contract-v1/owner_key.py',
       ROOT.parent/'x86-64-uefi-ble-program-loader-v0/program.S'])}}
    return image,report,modules

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner-public',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--module-output',type=Path,required=True);a=p.parse_args()
    image,report,modules=build(a.owner_public.read_bytes())
    # Create-only artifacts, never overwrite a previous approved image.
    with a.output.open('xb') as f:f.write(image)
    with a.module_output.open('xb') as f:f.write(modules[2])
    with a.output.with_suffix('.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True)
    print(json.dumps(report,indent=2,sort_keys=True))
    print('STOP: candidate only; integrated QEMU/recovery and exact local gate required. NO MEDIA WRITE.')
if __name__=='__main__':main()
