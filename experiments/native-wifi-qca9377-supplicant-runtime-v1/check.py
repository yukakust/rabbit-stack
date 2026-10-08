"""Public local closure check; no hardware, state or key imports."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def checked():
 c=json.loads((ROOT/'runs/coff/report.json').read_text());h=json.loads((ROOT/'runs/interop/report.json').read_text());p=json.loads((ROOT/'runs/platform/report.json').read_text())
 assert c['status']=='FREESTANDING-SUPPLICANT-RUNTIME-COFF-LINKED' and c['linked'] and c['unresolved_after_combining_units']==[] and c['OS_import_directory'] is False
 assert c['successful_units']==c['required_units']==27
 assert sha(ROOT/'runs/coff/runtime.dll')==c['image_sha256']
 assert c['file_bytes']<262144 and c['size_of_image']<4194304
 assert h['status']=='HOST-PATCHED-RSN-NATIVE-PLATFORM-INTEROP-PASS' and [r['mode'] for r in h['interop_scenarios']]==list(range(13))
 assert p['status']=='FREESTANDING-PLATFORM-ASAN-UBSAN-PROVIDER-TIMER-REVOKE-PASS' and p['production_providers_approved'] is False and p['native_radio_capability']=='UNKNOWN'
 assert p['interop_report_sha256']==sha(ROOT/'runs/interop/report.json')
 for n,pin in p['source_sha256'].items():assert sha(ROOT/n)==pin,n
 for r in [c,h]:
  for n,pin in r['local_sources'].items():assert sha(ROOT/n)==pin,n
 for n,pin in c['source_tree_sha256'].items():assert sha(ROOT/'runs/coff/tree'/n)==pin,n
 for n,v in h['compiled_fixture_sources_sha256'].items():assert sha(ROOT/'runs/interop'/n)==v['sha256']
 for r in h['interop_scenarios']:assert sha(ROOT/'runs/interop'/('mode-'+str(r['mode'])+'.log'))==r['log_sha256']
 for n,pin in p['host_log_sha256'].items():assert sha(ROOT/'runs/platform'/(n+'.log'))==pin
 for n,pin in json.loads((ROOT/'frozen-inputs.json').read_text()).items():assert sha(ROOT.parent.parent/n)==pin,n
 return c,h,p
if __name__=='__main__':print(checked()[0]['status'])
