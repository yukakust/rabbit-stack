#!/usr/bin/env python3
"""Pure transport ordering; actual compilation on Yukabox, no physical I/O."""
import hashlib,json,subprocess
from pathlib import Path
from verify_htc import CC
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/control';out.mkdir(parents=True,exist_ok=True)
 names=('htc_control.c','htc_control.h','htc_control_test.c','verify_control.py','htc_credit.c','htc_credit.h','htc_session.c','htc_session.h','htc_wire.c','htc_wire.h','verify_htc.py')
 inputs={n:sha((ROOT/n).read_bytes()) for n in names}
 sources=[str(ROOT/n) for n in ('htc_control.c','htc_credit.c','htc_session.c','htc_wire.c','htc_control_test.c')]
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(ROOT),*sources,'-o',str(out/'control-test')],check=True)
 result=subprocess.run([str(out/'control-test')],capture_output=True,text=True,timeout=30)
 (out/'host.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-c',str(ROOT/'htc_control.c'),'-o',str(out/'htc_control.obj')],check=True)
 assert inputs=={n:sha((ROOT/n).read_bytes()) for n in inputs}
 report={'status':'HTC-CONTROL-ORDER-ASAN-COFF-PASS','build_host':'yukabox','source_sha256':inputs,'host_log_sha256':sha((out/'host.log').read_bytes()),'native_integrated':False,'physical_verified':False,'wifi_connected':False,'scope':'endpoint-zero handshake only; caller owns actual DMA, deadlines and quiesce; early WMI service events not handled'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.stdout.strip());print(report['status'])
if __name__=='__main__':main()
