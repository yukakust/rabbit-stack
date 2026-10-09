import hashlib,json,runpy
from pathlib import Path
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((R/'freeze.json').read_text());assert f['status']=='FROZEN-SOFTWARE-EXPERIMENTAL-ETHERNET-TX-PASS'
for n,h in f['public_sources_sha256'].items():assert sha(R/n)==h,n
for n,h in f['binary_sha256'].items():assert sha(R/n)==h,n
r=json.loads((R/f['report']).read_text());assert sha(R/f['report'])==f['report_sha256'];assert r['status']=='EXPERIMENTAL-ETHERNET-TX-ACTUAL-PRODUCER-ASAN-COFF-PASS' and r['cases']==[31,32,33,34,35,36]
e=R/'evidence/2026-10-09'
for n,h in r['source_sha256'].items():assert sha(R/n)==h,n
for n,h in r['compiled_sources_sha256'].items():assert sha(e/'compiler-inputs'/n)==h,n
for n,h in r['compiled_glue_sources_sha256'].items():assert sha(R/n)==h,n;assert sha(e/'glue-compiler-inputs'/str(Path(n).relative_to('runs/glue-source')))==h,n
assert sha(e/'host.log')==r['host_log_sha256']
for flag in ['physical_verified','native_candidate_integrated','mature_handshake_in_this_producer','authenticated_data_delivery','controlled_port_authority','physical_wire_encryption_verified','policy_DMA_is_target_ACK','all47_stop_backend','rf_admission_granted']:assert r[flag] is False,flag
runpy.run_path(str(R/'check_primary.py'))
print('FROZEN EXPERIMENTAL PROTECTED TX SIX ACTUAL-C CASES / COFF / FULL COMPILER SOURCE CLOSURE PASS')
