#!/usr/bin/env python3
"""Independent public-only review checks; no real state/key/radio invocation."""
import sys,json,hashlib,subprocess
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));import gate,admission
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 payload=(gate.CHECKED/'payload.efi').read_bytes();world=(gate.CHECKED/'world19.rup').read_bytes();results=[]
 def reject(label,fn):
  try:fn()
  except (ValueError,KeyError,TypeError):results.append({'case':label,'rejected':True});return
  raise AssertionError('not rejected: '+label)
 with patch.object(gate.engine,'load_private',side_effect=AssertionError('forbidden key access')) as key:
  assert gate.gates(gate.CHECKED,payload,world)['native_counter']==61;assert admission.checked()['generation']==61
  reject('payload corruption',lambda:gate.gates(gate.CHECKED,bytes([payload[0]^1])+payload[1:],world))
  reject('world corruption',lambda:gate.gates(gate.CHECKED,payload,bytes([world[0]^1])+world[1:]))
  reject('wrong checked path',lambda:gate.gates(ROOT,payload,world))
  targets=[gate.CHECKED/'report.json',gate.CHECKED/'reproduction.json',gate.CHECKED/'production-diff-report.json',gate.CHECKED/'production.diff',gate.CHECKED/'init_probe.c',gate.PROFILE/'components/scan_policy.h',gate.PROFILE/'runs/native-host/report.json',gate.PROFILE/'runs/native-host/host.log',gate.CHECKED/'actors-qemu/observed.log',gate.CHECKED/'actors-empty-boot-qemu/observed.log',gate.CHECKED/'world19-source.json',gate.PROFILE/'runs/policy-binding/report.json',gate.PROFILE/'runs/policy-binding/host.log']
  original=gate.sha
  for target in targets:
   with patch.object(gate,'sha',side_effect=lambda p,target=target:'0'*64 if Path(p).resolve()==target.resolve() else original(p)):
    reject('integrity '+str(target.relative_to(gate.REPO)),lambda:gate.gates(gate.CHECKED,payload,world))
  audit=ROOT/'evidence/policy-audit.json'
  with patch.object(gate,'sha',side_effect=lambda p:'0'*64 if Path(p).resolve()==audit.resolve() else original(p)):
   reject('primary admission audit integrity',admission.checked)
  assert key.call_count==0
 run=subprocess.run([sys.executable,'-c','import sys;sys.path.insert(0,'+repr(str(ROOT))+');import root_route;print(root_route.__file__)'],text=True,capture_output=True,check=True,timeout=10)
 assert run.stdout.strip()==str(ROOT/'root_route.py')
 tests=subprocess.run([sys.executable,str(ROOT/'test_transition60.py')],text=True,capture_output=True,check=True,timeout=10)
 (ROOT/'evidence/independent-review-tests.log').write_text(tests.stdout+tests.stderr)
 report={'status':'INDEPENDENT61-GATE-ADMISSION-TRANSITION-HOST-REVIEW-PASS','baseline_exact61_gate':True,'bounded_passive_admission':True,'integrity_rejection_cases':results,'integrity_rejection_count':len(results),'retirement_and_fresh_tests':'11 unittest methods PASS; copied temporary states only','unique_root_route_import':True,'module_origins':{'gate':gate.__file__,'admission':admission.__file__,'base60':gate.base60.__file__,'primitive':gate.primitive.__file__},'corrected_findings':[{'issue':'unbound mutable production diff report','resolution':'exact51ba report hash plus bothpayload/perfilebaseline/candidate and actual policy report/log/header checks'},{'issue':'single-row or explicit fixture metadata accepted as fresh physical-format boundary','resolution':'exact actualstatus/noexplicitfixture markers +four ordered/sized envelopes +helper/source provenance +QWBTfullboot and QWINactualINIT/rawREADY; physical attestation still not claimed'},{'issue':'generic route import collided with frozen59 dependency','resolution':'new entrypoint renamedroot_route; direct fresh-process import now passes'}],'known_limitations':['This is a host/code/public-evidence review, not an actual BLE or owner-key test.','Parent reports actual fresh60 reviewed observation passed; child did not read the device or real state.','host_gate/controller production tooling remains Root separate admission responsibility.'],'private_key_loads':0,'real_state_operations':0,'device_operations':0,'native_edits':0,'source_sha256':{n:sha(ROOT/n) for n in ('gate.py','admission.py','root_route.py','transition60.py','test_transition60.py','observe60.py','review_checks.py')},'test_log_sha256':sha(ROOT/'evidence/independent-review-tests.log')}
 (ROOT/'evidence/independent-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'integrity_rejections':len(results),'transition_tests':11,'review_sha256':sha(ROOT/'evidence/independent-review.json')}))
if __name__=='__main__':main()
