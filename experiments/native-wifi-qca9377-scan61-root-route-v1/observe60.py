"""Two serialized known-peer read-only helpers under the sole state lock."""
from pathlib import Path
import argparse,os,subprocess,time
import gate,transition60 as transition
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.state=a.state.resolve();a.output=a.output.resolve()
 with gate.flow.state_lock(a.state):
  s=gate.flow.read_json(a.state);transition.verify(s);gate.gates(gate.CHECKED,(gate.CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes());before=a.state.read_bytes()
  import collector_gate
  collector=collector_gate.checked()
  reader=gate.REPO/'experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/runs/physical57/read-gatt'
  proof=gate.flow.read_json(gate.base60.prior.ROOT/'evidence/root-proof.json')
  gate.need(gate.sha(reader)==proof['source_sha256'][str(reader.relative_to(gate.REPO))],'frozen receipt helper changed')
  a.output.mkdir(parents=True,exist_ok=False);env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(gate.flow.LOCK_FD)
  result=subprocess.run([str(reader),'receipt'],capture_output=True,text=True,timeout=70,env=env,pass_fds=(gate.flow.LOCK_FD,))
  (a.output/'receipt.log').write_text(result.stdout+result.stderr);gate.need(result.returncode==0,'actual receipt read failed; no signing')
  result=subprocess.run([str(collector),'--collect',str(a.output/'collector.jsonl'),'--root-authorized-read'],capture_output=True,text=True,timeout=70,env=env,pass_fds=(gate.flow.LOCK_FD,))
  (a.output/'collector.log').write_text(result.stdout+result.stderr);gate.need(result.returncode==0,'actual release read failed; no signing')
  gate.need(a.state.read_bytes()==before,'state changed during observations')
  gate.flow.save(a.output/'report.json',{'status':'ACTUAL60-RELEASE14-PRE61-OBSERVATION','writes':0,'observed_at':time.time(),'state_sha256':gate.flow.sha(before),'receipt_reader_sha256':gate.sha(reader),'collector_sha256':gate.sha(collector),'observer_source_sha256':gate.sha(Path(__file__)),'inputs':{n:gate.sha(a.output/n) for n in ('receipt.log','collector.jsonl')}})
  transition.fresh(a.output,before);print('ACTUAL60-FRESH-RELEASE14-APPLIED-PASS')
if __name__=='__main__':main()
