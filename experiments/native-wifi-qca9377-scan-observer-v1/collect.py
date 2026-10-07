#!/usr/bin/env python3
"""Guarded known-peer zero-write native54 snapshot. --read is explicit."""
import argparse,contextlib,fcntl,hashlib,json,pathlib,subprocess,tempfile
from decode_scan import ROOT,PROFILE,PEER,PAYLOAD,decode_capture
REPO=ROOT.parent.parent
STATE=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
RECEIPT=STATE.parent/'pci-native-1qq9s17x/report.json'
EXPORT_SHA='172752fd6fac91d102157a2d640d58c3244919a72f9b3f69ad519517ee95edf1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pairs(items):
 d={}
 for k,v in items:
  if k in d:raise ValueError('duplicate JSON key')
  d[k]=v
 return d
def load(p):
 if p.stat().st_size>2_000_000:raise ValueError('JSON input budget')
 return json.loads(p.read_text(),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(mode='w',dir=p.parent,delete=False) as f:
  json.dump(v,f,indent=2);f.write('\n');name=f.name
 pathlib.Path(name).replace(p)
@contextlib.contextmanager
def lock():
 with (STATE.parent/'state.lock').open('a') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ValueError('sole controller still owns state lock')
  yield
def admission(state,receipt,candidate,report_digest):
 if any(state.get(k) for k in ('pending','native_pending','recovery_pending')):raise ValueError('active transport owner')
 if (state.get('engine',{}).get('native_counter'),state.get('engine',{}).get('payload_sha256'))!=(54,PAYLOAD):raise ValueError('exact installed native54')
 if (receipt.get('status'),receipt.get('counter'),receipt.get('payload_sha256'),receipt.get('receiver_reported_applied'))!=('EXACT-APPLIED-RECEIPT',54,PAYLOAD,True):raise ValueError('exact applied native54 receipt')
 if receipt.get('receiver_reported_applied') is not True:raise ValueError('applied flag must be genuine JSON boolean')
 if receipt.get('gate',{}).get('report_sha256')!=report_digest or candidate.get('payload_sha256')!=PAYLOAD:raise ValueError('receipt/candidate proof binding')
 if candidate.get('status')!='SCAN54-REPEATED-FULL-EFI-QEMU-WORLD17-OWNED-EXPORT-PASS':raise ValueError('exact checked profile')
 if state.get('hardware_trial_pending'):
  path=pathlib.Path(state['hardware_trial_pending']).resolve()
  if not path.is_relative_to(STATE.parent.resolve()):raise ValueError('asset owner path')
  asset_admission(load(path/'report.json'))
 return True
def asset_admission(a):
 r=a.get('last_receipt',{});policy=a.get('policy',{})
 if (a.get('status'),a.get('native_counter'),a.get('native_payload_sha256'),a.get('completed_chunks'))!=('EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM',54,PAYLOAD,12):raise ValueError('assets not fully accepted for54')
 if (r.get('bitmap'),r.get('ready'),r.get('error'),r.get('peripheral'))!=(4095,1,0,PEER):raise ValueError('exact fullRAM receiver receipt')
 if (policy.get('generation'),policy.get('target'),policy.get('owner'),policy.get('digest'),policy.get('total'),policy.get('type'),policy.get('version'))!=(54,
  '363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9',
  '622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac',
  '8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01',751436,8,84017153):raise ValueError('exact54 firmware/owner/target policy')
 if len(a.get('packets',[]))!=12 or any(p.get('generation')!=54 for p in a['packets']):raise ValueError('all12 immutable generation54 packets')
 return True
def compile_reader():
 out=ROOT/'runs/control';out.mkdir(parents=True,exist_ok=True);exe=out/'read-scan54'
 plist=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist'
 subprocess.run(['xcrun','--sdk','macosx','clang','-fobjc-arc','-Wall','-Wextra','-Werror',str(ROOT/'read_scan.m'),
                 '-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],check=True,timeout=60)
 return exe
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--read',action='store_true');ap.add_argument('--output',type=pathlib.Path,default=ROOT/'runs/control/scan54-capture.json')
 a=ap.parse_args();inputs={n:sha(ROOT/n) for n in ['collect.py','decode_scan.py','read_scan.m']};exe=compile_reader()
 if inputs!={n:sha(ROOT/n) for n in inputs}:raise ValueError('collector changed during compile')
 if not a.read:
  subprocess.run([str(exe),'--preflight'],check=True,timeout=5);return
 output=a.output.resolve()
 if not output.is_relative_to((ROOT/'runs').resolve()):raise ValueError('observer output must stay in its own ignored runs')
 with lock():
  s=load(STATE);receipt=load(RECEIPT);candidate_path=PROFILE/'runs/checked-candidate/report.json';candidate=load(candidate_path)
  admission(s,receipt,candidate,sha(candidate_path))
  if sha(PROFILE/'decode_exports.py')!=EXPORT_SHA:raise ValueError('frozen export decoder changed')
  for relative,h in candidate['source_sha256'].items():
   path=(REPO/relative).resolve()
   if not path.is_relative_to(REPO.resolve()) or sha(path)!=h:raise ValueError('frozen source closure changed '+relative)
  run=subprocess.run([str(exe),'--read'],text=True,capture_output=True,timeout=190)
  output.parent.mkdir(parents=True,exist_ok=True);output.with_suffix('.log').write_text(run.stderr)
  if run.returncode:raise RuntimeError(run.stderr)
  raw=json.loads(run.stdout,object_pairs_hook=pairs);d=decode_capture(raw)
  # Recheck exact state/receipt after the complete zero-write observation.
  admission(load(STATE),load(RECEIPT),candidate,sha(candidate_path))
  if inputs!={n:sha(ROOT/n) for n in inputs}:raise ValueError('collector changed during capture')
  d['physical_read_performed']=True
  d['physical_ssid_discovered']=bool(d['ssid_seen'] and d['pending_started'] and d['raw_beacon_matches_status'])
  d['native_receipt_sha256']=sha(RECEIPT);d['candidate_report_sha256']=sha(candidate_path)
  d['collector_source_sha256']=inputs;d['reader_executable_sha256']=sha(exe)
  save(output,raw);save(output.with_suffix('.decoded.json'),d)
  print(json.dumps({k:d[k] for k in ['native_phase','native_error','coordinator_phase','coordinator_error','pending_started','actual_owners_released','epoch','physical_ssid_discovered','wifi_connected']}))
  # Do NOT clear hardware_trial_pending or otherwise write controller state.
if __name__=='__main__':main()
