#!/usr/bin/env python3
"""Exact owner-provisioned bootstrap gate: absent QCA must stop before effects.

Interactive by default. Headless mode saves a screenshot for visual confirmation;
it does not pretend to OCR or automatically certify the displayed status.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from build_image import ROOT,NATIVE,V3,build,load,TEST_OWNER,digest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    keys=parser.add_mutually_exclusive_group(required=True)
    keys.add_argument('--owner-public',type=Path);keys.add_argument('--test-key-only',action='store_true')
    parser.add_argument('--ovmf-code',type=Path);parser.add_argument('--ovmf-vars',type=Path)
    parser.add_argument('--headless',action='store_true');args=parser.parse_args()
    qemu=shutil.which('qemu-system-x86_64')
    if not qemu:raise RuntimeError('QEMU required')
    roots=load('wireless_firmware_roots',V3/'run_qemu.py').roots(Path(qemu))
    code=args.ovmf_code;variables=args.ovmf_vars
    if code is None:code=next((root/name for root in roots for name in ('edk2-x86_64-code.fd','OVMF_CODE_4M.fd','OVMF_CODE.fd') if (root/name).is_file()),None)
    if variables is None:variables=next((root/name for root in roots for name in ('edk2-i386-vars.fd','OVMF_VARS_4M.fd','OVMF_VARS.fd') if (root/name).is_file()),None)
    if code is None or variables is None:raise RuntimeError('compatible explicit UEFI code/vars required')
    owner=TEST_OWNER if args.test_key_only else args.owner_public.read_bytes()
    image,report,_=build(owner,test_key=args.test_key_only);other,other_report,_=build(owner,test_key=args.test_key_only)
    if image!=other or report!=other_report:raise RuntimeError('non-deterministic exact bootstrap')
    directory=Path(tempfile.mkdtemp(prefix='gate-',dir=ROOT/'runs'));disk=directory/'bootstrap.img';disk.write_bytes(image)
    shutil.copyfile(variables,directory/'vars.fd')
    command=[qemu,'-machine','q35','-m','256M','-nic','none','-no-reboot',
             '-drive',f'if=pflash,format=raw,unit=0,readonly=on,file={code}',
             '-drive',f'if=pflash,format=raw,unit=1,file={directory}/vars.fd','-drive',f'file={disk},format=raw,snapshot=on',
             '-device','qemu-xhci,id=rabbit-xhci','-device','usb-kbd,bus=rabbit-xhci.0']
    print('IMAGE SHA256: '+report['image_sha256'],flush=True)
    print('Expected: RABBIT WIRELESS SUPERVISOR v1.0; TARGET NOT FOUND; NO DEVICE WRITE SENT.',flush=True)
    if not args.headless:return subprocess.run(command).returncode
    command+=['-display','none','-qmp',f'unix:{directory}/qmp.sock,server=on,wait=off']
    stderr=(directory/'stderr.log').open('wb');process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=stderr);monitor=None
    try:
        observer=load('wireless_gate_observer',NATIVE/'run_qemu.py');monitor=observer.QMP(directory/'qmp.sock',process)
        # The USB keyboard/XHCI firmware path can still be entering the app at
        # 12s on this host. This is a capture delay, never an automatic PASS gate.
        time.sleep(25)
        screenshot=directory/'fail-closed.ppm';monitor.execute('screendump',{'filename':str(screenshot)})
        report.update({'status':'CAPTURED-EXACT-QEMU-BOOTSTRAP-REQUIRES-VISUAL-CONFIRMATION','screenshot_sha256':digest(screenshot.read_bytes()).hex(),
                       'ovmf_code_sha256':digest(code.read_bytes()).hex(),'ovmf_initial_vars_sha256':digest(variables.read_bytes()).hex(),
                       'observer_sha256':digest(Path(__file__).read_bytes()).hex()})
        (directory/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('SCREENSHOT: '+str(screenshot));print('REPORT: '+str(directory/'report.json'))
    finally:
        if monitor:
            try:monitor.execute('quit')
            except (OSError,RuntimeError):pass
            monitor.close()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:process.kill();process.wait()
        stderr.close()
    return 0
if __name__=='__main__':raise SystemExit(main())
