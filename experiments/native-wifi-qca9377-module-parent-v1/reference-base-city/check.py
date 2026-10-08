from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;E=R/'evidence';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((E/'freeze.json').read_text())
for name,h in f['source_sha256'].items():assert sha(R/name)==h,name
for name,h in f['evidence_sha256'].items():assert sha(E/name)==h,name
for name in ['presentation-report.json','renderer-report.json','native-report.json']:
 r=json.loads((E/name).read_text());assert not r['physical_proved']
 for n,h in r['source_sha256'].items():assert sha(R/n)==h,(name,n)
n=json.loads((E/'native-report.json').read_text());q=json.loads((E/'qemu-report.json').read_text());p=json.loads((E/'reproduction.json').read_text())
assert n['file_bytes']==213504 and n['mapped_bytes']==2224128 and n['fits']
assert n['payload_sha256']==q['payload_sha256'] and p['payload_sha256']==[n['payload_sha256']]*3
assert not q['physical_proved'] and not q['signing_admitted']
assert q['test_source_sha256']==sha(R/'verify_qemu.py')
assert p['qemu_report_sha256']==sha(E/'qemu-report.json')
for i,name in enumerate(['qemu-normal.log','qemu-empty.log']):
 assert sha(E/name)==q['gates'][i]['observed_log_sha256']
 assert q['gates'][i]['empty_boot'] is bool(i) and not q['gates'][i]['physical_verified']
b=R.parent/'native-wifi-qca9377-city-arena-v1'
assert sha(b/'native_projection.py')==n['base_generator_sha256']
assert sha(b/'evidence/freeze.json')==f['base_freeze_sha256']
print('CACHED-CITY-SERVICE-SOURCE-ASAN-DIFFERENTIAL-THREE-EFI-QEMU-PASS; NOT PHYSICAL/ADMITTED')
