"""Single bounded controller; signs once, resumes the same exact saved session."""
import json,os,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parent
STATE=R.parent/'x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
def run(action,log):
 with log.open('x') as out:
  # Common sender has at most six individually bounded380s operations. Do not
  # interrupt its parent before those operations can persist/close normally.
  return subprocess.run([sys.executable,'-u',str(R/'route65.py'),action],stdout=out,stderr=subprocess.STDOUT,timeout=2700).returncode
def main():
 control=R/'runs/control';control.mkdir(parents=True,exist_ok=True)
 # O_EXCL makes a second controller require deliberate saved-state inspection.
 with (control/'controller65.json').open('x') as f:
  json.dump({'pid':os.getpid(),'started':time.time(),'source':'continue65.py','same_session_only':True},f);f.flush();os.fsync(f.fileno())
 if run('prepare',control/'prepare.log'):
  print('PREPARE FAILED; exact evidence retained; no blind signing retry',flush=True);return 1
 session=json.loads(STATE.read_text())['native_pending'];print('EXACT65 SESSION '+session,flush=True)
 # Budget checked between operations; an in-flight bounded operation may finish
 # beyond it. This is not advertised as a hard one-hour wall-clock limit.
 deadline=time.monotonic()+3600;floor=-1;stalls=0
 for attempt in range(8):
  if time.monotonic()>=deadline:break
  s=json.loads(STATE.read_text())
  if s.get('native_pending')!=session:
   if s['engine']['native_counter']==65 and s['engine']['payload_sha256']=='84b28939af3774620ec57e19e3fd09fc4315edaeb69e572f7fa982c648284d20':break
   raise ValueError('saved session changed; stop')
  code=run('deliver',control/('deliver-'+str(attempt)+'.log'))
  s=json.loads(STATE.read_text());r=json.loads((Path(session)/'report.json').read_text())
  print('ATTEMPT',attempt,'status',r['status'],'confirmed',r.get('confirmed_received',0),flush=True)
  if code==0:break
  if code==2 or r.get('receiver_loss_detected') or r['status'] in ('EXACT-REJECTED-RECEIPT','INVALID-RECEIVER-STATUS'):return 1
  new=r.get('confirmed_received',0);stalls=stalls+1 if new<=floor else 0;floor=new
  if stalls>=2:return 1
  time.sleep(20)
 s=json.loads(STATE.read_text())
 if s.get('native_pending') or s['engine']['native_counter']!=65:return 1
 for attempt in range(3):
  if run('collect',control/('collect-'+str(attempt)+'.log'))==0:
   print('PHYSICAL65 PUBLIC CPU/GETINFO COMPLETE; NO ENTROPY APPROVAL/IP',flush=True);return 0
  time.sleep(10)
 return 1
if __name__=='__main__':raise SystemExit(main())
