"""Fresh known-peer receipt and scan61 release; sequential reads, no signing."""
from pathlib import Path
import argparse, os, subprocess, time
import gate, transition61 as transition

def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.state=a.state.resolve();a.output=a.output.resolve()
 with gate.flow.state_lock(a.state):
  s=gate.flow.read_json(a.state);transition.verify(s)
  gate.gates(gate.CHECKED,(gate.CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes())
  tools=transition.observation_tools();before=a.state.read_bytes()
  reader=gate.REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt'
  inventory=gate.REPO/'experiments/native-wifi-qca9377-scan61-inventory-v3/runs/inventory'
  a.output.mkdir(parents=True,exist_ok=False);env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(gate.flow.LOCK_FD)
  for executable,args,name,bound in ((reader,['receipt'],'receipt.log',70),(inventory,['--root-authorized-read'],'inventory.jsonl',135)):
   with (a.output/name).open('x') as out:
    r=subprocess.run([str(executable),*args],stdout=out,stderr=subprocess.STDOUT,env=env,timeout=bound,pass_fds=(gate.flow.LOCK_FD,))
   gate.need(r.returncode==0,'fresh61 read failed; no signing')
  gate.need(a.state.read_bytes()==before,'state changed during observation')
  gate.flow.save(a.output/'report.json',{'status':'ACTUAL61-RELEASE14-PRE62-OBSERVATION','writes':0,'observed_at':time.time(),'state_sha256':gate.flow.sha(before),**tools,'inputs':{n:gate.sha(a.output/n) for n in ('receipt.log','inventory.jsonl')}})
  transition.fresh(a.output,before);print('ACTUAL61-FRESH-RELEASE14-APPLIED-PASS')
if __name__=='__main__':main()
