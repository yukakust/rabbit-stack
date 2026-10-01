#!/usr/bin/env python3
"""Observe resident Scene hot swaps through the real dispatcher with test frames."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from build_image import ROOT,NATIVE,V3,prepare,compile_efi,c_bytes,digest,load,build
from release import pack
from send_runtime import runtime_transport,encode_segments
import sys

def fixture_build(owner,key):
    ROOT.joinpath('runs').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='qemu-build-',dir=ROOT/'runs') as temp:
        directory=Path(temp);target,modules,crypto=prepare(directory,owner)
        sys.path.insert(0,str(V3))
        compiler=load('wireless_qemu_world_compiler',V3/'compile_world.py')
        transport=load('wireless_qemu_world_transport',V3/'transport.py')
        world=compiler.compile_world(ROOT.parent/'x86-64-uefi-god-runtime-v2/worlds/cat-chases-mouse.json',1,
                                     Ed25519PrivateKey.from_private_bytes(bytes(range(32))))
        def update(revision,base,counter):return pack(modules[revision],private=key,target=target,base_runtime=digest(modules[base]),world=world,counter=counter)
        a=update(2,1,1);b=update(1,2,2);bad=update(3,1,3);tampered=bytearray(update(2,1,4));tampered[-1]^=1
        import uuid
        prefix=b''.join(uuid.UUID(value).bytes for value in encode_segments(a)['segments'][0])
        header=c_bytes('test_world',world)+c_bytes('module_a_hash',digest(modules[2]))+c_bytes('module_b_hash',digest(modules[1]))
        header+=c_bytes('frames_world',b''.join(transport.encode_transfer(world)))+c_bytes('frames_prefix',prefix)
        for name,data in [('a',a),('b',b),('bad',bad),('tampered',bytes(tampered))]:header+=c_bytes('frames_'+name,b''.join(runtime_transport.encode(data)))
        (directory/'test_frames.h').write_text(header)
        efi=compile_efi(directory,'test',[ROOT/'qemu_test.c',ROOT/'supervisor.c',directory/'native_verify.c',NATIVE/'sha256.c',NATIVE/'transport_core.c',*crypto],definitions=('RABBIT_INTEGRATION_TEST',))
    media=load('wireless_test_media',ROOT.parent/'x86-64-uefi-v0/build_image.py')
    return media.build_image(efi),{'test_efi_sha256':digest(efi).hex(),'fixture_frames_sha256':digest(header.encode()).hex(),'world_sha256':digest(world).hex(),
                                  'test_module_hashes':{str(k):digest(v).hex() for k,v in modules.items()}}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--archive',action='store_true')
    parser.add_argument('--ovmf-code',type=Path,default=Path('/usr/share/OVMF/OVMF_CODE_4M.fd'))
    parser.add_argument('--ovmf-vars',type=Path,default=Path('/usr/share/OVMF/OVMF_VARS_4M.fd'))
    args=parser.parse_args()
    observer=load('wireless_qmp_observer',NATIVE/'run_qemu.py')
    key=Ed25519PrivateKey.from_private_bytes(bytes(range(32,64)));owner=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    image,report=fixture_build(owner,key);again,repeated=fixture_build(owner,key)
    if image!=again or report!=repeated:raise RuntimeError('non-deterministic fixture artifact')
    candidate,bindings,_=build(owner,test_key=True);candidate2,bindings2,_=build(owner,test_key=True)
    if candidate!=candidate2 or bindings!=bindings2:raise RuntimeError('non-deterministic wireless bootstrap')
    output=Path(tempfile.mkdtemp(prefix='q-',dir=ROOT/'runs'));disk=output/'test.img';disk.write_bytes(image)
    code=args.ovmf_code;variables=args.ovmf_vars;shutil.copyfile(variables,output/'vars.fd')
    log=output/'debug.log';stderr=(output/'stderr.log').open('wb');qemu=shutil.which('qemu-system-x86_64')
    command=[qemu,'-machine','q35','-m','256M','-nic','none','-display','none','-qmp',f'unix:{output}/qmp.sock,server=on,wait=off',
             '-debugcon',f'file:{log}','-drive',f'if=pflash,format=raw,unit=0,readonly=on,file={code}',
             '-drive',f'if=pflash,format=raw,unit=1,file={output}/vars.fd','-drive',f'file={disk},format=raw,snapshot=on']
    process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=stderr);monitor=None
    try:
        monitor=observer.QMP(output/'qmp.sock',process)
        text=observer.wait_for(log,'WIRELESS DISPATCH AND SCENE NATIVE INTEGRATION PASS',process,timeout=45)
        screenshot=output/'committed.ppm';monitor.execute('screendump',{'filename':str(screenshot)})
        report.update({'status':'OBSERVED-QEMU-RESIDENT-SCENE-NATIVE-DISPATCH','candidate_bindings':bindings,
            'physical_verified':False,'bluetooth_verified':False,'test_radio':'embedded canonical frames, no QCA emulation',
            'test_image_sha256':digest(image).hex(),'observer_sha256':digest(Path(__file__).read_bytes()).hex(),
            'test_harness_sha256':digest((ROOT/'qemu_test.c').read_bytes()).hex(),'host_verifier_sha256':digest((ROOT/'verify.py').read_bytes()).hex(),
            'log_sha256':digest(log.read_bytes()).hex(),'screenshot_sha256':digest(screenshot.read_bytes()).hex(),
            'qemu_version':subprocess.check_output([qemu,'--version'],text=True).splitlines()[0],
            'ovmf_code_sha256':digest(code.read_bytes()).hex(),'ovmf_initial_vars_sha256':digest(variables.read_bytes()).hex()})
        (output/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        if args.archive:
            ROOT.joinpath('evidence').mkdir(exist_ok=True)
            (ROOT/'evidence/qemu-observed.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
            (ROOT/'evidence/qemu-observed.log').write_text(text)
        print(text);print('OBSERVED: '+str(output/'report.json'))
        # Keep the separately built real receiver for fail-closed inspection.
        (output/'wireless-bootstrap.img').write_bytes(candidate)
    finally:
        if monitor:
            try:monitor.execute('quit')
            except (OSError,RuntimeError):pass
            monitor.close()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:process.kill();process.wait()
        stderr.close()
if __name__=='__main__':main()
