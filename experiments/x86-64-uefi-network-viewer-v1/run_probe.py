#!/usr/bin/env python3
"""Yukabox-only, temporary UEFI VM; does not open a physical device."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import socket
import time
import hashlib

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--efi',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--receiver',action='store_true')
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    for name in ('serial.log','frame.ppm','report.json'):
        (a.output/name).unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix='rabbit-network-') as temp:
        d=Path(temp); boot=d/'esp/EFI/BOOT'; boot.mkdir(parents=True)
        shutil.copyfile(a.efi,boot/'BOOTX64.EFI')
        shutil.copyfile('/usr/share/OVMF/OVMF_VARS_4M.fd',d/'vars.fd')
        cmd=['qemu-system-x86_64','-machine','q35','-accel','tcg',
             '-m','256','-nodefaults','-no-reboot','-display','none',
             '-drive','if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd',
             '-drive',f'if=pflash,format=raw,file={d}/vars.fd',
             '-drive',f'format=raw,file=fat:rw:{d}/esp',
             '-device','virtio-vga','-netdev','user,id=net0',
             '-device','rtl8139,netdev=net0,romfile=',
             '-serial',f'file:{a.output}/serial.log','-monitor','none',
             '-qmp',f'unix:{d}/qmp,server=on,wait=off']
        proc=None
        try:
            proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            deadline=time.monotonic()+45; captured=False
            while proc.poll() is None and time.monotonic()<deadline:
                log=a.output/'serial.log'
                if not captured and log.exists() and 'RABBIT FRAME VISIBLE' in log.read_text(errors='replace'):
                    with socket.socket(socket.AF_UNIX) as sock:
                        sock.settimeout(3)
                        sock.connect(str(d/'qmp')); f=sock.makefile('rwb'); f.readline()
                        f.write(b'{"execute":"qmp_capabilities"}\n');f.flush()
                        while True:
                            reply=json.loads(f.readline())
                            if 'error' in reply:raise RuntimeError(reply)
                            if 'return' in reply:break
                        f.write((json.dumps({'execute':'screendump','arguments':{'filename':str(a.output/'frame.ppm')}})+'\n').encode());f.flush()
                        while True:
                            reply=json.loads(f.readline())
                            if 'error' in reply:raise RuntimeError(reply)
                            if 'return' in reply:break
                    captured=True
                time.sleep(.05)
            if proc.poll() is None:
                proc.kill();proc.communicate();raise subprocess.TimeoutExpired(cmd,45)
            _,stderr=proc.communicate()
            report={'exit_code':proc.returncode,'stderr':stderr.decode(errors='replace'),
                    'screenshot_captured':captured,
                    'physical_dell':False,'network':'QEMU slirp loopback only',
                    'nic':'RTL8139, not Dell RTL8168','firmware':'OVMF 4M',
                    'physical_devices_opened':False}
        except subprocess.TimeoutExpired:
            report={'error':'QEMU timeout','physical_dell':False}
        finally:
            if proc is not None and proc.poll() is None:
                proc.kill();proc.communicate()
        log=(a.output/'serial.log').read_text(errors='replace')
        if a.receiver:
            markers=['DRIVER START 0000000000000000','DHCP STATUS 0000000000000000',
                     'HTTP FIRST 0000000000000000','DECODE FIRST 0000000000000000',
                     'SEQUENCE FIRST 0000000000000001','GOP PRESENT 0000000000000000',
                     'BAD SIGNATURE PRESERVED','SEQUENCE SECOND 0000000000000002',
                     'OVERSIZE PRESERVED','ABORT PRESERVED','REPLAY AFTER ABORT PRESERVED',
                     'CONFIG CLOSE 0000000000000000',
                     'DRIVER UNLOAD 0000000000000000','SNP FINAL 0000000000000000']
            report['required_markers']={m:('RABBIT '+m in log) for m in markers}
            ppm=a.output/'frame.ppm'
            if ppm.exists():
                magic,dimensions,maximum,rgb=ppm.read_bytes().split(b'\n',3)
                w,h=map(int,dimensions.split());x=w-640
                if magic!=b'P6' or maximum!=b'255' or len(rgb)!=w*h*3 or x<=0 or h<360:
                    raise RuntimeError('invalid screenshot dimensions')
                right=b''.join(rgb[(y*w+x)*3:(y*w+x+640)*3] for y in range(360))
                left=b''.join(rgb[y*w*3:(y*w+x)*3] for y in range(h))
                report['viewer_rgb_sha256']=hashlib.sha256(right).hexdigest()
                report['left_fixture_preserved']=left==bytes([32,160,32])*x*h
                expected=json.loads((a.efi.parent/'frame-server-evidence/input.json').read_text())['rgb_sha256']
                report['actual_network_pixels_match_ue']=report['viewer_rgb_sha256']==expected
            report['passed']=report.get('exit_code')==0 and all(report['required_markers'].values()) and \
                report.get('actual_network_pixels_match_ue',False) and report.get('left_fixture_preserved',False)
        else:report['passed']=report.get('exit_code')==0
        (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print((a.output/'serial.log').read_text(errors='replace'))
        print(json.dumps(report))
        return int(not report['passed'])
if __name__=='__main__': raise SystemExit(main())
