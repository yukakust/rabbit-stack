"""Read-only offline gate negatives on checked GEN56 artifacts, no hardware."""
import copy,json,hashlib
from pathlib import Path
import admission_gate as gate
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 d=ROOT/'runs/checked-candidate';report=json.loads((d/'report.json').read_text());payload=(d/'payload.efi').read_bytes();policy=json.loads((ROOT/'receiver-policy.json').read_text());np=ROOT/'runs/native-host/report.json';nb=np.read_bytes();log=np.with_name('host.log').read_bytes()
 result=gate.candidate_gate(d,ROOT.parent.parent);assert result['offline_candidate_validated'] and not result['physical_admission'] and not result['signing_admitted']
 count=1
 def reject(r=report,p=payload,pol=policy,n=nb,l=log):
  nonlocal count
  try:gate.check_report(r,p,pol,n,l)
  except (ValueError,KeyError,TypeError):count+=1
  else:raise AssertionError('corruption accepted')
 for name,value in [('status','bad'),('build_host','mac'),('payload_sha256','0'*64),('payload_bytes',0),('bounded_us',3000001),('raw_slots',5),('raw_pages',29),('firmware_op_is_authenticated_ie',False),('physical_verified',True),('signing_admitted',True),('rf_transmit',True),('htt_dataplane_ready',True),('world_package_sha256','0'*64),('world_semantic_sha256','0'*64),('source_sha256',{}),('generated_compiler_sources_sha256',{}),('gates',[])]:
  r=copy.deepcopy(report);r[name]=value;reject(r=r)
 for name,value in [('generation',55),('owner','0'*64),('target','0'*64),('digest','0'*64),('type',9),('version',0),('total',1),('kind',2)]:
  p=copy.deepcopy(policy);p[name]=value;r=copy.deepcopy(report);r['receiver_policy']=p;reject(r=r,pol=p)
 for name,value in [('status','bad'),('build_host','mac'),('scenarios',23),('actual_native_entrypoints',False),('production_loop',False),('authenticated_firmware_ie6',False),('native_version_query_implemented',False),('physical_verified',True),('signing_admitted',True),('request_is_rf',True),('htt_dataplane_ready',True),('wmi_credit_debit_for_htt',True),('duplicate_ce1_owner',True),('retained_export_slots',5),('compiled_fixture_sources_sha256',{})]:
  n=json.loads(nb);n[name]=value;b=json.dumps(n).encode();r=copy.deepcopy(report);r['native_report_sha256']=sha(b);reject(r=r,n=b)
 for key,value in [('sanitizers',False),('host_ticks',119),('adversarial_camera_frames',15)]:
  r=copy.deepcopy(report);r['host_checks'][key]=value;reject(r=r)
 r=copy.deepcopy(report);r['gates'][0]['empty_boot']=r['gates'][1]['empty_boot'];reject(r=r)
 r=copy.deepcopy(report);r['gates'][0]['payload_sha256']='0'*64;reject(r=r)
 r=copy.deepcopy(report);name=next(iter(json.loads(nb)['source_sha256']));r['source_sha256'][name]='0'*64;reject(r=r)
 reject(p=payload[:-1]);reject(n=nb+b' ');reject(l=log+b'x')
 proof={'status':'HTT56-OFFLINE-CANDIDATE-ADMISSION-GATE-NEGATIVES-PASS','checks':count,'physical_admission':False,'signing_admitted':False,'hardware_access':False,'state_access':False,'key_loads':0,'candidate_report_sha256':sha((d/'report.json').read_bytes()),'source_sha256':{p.name:sha(p.read_bytes()) for p in [ROOT/'admission_gate.py',ROOT/'test_gate.py']},'prior55_actual_evidence_required':True}
 (ROOT/'runs/gate-report.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof['status'],count)
if __name__=='__main__':main()
