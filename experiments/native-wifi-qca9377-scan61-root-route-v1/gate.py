"""Root exact61 public technical gate; no key, state mutation or radio APIs."""
from pathlib import Path
import sys,json,hashlib,struct
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
sys.path.insert(0,str(REPO/'experiments/native-wifi-qca9377-fullboot60-root-route-v1'))
import launch as base60
flow,engine=base60.flow,base60.engine
primitive=base60.prior.primitive
PROFILE=REPO/'experiments/native-wifi-qca9377-scan61-native-v1'
CHECKED=PROFILE/'runs/checked-candidate'
REPORT='0188ad2b1663804fbc6cf663beef4fb3cba2daa05c06eee2fe48fabece5dc388'
PAYLOAD='305d0171c3c2e296fdf00f82a01cc838d67c0a1f3ffa836a847f4f12770ce074'
WORLD=base60.prior.WORLD
SEMANTIC=base60.prior.SEMANTIC
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def safe(n):
 p=Path(n);need(not p.is_absolute() and '..' not in p.parts,'unsafe source path');return p
def gates(directory,payload,world):
 need(directory.resolve()==CHECKED.resolve(),'exact61 candidate path')
 need(sha(directory/'report.json')==REPORT and flow.sha(payload)==PAYLOAD and flow.sha(world)==WORLD,'frozen61 report/payload/world19')
 r=flow.read_json(directory/'report.json');rep=flow.read_json(directory/'reproduction.json',8*1024*1024)
 need(r['status']=='SCAN61-REPEATED-EFI-QEMU-WORLD19-DIAGNOSTIC-PASS' and r['native_counter']==61 and r['build_host']=='yukabox','checked native61 identity')
 need(len(payload)==r['payload_bytes']==191488 and r['mapped_bytes']==4177920 and r['mapped_bytes']<=4194304,'bounded whole EFI')
 pe=struct.unpack_from('<I',payload,60)[0];need(struct.unpack_from('<I',payload,pe+80)[0]==r['mapped_bytes'],'actual PE mapped size')
 need(sha(directory/'reproduction.json')==r['reproduction_sha256']=='79c658115d81b495ebd54842a3a1c2155ab261531777f95a19821cd471b92289' and rep['inputs']==r['source_sha256'] and rep['payload_sha256']==PAYLOAD,'three-build source closure')
 need(len(r['source_sha256'])==480 and len(r['generated_compiler_sources_sha256'])==194,'complete closure counts')
 for n,h in r['source_sha256'].items():need(sha(REPO/safe(n))==h,'source changed '+n)
 for n,h in r['generated_compiler_sources_sha256'].items():need(sha(directory/safe(n))==h,'compiler input changed '+n)
 npath=PROFILE/'runs/native-host/report.json';n=flow.read_json(npath)
 need(sha(npath)==r['native_report_sha256']=='99d4933001aa5bbc578dafed3a4b20bd507745ac36f1adaef516363769de839c' and n['scenarios']==19 and n['exact_passive_wire_asserted'] and n['policy_negatives_checked'] and sha(npath.parent/'host.log')==n['host_log_sha256'],'actual native ASAN/COFF evidence')
 need(len(n['compiled_fixture_sources_sha256'])==149,'native fixture closure')
 for name,h in n['compiled_fixture_sources_sha256'].items():need(sha(npath.parent/safe(name))==h,'fixture changed '+name)
 for sub,empty in (('actors-qemu',False),('actors-empty-boot-qemu',True)):
  q=flow.read_json(directory/sub/'report.json');need(q in r['gates'] and q['empty_boot']==empty and q['payload_sha256']==PAYLOAD and q['status']=='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS' and sha(directory/sub/'observed.log')==q['observed_log_sha256'],'actual EFI QEMU evidence')
 h=r['host_checks'];need(h['sanitizers'] and h['roof_cat_timing'] and h['host_ticks']==120 and h['adversarial_camera_frames']==16 and sha(directory/'world19-source.json')==r['world_source_sha256'],'current city/cat preservation')
 need(sha(directory/'production-diff-report.json')=='51ba3bbe4563fc253cf7b6d4afb91a6fff74f4e4571501ad02cc6875c4e2e3b8','frozen production diff report')
 d=flow.read_json(directory/'production-diff-report.json');need(d['baseline_payload_sha256']=='3984d3f5d1c9a3c3540bf2ef00972bea52406a6f78edc56bd215507110668fd6' and d['candidate_payload_sha256']==PAYLOAD and d['status']=='SCAN61-SCOPED-INTEGRATION-DIFF-FROZEN60-PASS' and d['USB_HCI_resident_unchanged'] and d['frozen60_all_source_hashes_verified'] and d['ATT_discovery29_31_holes_resolved'] and sha(directory/'production.diff')==d['diff_sha256']=='0b1023ee2014defa0146ec7d9638609a4cd623bc595708e015372bcf2fd4ff3a','scoped scan integration')
 need(set(d['production_changes'])=={'init_probe.c','prefix.c','diagnostic_gatt.c','overlay.h','wmi_scan.c'},'unexpected native changes')
 for name,entry in d['production_changes'].items():need(sha(base60.CHECKED/name)==entry['baseline_sha256'] and sha(directory/name)==entry['candidate_sha256'],'actual per-file integration diff '+name)
 for name in ('driver.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c'):
  need((directory/name).read_bytes()==(base60.CHECKED/name).read_bytes(),'protected transport changed '+name)
 for key,val in {'MAIN_bytes':727128,'BMI_DONE_commands':1,'WMI_INIT_commands':1,'WMI_READY_required_before_success':True,'bootstrap_deadline_us':5400000000,'scan_deadline_us':25000000,'raw_slots':22,'raw_pages':110,'active_probe':False,'association':False,'credentials':False,'physical_verified':False,'signing_admitted':False,'device_operations':0,'rf_admission_granted':False}.items():need(r[key]==val,'scope changed '+key)
 policy=flow.read_json(PROFILE/'receiver-policy.json');need(policy==r['receiver_policy'] and policy=={**flow.read_json(base60.PROFILE/'receiver-policy.json'),'generation':61},'exact signed firmware generation61')
 e=PROFILE/'evidence/2026-10-08/frozen-offline-proof'
 need(sha(e/'policy-binding.json')==r['authenticated_policy_binding_sha256']=='e6700e37deb752f0731deff5edf3ccf3839558e425bec3e0edb4755e62089ef4','authenticated policy binding')
 pb=flow.read_json(e/'policy-binding.json');need(sha(PROFILE/'runs/policy-binding/report.json')==pb['report_sha256'] and sha(PROFILE/'runs/policy-binding/host.log')==pb['host_log_sha256'] and sha(PROFILE/'components/scan_policy.h')==pb['header_sha256'],'actual policy sanitizer/evidence/header')
 return {'report_sha256':REPORT,'payload_sha256':PAYLOAD,'profile_status':r['status'],'receiver_policy':policy,'native_counter':61,'world_package_sha256':WORLD,'source_model_verified':True}
if __name__=='__main__':
 s=flow.read_json(REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json')
 print(json.dumps(gates(CHECKED,(CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes()),indent=2))
