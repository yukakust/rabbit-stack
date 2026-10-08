"""Prepared60s Mac Wi-Fi-off experiment; requires explicit human authorization."""
import sys,time,subprocess,argparse
from pathlib import Path
import launch,continue_assets60_after_checked_disconnect as ctx
NET='/usr/sbin/networksetup'
RESTORE="import time,subprocess;time.sleep(75);subprocess.run(['/usr/sbin/networksetup','-setairportpower','en0','on'],check=False)"
def quiet(command,output,run=subprocess.run,popen=subprocess.Popen,pause=time.sleep):
 power=run([NET,'-getairportpower','en0'],capture_output=True,text=True,check=True)
 launch.t.need(power.stdout.strip().endswith(': On'),'Mac Wi-Fi must initially be On')
 watchdog=popen([sys.executable,'-c',RESTORE],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  run([NET,'-setairportpower','en0','off'],check=True);pause(2)
  try:return run(command,stdout=output,stderr=subprocess.STDOUT,timeout=60,pass_fds=(launch.flow.LOCK_FD,))
  except subprocess.TimeoutExpired:
   output.write('CONTROLLED60s LIMIT: outcome unknown; preserve checkpoint, query before further delivery\n');return subprocess.CompletedProcess(command,1)
 finally:
  run([NET,'-setairportpower','en0','on'],check=True)
  power=run([NET,'-getairportpower','en0'],capture_output=True,text=True,check=True);launch.t.need(power.stdout.strip().endswith(': On'),'automatic restoration not confirmed; watchdog retained')
  watchdog.terminate();watchdog.wait(timeout=5)
def main():
 p=argparse.ArgumentParser();p.add_argument('--observation',type=Path,required=True);p.add_argument('--human-authorized-wifi-off',action='store_true');a=p.parse_args();launch.t.need(a.human_authorized_wifi_off,'human authorization missing; no network/BLE change')
 with launch.flow.state_lock(ctx.STATE):
  s=launch.flow.read_json(ctx.STATE);launch.current(s,launch.CHECKED);session=ctx.check(a.observation,s)
  import assets as original
  original.observer_gate();report=launch.flow.read_json(session/'report.json');packet=session/report['packets'][1]['file'];public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes()
  launch.t.need(original.validate(packet.read_bytes(),public)=={k:v for k,v in report['packets'][1].items() if k!='file'},'exact saved owner signature required')
  output=launch.ROOT/'runs/control/wifi-quiet60-sender.log';diag=launch.ROOT/'runs/control/wifi-quiet60-prefix.jsonl';launch.t.need(not output.exists() and not diag.exists(),'one trial only; preserve previous result')
  import os
  os.environ['RABBIT_ASSET_PEER']=launch.prior.PEER;os.environ['RABBIT_CONNECTED_LOCK_FD']=str(launch.flow.LOCK_FD)
  cmd=[str(original.OBSERVER/'runs/control/sender'),str(packet),str(packet.with_suffix(packet.suffix+'.checkpoint.json')),'--send','--prefix-log',str(diag)]
  with output.open('x') as f:r=quiet(cmd,f)
  print('TRIAL EXIT',r.returncode,'Wi-Fi restored; root must classify raw receipts before any resume');return r.returncode
if __name__=='__main__':raise SystemExit(main())
