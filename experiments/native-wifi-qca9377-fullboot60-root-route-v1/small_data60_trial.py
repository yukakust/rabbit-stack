"""One fresh-context saved60 DATA100 trial; no resign or reconnect loop."""
import sys,argparse
from pathlib import Path
import launch
import continue_assets60_after_checked_disconnect as context
import assets as legacy
flow=launch.flow;ROOT=launch.ROOT;SMALL=launch.prior.REPO/'experiments/native-wifi-qca9377-asset-observer-small-data-v1'
def gate():
 launch.t.need(launch.prior.sha(SMALL/'evidence/host-proof.json')=='8ee677d70d128280fbae23cedfc5bb70449a8afb9e8e1596925153bd9e7eed8c','frozen65 DATA100 proof')
 r=flow.read_json(SMALL/'evidence/host-proof.json');launch.t.need(r['host_callback_checks']==65 and r['data_payload_cap']==100 and r['pacing_ms']==50 and r['send_timeout_seconds']==240 and not r['physical_trial_performed'],'narrow host100 scope')
 for n,h in r['source_sha256'].items():launch.t.need(Path(n).name==n and launch.prior.sha(SMALL/n)==h,'small source changed')
 for n,h in r['original_source_sha256'].items():launch.t.need(launch.prior.sha(launch.prior.REPO/n)==h,'frozen original changed')
 old=(launch.prior.REPO/'experiments/native-wifi-qca9377-asset-observer-v1/sender.m').read_bytes();launch.t.need(old.count(b'if(count>240)count=240')==1 and old.replace(b'if(count>240)count=240',b'if(count>100)count=100')==(SMALL/'sender.m').read_bytes(),'one exact host DATAcap change')
 c=r['compile_report']
 for n,h in c['source_sha256'].items():launch.t.need(launch.prior.sha(launch.prior.REPO/n)==h,'compiled input changed')
 launch.t.need(launch.prior.sha(Path(c['executable_path']))==c['executable_sha256'] and launch.prior.sha(SMALL/'evidence/host.log')==r['host_log_sha256'],'actual host exe/log')
def main():
 p=argparse.ArgumentParser();p.add_argument('--observation',type=Path);p.add_argument('--check-only',action='store_true');a=p.parse_args();gate()
 if a.check_only:print('ROOT-EXACT-DATA100-FROZEN65-INPUT-EXE-DIFF-PASS');return 0
 launch.t.need(a.observation is not None,'explicit fresh knownpeer context required')
 with flow.state_lock(context.STATE):
  s=flow.read_json(context.STATE);launch.current(s,launch.CHECKED);session=context.check(a.observation,s)
  a.state=context.STATE;a.session=session
  old_path,old_gate,old_current=legacy.OBSERVER,legacy.observer_gate,legacy.current
  try:
   legacy.OBSERVER=SMALL;legacy.observer_gate=gate;legacy.current=launch.current
   return legacy.deliver(a,s)
  finally:legacy.OBSERVER,legacy.observer_gate,legacy.current=old_path,old_gate,old_current
if __name__=='__main__':raise SystemExit(main())
