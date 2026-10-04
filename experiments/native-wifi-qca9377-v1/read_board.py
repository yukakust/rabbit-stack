#!/usr/bin/env python3
"""Compile-only by default; --read observes the known Dell without writes."""
import argparse,json,subprocess
from pathlib import Path
import diagnostic_build
from decode_board import decode
ROOT=Path(__file__).resolve().parent
flow=diagnostic_build.actors.engine.flow
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--read',action='store_true');p.add_argument('--output',type=Path);p.add_argument('--state',type=Path,default=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json');a=p.parse_args()
 out=ROOT/'runs/mac-control';out.mkdir(parents=True,exist_ok=True);exe=out/'board-reader';plist=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist'
 subprocess.run(['xcrun','--sdk','macosx','clang','-fobjc-arc','-Wall','-Wextra','-Werror',str(ROOT/'read_board.m'),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],check=True,timeout=60)
 subprocess.run([str(exe),'--preflight'],check=True)
 if not a.read:return 0
 if not a.output:p.error('--read requires --output for public raw observation')
 with flow.state_lock(a.state):
  state=flow.read_json(a.state);flow.current(state)
  if any(state.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('pending operation; preserve exact session')
  r=subprocess.run([str(exe),'--read'],capture_output=True,text=True,timeout=70)
  a.output.parent.mkdir(parents=True,exist_ok=True);a.output.with_suffix('.log').write_text(r.stderr)
  if r.returncode:raise RuntimeError(r.stderr)
  raw=json.loads(r.stdout)
  if raw['peripheral'].upper()!='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF' or raw['writes']!=0:raise ValueError('known-peer read-only observation required')
  flow.save(a.output,raw);decoded=decode(raw);flow.save(a.output.with_suffix('.decoded.json'),decoded);print(json.dumps(decoded,ensure_ascii=False))
if __name__=='__main__':raise SystemExit(main())
