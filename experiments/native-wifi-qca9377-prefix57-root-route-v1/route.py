"""Root sequential exact57 launch; frozen native/asset primitives are unchanged."""
from pathlib import Path
import sys,json,time,argparse
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
PROFILE=REPO/'experiments/native-wifi-qca9377-boot-prefix57-native-v1'
sys.path.insert(0,str(REPO/'experiments/native-wifi-qca9377-prefix57-admission-v1'))
import gate as admission
sys.path.insert(0,str(REPO/'experiments/native-wifi-qca9377-v1'))
import native_route as primitive
import boot_asset_route as asset
flow,engine=primitive.flow,primitive.engine
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
REPORT_SHA='c362eb73bdfa96cef85962db9d625d6aa9664476f8b47b44fb60756f6f5099d1'
PAYLOAD_SHA='9c63e6622c10190a8a17de2ff01ee03f72de95e93fd7326ca4da6e2c429be161'
def gates(directory,payload,world):
 if directory.resolve()!=(PROFILE/'runs/checked-candidate').resolve():raise ValueError('exact frozen directory')
 offline=admission.candidate57(PROFILE)
 if flow.sha((directory/'report.json').read_bytes())!=REPORT_SHA or flow.sha(payload)!=PAYLOAD_SHA or flow.sha(world)!='f306120fdd548b6d4cc1d3915a13ae8cbe7848b162caa78528add353b9cb3f32':raise ValueError('exact candidate/world binding')
 return {**offline,'report_sha256':REPORT_SHA,'receiver_policy':flow.read_json(PROFILE/'receiver-policy.json')}
def current_assets(s,checked):
 if any(s.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('transport active')
 flow.current(s);p=flow.read_json(PROFILE/'receiver-policy.json');public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes();installed=engine.gate_check(Path(s['engine']['installed_gate']))
 g=gates(checked,(checked/'payload.efi').read_bytes(),Path(s['package']).read_bytes());r=flow.read_json(Path(s['engine']['last_release_report']))
 if s['engine']['native_counter']!=57 or s['engine']['payload_sha256']!=PAYLOAD_SHA or p['generation']!=57 or p['owner']!=public.hex() or flow.sha(public)!=installed['owner_public_sha256'] or p['target']!=installed['target_sha256'] or flow.sha(Path(s['engine']['installed_gate']).read_bytes())!=s['engine']['installed_gate_sha256'] or r['status']!='EXACT-APPLIED-RECEIPT' or r['counter']!=57 or not r['receiver_reported_applied'] or r['payload_sha256']!=PAYLOAD_SHA:raise ValueError('exact applied57 owner/target required')
 return p,public,g
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','deliver','asset-prepare','asset-deliver']);p.add_argument('--state',type=Path,required=True);p.add_argument('--checked',type=Path,default=PROFILE/'runs/checked-candidate');p.add_argument('--observation-dir',type=Path);p.add_argument('--diagnostic',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--session',type=Path);p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');a=p.parse_args();a.state=a.state.resolve()
 with flow.state_lock(a.state):
  s=flow.read_json(a.state)
  if a.action.startswith('asset-'):
   old=asset.current
   try:
    asset.current=current_assets
    return asset.prepare(a,s) if a.action=='asset-prepare' else asset.deliver(a,s)
   finally:asset.current=old
  old=primitive.gates
  try:
   primitive.gates=gates
   if a.action=='prepare':
    if not a.observation_dir:raise ValueError('fresh root observation directory required')
    q=a.observation_dir;plan=a.state.parent/'native56-city-recovery-plan';retire=REPO/'experiments/native-wifi-qca9377-reboot-recovery55-root-v1/evidence/2026-10-07/actual-reboot-retirement/retirement.json'
    before=a.state.read_bytes();result=admission.evaluate(PROFILE,before,plan,retire,(q/'observation.json').read_bytes(),(q/'report.json').read_bytes(),(q/'query-0.log').read_bytes(),time.time())
    if s['engine']['native_counter']!=56 or s['counter']!=18 or a.state.read_bytes()!=before:raise ValueError('exact unchanged prior56/world18')
    directory=primitive.prepare(a.state,s,a.checked,a.private)
    (directory/'root-before-state.json').write_bytes(before)
    for n in ['observation.json','report.json','query-0.log']:(directory/('prior18-'+n)).write_bytes((q/n).read_bytes())
    flow.save(directory/'root-admission.json',result)
    print(directory,flush=True);return 0
   directory=Path(s['native_pending']);before=(directory/'root-before-state.json').read_bytes();expected=flow.read_json(directory/'root-before-state.json');expected['native_pending']=str(directory)
   result=flow.read_json(directory/'root-admission.json')
   if expected!=s or result['state_sha256']!=flow.sha(before) or result['observation_sha256']!=flow.sha((directory/'prior18-observation.json').read_bytes()) or result['query_report_sha256']!=flow.sha((directory/'prior18-report.json').read_bytes()):raise ValueError('saved root admission/session changed')
   return primitive.deliver(a.state,s,a.private)
  finally:primitive.gates=old
if __name__=='__main__':main()
