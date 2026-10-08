"""Finish exact staged61 through corrected host readers, only after old controller exits."""
from pathlib import Path
import argparse,os,sys,subprocess,time
import gate,assets61,host_gate,monitor_gate_v2
ROOT=Path(__file__).resolve().parent
def validate_completed_assets(d,r,policy,public,g):
 gate.need(r['status']=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and r['completed_chunks']==12 and r['policy']==policy and r['gate']==g and r['native_counter']==61 and r['native_payload_sha256']==gate.PAYLOAD and len(r['packets'])==12 and r['last_receipt']['action']==4 and r['last_receipt']['bitmap']==4095 and r['last_receipt']['ready']==1 and r['last_receipt']['peripheral'].upper()==gate.base60.prior.PEER,'actual completed exact61 asset session required')
 body=bytearray()
 for item in r['packets']:
  packet=(d/gate.safe(item['file'])).read_bytes();v=assets61.observer.validate(packet,public)
  gate.need(v=={k:x for k,x in item.items() if k!='file'} and v['generation']==61 and v['offset']==len(body),'immutable exact firmware signature/ordering changed')
  body.extend(packet[224:])
 gate.need(len(body)==policy['total'] and gate.flow.sha(body)==policy['digest'],'exact full firmware container required before monitor')
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.state=a.state.resolve();a.output=a.output.resolve()
 with gate.flow.state_lock(a.state):
  for path in (ROOT/'runs/control').glob('controller61*.json'):
   meta=gate.flow.read_json(path)
   try:os.kill(meta['pid'],0)
   except ProcessLookupError:pass
   else:raise ValueError('previous controller still exists; no second BLE path')
  s=gate.flow.read_json(a.state);policy,public,g=assets61.route.current(s,gate.CHECKED);d=Path(s['hardware_trial_pending']);r=gate.flow.read_json(d/'report.json')
  validate_completed_assets(d,r,policy,public,g)
  tools=host_gate.checked();monitor=monitor_gate_v2.checked();before=a.state.read_bytes();a.output.mkdir(parents=True,exist_ok=False)
  gate.flow.save(a.output/'controller.json',{'pid':os.getpid(),'started_at':time.time(),'writes':0,'new_signatures':0,'native_counter':61,'asset_session':str(d),'state_sha256':gate.flow.sha(before),'corrected_monitor':monitor,'monitor_sha256':gate.sha(monitor)})
  env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(gate.flow.LOCK_FD)
  with (a.output/'progress.log').open('x') as out:r=subprocess.run([monitor,'--monitor',str(a.output/'progress.jsonl'),'--root-authorized-read'],stdout=out,stderr=subprocess.STDOUT,env=env,timeout=5580,pass_fds=(gate.flow.LOCK_FD,))
  gate.need(r.returncode==0,'fresh61 quiescence unconfirmed; preserve raw, no next read')
  reader=tools['native-wifi-qca9377-scan61-observer-v1']
  with (a.output/'raw.log').open('x') as out:r=subprocess.run([reader,'--root-authorized-read','--log',str(a.output/'raw.jsonl')],stdout=out,stderr=subprocess.STDOUT,env=env,timeout=660,pass_fds=(gate.flow.LOCK_FD,))
  gate.need(r.returncode==0 and a.state.read_bytes()==before,'complete capture/state unconfirmed; no SSID claim')
 # Classification is read-only and itself rechecks source/signature/state/raw joins.
 result=subprocess.run([sys.executable,str(ROOT/'classify_scan61.py'),'--state',str(a.state),'--capture-log',str(a.output/'raw.log'),'--raw-log',str(a.output/'raw.jsonl'),'--output',str(a.output/'classification.json')],cwd=gate.REPO)
 gate.need(result.returncode==0,'physical capture classification failed; preserve evidence')
if __name__=='__main__':main()
