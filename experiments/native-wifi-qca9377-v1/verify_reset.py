#!/usr/bin/env python3
"""Yukabox-only host and COFF reset component gate; no physical reset."""
import hashlib,json,subprocess
from pathlib import Path
from verify_port import CC
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/reset-core';out.mkdir(parents=True,exist_ok=True)
 exe=out/'test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(ROOT/'reset_core.c'),str(ROOT/'reset_test.c'),'-o',str(exe)],check=True)
 run=subprocess.run([str(exe)],capture_output=True,text=True,check=True)
 (out/'host.log').write_text(run.stdout+run.stderr)
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-c',str(ROOT/'reset_core.c'),'-o',str(out/'reset_core.obj')],check=True)
 names=('reset_core.c','reset_core.h','reset_test.c','wake_core.h','reset-target.json','verify_reset.py')
 report={'status':'COOPERATIVE-COLD-RESET-HOST-AND-COFF-PASS','source_sha256':{n:sha((ROOT/n).read_bytes()) for n in names},'host_log_sha256':sha((out/'host.log').read_bytes()),'build_host':'yukabox','physical_reset':False,'native_profile_integrated':False,'dma':False,'firmware_uploaded':False,'wifi_association':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
