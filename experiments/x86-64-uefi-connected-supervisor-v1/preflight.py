#!/usr/bin/env python3
"""Mac pre-install checks and exact owner QEMU gate. NEVER writes physical media."""
import argparse
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from build_image import ROOT,LINK,NATIVE,old,load,build,digest
from run_qemu import firmware

def main():
    p=argparse.ArgumentParser(description=__doc__)
    keys=p.add_mutually_exclusive_group(required=True)
    keys.add_argument('--owner-public',type=Path);keys.add_argument('--test-key-only',action='store_true')
    p.add_argument('--headless',action='store_true',help='capture only; does not open a physical gate')
    p.add_argument('--ovmf-code',type=Path);p.add_argument('--ovmf-vars',type=Path);a=p.parse_args()
    if a.test_key_only and not a.headless:p.error('public fixture capture must be headless/non-installable')
    # Tests use public fixtures; no owner private key is requested or accessed.
    for path in (ROOT/'verify.py',LINK/'verify_link.py',LINK/'verify_usb.py'):
        subprocess.run([sys.executable,str(path)],cwd=path.parent,check=True)
    for arguments in ([],['--loop-test']):
        if a.ovmf_code:arguments+=['--ovmf-code',str(a.ovmf_code)]
        if a.ovmf_vars:arguments+=['--ovmf-vars',str(a.ovmf_vars)]
        subprocess.run([sys.executable,str(ROOT/'run_qemu.py'),*arguments],cwd=ROOT,check=True)
    if not a.headless:
        if platform.system()!='Darwin':raise RuntimeError('installation gate requires real Mac compile and owner observation')
        subprocess.run([sys.executable,str(ROOT/'send_file.py')],cwd=ROOT,check=True)
    owner=old.TEST_OWNER if a.test_key_only else a.owner_public.read_bytes()
    image,report,modules=build(owner,a.test_key_only);other,again,_=build(owner,a.test_key_only)
    if image!=other or report!=again:raise RuntimeError('owner build not deterministic')
    out=Path(tempfile.mkdtemp(prefix='owner-gate-',dir=ROOT/'runs'))
    disk=out/'connected-supervisor.img';disk.write_bytes(image)
    (out/'driver-revision-2.efi').write_bytes(modules[2])
    code,variables=firmware(a.ovmf_code,a.ovmf_vars);shutil.copyfile(variables,out/'vars.fd')
    command=[shutil.which('qemu-system-x86_64'),'-machine','q35','-m','256M','-nic','none','-no-reboot',
        '-drive',f'if=pflash,format=raw,unit=0,readonly=on,file={code}',
        '-drive',f'if=pflash,format=raw,unit=1,file={out}/vars.fd','-drive',f'file={disk},format=raw,snapshot=on',
        '-device','qemu-xhci,id=rabbit-xhci','-device','usb-kbd,bus=rabbit-xhci.0']
    report.update({'ovmf_code_sha256':digest(code.read_bytes()).hex(),
        'ovmf_initial_vars_sha256':digest(variables.read_bytes()).hex()})
    print('IMAGE: '+str(disk),flush=True);print('IMAGE SHA256: '+report['image_sha256'],flush=True)
    print('Expected: RABBIT CONNECTED SUPERVISOR v1.0; TARGET NOT FOUND; NO DEVICE WRITE SENT.',flush=True)
    if a.headless:
        import time
        sockets=tempfile.TemporaryDirectory(prefix='rabbit-gate-',dir='/tmp')
        command+=['-display','none','-qmp',f'unix:{sockets.name}/qmp.sock,server=on,wait=off']
        err=(out/'stderr.log').open('wb');process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=err);monitor=None
        try:
            monitor=load('connected_owner_qmp',NATIVE/'run_qemu.py').QMP(Path(sockets.name)/'qmp.sock',process)
            time.sleep(25);screenshot=out/'fail-closed.ppm'
            monitor.execute('screendump',{'filename':str(screenshot)})
            report.update({'status':'CAPTURED-EXACT-QEMU-REQUIRES-VISUAL-CONFIRMATION','screenshot_sha256':digest(screenshot.read_bytes()).hex()})
            print('SCREENSHOT: '+str(screenshot))
        finally:
            if monitor:
                try:monitor.execute('quit')
                except (OSError,RuntimeError):pass
                monitor.close()
            try:process.wait(timeout=3)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            err.close()
            sockets.cleanup()
    else:
        print('Close QEMU after checking all expected lines. Do not reboot the physical Dell.',flush=True)
        if subprocess.run(command).returncode:raise RuntimeError('QEMU failed; gate remains closed')
        if input('Did QEMU show every expected line? Type YES: ').strip()!='YES':raise RuntimeError('no observation; gate remains closed')
        report.update({'status':'OWNER-OBSERVED-EXACT-MAC-QEMU-NO-DEVICE','qemu_verified':True,
            'mac_sender_compile_verified':True,'observation':'owner reported; not automatic OCR or physical Bluetooth'})
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('REPORT: '+str(out/'report.json'))
    if not a.headless:subprocess.run(['diskutil','list','external','physical'],check=True)
    print('STOP: no physical media unmounted, erased or written. Fresh exact USB identity required separately.')
if __name__=='__main__':main()
