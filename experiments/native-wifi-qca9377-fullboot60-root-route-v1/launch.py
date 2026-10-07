"""ROOT exact new60 admission; validated59 archive precedes local owner signing."""
from pathlib import Path
import sys,json,argparse,struct
import transition59 as t
prior=t.prior;flow,engine=prior.flow,prior.engine
ROOT=Path(__file__).resolve().parent;PROFILE=prior.REPO/'experiments/native-wifi-qca9377-fullboot60-native-v1';CHECKED=PROFILE/'runs/checked-candidate'
def gates(directory,payload,world):
 m=flow.read_json(ROOT/'frozen.json');t.need(directory.resolve()==CHECKED.resolve(),'exact60 directory')
 t.need(prior.sha(directory/'report.json')==m['report_sha256'] and flow.sha(payload)==m['payload_sha256'] and flow.sha(world)==prior.WORLD,'frozen60 actual report/payload/world19')
 r=flow.read_json(directory/'report.json');rep=flow.read_json(directory/'reproduction.json',8*1024*1024)
 t.need(r['status']==m['report_status'] and r['native_counter']==60 and r['build_host']=='yukabox','actual60 host/generation')
 t.need(r['world_package_sha256']==prior.WORLD and r['world_semantic_sha256']==prior.SEMANTIC and r['MAIN_bytes']==727128 and r['BMI_DONE_commands']==1 and r['WMI_INIT_commands']==1 and r['WMI_READY_required_before_success'] and r['deadline_us']==5400000000 and r['scan_commands']==0 and r['physical_verified'] is False and r['signing_admitted'] is False and r['device_operations']==0,'exact bounded fullboot scope; no physical/scan claim')
 t.need(0<len(payload)<=262144 and r['mapped_bytes']<=4194304,'file/mapped caps');off=struct.unpack_from('<I',payload,60)[0];t.need(struct.unpack_from('<I',payload,off+80)[0]==r['mapped_bytes'],'actual mapped PE')
 t.need(prior.sha(directory/'reproduction.json')==r['reproduction_sha256'] and rep['inputs']==r['source_sha256'] and rep['payload_sha256']==m['payload_sha256'],'full source closure')
 for n,h in r['source_sha256'].items():t.need(prior.sha(prior.REPO/prior.safe(n))==h,'source changed '+n)
 for n,h in r['generated_compiler_sources_sha256'].items():t.need(prior.sha(directory/prior.safe(n))==h,'generated changed '+n)
 for name in ('driver.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c'):
  t.need((directory/name).read_bytes()==(prior.CHECKED/name).read_bytes(),'USB/HCI/driver logic changed '+name)
 diff=flow.read_json(directory/'production-diff-report.json');t.need(diff['status']=='FULLBOOT60-SCOPED-PRODUCTION-DIFF-PASS' and diff['baseline_report_sha256']==prior.REPORT and diff['candidate_report_sha256']==m['report_sha256'] and diff['USB_HCI_resident_unchanged'] and prior.sha(directory/'production.diff')=='6c8f360993ec0b0968832887f5b038789111cefbaf3c0cf8c86970a80a45125e','exact scoped production diff')
 t.need(set(diff['production_changes'])=={'init_probe.c','prefix.c','prefix.h','overlay.h'},'only four fullboot changes')
 baseline=flow.read_json(prior.CHECKED/'report.json');t.need(prior.sha(prior.CHECKED/'report.json')==prior.REPORT,'frozen59 baseline')
 for name,h in baseline['generated_compiler_sources_sha256'].items():
  if '/' in name:continue
  b=(prior.CHECKED/name).read_bytes();t.need(flow.sha(b)==h,'baseline generated source changed')
  if name in diff['production_changes']:
   d=diff['production_changes'][name];t.need(d['baseline_sha256']==h and prior.sha(directory/name)==d['candidate_sha256'],'declared fullboot diff hash')
   continue
  if name in diff['absolute_include_root_relocations']:b=b.replace(b'/home/yuka/rabbit-world/parallel-observation59-native-v1/source',b'/home/yuka/rabbit-world/parallel-fullboot60-native-v1/source')
  t.need(b==(directory/name).read_bytes(),'unexpected production change '+name)
 npath=PROFILE/'runs/native-host/report.json';n=flow.read_json(npath)
 t.need(prior.sha(npath)==r['native_report_sha256'] and n['status']==m['native_status'] and n['scenarios']==m['native_scenarios'] and prior.sha(npath.parent/'host.log')==n['host_log_sha256'],'actual native fullboot models')
 for name,h in n['source_sha256'].items():t.need(r['source_sha256'].get(name)==h,'native source missing from whole closure '+name)
 for name,h in n['compiled_fixture_sources_sha256'].items():t.need(prior.sha(npath.parent/prior.safe(name))==h,'native fixture changed '+name)
 for sub,empty in (('actors-qemu',False),('actors-empty-boot-qemu',True)):
  q=flow.read_json(directory/sub/'report.json');t.need(q in r['gates'] and q['empty_boot']==empty and q['payload_sha256']==m['payload_sha256'] and q['status']=='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS' and prior.sha(directory/sub/'observed.log')==q['observed_log_sha256'],'actual full EFI/QEMU')
 h=r['host_checks'];t.need(h['sanitizers'] and h['roof_cat_timing'] and h['host_ticks']==120 and h['adversarial_camera_frames']==16,'current world ASAN/timing')
 t.need(prior.sha(directory/'world19-source.json')==r['world_source_sha256'],'exact world source')
 policy=flow.read_json(PROFILE/'receiver-policy.json');t.need(policy=={**flow.read_json(prior.PROFILE/'receiver-policy.json'),'generation':60} and policy==r['receiver_policy'],'actual owner/target/generation60 firmware')
 return {'report_sha256':m['report_sha256'],'payload_sha256':m['payload_sha256'],'profile_status':r['status'],'receiver_policy':policy,'native_counter':60,'world_package_sha256':prior.WORLD,'source_model_verified':True}
def current(s,checked):
 t.need(not any(s.get(k) for k in ('pending','native_pending','recovery_pending')),'competing operation');flow.current(s)
 g=gates(checked,(checked/'payload.efi').read_bytes(),Path(s['package']).read_bytes());m=flow.read_json(ROOT/'frozen.json');policy=g['receiver_policy'];public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes();installed=engine.gate_check(Path(s['engine']['installed_gate']))
 t.need(public.hex()==prior.OWNER and flow.sha(public)==installed['owner_public_sha256'] and policy['target']==installed['target_sha256'] and prior.sha(s['engine']['installed_gate'])==s['engine']['installed_gate_sha256'],'actual owner/target installation')
 t.need(s['engine']['native_counter']==60 and s['engine']['payload_sha256']==m['payload_sha256'] and s['counter']==19 and s['world_sha256']==prior.SEMANTIC and s['package_sha256']==prior.WORLD,'actual60/world19')
 r=flow.read_json(Path(s['engine']['last_release_report']));t.need(r['status']=='EXACT-APPLIED-RECEIPT' and r['receiver_reported_applied'] and r['counter']==60 and r['payload_sha256']==m['payload_sha256'],'actual60 applied')
 return policy,public,g
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('check','prepare','deliver'));p.add_argument('--state',type=Path,required=True);p.add_argument('--observation',type=Path);p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key');a=p.parse_args();a.state=a.state.resolve()
 with flow.state_lock(a.state):
  s=flow.read_json(a.state);g=gates(CHECKED,(CHECKED/'payload.efi').read_bytes(),Path(s['package']).read_bytes())
  if a.action=='check':t.verify(s);print('ROOT60-SOURCE-MODEL-PRIOR59-WORLD19-PASS');return 0
  old=prior.primitive.gates;prior.primitive.gates=gates
  try:
   if a.action=='prepare':
    import collector_gate
    collector_gate.checked()
    tools=flow.read_json(ROOT/'host-tools.json');t.need(prior.sha(prior.ROOT/'runs/control/read-initial59')==tools['initial_reader_sha256'] and prior.sha(prior.ROOT/'read_initial59.m')==tools['initial_reader_source_sha256'] and prior.sha(prior.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist')==tools['info_plist_sha256'],'checked host tools changed')
    t.need(a.observation is not None,'fresh observed59 release required');s,retired=t.retire(a.state,s,a.observation,g);before=a.state.read_bytes();d=prior.primitive.prepare(a.state,s,CHECKED,a.private)
    (d/'root-before-state.json').write_bytes(before);flow.save(d/'root-admission.json',{'candidate':g,'retirement':str(retired/'retirement.json'),'retirement_sha256':prior.sha(retired/'retirement.json'),'prior_state_sha256':flow.sha(before)});print(d);return 0
   d=Path(s['native_pending']);b=flow.read_json(d/'root-before-state.json');b['native_pending']=str(d);admit=flow.read_json(d/'root-admission.json');t.need(b==s and admit['candidate']==g and admit['prior_state_sha256']==prior.sha(d/'root-before-state.json') and admit['retirement_sha256']==prior.sha(admit['retirement']),'exact saved60 admission')
   return prior.primitive.deliver(a.state,s,a.private)
  finally:prior.primitive.gates=old
if __name__=='__main__':raise SystemExit(main())
