"""Sequential exact53 read-only combined observation; clear only proven owner state."""
from pathlib import Path
import json,subprocess,sys,hashlib,time
from decode_release import decode,route,ROOT
CONTROL=route.ROOT/'runs/control';STATE=route.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
with route.flow.state_lock(STATE):
 s=route.flow.read_json(STATE)
 if any(s.get(k) for k in ('pending','native_pending','recovery_pending')) or s['engine']['native_counter']!=53 or s['engine']['payload_sha256']!=route.PAYLOAD_SHA:raise ValueError('exact applied53 required')
 assets=Path(s['hardware_trial_pending'])
 if assets.name!='firmware-ram-8sztj97t':raise ValueError('exact53 saved asset session required')
 ar=route.flow.read_json(assets/'report.json');release=route.flow.read_json(Path(s['engine']['last_release_report']))
 if release['status']!='EXACT-APPLIED-RECEIPT' or release['counter']!=53 or not release['receiver_reported_applied'] or release['payload_sha256']!=route.PAYLOAD_SHA:raise ValueError('actual53 receipt required')
 policy,public,gate=route.current_assets(s,Path(ar['checked_directory']))
 if ar['gate']!=gate or ar['policy']!=policy:raise ValueError('source/session policy binding changed')
 exe=route.REPO/'experiments/native-wifi-qca9377-v1/runs/mac-control/boot-reader'
 run=subprocess.run([str(exe),'--read'],capture_output=True,text=True,timeout=70)
 out=ROOT/'runs/control';out.mkdir(parents=True,exist_ok=True);(out/'boot53.log').write_text(run.stderr)
 if run.returncode:raise RuntimeError(run.stderr)
 raw=json.loads(run.stdout);route.flow.save(out/'boot53.json',raw)
 observed=[]
 for name in ('startup','profile'):
  p=CONTROL/(name+'53.json')
  if not 0<=time.time()-p.stat().st_mtime<300:raise ValueError('fresh '+name+' observation required')
  observed.append(route.flow.read_json(p))
 d,w,p=decode(raw,*observed,ar)
 route.flow.save(out/'boot53.decoded.json',d)
 report={'status':'PHYSICAL53-BOUNDED-RX-READY-ALL-OWNER-RELEASE-PASS','native_counter':53,'native_payload_sha256':route.PAYLOAD_SHA,'asset_session':str(assets),'router_connected':False,'ip_verified':False,'device_attestation':False,'files_sha256':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in (out/'boot53.json',CONTROL/'startup53.json',CONTROL/'profile53.json')},'decoder_sha256':hashlib.sha256((ROOT/'decode_release.py').read_bytes()).hexdigest()}
 route.flow.save(out/'result53.json',report)
 ar.update(boot_observation=str(out/'boot53.json'),boot_observation_sha256=hashlib.sha256((out/'boot53.json').read_bytes()).hexdigest(),boot_observed=d,bounded_rx_result=str(out/'result53.json'))
 route.flow.save(assets/'report.json',ar);s['hardware_trial_pending']=None;route.flow.save(STATE,s)
 print(json.dumps(report))
