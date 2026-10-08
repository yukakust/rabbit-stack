"""Pure pinned-input tamper simulation; never touches frozen files or devices."""
import importlib.util,json,hashlib,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'host_gate.py';spec=importlib.util.spec_from_file_location('_independent_htt62_host_gate',p);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
checks=0
assert len(g.checked())==2;checks+=1
paths=[g.NATIVE/n for n in ('report.json','payload.efi','profile_gatt.c','init_probe.c','boot_gatt.c','firmware_op.c','version.c','htt_native.c')]
for name in g.PINS:
 R=g.REPO/'experiments'/name;paths +=[R/n for n in ('evidence/host-proof.json','evidence/bindings.json','runs/control/host-test')]
 r=json.loads((R/'evidence/host-proof.json').read_text());paths +=[Path(r['compile_report']['executable_path']) if 'compile_report' in r else Path(r['reader_path']),R/'evidence'/('callbacks.log' if 'compile_report' in r else 'host.log')]
 for n in r['source_sha256']:paths.append(g.REPO/n if n.startswith('experiments/') else R/n)
paths +=[g.REPO/'experiments/native-wifi-qca9377-htt62-observer-v2/runs/public-fixture/firmware-6.bin']
original=g.sha
for target in set(x.resolve() for x in paths):
 g.sha=lambda x,target=target:'0'*64 if Path(x).resolve()==target else original(x)
 try:g.checked()
 except ValueError:checks+=1
 else:raise AssertionError('accepted altered hash '+str(target))
 finally:g.sha=original
for name,pin in g.PINS.items():
 R=g.REPO/'experiments'/name;r=json.loads((R/'evidence/host-proof.json').read_text());staging='staging' in name
 for field,value in [('status','BAD'),('bluetooth_manager_started',True),('private_key_loads',1),('python_checks',0)]+([('DATA_cap',100),('readiness_verified',True),('resource_release_verified',True),('signatures_created',1)] if staging else [('physical_admission',True),('writes',1),('association',True),('IP',True)]):
  bad=copy.deepcopy(r);bad[field]=value
  try:g.helper_metadata(bad,pin,staging)
  except ValueError:checks+=1
  else:raise AssertionError(field)
e=ROOT/'evidence/host-gate-offline';e.mkdir(parents=True,exist_ok=True);result={'status':'HTT62-PINNED-HOST-GATE-OFFLINE-TAMPER-TESTS-PASS','checks':checks,'gate_source_sha256':original(p),'test_source_sha256':original(Path(__file__)),'helpers':g.checked(),'physical_admission':False,'frozen_files_modified':False,'manager_started':False,'state_key_accesses':0,'gate_py_dependency':False};(e/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checks':checks,'gate_sha256':original(p),'test_report_sha256':original(e/'report.json')},indent=2))
