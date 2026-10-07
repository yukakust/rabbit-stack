"""One sequential once-signed60 controller; no reset/reboot/re-sign or parallel BLE."""
from pathlib import Path
import sys,subprocess,os,json,time
import launch
import collector_gate
ROOT=launch.ROOT;REPO=launch.prior.REPO;flow=launch.flow
STATE=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
def main():
 expected=Path(sys.argv[1]).resolve();control=ROOT/'runs/control';control.mkdir(parents=True,exist_ok=True)
 s=flow.read_json(STATE);launch.t.need(s.get('native_pending')==str(expected),'exact signed60 session required')
 r=subprocess.run([sys.executable,str(ROOT/'launch.py'),'deliver','--state',str(STATE)],cwd=REPO)
 launch.t.need(r.returncode==0,'native60 delivery not confirmed; preserve saved signature')
 s=flow.read_json(STATE);launch.current(s,launch.CHECKED)
 helper=launch.prior.ROOT/'runs/control/read-initial59'
 proof=flow.read_json(ROOT/'host-tools.json');launch.t.need(launch.prior.sha(helper)==proof['initial_reader_sha256'],'initial reader changed')
 for attempt in range(8):
  with flow.state_lock(STATE):
   env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(flow.LOCK_FD)
   result=subprocess.run([str(helper)],capture_output=True,text=True,env=env,timeout=70,pass_fds=(flow.LOCK_FD,));(control/f'initial60-{attempt}.log').write_text(result.stdout+result.stderr)
   if result.returncode==0:
    flow.save(control/'initial60.json',json.loads(result.stdout));break
  launch.t.need('probe still active; retry read-only after cleanup' in result.stderr,'initial60 read failed; preserve raw callback')
  time.sleep(3)
 else:raise ValueError('initial60 cleanup not confirmed')
 collector_gate.checked()
 subprocess.run([sys.executable,str(ROOT/'assets60.py'),'prepare','--state',str(STATE),'--diagnostic',str(control/'initial60.json'),'--firmware',str(REPO/'experiments/native-wifi-qca9377-v1/runs/mac-control/firmware-6.bin')],cwd=REPO,check=True)
 s=flow.read_json(STATE);session=Path(s['hardware_trial_pending'])
 result=subprocess.run([sys.executable,str(ROOT/'resume_assets60.py'),str(session)],cwd=REPO)
 launch.t.need(result.returncode==0,'exact60 radio result unconfirmed; keep packets/floors/diagnostics')
 print('Exact60 monitor finished; root classification before scan/signing',flush=True)
if __name__=='__main__':main()
