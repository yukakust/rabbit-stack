"""Known-peer read-only startup and bounded RX telemetry of exact53."""
import argparse,json,subprocess,sys
from pathlib import Path
import route
sys.path.insert(0,str(route.PROFILE));from decode_profile import decode as profile_decode
sys.path.insert(0,str(route.V5));from read_startup import decode as startup_decode
def main():
 p=argparse.ArgumentParser();p.add_argument('kind',choices=('profile','startup'));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 root=route.ROOT;out=root/'runs/control';out.mkdir(parents=True,exist_ok=True)
 source=(route.PROFILE/'read_profile.m') if a.kind=='profile' else route.V5/'read_startup.m';exe=out/('read-'+a.kind)
 plist=root.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist'
 subprocess.run(['xcrun','--sdk','macosx','clang','-fobjc-arc','-Wall','-Wextra','-Werror',str(source),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],check=True,timeout=60)
 state=root.parent/'x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
 with route.flow.state_lock(state):
  s=route.flow.read_json(state)
  if any(s.get(k) for k in ('pending','native_pending','recovery_pending')) or s['engine']['native_counter']!=53 or s['engine']['payload_sha256']!=route.PAYLOAD_SHA:raise ValueError('exact installed53 with no transport owner required')
  run=subprocess.run([str(exe),'--read'],capture_output=True,text=True,timeout=70);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.with_suffix('.log').write_text(run.stderr)
  if run.returncode:raise RuntimeError(run.stderr)
  raw=json.loads(run.stdout)
  if raw.get('peripheral','').upper()!=route.PEER or raw.get('writes')!=0:raise ValueError('known-peer zero-write observation required')
  d=(profile_decode if a.kind=='profile' else startup_decode)(raw);route.flow.save(a.output,raw);route.flow.save(a.output.with_suffix('.decoded.json'),d);print(json.dumps(d))
if __name__=='__main__':main()
