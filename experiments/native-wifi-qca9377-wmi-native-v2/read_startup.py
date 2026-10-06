"""Exact known-peer zero-write startup diagnostic; no secret access."""
import argparse,json,struct,subprocess
from pathlib import Path
import startup_build as build
import operating_route as route
ROOT=build.ROOT
FIELDS='phase error transaction_phase tx_posted tx_count rx_count ready_seen tx_complete abi_minor credit_available credit_outstanding memory_count'.split()
RX='pipe step hardware_index read_index write_index published_index cookie bytes'.split()
def decode(raw):
 if raw.get('peripheral','').upper()!='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF' or raw.get('writes')!=0:raise ValueError('known-peer zero-write observation required')
 b=bytes.fromhex(raw.get('raw_hex',''))
 if len(b)!=96 or b[:8]!=b'QWIN0001' or b[62:64]!=b'\0\0':raise ValueError('exact startup envelope required')
 d=dict(zip(FIELDS,struct.unpack('<12I',b[8:56])));d['mac_hex']=b[56:62].hex();d['receive']=dict(zip(RX,struct.unpack('<8I',b[64:96])))
 d['wifi_connected']=False;d['device_attestation']=False;return d
def main():
 p=argparse.ArgumentParser();p.add_argument('--read',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
 out=ROOT/'runs/control';out.mkdir(parents=True,exist_ok=True);exe=out/'read-startup'
 plist=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist'
 subprocess.run(['xcrun','--sdk','macosx','clang','-fobjc-arc','-Wall','-Wextra','-Werror',str(ROOT/'read_startup.m'),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],check=True,timeout=60)
 if not a.read:return 0
 if not a.output:p.error('--read requires --output')
 state=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
 with route.flow.state_lock(state):
  s=route.flow.read_json(state)
  if any(s.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('active transport owner')
  report=route.flow.read_json(ROOT/'runs/checked-candidate/report.json')
  if s.get('engine',{}).get('native_counter')!=49 or s['engine'].get('payload_sha256')!=report['payload_sha256']:raise ValueError('exact installed startup candidate required')
  run=subprocess.run([str(exe),'--read'],capture_output=True,text=True,timeout=70)
  a.output.parent.mkdir(parents=True,exist_ok=True);a.output.with_suffix('.log').write_text(run.stderr)
  if run.returncode:raise RuntimeError(run.stderr)
  raw=json.loads(run.stdout);d=decode(raw);route.flow.save(a.output,raw);route.flow.save(a.output.with_suffix('.decoded.json'),d);print(json.dumps(d))
if __name__=='__main__':main()
