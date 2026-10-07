"""Read-only offline GEN56 candidate gate. No keys/state/signing/radio APIs.

This is not physical admission: actual55 receipt, full110-page2x capture and
actual all-owner release must be checked separately by the sole root controller.
No caller boolean/host fixture can replace that pending external prerequisite.
"""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CANDIDATE='HTT56-AUTHENTICATED-IE6-REPEATED-EFI-QEMU-WORLD17-RAW-PASS'
NATIVE='HTT56-PRODUCTION-AUTHENTICATED-IE6-RAW-EXPORT-ACTUAL-NATIVE-ASAN-COFF-PASS'
WORLD='47d63aa6e81b35fc355005cf65f889b9c43bc332443e37ddbba672b920c2fc2b'
SEMANTIC='fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74'
def sha(data):return hashlib.sha256(data).hexdigest()
def check_report(r,payload,policy,native_bytes,native_log):
 if r.get('status')!=CANDIDATE or r.get('build_host')!='yukabox':raise ValueError('exact GEN56 candidate status/host')
 if r.get('payload_sha256')!=sha(payload) or r.get('payload_bytes')!=len(payload) or not 0<len(payload)<=262144:raise ValueError('exact bounded payload')
 if r.get('receiver_policy')!=policy or policy.get('generation')!=56:raise ValueError('exact public owner/target/firmware policy56')
 expected={'owner':'622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac','target':'363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9','digest':'8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01','total':751436,'type':8,'version':0x05020001,'kind':1,'generation':56}
 if policy!=expected:raise ValueError('frozen public owner/target/asset identity')
 if r.get('world_package_sha256')!=WORLD or r.get('world_semantic_sha256')!=SEMANTIC:raise ValueError('exact frozen world17')
 if r.get('bounded_us')!=3000000 or r.get('raw_slots')!=6 or r.get('raw_pages')!=30 or r.get('firmware_op_is_authenticated_ie') is not True:raise ValueError('exact bounded authenticated-IE6/raw contract')
 for k in ('physical_verified','signing_admitted','rf_transmit','htt_dataplane_ready'):
  if r.get(k) is not False:raise ValueError('host-only scope:'+k)
 if sha(native_bytes)!=r.get('native_report_sha256'):raise ValueError('native proof bytes')
 n=json.loads(native_bytes)
 if n.get('status')!=NATIVE or n.get('build_host')!='yukabox' or n.get('scenarios')!=24 or n.get('actual_native_entrypoints') is not True:raise ValueError('actual native24 proof')
 for k in ('production_loop','authenticated_firmware_ie6','native_version_query_implemented'):
  if n.get(k) is not True:raise ValueError('native boundary:'+k)
 for k in ('physical_verified','signing_admitted','request_is_rf','htt_dataplane_ready','wmi_credit_debit_for_htt','duplicate_ce1_owner'):
  if n.get(k) is not False:raise ValueError('native scope:'+k)
 if n.get('retained_export_slots')!=6 or sha(native_log)!=n.get('host_log_sha256'):raise ValueError('native export/log')
 if not n.get('source_sha256') or not n.get('compiled_fixture_sources_sha256') or not r.get('generated_compiler_sources_sha256') or not r.get('source_sha256'):raise ValueError('source closure missing')
 for name,h in n['source_sha256'].items():
  if r['source_sha256'].get(name)!=h:raise ValueError('native source differs:'+name)
 host=r.get('host_checks',{})
 if host.get('sanitizers') is not True or host.get('host_ticks')!=120 or host.get('adversarial_camera_frames')!=16:raise ValueError('world17 native checks')
 gates=r.get('gates',[])
 if len(gates)!=2 or {g.get('empty_boot') for g in gates}!={False,True}:raise ValueError('normal/empty supervisor QEMU')
 for g in gates:
  if g.get('status')!='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS' or g.get('payload_sha256')!=sha(payload):raise ValueError('exact supervisor/payload proof')
 return {'offline_candidate_validated':True,'physical_admission':False,'signing_admitted':False,'prior55_required':'actual55 receipt + all110 pages twice + genuine all14-owner/lifecycle release; root controller only'}
def candidate_gate(directory,repository):
 d=Path(directory);repo=Path(repository);payload=(d/'payload.efi').read_bytes();r=json.loads((d/'report.json').read_text());policy=json.loads((ROOT/'receiver-policy.json').read_text())
 npath=ROOT/'runs/native-host/report.json';verdict=check_report(r,payload,policy,npath.read_bytes(),npath.with_name('host.log').read_bytes())
 for name,h in r['source_sha256'].items():
  p=Path(name)
  if p.is_absolute() or '..' in p.parts or sha((repo/p).read_bytes())!=h:raise ValueError('exact current source:'+name)
 for name,h in r['generated_compiler_sources_sha256'].items():
  if Path(name).name!=name or sha((d/name).read_bytes())!=h:raise ValueError('generated compiler input:'+name)
 n=json.loads(npath.read_text())
 for name,h in n['compiled_fixture_sources_sha256'].items():
  if Path(name).name!=name or sha((npath.parent/name).read_bytes())!=h:raise ValueError('compiled native fixture:'+name)
 for sub,empty in [('actors-qemu',False),('actors-empty-boot-qemu',True)]:
  g=json.loads((d/sub/'report.json').read_text());log=(d/sub/'observed.log').read_bytes()
  if g not in r['gates'] or g.get('empty_boot') is not empty or sha(log)!=g.get('observed_log_sha256'):raise ValueError('actual QEMU report/log binding')
 return verdict
