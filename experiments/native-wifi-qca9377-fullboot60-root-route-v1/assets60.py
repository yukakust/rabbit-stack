"""Exact60 asset admission uses unchanged sign/staging primitives and host observer."""
import argparse
from pathlib import Path
import launch
import assets as observer
import boot_asset_route as original
flow=launch.flow
ROOT=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','deliver'));p.add_argument('--state',type=Path,required=True);p.add_argument('--checked',type=Path,default=launch.CHECKED);p.add_argument('--diagnostic',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--session',type=Path);p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');a=p.parse_args()
 with flow.state_lock(a.state):
  s=flow.read_json(a.state);launch.current(s,a.checked)
  if a.action=='prepare':
   observer.observer_gate();old=original.current;original.current=launch.current
   try:return original.prepare(a,s)
   finally:original.current=old
  old=observer.current;observer.current=launch.current
  try:return observer.deliver(a,s)
  finally:observer.current=old
if __name__=='__main__':raise SystemExit(main())
