"""Sole-lock zero-write receipt/release observation before candidate64 admission."""
import argparse,os,subprocess,time,json
from pathlib import Path
import prior63 as prior
ROOT=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 route=prior.authority();g=route.gate
 with g.flow.state_lock(a.state):
  before=a.state.read_bytes();prior.verify(a.state)
  monitor=route.admission.monitor_gate.checked();reader=g.REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt'
  proof=g.flow.read_json(g.base60.prior.ROOT/'evidence/root-proof.json');expected=proof['source_sha256'][str(reader.relative_to(g.REPO))];prior.need(prior.sha(reader)==expected,'receipt executable changed')
  a.output.mkdir(parents=True,exist_ok=False);env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(g.flow.LOCK_FD)
  for exe,args,name in ((reader,['receipt'],'receipt.log'),(monitor,['--monitor',str(a.output/'monitor.jsonl'),'--root-authorized-read'],'monitor.log')):
   with (a.output/name).open('x') as log:result=subprocess.run([str(exe),*args],stdout=log,stderr=subprocess.STDOUT,env=env,timeout=135,pass_fds=(g.flow.LOCK_FD,))
   prior.need(result.returncode==0,'fresh63 read failed; preserve logs and current state')
  prior.need(a.state.read_bytes()==before,'state changed during actual observation')
  g.flow.save(a.output/'report.json',{'status':'ACTUAL63-RELEASE14-PRE64-OBSERVATION','observed_at':time.time(),'state_sha256':g.flow.sha(before),'observer_source_sha256':prior.sha(__file__),'receipt_reader_sha256':expected,'monitor_sha256':prior.sha(monitor),'writes':0,'inputs':{n:prior.sha(a.output/n) for n in ('receipt.log','monitor.jsonl')}})
  prior.fresh(a.output,before);print('ACTUAL63-FRESH-APPLIED-RELEASE14-PASS')
if __name__=='__main__':main()
