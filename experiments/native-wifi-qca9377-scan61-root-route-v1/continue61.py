"""One sequential once-signed61 controller. A real disconnect stops without replay."""
from pathlib import Path
import sys,subprocess,os,json,importlib.util,time
import gate,host_gate
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_controller_root61',ROOT/'root_route.py');route=importlib.util.module_from_spec(spec);spec.loader.exec_module(route)
STATE=gate.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
def run(args):
 r=subprocess.run([sys.executable,*map(str,args)],cwd=gate.REPO);gate.need(r.returncode==0,'operation unconfirmed; preserve exact session, no replay')
def progress(report,session):
 steps=report['sender_steps'];gate.need(steps,'prior attempt missing');step=steps[-1]
 gate.need(step['mode']=='--send' and step['exit_code']==1,'not ordinary stopped sender')
 rows=[json.loads(x) for x in (session/f"prefix-{step['chunk']}-{len(steps)-1}.jsonl").read_text().splitlines()];last=rows[-1]
 gate.need(last['stage']=='bounded-timeout' and last['NSError_domain']=='RabbitAssetObserver' and last['NSError_code']==1,'non-timeout failure requires investigation')
 gate.need(not any(x['stage'] in ('disconnected','connection-failed','required-service-missing','required-characteristic-missing') for x in rows),'actual disconnect/service failure; stop')
 reads=[x for x in rows if x['stage']=='boot-read'];gate.need(reads and all(x['NSError_code']==0 and x['raw_bytes']==160 and bytes.fromhex(x['raw_hex'])[:8]==b'QWBT0001' and bytes.fromhex(x['raw_hex'])[128:]==bytes.fromhex('8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01') for x in reads),'exact QWBT diagnostic chain missing')
 gate.need(last['confirmed_floor']>reads[0]['confirmed_floor'],'no progress; stop')
 return step['chunk']*65760+last['confirmed_floor']
def main():
 expected=Path(sys.argv[1]).resolve();control=ROOT/'runs/control';control.mkdir(parents=True,exist_ok=True)
 with gate.flow.state_lock(STATE):
  s=gate.flow.read_json(STATE);gate.need(s.get('native_pending')==str(expected),'exact signed61 session required');host_gate.checked()
 run([ROOT/'root_route.py','deliver','--state',STATE])
 with gate.flow.state_lock(STATE):
  s=gate.flow.read_json(STATE);route.current(s,gate.CHECKED)
  helper=gate.base60.prior.ROOT/'runs/control/read-initial59';proof=gate.flow.read_json(gate.base60.ROOT/'host-tools.json');gate.need(gate.sha(helper)==proof['initial_reader_sha256'],'initial reader changed')
  env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(gate.flow.LOCK_FD)
  for attempt in range(8):
   result=subprocess.run([str(helper)],capture_output=True,text=True,env=env,timeout=70,pass_fds=(gate.flow.LOCK_FD,));(control/f'initial61-{attempt}.log').write_text(result.stdout+result.stderr)
   if result.returncode==0:
    gate.flow.save(control/'initial61.json',json.loads(result.stdout));break
   gate.need('probe still active; retry read-only after cleanup' in result.stderr,'initial read failed; preserve raw, no firmware signing')
   time.sleep(3)
  else:raise ValueError('initial61 cleanup not confirmed; no firmware signing')
 run([ROOT/'assets61.py','prepare','--state',STATE,'--diagnostic',control/'initial61.json','--firmware',gate.REPO/'experiments/native-wifi-qca9377-v1/runs/mac-control/firmware-6.bin'])
 s=gate.flow.read_json(STATE);session=Path(s['hardware_trial_pending']);previous=-1
 for attempt in range(24):
  with gate.flow.state_lock(STATE):
   s=gate.flow.read_json(STATE);gate.need(s.get('hardware_trial_pending')==str(session),'exact pending61 session changed');route.current(s,gate.CHECKED)
   report=gate.flow.read_json(session/'report.json')
   if report['completed_chunks']==12 and report.get('last_receipt',{}).get('ready')==1:break
   floor=progress(report,session) if report['sender_steps'] else 0;gate.need(floor>previous,'no forward progress; stop');previous=floor
  print('EXACT61 QUERY-BEFORE-RESUME',attempt+1,'confirmed aggregate',floor,flush=True)
  result=subprocess.run([sys.executable,str(ROOT/'assets61.py'),'deliver','--state',str(STATE),'--session',str(session)],cwd=gate.REPO)
  gate.need(result.returncode in (0,1),'route failed; preserve session')
 else:raise ValueError('bounded resume limit; preserve exact session')
 with gate.flow.state_lock(STATE):
  s=gate.flow.read_json(STATE);route.current(s,gate.CHECKED);gate.need(s.get('hardware_trial_pending')==str(session),'asset session changed')
  tools=host_gate.checked();env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(gate.flow.LOCK_FD)
  monitor=tools['native-wifi-qca9377-scan61-progress-monitor-v1']
  with (control/'progress61.log').open('x') as out:
   r=subprocess.run([monitor,'--monitor',str(control/'progress61.jsonl'),'--root-authorized-read'],stdout=out,stderr=subprocess.STDOUT,env=env,timeout=5580,pass_fds=(gate.flow.LOCK_FD,))
  gate.need(r.returncode==0,'boot/scan release not confirmed; stop, no raw reconnect')
  reader=tools['native-wifi-qca9377-scan61-observer-v1']
  with (control/'raw61.log').open('x') as out:
   r=subprocess.run([reader,'--root-authorized-read','--log',str(control/'raw61.jsonl')],stdout=out,stderr=subprocess.STDOUT,env=env,timeout=240,pass_fds=(gate.flow.LOCK_FD,))
  gate.need(r.returncode==0,'complete stable raw scan archive unconfirmed; preserve logs')
 print('Exact61 scan raw saved; Root must classify actual SSID; no association/IP claim',flush=True)
if __name__=='__main__':main()
