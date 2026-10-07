#!/usr/bin/env python3
"""Fake callbacks + offline layout/preflight only, never a Bluetooth manager."""
import json,struct,subprocess,time
from pathlib import Path
import observer,decode_prefix
R=observer.ROOT

def main():
 out=R/'runs'/('host-proof-'+str(time.time_ns()));out.mkdir(parents=True)
 exe,inputs=observer.compile_host(True)
 run=subprocess.run([str(exe),str(out/'callbacks')],text=True,capture_output=True,check=True,timeout=10)
 (out/'callbacks.log').write_text(run.stdout+run.stderr)
 assert 'PASS 41 HOST OBJC' in run.stdout
 checks=0
 raw=b'QPFX0001'+struct.pack('<58I',59,*range(1,58));d=decode_prefix.decode(raw,59)
 assert d['fields']==dict(zip(decode_prefix.FIELDS,[59,*range(1,58)]));checks+=1
 for n in range(241):
  if n==240:continue
  try:decode_prefix.decode(raw[:n],59);raise AssertionError('accepted length')
  except ValueError:checks+=1
 for i in range(8):
  b=bytearray(raw);b[i]^=1
  try:decode_prefix.decode(bytes(b),59);raise AssertionError('accepted magic')
  except ValueError:checks+=1
 for gen in (0,-1,57,58,60,2**32,True,None):
  try:decode_prefix.decode(raw,gen);raise AssertionError('accepted generation')
  except ValueError:checks+=1
 packet=out/'callbacks/case0/dummy-layout-packet.bin'
 subprocess.run(['python3',str(R/'observer.py'),'--preflight','--packet',str(packet),'--checkpoint',str(out/'offline-checkpoint.json'),'--prefix-log',str(out/'offline-diagnostic.jsonl')],check=True,capture_output=True,timeout=60)
 assert not (out/'offline-diagnostic.jsonl').exists();checks+=1
 sender=(R/'sender.m').read_text();base=(observer.BASE/'mac_firmware_sender.m').read_text()
 # Existing timeout and pacing remain equal; only callback expiry logging changes.
 for text in ('scheduledTimerWithTimeInterval:s.sending?240:60','50*NSEC_PER_MSEC'):
  assert text in sender and text in base;checks+=1
 compile_report=json.loads((R/'runs/control/compile-report.json').read_text())
 sources={str(p.relative_to(observer.REPO)):observer.sha(p) for p in (R/'sender.m',R/'sequence.h',R/'host_test.m',R/'observer.py',R/'decode_prefix.py',R/'verify_host.py',observer.BASE/'mac_firmware_sender.m',observer.BASE/'firmware_sender_core.c',observer.BASE/'firmware_sender_core.h',observer.NATIVE/'sha256.c',observer.NATIVE/'sha256.h',R.parent/'native-wifi-qca9377-boot-prefix57-native-v1/prefix_build.py')}
 report={'status':'HOST-OBJC-ASSET-OBSERVER-CALLBACKS-PREFLIGHT-PASS','callback_checks':41,'python_checks':checks,'source_sha256':sources,'host_test_executable_sha256':observer.sha(exe),'compiler_input_sha256':inputs,'compile_report':compile_report,'callback_log_sha256':observer.sha(out/'callbacks.log'),'bluetooth_manager_started':False,'physical_trial':False,'signature_verified':False,'private_key_loads':0,'signatures_created':0,'native_source_changes':False,'timer_intervals_unchanged':True}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 evidence=R/'evidence';evidence.mkdir(exist_ok=True);(evidence/'host-proof.json').write_text(json.dumps(report,indent=2)+'\n');(evidence/'callbacks.log').write_text(run.stdout+run.stderr)
 print(json.dumps({'callback_checks':41,'python_checks':checks,'report':str(out/'report.json')}))
if __name__=='__main__':main()
