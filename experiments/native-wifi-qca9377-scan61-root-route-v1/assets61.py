"""Reuse unchanged signing/QFS primitives with exact61 Root bindings and QWBT helper."""
import argparse,importlib.util
from pathlib import Path
import gate,host_gate
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_root_scan61_route',ROOT/'root_route.py')
route=importlib.util.module_from_spec(spec);spec.loader.exec_module(route)
observer=gate.base60.t.assets
import boot_asset_route as original
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','deliver'));p.add_argument('--state',type=Path,required=True);p.add_argument('--checked',type=Path,default=gate.CHECKED);p.add_argument('--diagnostic',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--session',type=Path);p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');a=p.parse_args();a.state=a.state.resolve()
 with gate.flow.state_lock(a.state):
  s=gate.flow.read_json(a.state);route.current(s,a.checked);host_gate.checked()
  old=(original.current,observer.current,observer.observer_gate,observer.OBSERVER)
  original.current=route.current;observer.current=route.current;observer.observer_gate=host_gate.checked;observer.OBSERVER=gate.REPO/'experiments/native-wifi-qca9377-scan61-staging-observer-v1'
  try:
   if a.action=='prepare':
    gate.need(a.diagnostic is not None and a.firmware is not None,'fresh61 setup and exact firmware required')
    return original.prepare(a,s)
   gate.need(a.session is not None,'exact saved61 session required');a.session=a.session.resolve()
   return observer.deliver(a,s)
  finally:original.current,observer.current,observer.observer_gate,observer.OBSERVER=old
if __name__=='__main__':raise SystemExit(main())
