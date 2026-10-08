import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'full-closure.json').read_text());r=json.loads((R/'main-report.json').read_text())
assert sha(R/'main-report.json')==m['main_report_sha256']
assert sha(R/'main-freeze.json')==m['main_freeze_sha256']
assert sha(R/'host.log')==m['host_log_sha256']
for name,entry in m['files'].items():assert sha(R/name)==entry['sha256'],name
for name,h in r['compiled_sources_sha256'].items():assert sha(R/'sources/producer'/name)==h,name
assert len(r['compiled_sources_sha256'])==195
assert sha(R/'sources/producer/fixture.c')==m['actual_final_fixture_sha256']
assert r['test_sha256']==m['ASAN_executable_sha256']
assert m['fixture_kind']=='synthetic-actual-C-producer' and not m['physical']
print('ACTUAL-STATION-CLOSURE-PASS files='+str(len(m['files'])))
