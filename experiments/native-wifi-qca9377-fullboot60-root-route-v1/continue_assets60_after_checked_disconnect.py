"""ROOT-reviewed single resume after exact fresh native/prefix/asset retention proof."""
import sys,json,time,struct,subprocess
from pathlib import Path
import launch
ROOT=launch.ROOT;REPO=launch.prior.REPO;flow=launch.flow
STATE=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
def raw(p,size):
 rows=[json.loads(x) for x in p.read_text().splitlines() if x.startswith('{')];launch.t.need(all(v['code']==0 and not v['domain'] for v in rows),'read error')
 v=[x['stage'].split(' hex:')[1] for x in rows if x.get('stage','').startswith(f'value bytes:{size} hex:')];launch.t.need(len(v)==1,'exact raw callback required');return bytes.fromhex(v[0])
def check(q,s):
 r=flow.read_json(q/'report.json');launch.t.need(r['writes']==0 and r['state_sha256']==flow.sha(STATE.read_bytes()) and 0<=time.time()-r['observed_at']<=300,'fresh unchanged context')
 for n,h in r['logs'].items():launch.t.need(launch.prior.sha(q/n)==h,'diagnostic changed')
 packet=flow.read_json(Path(s['engine']['last_release_report']))['package_sha256'];receipt=raw(q/'receipt.log',60)
 launch.t.need(receipt[:4]==b'RFS\1' and receipt[20:24]==b'\2\0\0\0' and int.from_bytes(receipt[24:28],'little')==60 and receipt[28:].hex()==packet,'actual60 applied context')
 p=raw(q/'prefix.log',240);v=struct.unpack('<58I',p[8:]);launch.t.need(p[:8]==b'QPFX0001' and v[0]==60 and v[1]==0 and v[50]==0 and v[49]==0,'actual60 beforeboot/noUSBfault/overflow')
 d=Path(s['hardware_trial_pending']);report=flow.read_json(d/'report.json');a=raw(q/'asset.log',64)
 launch.t.need(report['completed_chunks']==1 and a[:8]==b'RFCS0001' and int.from_bytes(a[8:12],'little')==1 and not int.from_bytes(a[12:16],'little') and a[24:56].hex()==report['packets'][1]['packet_sha256'] and int.from_bytes(a[16:20],'little')==65760 and 17280<=int.from_bytes(a[20:24],'little')<=65760 and int.from_bytes(a[56:60],'little')==1 and int.from_bytes(a[60:64],'little')==0,'exact retained chunk1 receipt')
 return d
def main():
 q=Path(sys.argv[1]).resolve()
 with flow.state_lock(STATE):
  s=flow.read_json(STATE);launch.current(s,launch.CHECKED);session=check(q,s)
 print('REVIEWED exact60 native/prefix/retainedchunk; single query-before-resume',flush=True)
 r=subprocess.run([sys.executable,str(ROOT/'assets60.py'),'deliver','--state',str(STATE),'--session',str(session)],cwd=REPO)
 launch.t.need(r.returncode in (0,1),'nonordinary delivery failure; preserve session')
 # v2 permits only ordinary progressing timeout; another disconnect stops there.
 r=subprocess.run([sys.executable,str(ROOT/'resume_assets60_v2.py'),str(session)],cwd=REPO)
 launch.t.need(r.returncode==0,'continued60 outcome unconfirmed; preserve exact packets and diagnostics')
if __name__=='__main__':main()
