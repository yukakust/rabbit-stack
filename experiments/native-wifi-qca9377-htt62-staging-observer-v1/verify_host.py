#!/usr/bin/env python3
"""Fake callbacks + offline layout/preflight only, never a Bluetooth manager."""
import json,struct,subprocess,time
from pathlib import Path
import observer,decode_boot
R=observer.ROOT

def main():
 out=R/'runs'/('host-proof-'+str(time.time_ns()));out.mkdir(parents=True)
 exe,inputs=observer.compile_host(True)
 run=subprocess.run([str(exe),str(out/'callbacks')],text=True,capture_output=True,check=True,timeout=10)
 (out/'callbacks.log').write_text(run.stdout+run.stderr)
 assert 'PASS 41 HOST OBJC' in run.stdout
 checks=0
 firmware=bytes(range(32));raw=b'QWBT0001'+struct.pack('<30I',*range(30))+firmware;d=decode_boot.decode(raw,firmware)
 assert d['fields']==dict(zip(decode_boot.FIELDS,range(30)));assert d['native_generation_verified'] is False and d['readiness_verified'] is False and d['resource_release_verified'] is False;checks+=1
 for n in range(162):
  if n==160:continue
  try:decode_boot.decode(raw[:n] if n<160 else raw+b'X',firmware);raise AssertionError('accepted length')
  except ValueError:checks+=1
 for i in range(8):
  b=bytearray(raw);b[i]^=1
  try:decode_boot.decode(bytes(b),firmware);raise AssertionError('accepted magic')
  except ValueError:checks+=1
 for i in range(32):
  b=bytearray(firmware);b[i]^=1
  try:decode_boot.decode(raw,bytes(b));raise AssertionError('accepted firmware digest')
  except ValueError:checks+=1
 for digest in (b'',bytes(31),bytes(33),None,'00'*32):
  try:decode_boot.decode(raw,digest);raise AssertionError('accepted digest bounds')
  except ValueError:checks+=1
 packet=out/'callbacks/case0/dummy-layout-packet.bin'
 subprocess.run(['python3',str(R/'observer.py'),'--preflight','--packet',str(packet),'--checkpoint',str(out/'offline-checkpoint.json'),'--boot-log',str(out/'offline-diagnostic.jsonl')],check=True,capture_output=True,timeout=60)
 assert not (out/'offline-diagnostic.jsonl').exists();checks+=1
 sender=(R/'sender.m').read_text();base=(observer.BASE/'mac_firmware_sender.m').read_text()
 # Existing timeout and pacing remain equal; only callback expiry logging changes.
 for text in ('scheduledTimerWithTimeInterval:s.sending?240:60','50*NSEC_PER_MSEC'):
  assert text in sender and text in base;checks+=1
 compile_report=json.loads((R/'runs/control/compile-report.json').read_text())
 sender_exe=Path(compile_report['executable_path'])
 subprocess.run([str(sender_exe),str(packet),str(out/'alias-checkpoint.json'),'--preflight','--prefix-log',str(out/'alias-diagnostic.jsonl')],check=True,capture_output=True,timeout=10);assert not (out/'alias-diagnostic.jsonl').exists();checks+=1
 wrong=bytearray(packet.read_bytes());wrong[120]=61;wrong_packet=out/'wrong-generation.bin';wrong_packet.write_bytes(wrong)
 failed=subprocess.run([str(sender_exe),str(wrong_packet),str(out/'wrong-checkpoint.json'),'--preflight','--prefix-log',str(out/'wrong-diagnostic.jsonl')],capture_output=True,timeout=10);assert failed.returncode==2 and not (out/'wrong-checkpoint.json').exists();checks+=1
 # Immutable transport/checkpoint/ACK functions are exactly baseline bytes.
 def section(text,first,last):a=text.index(first);return text[a:text.index(last,a)]
 baseline=(observer.REPO/'experiments/native-wifi-qca9377-asset-observer-v1/sender.m').read_text()
 for first,last in [('- (void)save{','- (void)centralManagerDidUpdateState:'),('- (void)write:(NSData*)','- (void)peripheral:(CBPeripheral*)p didUpdateValue'),('- (void)nextActionAfterDiagnostic{','\n@end')]:assert section(sender,first,last)==section(baseline,first,last);checks+=1
 assert (R/'sequence.h').read_bytes()==(observer.REPO/'experiments/native-wifi-qca9377-asset-observer-v1/sequence.h').read_bytes();checks+=1

 sources={str(p.relative_to(observer.REPO)):observer.sha(p) for p in (R/'sender.m',R/'sequence.h',R/'host_test.m',R/'observer.py',R/'decode_boot.py',R/'verify_host.py',observer.BASE/'mac_firmware_sender.m',observer.BASE/'firmware_sender_core.c',observer.BASE/'firmware_sender_core.h',observer.NATIVE/'sha256.c',observer.NATIVE/'sha256.h',observer.REPO/'experiments/native-wifi-qca9377-asset-observer-v1/sender.m')}
 report={'status':'HOST-OBJC-HTT62-STAGING-QWBT-CALLBACKS-PREFLIGHT-PASS','callback_checks':41,'python_checks':checks,'source_sha256':sources,'host_test_executable_sha256':observer.sha(exe),'compiler_input_sha256':inputs,'compile_report':compile_report,'callback_log_sha256':observer.sha(out/'callbacks.log'),'bluetooth_manager_started':False,'physical_trial':False,'signature_verified':False,'private_key_loads':0,'signatures_created':0,'native_source_changes':False,'timer_intervals_unchanged':True,'existing_prefix_log_alias_tested':True,'QFS_write_ACK_checkpoint_methods_byte_identical':True,'DATA_cap':240,'observed_envelope':'QWBT0001/160/UUID22-23','native_generation_verified':False,'readiness_verified':False,'resource_release_verified':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 evidence=R/'evidence';evidence.mkdir(exist_ok=True);(evidence/'host-proof.json').write_text(json.dumps(report,indent=2)+'\n');(evidence/'callbacks.log').write_text(run.stdout+run.stderr)
 print(json.dumps({'callback_checks':41,'python_checks':checks,'report':str(out/'report.json')}))
if __name__=='__main__':main()
