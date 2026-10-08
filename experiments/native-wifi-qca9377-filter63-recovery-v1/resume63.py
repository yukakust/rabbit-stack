"""Explicit fresh read-gated same-session resume after physical disconnect."""
from pathlib import Path
import sys,os,json,time,subprocess,hashlib
REPO=Path('/Users/yukakust/rabbit-stack');ROUTE=REPO/'experiments/native-wifi-qca9377-filter63-root-route-v1'
sys.path.insert(0,str(ROUTE))
import gate,host_gate,root_route,continue63
STATE=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
ROOT=Path(__file__).resolve().parent
PROOF=ROUTE/'runs/recovery-disconnect63-1'
def main():
 with gate.flow.state_lock(STATE):
  for pid in (8034,8689):
   try:os.kill(pid,0)
   except ProcessLookupError:pass
   else:raise ValueError('prior controller exists')
  state=gate.flow.read_json(STATE);root_route.current(state,gate.CHECKED);host_gate.checked()
  session=Path(state['hardware_trial_pending']);gate.need(session.name=='firmware-ram-d7zhmz9c','same saved asset session required')
  report=gate.flow.read_json(session/'report.json');gate.need(report['completed_chunks']==7 and report['native_counter']==63,'saved63 seven accepted parts required')
  pins=gate.flow.read_json(ROOT/'proof-pins.json')
  for name,h in pins['inputs'].items():gate.need(gate.sha(PROOF/name)==h,'fresh recovery evidence changed')
  receipts=[json.loads(line) for line in (PROOF/'query.log').read_text().splitlines() if line.startswith('{')];gate.need(len(receipts)==1,'one fresh actual receipt required');r=receipts[0]
  gate.need(r['action']==2 and r['state']==1 and r['error']==0 and r['bitmap']==127 and r['ready']==0 and r['confirmed_floor']==r['received']==52080 and r['length']==65760 and r['packet_sha256']==report['packets'][7]['packet_sha256'] and r['peripheral'].upper()==gate.base60.prior.PEER,'fresh exact stopped partial8 ownership')
  rows=[json.loads(line) for line in (PROOF/'query.jsonl').read_text().splitlines() if line.startswith('{')]
  gate.need(rows and 0<=time.time()-rows[-1]['timestamp_unix']<=300,'fresh recovery read required')
  for row in rows:gate.need(row['peripheral'].upper()==gate.base60.prior.PEER and row['NSError_code']==0 and not row['NSError_domain'] and not row.get('cached_value_possible'),'failed/cached recovery callback')
  native=Path(state['engine']['last_release_report']).parent
  gate.flow.save(ROOT/'live-controller.json',{'pid':os.getpid(),'native_session':str(native),'asset_session':str(session),'fresh_confirmed_floor':52080,'new_signatures':0,'source_sha256':gate.sha(__file__)})
 # Exact unchanged route queries again before any resume write; never prepares.
 result=subprocess.run([sys.executable,str(ROUTE/'assets63.py'),'deliver','--state',str(STATE),'--session',str(session)],cwd=REPO)
 gate.need(result.returncode in (0,1),'delivery failed; preserve session')
 with gate.flow.state_lock(STATE):
  state=gate.flow.read_json(STATE);root_route.current(state,gate.CHECKED);gate.need(state['hardware_trial_pending']==str(session),'session changed')
  report=gate.flow.read_json(session/'report.json')
  if report['completed_chunks']!=12:continue63.progress(report,session)
 os.execv(sys.executable,[sys.executable,str(ROUTE/'continue63.py'),'firmware',str(native)])
if __name__=='__main__':main()
