"""Fresh62 receipt/release only; caller preserves sole sequential state lock."""
from pathlib import Path
import argparse,os,subprocess,time
import transition62 as transition
ROOT=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.state=a.state.resolve();a.output=a.output.resolve()
 route=transition.prior();g=route.gate
 with g.flow.state_lock(a.state):
  before=a.state.read_bytes();transition.verify(g.flow.read_json(a.state));tools=transition.observation_tools()
  reader=g.REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt';monitor=route.admission.monitor_gate.checked()
  a.output.mkdir(parents=True,exist_ok=False);env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(g.flow.LOCK_FD)
  for executable,args,log in ((reader,['receipt'],'receipt.log'),(monitor,['--monitor',str(a.output/'monitor.jsonl'),'--root-authorized-read'],'monitor.log')):
   with (a.output/log).open('x') as out:result=subprocess.run([str(executable),*args],stdout=out,stderr=subprocess.STDOUT,env=env,timeout=135,pass_fds=(g.flow.LOCK_FD,))
   transition.need(result.returncode==0,'fresh62 read failed; no state mutation/signing')
  transition.need(a.state.read_bytes()==before,'state changed during observation')
  g.flow.save(a.output/'report.json',{'status':'ACTUAL62-RELEASE14-PRE63-OBSERVATION','writes':0,'observed_at':time.time(),'state_sha256':g.flow.sha(before),**tools,'inputs':{n:transition.sha(a.output/n) for n in ('receipt.log','monitor.jsonl')}})
  transition.fresh(a.output,before);print('ACTUAL62-FRESH-APPLIED-RELEASE14-PASS')
if __name__=='__main__':main()
