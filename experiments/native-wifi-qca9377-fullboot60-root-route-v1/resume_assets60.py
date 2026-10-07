"""Bounded same-session resumes ONLY after progressing ordinary host timeout."""
import sys,os,json,time,subprocess
from pathlib import Path
import launch as route
import assets60 as assets
route.REPO=route.prior.REPO
route.need=route.prior.need
route.sha=route.prior.sha
route.PEER=route.prior.PEER
STATE=route.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
def retry_progress(report,session):
 steps=report['sender_steps'];route.need(bool(steps),'no prior attempt')
 step=steps[-1];route.need(step['mode']=='--send' and step['exit_code']==1,'not ordinary stopped sender')
 p=session/f"prefix-{step['chunk']}-{len(steps)-1}.jsonl"
 rows=[json.loads(x) for x in p.read_text().splitlines()];v=rows[-1]
 route.need(v['stage']=='bounded-timeout' and v['NSError_domain']=='RabbitAssetObserver' and v['NSError_code']==1,'non-timeout requires investigation')
 route.need(not any(x['stage'] in ('disconnected','connection-failed','required-service-missing','required-characteristic-missing') for x in rows),'transport/service fault requires investigation')
 read=[x for x in rows if x['stage']=='prefix-read'];route.need(read and all(x['NSError_code']==0 and x['raw_bytes']==240 and bytes.fromhex(x['raw_hex'])[:12]==b'QPFX0001'+(60).to_bytes(4,'little') for x in read),'no valid60 diagnostic chain')
 route.need(v['confirmed_floor']>read[0]['confirmed_floor'],'no progress within attempt; stop')
 return step['chunk']*65760+v['confirmed_floor']
def main():
 session=Path(sys.argv[1]).resolve();control=route.ROOT/'runs/control';previous=-1
 for attempt in range(24):
  with route.flow.state_lock(STATE):
   s=route.flow.read_json(STATE);route.need(s.get('hardware_trial_pending')==str(session),'exact pending session changed');assets.current(s,route.CHECKED)
   report=route.flow.read_json(session/'report.json')
   if report['completed_chunks']==12 and report.get('last_receipt',{}).get('ready')==1:break
   progress=retry_progress(report,session) if report['sender_steps'] else 0;route.need(progress>previous,'no forward progress; stop');previous=progress
  print('EXACT60 QUERY-BEFORE-RESUME',attempt+1,'confirmed aggregate',progress,flush=True)
  result=subprocess.run([sys.executable,str(route.ROOT/'assets60.py'),'deliver','--state',str(STATE),'--session',str(session)],cwd=route.REPO)
  route.need(result.returncode in (0,1),'nonordinary route failure; stop')
 else:raise ValueError('bounded resume limit; preserve exact session')
 print('ALL12 accepted; one-connection fullboot observer starts, no reconnect polling',flush=True)
 with route.flow.state_lock(STATE):
  s=route.flow.read_json(STATE);route.need(s.get('hardware_trial_pending')==str(session) and s['engine']['native_counter']==60,'final context changed')
  import collector_gate
  executable=collector_gate.checked()
  env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(route.flow.LOCK_FD)
  with (control/'fullboot60-monitor.log').open('x') as out:
   result=subprocess.run([str(executable),'--monitor',str((control/'fullboot60-monitor.jsonl').resolve()),'--root-authorized-read'],stdout=out,stderr=subprocess.STDOUT,env=env,timeout=5520,pass_fds=(route.flow.LOCK_FD,))
  route.need(result.returncode==0,'fullboot raw monitor failed; preserve exact evidence; no reconnect')
 print('Physical60 complete raw saved; classification required; no scan/IP claim',flush=True)
if __name__=='__main__':main()
