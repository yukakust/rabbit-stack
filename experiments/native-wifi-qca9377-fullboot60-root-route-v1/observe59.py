"""Known-peer two serialized reads under sole state lock; never writes device."""
from pathlib import Path
import argparse,os,subprocess,time
import transition59 as t
ROOT=t.ROOT
READER=t.prior.REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt'
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 with t.flow.state_lock(a.state):
  s=t.flow.read_json(a.state);t.verify(s);before=a.state.read_bytes();a.output.mkdir(parents=True,exist_ok=False)
  proof=t.flow.read_json(t.prior.ROOT/'evidence/root-proof.json');name=str(READER.relative_to(t.prior.REPO));t.need(t.prior.sha(READER)==proof['source_sha256'][name],'frozen read helper changed')
  env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(t.flow.LOCK_FD)
  for name in ('receipt','prefix'):
   result=subprocess.run([str(READER),name],capture_output=True,text=True,timeout=70,env=env,pass_fds=(t.flow.LOCK_FD,));(a.output/(name+'.log')).write_text(result.stdout+result.stderr);t.need(result.returncode==0,'actual knownpeer read failed; no retirement/signing')
  t.need(a.state.read_bytes()==before,'state changed')
  t.flow.save(a.output/'report.json',{'status':'ACTUAL59-CHECKED-RELEASE-PRE60-OBSERVATION','writes':0,'observed_at':time.time(),'state_sha256':t.flow.sha(before),'inputs':{n:t.prior.sha(a.output/n) for n in ('receipt.log','prefix.log')}})
  fields=t.fresh(a.output,before);print('ACTUAL59-RELEASE14-AND-APPLIED-READ-PASS',fields['stop_offset'])
if __name__=='__main__':main()
