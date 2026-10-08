#!/usr/bin/env python3
"""Only host fake callbacks/offline preflight; no Bluetooth manager/key/state."""
import hashlib,json,subprocess,time
from pathlib import Path
import observer
R=observer.ROOT;OLD=R.parent/'native-wifi-qca9377-asset-observer-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def derivation():
 proof=json.loads((OLD/'evidence/host-proof.json').read_text())
 for name,h in proof['source_sha256'].items():
  if name.startswith('experiments/native-wifi-qca9377-asset-observer-v1/'):
   if sha(R.parent.parent/name)!=h:raise ValueError('frozen original changed')
 expected=(OLD/'sender.m').read_bytes().replace(b'if(count>240)count=240;',b'if(count>100)count=100;')
 if (R/'sender.m').read_bytes()!=expected:raise ValueError('only single DATA cap replacement permitted')
 for n in ('sequence.h','observer.py','decode_prefix.py'):
  if (R/n).read_bytes()!=(OLD/n).read_bytes():raise ValueError('frozen helper clone changed '+n)
 return {str(p.relative_to(R.parent.parent)):sha(p) for p in (OLD/'sender.m',OLD/'sequence.h',OLD/'observer.py',OLD/'decode_prefix.py',OLD/'host_test.m')}
def main():
 originals=derivation();out=R/'runs'/('proof-'+str(time.time_ns()));out.mkdir(parents=True)
 exe,inputs=observer.compile_host(True)
 run=subprocess.run([str(exe),str(out/'fixtures')],text=True,capture_output=True,check=True,timeout=10);(out/'host.log').write_text(run.stdout+run.stderr);assert 'PASS 65 HOST OBJC' in run.stdout
 # This is unsigned dummy layout, never an actual immutable owner packet.
 packet=out/'fixtures/large0/large-dummy-packet.bin'
 subprocess.run(['python3',str(R/'observer.py'),'--preflight','--packet',str(packet),'--checkpoint',str(out/'offline-checkpoint.json'),'--prefix-log',str(out/'offline-diagnostic.jsonl')],check=True,capture_output=True,timeout=60)
 assert not (out/'offline-diagnostic.jsonl').exists();assert originals==derivation()
 comp=json.loads((R/'runs/control/compile-report.json').read_text())
 report={'status':'HOST-ONLY-SINGLE-DATA-CAP100-DERIVATIVE-PASS','host_callback_checks':65,'data_payload_cap':100,'offset_prefix_bytes':4,'max_ATT_value_bytes':104,'pacing_ms':50,'send_timeout_seconds':240,'query_timeout_seconds':60,'resume_floor_fixture':18480,'next_offset_fixture':18580,'confirmed_floor_after_synthetic_RFCS':18680,'final_short_payload_fixture':37,'exact100byte_final_fixture':True,'whole_packet_unchanged':True,'original_source_sha256':originals,'source_sha256':{n:sha(R/n) for n in ('sender.m','sequence.h','observer.py','host_test.m','decode_prefix.py','verify_host.py')},'compiler_input_sha256':inputs,'host_test_executable_sha256':sha(exe),'compile_report':comp,'host_log_sha256':sha(out/'host.log'),'bluetooth_manager_started':False,'private_key_loads':0,'signatures_created':0,'native_code_modified':False,'state_modified':False,'physical_trial_performed':False,'linkloss_cause_proven':False,'actual_production_admission':'Root sole-controller freshgen60/currentasset context required'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');e=R/'evidence';e.mkdir(exist_ok=True);(e/'host-proof.json').write_text(json.dumps(report,indent=2)+'\n');(e/'host.log').write_text(run.stdout+run.stderr);print(json.dumps({'host_callback_checks':65,'report':str(out/'report.json'),'sender_executable_sha256':comp['executable_sha256']}))
if __name__=='__main__':main()
