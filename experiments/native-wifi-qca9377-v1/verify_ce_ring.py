#!/usr/bin/env python3
"""Yukabox host/COFF gate; not a physical CE/DMA transfer."""
import hashlib,json,subprocess,os
from pathlib import Path
from verify_port import CC
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/ce-ring';out.mkdir(parents=True,exist_ok=True);exe=out/'test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(ROOT/'ce_ring.c'),str(ROOT/'ce_ring_test.c'),'-o',str(exe)],check=True)
 run=subprocess.run([str(exe)],capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
 (out/'host.log').write_text(run.stdout+run.stderr)
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-c',str(ROOT/'ce_ring.c'),'-o',str(out/'ce_ring.obj')],check=True)
 names=('ce_ring.c','ce_ring.h','ce_ring_test.c','verify_ce_ring.py')
 report={'status':'CE-RING-BOUNDS-LIFETIME-HOST-AND-COFF-PASS','source_sha256':{n:sha((ROOT/n).read_bytes()) for n in names},'host_log_sha256':sha((out/'host.log').read_bytes()),'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','reference':'ath10k ce.c/ce.h 32bit descriptor and qca6174_values metadata','build_host':'yukabox','dma_mapping_implemented':False,'ce_mmio_implemented':False,'physical_ce_transfer':False,'firmware_uploaded':False,'wifi_association':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
