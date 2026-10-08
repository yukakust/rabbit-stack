"""Offline evidence/source consistency; no compiler, signing or device access."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((R/'evidence'/n).read_text())
f=load('freeze.json')
for n,h in f['source_sha256'].items():assert sha(R/n)==h,n
for n,h in f['evidence_sha256'].items():assert sha(R/'evidence'/n)==h,n
for name in ['allocator-report.json','renderer-report.json','native-report.json']:
 r=load(name)
 for n,h in r['source_sha256'].items():assert sha(R/n)==h,(name,n)
 assert r['physical_proved'] is False
r=load('native-report.json');q=load('qemu-report.json');rep=load('reproduction.json')
assert r['file_bytes']==212480 and r['mapped_bytes']==2195456 and r['fits']
assert r['payload_sha256']==q['payload_sha256'] and rep['payload_sha256']==[r['payload_sha256']]*3
assert q['physical_proved'] is False and q['signing_admitted'] is False
assert q['test_source_sha256']==sha(R/'verify_projection.py')
assert rep['qemu_report_sha256']==sha(R/'evidence/qemu-report.json')
for i,name in enumerate(['qemu-normal.log','qemu-empty.log']):
 assert sha(R/'evidence'/name)==q['gates'][i]['observed_log_sha256']
 assert q['gates'][i]['empty_boot'] is bool(i) and q['gates'][i]['physical_verified'] is False
base=R.parent/'native-wifi-qca9377-htt-persistent-runtime-v1'
assert sha(base/'runtime_native_prototype.py')==r['base_generator_sha256']
for n,h in f['prototype_source_sha256'].items():assert sha(base/n)==h,n
assert f['prototype_report_sha256']==sha(base/'evidence/2026-10-09/report.json')
print('CITY-ARENA-OWNERSHIP-DIFFERENTIAL-THREE-EFI-NORMAL-EMPTY-QEMU-PASS; NOT PHYSICAL/ADMITTED')
