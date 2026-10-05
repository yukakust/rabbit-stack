"""Known-peer read-only diagnostic. Compile on Mac; no secret loading."""
import argparse,json,struct,subprocess
from pathlib import Path
import operating_route as route
ROOT=Path(__file__).resolve().parent
NAMES='phase error session_phase posted deferred_bytes tx_count rx_count service_bytes service_valid wmi_endpoint htt_endpoint build abi_minor chains memory_count regdomain low2 high2 low5 high5 credit_available credit_outstanding'.split()
RX='pipe step hardware_index read_index write_index published_index cookie bytes ring_fault hardware_error'.split()
def decode(raw):
 if raw.get('peripheral','').upper()!='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF' or raw.get('writes')!=0:raise ValueError('known-peer zero-write observation required')
 b=bytes.fromhex(raw.get('raw_hex',''))
 if len(b)!=208 or b[:8]!=b'QWOP0002':raise ValueError('exact diagnostic envelope required')
 d=dict(zip(NAMES,struct.unpack('<22I',b[8:96])))
 d['receive']=dict(zip(RX,struct.unpack('<10I',b[96:136])))
 d['descriptor_hex']=b[136:144].hex();d['prefix_hex']=b[144:208].hex()
 d['wifi_connected']=False;d['device_attestation']=False
 return d
def main():
 p=argparse.ArgumentParser();p.add_argument('--read',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
 out=ROOT/'runs/control';out.mkdir(parents=True,exist_ok=True);exe=out/'read-diagnostic'
 plist=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist'
 subprocess.run(['xcrun','--sdk','macosx','clang','-fobjc-arc','-Wall','-Wextra','-Werror',str(ROOT/'read_diagnostic.m'),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],check=True,timeout=60)
 if not a.read:return 0
 if not a.output:p.error('--read requires --output')
 state=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
 with route.flow.state_lock(state):
  s=route.flow.read_json(state)
  if any(s.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('active transport owner')
  run=subprocess.run([str(exe),'--read'],capture_output=True,text=True,timeout=70)
  a.output.parent.mkdir(parents=True,exist_ok=True);a.output.with_suffix('.log').write_text(run.stderr)
  if run.returncode:raise RuntimeError(run.stderr)
  raw=json.loads(run.stdout);d=decode(raw);route.flow.save(a.output,raw);route.flow.save(a.output.with_suffix('.decoded.json'),d);print(json.dumps(d))
if __name__=='__main__':main()

