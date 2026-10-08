from pathlib import Path
import hashlib,json,tempfile
import derive
R=Path(__file__).resolve().parent;E=R/'evidence';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((E/'freeze.json').read_text())
for n,h in f['source_sha256'].items():assert sha(R/n)==h,n
assert sha(E/'report.json')==f['report_sha256']
r=json.loads((E/'report.json').read_text())
assert r['status']=='SYNTHETIC-FALLIBLE-RNG-LWIP-LEASE-TCP-ASAN-COFF-PASS'
assert not r['physical_proved'] and not r['entropy_authority_proved'] and not r['native_integrated']
for n,h in r['source_sha256'].items():assert sha(R/n)==h,n
assert len(r['derived_report']['coff_object_sha256'])==23
with tempfile.TemporaryDirectory() as t:
 out=Path(t)/'derived';base=derive.derive(out)
 assert base==r['original_inputs']
 for n,h in r['derived_report']['source_sha256'].items():assert sha(out/n)==h,n
print('FALLIBLE-RNG-SOURCE-REAL-LWIP-ASAN-COFF-EVIDENCE-PASS; NOT PHYSICAL/RNG-AUTHORITY')
