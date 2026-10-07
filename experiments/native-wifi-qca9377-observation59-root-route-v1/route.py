"""ROOT-only exact59 observation trial; no change to HCI/USB/watchdog/timers."""
from pathlib import Path
import argparse,base64,json,struct,sys,time
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
PROFILE=REPO/'experiments/native-wifi-qca9377-transport-observation59-native-v1'
CHECKED=PROFILE/'runs/checked-candidate'
sys.path.insert(0,str(REPO/'experiments/native-wifi-qca9377-v1'))
import native_route as primitive
import reboot_recovery as recovery
flow,engine=primitive.flow,primitive.engine
REPORT='030bafe91d289a71264e5c7af86753517ad33dfc890ff2cf4c32508e877acf3a'
PAYLOAD='eb38baaf0b8e2ee120290744a116d02c33ff7bf2f011a73e945a10e239d51e55'
WORLD='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7'
SEMANTIC='fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74'
OWNER='622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac'
TARGET='363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9'
PLAIN='0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce'
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):return flow.sha(Path(p).read_bytes())
def safe(n):
 p=Path(n);need(not p.is_absolute() and '..' not in p.parts,'unsafe proof path');return p
def gates(directory,payload,world):
 need(directory.resolve()==CHECKED.resolve() and sha(directory/'report.json')==REPORT,'exact frozen59 report')
 r=flow.read_json(directory/'report.json');rep=flow.read_json(directory/'reproduction.json',8*1024*1024)
 need(r['status']=='BOOT-PREFIX59-REPEATED-EFI-QEMU-WORLD19-DIAGNOSTIC-PASS' and r['native_counter']==59 and flow.sha(payload)==PAYLOAD and flow.sha(world)==WORLD,'exact59/currentworld19')
 need(len(payload)==150528 and r['mapped_bytes']==4083712<=4194304 and len(payload)<=262144,'whole EFI caps')
 off=struct.unpack_from('<I',payload,60)[0];need(struct.unpack_from('<I',payload,off+80)[0]==r['mapped_bytes'],'actual mapped PE size')
 need(sha(directory/'reproduction.json')==r['reproduction_sha256'] and rep['inputs']==r['source_sha256'] and rep['payload_sha256']==PAYLOAD,'reproduction source binding')
 for n,h in r['source_sha256'].items():need(sha(REPO/safe(n))==h,'source changed '+n)
 for n,h in r['generated_compiler_sources_sha256'].items():need(sha(directory/safe(n))==h,'compiled source changed '+n)
 nr=flow.read_json(PROFILE/'runs/native-host/report.json');need(sha(PROFILE/'runs/native-host/report.json')==r['native_report_sha256'] and nr['scenarios']==8 and nr['actual_driver_poll'] and nr['actual_native_PCI_CE_DMA_model'] and nr['actual_driver_overlay_canary_test'],'actual eight native models')
 need(sha(PROFILE/'runs/native-host/host.log')==nr['host_log_sha256'],'actual native model log')
 for n,h in nr['compiled_fixture_sources_sha256'].items():
  p=PROFILE/'runs/native-host'/safe(n)
  if not p.exists():p=REPO/'experiments/native-wifi-qca9377-v1/runs/firmware-chunks'/safe(n)
  need(sha(p)==h,'native fixture changed '+n)
 for sub,empty in (('actors-qemu',False),('actors-empty-boot-qemu',True)):
  g=flow.read_json(directory/sub/'report.json');need(g in r['gates'] and g['empty_boot']==empty and g['physical_verified'] is False and g['payload_sha256']==PAYLOAD and sha(directory/sub/'observed.log')==g['observed_log_sha256'],'actual whole EFI/world19 QEMU')
 need(r['host_checks']['sanitizers'] and r['host_checks']['roof_cat_timing'] and r['host_checks']['host_ticks']==120 and r['host_checks']['adversarial_camera_frames']==16 and r['exact_world19_QEMU'],'current-world ASAN/timing')
 need((r['max_MAIN_bytes'],r['max_MAIN_descriptors'],r['BMI_DONE_commands'],r['HTC_INIT_scan_commands'],r['deadline_us'])==(32984,133,0,0,600000000),'unchanged bounded prefix scope')
 diff=flow.read_json(directory/'production-diff-report.json');need(diff['status']=='EXACT-THREE-GENERATION-CONSTANTS-PASS' and diff['candidate_report_sha256']==REPORT and diff['source_changes']==3 and diff['USB_HCI_watchdog_unchanged'] and diff['production_source_count']==127 and sha(directory/'production.diff')==diff['diff_sha256'],'exact production diff')
 baseline=REPO/'experiments/native-wifi-qca9377-boot-prefix57-native-v1/runs/checked-candidate'
 old=flow.read_json(baseline/'report.json');need(sha(baseline/'report.json')==diff['baseline_report_sha256'],'frozen57 baseline')
 allowed={'init_probe.c':[(b'.generation=57ull',b'.generation=59ull'),(b'uint32_t f[58]={57,',b'uint32_t f[58]={59,')],'prefix.c':[(b'const uint32_t v[14]={57,',b'const uint32_t v[14]={59,')]}
 for n,h in old['generated_compiler_sources_sha256'].items():
  if '/' in n:continue
  b=(baseline/n).read_bytes();need(flow.sha(b)==h,'baseline compiled source changed')
  for x,y in allowed.get(n,[]):need(b.count(x)==1,'exact generation constant');b=b.replace(x,y)
  if n in diff['absolute_include_root_relocations']:
   b=b.replace(b'/home/yuka/rabbit-world/parallel-boot-prefix57-native-v1/source',b'/home/yuka/rabbit-world/parallel-observation59-native-v1/source')
  need(b==(directory/n).read_bytes(),'unexpected production change '+n)
 policy=flow.read_json(PROFILE/'receiver-policy.json');need(policy==r['receiver_policy'] and policy['owner']==OWNER and policy['target']==TARGET and policy['generation']==59 and sha(PROFILE/'receiver-policy.json')==r['receiver_policy_sha256'],'explicit public owner/target/generation59')
 return {'report_sha256':REPORT,'reproduction_sha256':r['reproduction_sha256'],'profile_status':r['status'],'receiver_policy':policy}
def prior58(s):
 need(all(s.get(k) is None for k in ('pending','native_pending','recovery_pending','hardware_trial_pending')),'competing operation')
 need(s['counter']==19 and s['world_sha256']==SEMANTIC and s['package_sha256']==WORLD and s['engine']['native_counter']==58 and s['engine']['payload_sha256']==PLAIN,'exact current58/world19')
 flow.current(s);p=Path(s['engine']['last_release_report']).parent;r=flow.read_json(p/'report.json');plan=flow.read_json(p/'plan.json')
 need(r['status']=='APPLIED' and r['engine_done'] and r['world_done'] and r.get('manual_reboot_confirmed') is False,'actual observed-bootstrap58 recovery')
 need(recovery.hashes(p,plan['files'])==plan['files'],'saved signed58 plan changed')
 installed=engine.gate_check(Path(s['engine']['installed_gate']));need(sha(s['engine']['installed_gate'])==s['engine']['installed_gate_sha256'],'installed gate changed')
 packet=(p/'native.rrt').read_bytes();v=engine.verify(packet,target=bytes.fromhex(TARGET),owner=bytes.fromhex(OWNER),base_runtime=bytes.fromhex(installed['module_hashes']['1']),world=b'',counter=57)
 need(v.counter==58 and flow.sha(v.payload)==PLAIN,'public58 signature')
 wr=flow.read_json(p/'restored-world/report.json');need(wr['status']=='EXACT-APPLIED-RECEIPT' and wr['counter']==19 and wr['package_sha256']==WORLD and wr['receiver_reported_applied'] and sha(p/'restored-world/world.rup')==WORLD,'actual world19 applied proof')
 need(flow.compile_world(Path(s['world']),19,flow.CREATOR)==Path(s['package']).read_bytes(),'exact preserved world19 bytes')
 return installed
def fresh(q,state_bytes):
 o=flow.read_json(q/'report.json');need(type(o['writes']) is int and o['writes']==0 and o['state_sha256']==flow.sha(state_bytes) and o['query_sha256']==sha(q/'query.log') and 0<=time.time()-o['observed_at']<=300,'fresh real unchanged world19 query')
 raw=bytes.fromhex(o['raw_hex']);need(len(raw)==60 and raw[:4]==b'RFS\x01' and raw[20:22]==b'\x02\x00' and int.from_bytes(raw[24:28],'little')==19 and raw[28:].hex()==WORLD,'actual world19 receipt')
 rows=[json.loads(x) for x in (q/'query.log').read_text().splitlines() if x.startswith('{')];need([x['stage'] for x in rows if x.get('stage','').startswith('value bytes:')]==['value bytes:60 hex:'+raw.hex()],'raw callback binding')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['check','prepare','deliver']);ap.add_argument('--state',type=Path,required=True);ap.add_argument('--observation',type=Path);ap.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');a=ap.parse_args()
 with flow.state_lock(a.state):
  raw=a.state.read_bytes();s=flow.read_json(a.state);proof=gates(CHECKED,(CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes())
  if a.action in ('check','prepare'):
   installed=prior58(s)
   if a.action=='check':print('EXACT59-PUBLIC-SOURCE-MODEL-BASE58-WORLD19-CHECK-PASS');return 0
   need(a.observation is not None,'fresh explicit observation required');fresh(a.observation,raw)
   public=a.private.with_suffix('.pub').read_bytes();need(public.hex()==OWNER and flow.sha(public)==installed['owner_public_sha256'],'actual owner public identity')
  old=primitive.gates;primitive.gates=gates
  try:
   if a.action=='prepare':
    need(a.state.read_bytes()==raw,'state changed before key');d=primitive.prepare(a.state,s,CHECKED,a.private);(d/'root-before-state.json').write_bytes(raw)
    for n in ('report.json','query.log'):(d/('prior19-'+n)).write_bytes((a.observation/n).read_bytes())
    flow.save(d/'root-admission.json',{'state_sha256':flow.sha(raw),'candidate':proof,'observation_sha256':sha(d/'prior19-report.json'),'read_only_DIAGNOSTIC_scope':True,'timer_fix_included':False});print(d);return 0
   d=Path(s['native_pending']);before=flow.read_json(d/'root-before-state.json');before['native_pending']=str(d)
   admit=flow.read_json(d/'root-admission.json');need(before==s and admit['state_sha256']==sha(d/'root-before-state.json') and admit['candidate']==proof and admit['observation_sha256']==sha(d/'prior19-report.json'),'exact saved59 session/admission')
   return primitive.deliver(a.state,s,a.private)
  finally:primitive.gates=old
if __name__=='__main__':raise SystemExit(main())
