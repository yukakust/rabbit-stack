"""Source-closed public proof check. Never executes C or accesses hardware/state."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
REPORT='049bcdf749c9c8a1231a1c01a086d533b2866bd3b6367478b1a93e3bf450a08e'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 out=ROOT/'runs';assert sha(out/'report.json')==REPORT;r=json.loads((out/'report.json').read_text());assert r['status']=='PURE-HTT3.56-TLV-RX-ABI-OWNERSHIP-FRAME-ASAN-COFF-PASS' and r['cases']==705 and r['build_host']=='yukabox'
 for section in ('source_sha256','compiled_inputs_sha256'):
  for n,h in r[section].items():
   p=Path(n);assert not p.is_absolute() and '..' not in p.parts;assert sha(ROOT/p)==h,n
 assert sha(out/'host.log')==r['host_log_sha256'] and sha(out/'rx_decode.obj')==r['coff_object_sha256'];assert r['coff_linked'] is False and r['native_integration'] is False and r['physical_verified'] is False and r['service65_physical_proof'] is False and r['provisional_generation'] is None and r['device_operations']==r['private_key_accesses']==0
 return {'status':'SOURCE-CLOSED-PUBLIC-HTT-RX-COMPONENT-GATE-PASS','report_sha256':REPORT,'decoder_source_sha256':sha(ROOT/'rx_decode.c'),'decoder_header_sha256':sha(ROOT/'rx_decode.h'),'source_count':len(r['source_sha256']),'compiled_count':len(r['compiled_inputs_sha256']),'physical_admission':False,'native_integration':False}
if __name__=='__main__':print(json.dumps(check(),indent=2))
