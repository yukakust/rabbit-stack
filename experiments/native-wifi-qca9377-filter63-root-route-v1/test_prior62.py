"""Read-only public proof rejection cases; no mock result is physical freshness."""
from pathlib import Path
import copy,json,sys,types,hashlib
import transition62 as t
ROOT=Path(__file__).resolve().parent
state=json.loads((t.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json').read_text())
checks=[]
assert t.verify(state)['state_mutations']==0;checks.append('actual public62 proof PASS')
for name,mutate in [('wrong counter',lambda s:s['engine'].update(native_counter=61)),('wrong payload',lambda s:s['engine'].update(payload_sha256='00'*32)),('wrong world',lambda s:s.update(world_sha256='00'*32)),('competing native',lambda s:s.update(native_pending='/not-authorized')),('competing world',lambda s:s.update(pending='/not-authorized')),('missing completed assets',lambda s:s.update(hardware_trial_pending=None))]:
 bad=copy.deepcopy(state);mutate(bad)
 try:t.verify(bad)
 except ValueError:checks.append(name+' rejected')
 else:raise AssertionError(name)
old=sys.modules.get('gate');sentinel=types.ModuleType('gate');sys.modules['gate']=sentinel
try:
 route=t.prior();assert route.gate is not sentinel and sys.modules['gate'] is sentinel;checks.append('generic gate restored; prior has own identity')
finally:
 if old is None:sys.modules.pop('gate',None)
 else:sys.modules['gate']=old
assert t.capture()[0]['version_only_pass'];checks.append('actual raw VERSION3.56 release proof joined')
e=ROOT/'evidence';e.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'status':'PUBLIC62-PRE63-READ-ONLY-PROOF-CHECKS-PASS','checks':checks,'source_sha256':{p.name:sha(p) for p in (Path(__file__),ROOT/'transition62.py',ROOT/'observe62.py',ROOT/'prior62-pins.json')},'device_operations':0,'state_mutations':0,'new_signatures':0,'native63_admitted':False}
(e/'prior62-checks.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(checks),'read-only checks')
