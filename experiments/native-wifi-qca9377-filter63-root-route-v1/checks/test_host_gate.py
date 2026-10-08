"""Public-only hash tamper simulations, no frozen writes or physical APIs."""
from pathlib import Path
import importlib.util,json,hashlib
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'host_gate.py';s=importlib.util.spec_from_file_location('_filter63_host_gate_test',p);g=importlib.util.module_from_spec(s);s.loader.exec_module(g);assert len(g.checked())==3;checks=1;original=g.sha
paths=[g.CHECKED/'report.json',g.CHECKED/'payload.efi',g.NATIVE/'native-abi.json']
for name,(_,_,exe,_,_) in g.HELPERS.items():
 R=g.REPO/'experiments'/name;paths +=[R/n for n in ('evidence/host-proof.json','evidence/bindings.json','runs/control/host-test')]+[R/'runs/control'/exe];r=json.loads((R/'evidence/host-proof.json').read_text());paths +=[R/'evidence'/('callbacks.log' if 'staging' in name else 'host.log')]
 for n in r['source_sha256']:paths.append(g.REPO/n if n.startswith('experiments/') else R/n)
paths +=[g.NATIVE/'components'/n for n in ('pipeline_status.inc','pipeline_gatt.c','scan_status.inc','scan_native.c','rx.c')]
oracle=g.REPO/'experiments/native-wifi-qca9377-native63-host-oracle-v1/evidence/2026-10-08';paths +=[oracle/'report.json',*[oracle/f'capture-scan0-filter{case}.json' for case in (0,4,2)]]
for target in set(p.resolve() for p in paths):
 g.sha=lambda p,target=target:'0'*64 if Path(p).resolve()==target else original(p)
 try:g.checked()
 except ValueError:checks+=1
 else:raise AssertionError('tampered input accepted '+str(target))
 finally:g.sha=original
for n in ('../secret','/absolute'):
 try:g.safe(n)
 except ValueError:checks+=1
 else:raise AssertionError('unsafe path accepted')
e=ROOT/'evidence/host63-gate';e.mkdir(parents=True,exist_ok=True);r={'status':'FROZEN-HOST63-PUBLIC-GATE-TAMPER-CHECKS-PASS','checks':checks,'gate_source_sha256':original(p),'monitor_gate_source_sha256':original(ROOT/'monitor_gate.py'),'test_source_sha256':original(Path(__file__)),'helpers':g.checked(),'source_hashes_rechecked':True,'frozen_input_changes':0,'state_key_accesses':0,'BLE_operations':0,'physical_admission':False};(e/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',checks,'gateSHA',original(p),'monitorGateSHA',original(ROOT/'monitor_gate.py'),'reportSHA',original(e/'report.json'))
