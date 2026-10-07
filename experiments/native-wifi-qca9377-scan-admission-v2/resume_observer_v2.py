"""Bounded wait for previous controller exit, then sole exact-session observer."""
from pathlib import Path
import json,os,time,subprocess,sys,hashlib,datetime
root=Path(__file__).resolve().parent; c=root/'runs/control'
old=json.loads((c/'controller55.json').read_text());pid=old['pid']
for _ in range(450):
 try:os.kill(pid,0)
 except ProcessLookupError:break
 time.sleep(2)
else:raise SystemExit('Previous controller still live; no second controller')
current=json.loads((c/'controller55.json').read_text())
if current['pid']!=pid:raise SystemExit('Controller identity changed; no second controller')
ps=subprocess.check_output(['ps','ax','-o','command='],text=True)
for line in ps.splitlines():
 if any(x in line for x in ['read_boot55.py','read_boot55_v2.py','/runs/mac-control/boot-reader --read','/runs/control/boot-reader-v2 --read']):raise SystemExit('Prior BLE read still live; no second controller')
(c/'controller55-before-v2.json').write_text(json.dumps(old,indent=2)+'\n')
f=open(c/'continue55.log','ab',buffering=0);f.write(b'\nROOT OBSERVER V2: previous controller exited; 120s stage logging; no resign/replay\n')
p=root/'continue55_v2.py';proc=subprocess.Popen([sys.executable,str(p),old['native_session']],cwd=root.parents[1],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
awake=subprocess.Popen(['caffeinate','-i','-w',str(proc.pid)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
old.update(pid=proc.pid,caffeinate_pid=awake.pid,controller=str(p),controller_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),prior_pid=pid,observer_timeout_seconds=120,resumed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(c/'controller55.json').write_text(json.dumps(old,indent=2)+'\n');print('Sole observer controller',proc.pid,flush=True)
