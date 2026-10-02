#!/usr/bin/env python3
"""Actual UEFI driver swaps with mock USB; not Bluetooth/physical evidence."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from build_image import ROOT,OLD,LINK,NATIVE,V3,old,load,build,prepare,compile_efi,supervisor_source,c_bytes,digest
from release import pack

def fixture_build(owner,key,loop_test=False,fault_test=False):
    ROOT.joinpath('runs').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='fixture-',dir=ROOT/'runs') as temp:
        d=Path(temp);target,modules,crypto=prepare(d,owner)
        hung=compile_efi(d,'hung',[ROOT/'driver.c',LINK/'usb_port.c',LINK/'hci_link.c',LINK/'gatt_core.c',
            LINK/'file_core.c',NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=4',))
        sys.path.insert(0,str(V3))
        compiler=load('connected_fixture_compiler',V3/'compile_world.py')
        world=compiler.compile_world(ROOT.parent/'x86-64-uefi-god-runtime-v2/worlds/cat-chases-mouse.json',1,
            Ed25519PrivateKey.from_private_bytes(bytes(range(32))))
        def release(payload,base,counter):return pack(payload,private=key,target=target,
            base_runtime=digest(base),world=world,counter=counter)
        a=release(modules[2],modules[1],1);b=release(modules[1],modules[2],2)
        bad=release(modules[3],modules[1],3)
        tampered=bytearray(release(modules[2],modules[1],4));tampered[-1]^=1
        releases={'world':world,'a':a,'b':b,'bad':bad,'tampered':bytes(tampered),'hung':release(hung,modules[1],4)}
        header=''.join(c_bytes(name+'_stream',digest(data)+data) for name,data in releases.items())
        header+=c_bytes('base_hash',digest(modules[1]))+c_bytes('a_hash',digest(modules[2]))
        (d/'test_data.h').write_text(header);(d/'supervisor.c').write_text(supervisor_source())
        definitions=('RABBIT_INTEGRATION_TEST',)+(('RABBIT_LOOP_TEST',) if loop_test else ())+(('RABBIT_FAULT_TEST',) if fault_test else ())
        efi=compile_efi(d,'fixture',[ROOT/'qemu_test.c',d/'supervisor.c',d/'native_verify.c',
            NATIVE/'transport_core.c',NATIVE/'sha256.c',LINK/'file_core.c',*crypto],definitions=definitions)
    image=old.load('connected_fixture_media',ROOT.parent/'x86-64-uefi-v0/build_image.py').build_image(efi)
    return image,{'efi_sha256':digest(efi).hex(),'image_sha256':digest(image).hex(),
        'fixture_sha256':digest(header.encode()).hex(),'world_sha256':digest(world).hex()}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',action='store_true')
    p.add_argument('--loop-test',action='store_true')
    p.add_argument('--fault-test',action='store_true',help='actual root-loop screen diagnostics and watchdog under mock USB failure')
    p.add_argument('--ovmf-code',type=Path)
    p.add_argument('--ovmf-vars',type=Path);a=p.parse_args()
    a.ovmf_code,a.ovmf_vars=firmware(a.ovmf_code,a.ovmf_vars)
    observer=load('connected_qmp',NATIVE/'run_qemu.py')
    key=Ed25519PrivateKey.from_private_bytes(bytes(range(32,64)))
    owner=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    if a.loop_test and a.fault_test:p.error('select only one root loop test')
    image,bindings=fixture_build(owner,key,a.loop_test,a.fault_test);image2,bindings2=fixture_build(owner,key,a.loop_test,a.fault_test)
    if image!=image2 or bindings!=bindings2:raise RuntimeError('fixture build nondeterministic')
    candidate,report,_=build(owner,True);candidate2,report2,_=build(owner,True)
    if candidate!=candidate2 or report!=report2:raise RuntimeError('bootstrap build nondeterministic')
    out=Path(tempfile.mkdtemp(prefix='q-',dir=ROOT/'runs'));disk=out/'test.img';disk.write_bytes(image)
    sockets=tempfile.TemporaryDirectory(prefix='rabbit-q-',dir='/tmp')
    shutil.copyfile(a.ovmf_vars,out/'vars.fd');log=out/'debug.log';err=(out/'stderr.log').open('wb')
    qemu=shutil.which('qemu-system-x86_64')
    cmd=[qemu,'-machine','q35','-m','256M','-nic','none','-display','none',
       '-qmp',f'unix:{sockets.name}/qmp.sock,server=on,wait=off','-debugcon',f'file:{log}',
       '-drive',f'if=pflash,format=raw,unit=0,readonly=on,file={a.ovmf_code}',
       '-drive',f'if=pflash,format=raw,unit=1,file={out}/vars.fd','-drive',f'file={disk},format=raw,snapshot=on',
       '-device','qemu-xhci,id=rabbit-xhci','-device','usb-kbd,bus=rabbit-xhci.0']
    process=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=err);monitor=None
    try:
        monitor=observer.QMP(Path(sockets.name)/'qmp.sock',process)
        if a.fault_test:
            observer.wait_for(log,'RADIO OUTCOME UNKNOWN; WATCHDOG RECOVERY',process)
            text=log.read_text()
            for marker in ('BLE POLL ERROR CODE=00000005','BLE LINK STATE=00000002',
                           'CONNECTED FAILURE: ','RADIO POLL; SEE BLE ERROR CODE',
                           'HCI RAW: 3E 13 01 00 40 00 01',
                           'HCI INPUT IGNORED: EVENT LENGTH MISMATCH',
                           'HCI LE META: SUBEVENT NOT HANDLED BY THIS DRIVER',
                           'USB EVENT MAX_PACKET=00000010',
                           'USB EVENT BINTERVAL RAW=00000001',
                           'USB EVENT TIMEOUT MS=00000014',
                           'HCI GENERAL MASK SUBMITTED: 10 E0 04 00 00 00 00 20',
                           'HCI LE MASK SUBMITTED: 1F 00 00 00 00 00 00 00'):
                if marker not in text:raise RuntimeError('missing real ConOut diagnostic: '+marker)
            monitor.execute('screendump',{'filename':str(out/'diagnostics.ppm')})
            text=observer.wait_for(log,'ACTUAL ROOT LOOP FAULT TEST',process,count=2)
            observed_log=log.read_bytes()  # One immutable snapshot while QEMU is still writing.
            result={'status':'OBSERVED-QEMU-ROOT-LOOP-USB-FAILURE-DIAGNOSTICS-WATCHDOG',
              'fixture':bindings,'candidate_bindings':report,'log_sha256':digest(observed_log).hex(),
              'observer_sha256':digest(Path(__file__).read_bytes()).hex(),
              'harness_sha256':digest((ROOT/'qemu_test.c').read_bytes()).hex(),
              'screenshot_sha256':digest((out/'diagnostics.ppm').read_bytes()).hex(),
              'physical_verified':False,'bluetooth_verified':False,
              'fault':'malformed/unsupported mock HCI events then bulk IN EFI_DEVICE_ERROR; actual driver ConOut forwarded to firmware',
              'ovmf_code_sha256':digest(a.ovmf_code.read_bytes()).hex(),
              'ovmf_initial_vars_sha256':digest(a.ovmf_vars.read_bytes()).hex()}
            (out/'report.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            if a.archive:
                (ROOT/'evidence').mkdir(exist_ok=True)
                (ROOT/'evidence/qemu-fault-observed.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
                (ROOT/'evidence/qemu-fault-observed.log').write_bytes(observed_log)
            print(text);print('SCREENSHOT: '+str(out/'diagnostics.ppm'));print('OBSERVED: '+str(out/'report.json'));return
        if a.loop_test:
            observer.wait_for(log,'ACTUAL ROOT LOOP STARTING',process)
            time.sleep(2);monitor.key('esc')
            text=observer.wait_for(log,'ACTUAL ROOT LOOP ESC CLEANUP PASS',process)
            observed_log=log.read_bytes()
            result={'status':'OBSERVED-QEMU-ROOT-LOOP-ESC-CLEANUP','fixture':bindings,
              'candidate_bindings':report,'log_sha256':digest(observed_log).hex(),
              'observer_sha256':digest(Path(__file__).read_bytes()).hex(),
              'harness_sha256':digest((ROOT/'qemu_test.c').read_bytes()).hex(),
              'physical_verified':False,'bluetooth_verified':False,
              'ovmf_code_sha256':digest(a.ovmf_code.read_bytes()).hex(),
              'ovmf_initial_vars_sha256':digest(a.ovmf_vars.read_bytes()).hex()}
            (out/'report.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            if a.archive:
                (ROOT/'evidence').mkdir(exist_ok=True)
                (ROOT/'evidence/qemu-loop-observed.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
                (ROOT/'evidence/qemu-loop-observed.log').write_bytes(observed_log)
            print(text);print('OBSERVED: '+str(out/'report.json'));return
        observer.wait_for(log,'CONNECTED BOOTSTRAP FALLBACK ACTIVE',process)
        monitor.key('t');text=observer.wait_for(log,'CONNECTED NATIVE INTEGRATION PASS',process,timeout=45)
        print(text,flush=True)
        monitor.execute('screendump',{'filename':str(out/'committed.ppm')})
        started=time.monotonic();monitor.key('h')
        observer.wait_for(log,'CONNECTED HUNG INIT ENTERED',process)
        text=observer.wait_for(log,'CONNECTED BOOTSTRAP FALLBACK ACTIVE',process,count=2)
        tail=text.split('CONNECTED HUNG INIT ENTERED',1)[1]
        if 'DRIVER A COMMITTED' in tail:raise RuntimeError('volatile driver was relaunched after watchdog')
        monitor.execute('screendump',{'filename':str(out/'fallback.ppm')})
        observed_log=log.read_bytes()
        observation={'schema_version':1,'status':'OBSERVED-QEMU-CONNECTED-DRIVER-SWAPS-WATCHDOG',
          'fixture':bindings,'candidate_bindings':report,'physical_verified':False,'bluetooth_verified':False,
          'controller':'mock USB descriptors/control/events; no QCA hardware emulation',
          'hung_init_to_fallback_seconds':round(time.monotonic()-started,3),
          'recovery_scope':'reviewed interrupts-enabled hang only; no native isolation guarantee',
          'observer_sha256':digest(Path(__file__).read_bytes()).hex(),
          'harness_sha256':digest((ROOT/'qemu_test.c').read_bytes()).hex(),
          'log_sha256':digest(observed_log).hex(),
          'qemu_version':subprocess.check_output([qemu,'--version'],text=True).splitlines()[0],
          'ovmf_code_sha256':digest(a.ovmf_code.read_bytes()).hex(),
          'ovmf_initial_vars_sha256':digest(a.ovmf_vars.read_bytes()).hex()}
        (out/'report.json').write_text(json.dumps(observation,indent=2,sort_keys=True)+'\n')
        if a.archive:
            (ROOT/'evidence').mkdir(exist_ok=True)
            (ROOT/'evidence/qemu-observed.json').write_text(json.dumps(observation,indent=2,sort_keys=True)+'\n')
            (ROOT/'evidence/qemu-observed.log').write_bytes(observed_log)
        print(text);print('OBSERVED: '+str(out/'report.json'))
    finally:
        if monitor:
            try:monitor.execute('quit')
            except (OSError,RuntimeError):pass
            monitor.close()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:process.kill();process.wait()
        err.close()
        sockets.cleanup()
def firmware(code=None,variables=None):
    qemu=shutil.which('qemu-system-x86_64')
    if not qemu:raise RuntimeError('QEMU required')
    roots=old.load('connected_firmware_roots',V3/'run_qemu.py').roots(Path(qemu))
    if code is None:code=next((r/n for r in roots for n in ('edk2-x86_64-code.fd','OVMF_CODE_4M.fd','OVMF_CODE.fd') if (r/n).is_file()),None)
    if variables is None:variables=next((r/n for r in roots for n in ('edk2-i386-vars.fd','OVMF_VARS_4M.fd','OVMF_VARS.fd') if (r/n).is_file()),None)
    if not code or not variables:raise RuntimeError('compatible explicit UEFI code/vars required')
    return code,variables
if __name__=='__main__':main()
