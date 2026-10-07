#!/usr/bin/env python3
"""Default compile/preflight only. ROOT alone may invoke --read --context PATH."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
from decode_prefix import loads,decode_capture,sha
from context import verify_context
from cryptography.exceptions import InvalidSignature
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
def save(p,value):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(mode='w',dir=p.parent,delete=False) as f:json.dump(value,f,indent=2);f.write('\n');name=f.name
 Path(name).replace(p)
def compile_reader():
 exe=ROOT/'runs/mac-control/read-prefix57';exe.parent.mkdir(parents=True,exist_ok=True)
 plist=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist'
 env=os.environ.copy()
 for n in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):env.pop(n,None)
 subprocess.run(['xcrun','--sdk','macosx','clang','-fobjc-arc','-Wall','-Wextra','-Werror',str(ROOT/'read_prefix.m'),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],check=True,timeout=60,env=env)
 return exe
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--read',action='store_true');ap.add_argument('--context',type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args()
 exe=compile_reader()
 if not a.read:return subprocess.run([str(exe),'--preflight'],check=True,timeout=10).returncode
 if a.context is None or a.output is None:ap.error('--read requires explicit --context and fresh --output directory')
 # Caller ROOT must hold existing operation lock externally. No lock/state mutation here.
 ctx=verify_context(a.context)
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
 save(out/'context-before.json',ctx);raw=out/'capture.json';decoded=out/'decoded.json'
 save(decoded,{'status':'NOT-CAPTURED','stable_capture':False,'state_cleared':False})
 with (out/'reader.log').open('wb') as log:
  try:r=subprocess.run([str(exe),'--read',str(raw)],stdout=log,stderr=subprocess.STDOUT,timeout=620);code=r.returncode
  except subprocess.TimeoutExpired:code=-1
 # Helper atomically persisted every received value; preserve partial on all failures.
 try:
  if code:raise ValueError('bounded reader failed: '+str(code))
  data=raw.read_bytes();c=loads(data)
  if any(k in c for k in ('fixture_kind','synthetic_only','mocked','test_clock','host_fixture')):raise ValueError('host fixture cannot supply actual capture')
  result=decode_capture(c)
  after=verify_context(a.context)
  if after!=ctx:raise ValueError('public context changed during capture')
  result.update(capture_origin='MAC-COREBLUETOOTH-READ',context_verified=True,context=after,capture_sha256=sha(data),reader_log_sha256=sha((out/'reader.log').read_bytes()),stable_capture=True,state_cleared=False)
  save(decoded,result);return 0
 except (ValueError,KeyError,TypeError,OSError,InvalidSignature) as e:
  save(decoded,{'status':'CAPTURE-OR-CONTEXT-REJECTED','error':str(e),'raw_sha256':sha(raw.read_bytes()) if raw.exists() else None,'stable_capture':False,'state_cleared':False});return 1
if __name__=='__main__':raise SystemExit(main())
