"""One sequential once-signed63 controller. A real disconnect stops without replay."""
from pathlib import Path
import sys,subprocess,os,json,importlib.util,time
import gate,host_gate,monitor_gate
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_controller_root63',ROOT/'root_route.py');route=importlib.util.module_from_spec(spec);spec.loader.exec_module(route)
STATE=gate.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
def run(args):
 r=subprocess.run([sys.executable,*map(str,args)],cwd=gate.REPO);gate.need(r.returncode==0,'operation unconfirmed; preserve exact session, no replay')
def progress(report,session):
 steps=report['sender_steps'];gate.need(steps,'prior attempt missing');step=steps[-1]
 gate.need(step['mode']=='--send' and step['exit_code']==1,'not ordinary stopped sender')
 rows=[json.loads(x) for x in (session/f"prefix-{step['chunk']}-{len(steps)-1}.jsonl").read_text().splitlines()];last=rows[-1]
 gate.need(last['stage']=='bounded-timeout' and last['NSError_domain']=='RabbitAssetObserver' and last['NSError_code']==1,'non-timeout failure requires investigation')
 gate.need(not any(x['stage'] in ('disconnected','connection-failed','required-service-missing','required-characteristic-missing') for x in rows),'actual disconnect/service failure; stop')
 reads=[x for x in rows if x['stage']=='boot-read'];gate.need(reads and all(x['peripheral'].upper()==gate.base60.prior.PEER and not x.get('cached_value_possible') and x['NSError_code']==0 and x['raw_bytes']==160 and bytes.fromhex(x['raw_hex'])[:8]==b'QWBT0001' and bytes.fromhex(x['raw_hex'])[128:]==bytes.fromhex('8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01') for x in reads),'exact QWBT diagnostic chain missing')
 gate.need(last['confirmed_floor']>reads[0]['confirmed_floor'],'no progress; stop')
 return step['chunk']*65760+last['confirmed_floor']
def native_progress(report,directory):
 gate.need(report['status']=='DELIVERY-NOT-CONFIRMED' and report['counter']==63 and report.get('confirmed_received',0)>0,'native continuation requires stopped progressing63')
 steps=report['sender_steps'];gate.need(len(steps)>=2 and steps[-1]['name']=='paced-stage' and steps[-1]['exit_code']==1,'not ordinary native stage timeout')
 stage=steps[-1];gate.need(gate.sha(stage['log'])==stage['log_sha256'] and Path(stage['log']).resolve().is_relative_to(directory.resolve()),'saved native stage log changed')
 text=Path(stage['log']).read_text();fails=[line for line in text.splitlines() if line.startswith('FAIL:')]
 gate.need(fails==['FAIL: 300-second bounded timeout; application outcome may be unknown; staging retained if Dell remains powered'] and not any(x in text for x in ('CBErrorDomain','RECEIVER STAGING REGRESSED:','disconnected','connection-failed')),'native transport fault; preserve session')
 query=steps[-2];gate.need(query['name']=='query' and query['exit_code']==0 and gate.sha(query['log'])==query['log_sha256'],'saved exact native query required')
 session=gate.flow.validate_session(gate.flow.read_json(directory/'session.json'));before=gate.flow.parse_status(Path(query['log']).read_text(),session)
 floor=gate.flow.confirmed_prefix(text,len((directory/'native.rrt').read_bytes())+32)
 gate.need(before['outcome']=='staging' and floor>before['received'],'native no forward progress; stop')
 return floor
def main():
 gate.need(len(sys.argv)==3 and sys.argv[1] in ('native','firmware'),'explicit native or firmware phase required');action=sys.argv[1];expected=Path(sys.argv[2]).resolve();controls=ROOT/'runs/control';controls.mkdir(parents=True,exist_ok=True);control=controls/('attempt-'+str(time.time_ns()));control.mkdir()
 with gate.flow.state_lock(STATE):
  for meta_path in controls.glob('controller63-*.json'):
   meta=gate.flow.read_json(meta_path)
   if meta['pid']==os.getpid():continue
   try:os.kill(meta['pid'],0)
   except ProcessLookupError:pass
   else:raise ValueError('another63 controller exists; stop')
  s=gate.flow.read_json(STATE);gate.need((action=='native' and s.get('native_pending')==str(expected)) or (action=='firmware' and not s.get('native_pending')),'exact phase/session required');host_gate.checked()
  gate.flow.save(controls/('controller63-'+str(os.getpid())+'.json'),{'pid':os.getpid(),'started_at':time.time(),'action':action,'exact_native_session':str(expected),'script_sha256':gate.sha(__file__),'attempt_directory':str(control),'new_native_signatures':0})
 if action=='native':
  previous=-1
  for attempt in range(8):
   with gate.flow.state_lock(STATE):
    s=gate.flow.read_json(STATE);gate.need(s.get('native_pending')==str(expected),'same native63 session required')
    r=gate.flow.read_json(expected/'report.json')
    if r['sender_steps']:
     floor=native_progress(r,expected);gate.need(floor>previous,'native stalled; preserve session');previous=floor
   result=subprocess.run([sys.executable,str(ROOT/'root_route.py'),'deliver','--state',str(STATE)],cwd=gate.REPO)
   if result.returncode==0:
    with gate.flow.state_lock(STATE):route.current(gate.flow.read_json(STATE),gate.CHECKED)
    return
   gate.need(result.returncode==1,'native route failed; stop')
  raise ValueError('native bounded resume limit; same session preserved')
 with gate.flow.state_lock(STATE):
  s=gate.flow.read_json(STATE);route.current(s,gate.CHECKED)
  gate.need(Path(s['engine']['last_release_report']).parent.resolve()==expected,'exact applied native63 session required')
 if not gate.flow.read_json(STATE).get('hardware_trial_pending'):
  with gate.flow.state_lock(STATE):
   s=gate.flow.read_json(STATE);route.current(s,gate.CHECKED)
   helper=gate.base60.prior.ROOT/'runs/control/read-initial59';proof=gate.flow.read_json(gate.base60.ROOT/'host-tools.json');gate.need(gate.sha(helper)==proof['initial_reader_sha256'],'initial reader changed')
   env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(gate.flow.LOCK_FD)
   for attempt in range(8):
    result=subprocess.run([str(helper)],capture_output=True,text=True,env=env,timeout=70,pass_fds=(gate.flow.LOCK_FD,));(control/f'initial63-{attempt}.log').write_text(result.stdout+result.stderr)
    if result.returncode==0:
     gate.flow.save(control/'initial63.json',json.loads(result.stdout));break
    gate.need('probe still active; retry read-only after cleanup' in result.stderr,'initial read failed; preserve raw, no firmware signing')
    time.sleep(3)
   else:raise ValueError('initial63 cleanup not confirmed; no firmware signing')
  run([ROOT/'assets63.py','prepare','--state',STATE,'--diagnostic',control/'initial63.json','--firmware',gate.REPO/'experiments/native-wifi-qca9377-v1/runs/mac-control/firmware-6.bin'])
 s=gate.flow.read_json(STATE);session=Path(s['hardware_trial_pending']);previous=-1
 for attempt in range(24):
  with gate.flow.state_lock(STATE):
   s=gate.flow.read_json(STATE);gate.need(s.get('hardware_trial_pending')==str(session),'exact pending63 session changed');route.current(s,gate.CHECKED)
   report=gate.flow.read_json(session/'report.json')
   if report['completed_chunks']==12 and report.get('last_receipt',{}).get('ready')==1:break
   floor=progress(report,session) if report['sender_steps'] else 0;gate.need(floor>previous,'no forward progress; stop');previous=floor
  print('EXACT63 QUERY-BEFORE-RESUME',attempt+1,'confirmed aggregate',floor,flush=True)
  result=subprocess.run([sys.executable,str(ROOT/'assets63.py'),'deliver','--state',str(STATE),'--session',str(session)],cwd=gate.REPO)
  gate.need(result.returncode in (0,1),'route failed; preserve session')
 else:raise ValueError('bounded resume limit; preserve exact session')
 with gate.flow.state_lock(STATE):
  s=gate.flow.read_json(STATE);route.current(s,gate.CHECKED);gate.need(s.get('hardware_trial_pending')==str(session),'asset session changed')
  tools=host_gate.checked();env=os.environ.copy();env['RABBIT_CONNECTED_LOCK_FD']=str(gate.flow.LOCK_FD)
  monitor=monitor_gate.checked()
  with (control/'progress63.log').open('x') as out:
   r=subprocess.run([monitor,'--monitor',str(control/'progress63.jsonl'),'--root-authorized-read'],stdout=out,stderr=subprocess.STDOUT,env=env,timeout=5580,pass_fds=(gate.flow.LOCK_FD,))
  gate.need(r.returncode==0,'boot/filter/HTT/scan release not confirmed; stop, no raw reconnect')
  reports=[json.loads(line) for line in (control/'progress63.log').read_text().splitlines() if line.startswith('{')]
  gate.need(len(reports)==1,'one terminal monitor report required');terminal=reports[0]
  gate.need(terminal['generation']==63 and terminal['peripheral'].upper()==gate.base60.prior.PEER and terminal['writes']==0 and terminal['raw_read_safe'] is True and terminal['terminal_result'] in ('RELEASED_PARTIAL_PIPELINE','RELEASED_DIAGNOSTIC_FAILURE'),'terminal63 release metadata differs')
  import classify_filter63
  gate.need(len(terminal['reports'])==2 and terminal['reports'][1]['format']=='QF630001','exact terminal boot/pipeline pair required')
  classify_filter63.decode.pipeline(bytes.fromhex(terminal['reports'][1]['raw_hex']))
  reader=tools['native-wifi-qca9377-filter63-observer-v2']
  with (control/'raw63.log').open('x') as out:
   r=subprocess.run([reader,'--root-authorized-read','--log',str(control/'raw63.jsonl')],stdout=out,stderr=subprocess.STDOUT,env=env,timeout=660,pass_fds=(gate.flow.LOCK_FD,))
  gate.need(r.returncode==0,'complete stable raw HTT archive unconfirmed; preserve logs')
 run([ROOT/'classify_filter63.py','--state',STATE,'--capture-log',control/'raw63.log','--raw-log',control/'raw63.jsonl','--output',control/'classification63.json'])
 print('Exact63 partial passive scan classification saved; no association/IP claim',flush=True)
if __name__=='__main__':main()
