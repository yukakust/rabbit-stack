#!/usr/bin/env python3
"""Compile/preflight only; no manager or actual reads are executed by this helper."""
import hashlib,json,subprocess,os,time
from pathlib import Path
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def compile_host(test=False):
 out=R/'runs/control';out.mkdir(parents=True,exist_ok=True);exe=out/('host-test' if test else 'collector')
 source=R/('host_test.m' if test else 'collector.m');plist=R.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist'
 inputs={str(p):sha(p) for p in (R/'collector.m',source,plist)};env=os.environ.copy()
 for n in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):env.pop(n,None)
 subprocess.run(['xcrun','--sdk','macosx','clang','-x','objective-c','-fobjc-arc','-Wall','-Wextra','-Werror',str(source),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],check=True,env=env,timeout=60)
 assert inputs=={n:sha(Path(n)) for n in inputs};return exe,inputs
if __name__=='__main__':
 exe,inputs=compile_host();subprocess.run([str(exe),'--preflight',str(R/'runs/control/preflight.jsonl')],check=True,timeout=10)
 test,testinputs=compile_host(True);out=R/'runs'/('proof-'+str(time.time_ns()));out.mkdir();p=subprocess.run([str(test),str(out)],check=True,text=True,capture_output=True,timeout=10);(out/'host.log').write_text(p.stdout+p.stderr)
 report={'status':'HOST-SCAN61-PROGRESS-QUIESCENCE-PREFLIGHT-PASS','executable':str(exe),'executable_sha256':sha(exe),'compiler_input_sha256':inputs,'test_executable_sha256':sha(test),'test_inputs':testinputs,'host_log_sha256':sha(out/'host.log'),'host_result':p.stdout.splitlines()[-1],'bluetooth_manager_started':False,'writes':0,'private_key_loads':0,'physical_readiness_proven':False,'source_sha256':{n:sha(R/n) for n in ('collector.m','host_test.m','compile_host.py')}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');e=R/'evidence';e.mkdir(exist_ok=True);(e/'host-proof.json').write_text(json.dumps(report,indent=2)+'\n');(e/'host.log').write_text(p.stdout+p.stderr);print(report['host_result']);print(out/'report.json')
