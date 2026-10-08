"""Same signed native62 continuation after a stopped progressing host timeout only."""
from pathlib import Path
import os,sys,time,json
ROOT=Path(__file__).resolve().parents[1]/'native-wifi-qca9377-htt62-root-route-v1'
sys.path.insert(0,str(ROOT))
import gate,host_gate,monitor_gate,admission
STATE=gate.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
def ordinary(report,directory):
 gate.need(report['status']=='DELIVERY-NOT-CONFIRMED' and report['counter']==62 and report.get('confirmed_received',0)>0,'not a progressing stopped native62')
 steps=report['sender_steps'];gate.need(steps and steps[-1]['name']=='paced-stage' and steps[-1]['exit_code']==1,'not native stage timeout')
 gate.need(gate.sha(steps[-1]['log'])==steps[-1]['log_sha256'],'stopped sender log changed')
 text=Path(steps[-1]['log']).read_text();fails=[line for line in text.splitlines() if line.startswith('FAIL:')]
 gate.need(fails==['FAIL: 300-second bounded timeout; application outcome may be unknown; staging retained if Dell remains powered'],'actual fault requires investigation')
 gate.need(not any(x in text for x in ('CBErrorDomain','RECEIVER STAGING REGRESSED:','disconnected','connection-failed')),'transport/receiver failure requires investigation')
 query=steps[-2];gate.need(query['name']=='query' and query['exit_code']==0 and gate.sha(query['log'])==query['log_sha256'],'exact pre-stage query required')
 session=gate.flow.validate_session(gate.flow.read_json(directory/'session.json'));before=gate.flow.parse_status(Path(query['log']).read_text(),session)
 floor=gate.flow.confirmed_prefix(text,173856);gate.need(before['outcome']=='staging' and floor>before['received'],'no confirmed forward staging in stopped attempt')
 gate.need(Path(steps[-1]['log']).resolve().is_relative_to(directory.resolve()),'log outside saved native session')
 return floor
def main():
 with gate.flow.state_lock(STATE):
  s=gate.flow.read_json(STATE);gate.need(s.get('native_pending'),'no signed native operation to resume');d=Path(s['native_pending']);r=gate.flow.read_json(d/'report.json')
  gate.need(r['package_sha256']=='874b02081c58525bc2fb2efaec0dd3f3b53d84b8a64f8955ab93dcd17fb27ca5' and gate.sha(d/'native.rrt')==r['package_sha256'] and r['payload_sha256']==gate.PAYLOAD,'same exact signed native62 required')
  control=ROOT/'runs/control'
  for file in control.glob('controller62*.json'):
   meta=gate.flow.read_json(file);pid=meta['pid']
   try:os.kill(pid,0)
   except ProcessLookupError:pass
   else:raise ValueError('previous controller still exists; never start a second controller')
  floor=ordinary(r,d);host_gate.checked();monitor_gate.checked();admission.checked();gate.gates(gate.CHECKED,(gate.CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes())
  gate.flow.save(control/f'controller62-resume-{os.getpid()}.json',{'pid':os.getpid(),'started_at':time.time(),'native_session':str(d),'native_packet_sha256':r['package_sha256'],'previous_confirmed_floor':floor,'script':str(ROOT/'continue62.py'),'script_sha256':gate.sha(ROOT/'continue62.py'),'new_native_signatures':0,'requires_query_before_write':True})
 os.execv(sys.executable,[sys.executable,str(ROOT/'continue62.py'),str(d)])
if __name__=='__main__':main()
