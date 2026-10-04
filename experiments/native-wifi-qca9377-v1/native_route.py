"""Exact PCI diagnostic delivery; Yukabox gates precede local owner signing."""
import argparse,base64,tempfile
from pathlib import Path
import diagnostic_build as build
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
engine=build.actors.engine
flow=engine.flow
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
RECEIVER_STATUS="QCA-SETUP-SIGNED-RAM-RECEIVER-CITY-PROFILE-GATES-PASS"
BOOT_STATUS="QCA-EXACT-RAM-MAIN-BOOT-CITY-PROFILE-GATES-PASS"
BOARD_STATUS="QCA-FRESH-BOARD-HELPER-QUERY-CITY-PROFILE-GATES-PASS"
def gates(directory,payload,world):
 report=flow.read_json(directory/'report.json')
 reproduction=flow.read_json(directory/'reproduction.json',8*1024*1024)
 if report['status'] not in ('READ-ONLY-PCI-CITY-PROFILE-GATES-PASS','REVERSIBLE-PCI-WAKE-CITY-PROFILE-GATES-PASS','READ-ONLY-PCI-POWER-CITY-PROFILE-GATES-PASS','REVERSIBLE-PCI-RESET-CITY-PROFILE-GATES-PASS','QCA-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-BOOTIRQ-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-WARM-FULL-CHANNEL-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CE7-READ-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CONFIG-READ-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CONFIG-SETUP-BMI-CITY-PROFILE-GATES-PASS',RECEIVER_STATUS,BOARD_STATUS,BOOT_STATUS) or report['payload_sha256']!=flow.sha(payload):
  raise ValueError('exact diagnostic profile gates required')
 if reproduction['status']!='CURRENT-SOURCES-TWO-REBUILDS-WORLD-C-CHECK-PASS' or reproduction['payload_sha256']!=flow.sha(payload) or reproduction['world_package_sha256']!=flow.sha(world):
  raise ValueError('current-source/current-world reproduction required')
 for name,expected in reproduction['inputs'].items():
  path=Path(name)
  if path.is_absolute() or '..' in path.parts or flow.sha((REPO/path).read_bytes())!=expected:
   raise ValueError('source snapshot changed: '+name)
 for name,expected in report['source_sha256'].items():
  if reproduction['inputs'].get(name)!=expected:raise ValueError('gate source snapshot differs')
 if flow.sha((directory/'host.log').read_bytes())!=report['host_log_sha256']:raise ValueError('host evidence changed')
 if report['status'] in ('REVERSIBLE-PCI-WAKE-CITY-PROFILE-GATES-PASS','REVERSIBLE-PCI-RESET-CITY-PROFILE-GATES-PASS','QCA-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-BOOTIRQ-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-WARM-FULL-CHANNEL-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CE7-READ-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CONFIG-READ-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CONFIG-SETUP-BMI-CITY-PROFILE-GATES-PASS',RECEIVER_STATUS,BOARD_STATUS,BOOT_STATUS):
  port=flow.read_json(directory/'port-report.json')
  if (port['status']!='INITIAL-UEFI-PCI-WAKE-PORT-HOST-MOCK-AND-COFF-ABI-PASS'
   or flow.sha((directory/'port-report.json').read_bytes())!=report['port_report_sha256']
   or flow.sha((directory/'port-host.log').read_bytes())!=port['host_log_sha256']):raise ValueError('exact port gates required')
  for name,expected in port['source_sha256'].items():
   if reproduction['inputs'].get('experiments/native-wifi-qca9377-v1/'+name)!=expected:raise ValueError('port gate sources changed')
 if report['status'] in ('REVERSIBLE-PCI-RESET-CITY-PROFILE-GATES-PASS','QCA-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-BOOTIRQ-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-WARM-FULL-CHANNEL-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CE7-READ-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CONFIG-READ-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CONFIG-SETUP-BMI-CITY-PROFILE-GATES-PASS',RECEIVER_STATUS,BOARD_STATUS,BOOT_STATUS):
  reset=flow.read_json(directory/'reset-report.json')
  if reset['status']!='COOPERATIVE-COLD-RESET-HOST-AND-COFF-PASS' or flow.sha((directory/'reset-report.json').read_bytes())!=report['reset_report_sha256'] or flow.sha((directory/'reset-host.log').read_bytes())!=reset['host_log_sha256']:raise ValueError('reset component gate mismatch')
  for name,expected in reset['source_sha256'].items():
   if reproduction['inputs'].get('experiments/native-wifi-qca9377-v1/'+name)!=expected:raise ValueError('reset gate sources changed')
 if report['status'] in ('QCA-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-BOOTIRQ-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS'):
  components=[('ce','CE-MMIO-UEFI-MAPPED-LIFETIME-HOST-COFF-PASS'),('bmi','ROM-BMI-CE0-CE1-INTEGRATION-HOST-COFF-PASS')]
  if report['status'] in ('QCA-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-BOOTIRQ-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS'):
   if report.get('pcie_aspm_reversible') is not True:raise ValueError('PCIe lifecycle gate required')
   components.append(('dma','UEFI-COMMON-DMA-LIFETIME-HOST-COFF-ABI-PASS'))
  if report['status']=='QCA-BOOTIRQ-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS':
   if report.get('boot_irq_host_isolation') is not True:raise ValueError('host IRQ isolation gate required')
   if report.get('ble_untracked_disconnect_recovery') is not True:raise ValueError('preserved Bluetooth recovery gate required')
   if report.get('ce_snapshot_pre_cleanup') is not True:raise ValueError('bounded pre-cleanup CE telemetry gate required')
   if report.get('ce_registers_before_first_halt') is not True:raise ValueError('bounded pre-halt CE register gate required')
   if report.get('fixed_ce7_read_only') is not True:raise ValueError('fixed read-only CE7 gate required')
   if report.get('ce7_completion_before_timeout') is not True:raise ValueError('CE7 completion-before-timeout gate required')
   if report.get('bounded_init_config_read') is not True:raise ValueError('bounded initialization configuration read gate required')
   if report.get('hash_bound_split_diagnostic') is not True:raise ValueError('hash-bound split diagnostic gate required')
  for component,status in components:
   subreport=flow.read_json(directory/(component+'-report.json'))
   if (subreport['status']!=status or flow.sha((directory/(component+'-report.json')).read_bytes())!=report[component+'_report_sha256']
    or flow.sha((directory/(component+'-host.log')).read_bytes())!=subreport['host_log_sha256']):raise ValueError('component gate mismatch: '+component)
   for name,expected in subreport['source_sha256'].items():
    if reproduction['inputs'].get('experiments/native-wifi-qca9377-v1/'+name)!=expected:raise ValueError('component sources changed: '+name)
 if report['status'] in ('QCA-WARM-FULL-CHANNEL-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CE7-READ-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CONFIG-READ-CITY-PROFILE-GATES-PASS','QCA-FULL-CHANNEL-CONFIG-SETUP-BMI-CITY-PROFILE-GATES-PASS',RECEIVER_STATUS,BOARD_STATUS,BOOT_STATUS):
  setup=report['status'] in ('QCA-FULL-CHANNEL-CONFIG-SETUP-BMI-CITY-PROFILE-GATES-PASS',RECEIVER_STATUS,BOARD_STATUS,BOOT_STATUS)
  config=setup or report['status']=='QCA-FULL-CHANNEL-CONFIG-READ-CITY-PROFILE-GATES-PASS'
  if setup and any(report.get(flag) is not True for flag in ('config_write_readback','config_done_last','cpu_wake_and_bmi')):raise ValueError('setup gates required')
  full=config or report['status']=='QCA-FULL-CHANNEL-CE7-READ-CITY-PROFILE-GATES-PASS'
  if config and report.get('full_channel_config_read') is not True:raise ValueError('config read proof required')
  if full and any(report.get(flag) is not True for flag in ('full_channel_ce7_read','active_dma_guard','completion_before_timeout')):raise ValueError('full CE7 scope gates required')
  for flag in ('native_init_entrypoints','mapped_irq_scope','warm_and_cold_recovery','full_channel_ownership','hash_bound_split_diagnostic','ble_untracked_disconnect_recovery','post_cold_ce_stop','warm_failure_telemetry','warm_cooperative_deadline'):
   if report.get(flag) is not True:raise ValueError('native init gate missing: '+flag)
  if report.get('target_ram_writes') is not setup or report.get('firmware_upload') is not (report['status']==BOOT_STATUS) or report.get('build_host')!='yukabox':raise ValueError('native init scope/host mismatch')
  for component,status in [('init','WARM-RESET-FULL-CHANNEL-CORE-HOST-COFF-PASS'),('probe','NATIVE-FULL-CHANNEL-CONFIG-SETUP-BMI-PROBE-HOST-PASS' if setup else 'NATIVE-FULL-CHANNEL-CONFIG-READ-PROBE-HOST-PASS' if config else 'NATIVE-FULL-CHANNEL-CE7-READ-PROBE-HOST-PASS' if full else 'NATIVE-WARM-FULL-CHANNEL-PROBE-ENTRYPOINT-HOST-PASS')]:
   subreport=flow.read_json(directory/(component+'-report.json'))
   if subreport['status']!=status or flow.sha((directory/(component+'-report.json')).read_bytes())!=report[component+'_report_sha256'] or flow.sha((directory/(component+'-host.log')).read_bytes())!=subreport['host_log_sha256']:
    raise ValueError('native init component evidence mismatch: '+component)
   if subreport.get('cold_reset_clears_ce_fixture') is not True:raise ValueError('post-cold CE reset fixture required')
   if subreport.get('build_host')!='yukabox':raise ValueError('native component host mismatch')
   for name,expected in subreport['source_sha256'].items():
    if reproduction['inputs'].get('experiments/native-wifi-qca9377-v1/'+name)!=expected:raise ValueError('native init source changed: '+name)
   for name,expected in subreport.get('dependency_sha256',{}).items():
    if reproduction['inputs'].get(name)!=expected:raise ValueError('native init ABI changed: '+name)
   if component=='probe' and full and any(subreport.get(flag) is not True for flag in ('full_channel_ce7_read','active_dma_guard','completion_before_timeout')):raise ValueError('native full read fixture proof missing')
   if component=='probe' and setup and any(subreport.get(flag) is not True for flag in ('config_write_readback','config_done_last','cpu_wake_and_bmi')):raise ValueError('setup native fixtures required')
   if component=='init':
    for flag in ('legacy_no_dma_irq_guard_preserved','cold_recovery_requires_rom_and_all_eight_stop','warm_each_io_fault_injected','warm_each_phase_cancelled','warm_full_channel_joint_fixture'):
     if subreport.get(flag) is not True:raise ValueError('native core proof missing: '+flag)
    if subreport.get('channel_scenarios')!=27 or subreport.get('mapped_irq_scenarios')!=36 or subreport.get('native_pci_adapter_scenarios')!=13:raise ValueError('native core scenarios differ')
    if flow.sha((directory/'pack-report.json').read_bytes())!=subreport['pack_report_sha256'] or subreport['pack_report_sha256']!=report['pack_report_sha256']:raise ValueError('source-pinned pack evidence changed')
   if component=='probe' and (subreport.get('scenarios')!=(73 if report['status']==BOARD_STATUS else 65 if setup else 30 if config else 25 if full else 19) or subreport.get('native_entrypoints_integrated') is not True or subreport.get('slow_cooperative_poll_fixture') is not True):raise ValueError('native entrypoint proof missing')
 if report['status'] in (RECEIVER_STATUS,BOOT_STATUS):
  if report['status']==BOOT_STATUS:import boot_build as receiver_build
  else:import receiver_build
  policy=receiver_build.policy()
  if report.get('receiver_policy')!=policy or report.get('receiver_policy_sha256')!=flow.sha(receiver_build.POLICY.read_bytes()) or any(report.get(k) is not True for k in ('signed_ram_receiver_integrated',)) or report.get('firmware_staging_only') is not (report['status']==RECEIVER_STATUS) or report.get('firmware_execution') is not (report['status']==BOOT_STATUS):raise ValueError('exact RAM-only receiver policy required')
  probe=flow.read_json(directory/'probe-report.json')
  if any(probe.get(k) is not True for k in ('signed_ram_receiver_integrated','full_asset_fixture','pinned_unload_retained','fixture_owner_override_only')):raise ValueError('integrated RAM entrypoint fixture required')
  for name,status in [('asset-core','SIGNED-RAM-CHUNKS-HOST-SANITIZERS-COFF-PASS'),('asset-channel','SIGNED-RAM-CHUNK-ATT-CHANNEL-HOST-COFF-PASS'),('asset-port','FIRMWARE-UEFI-RAM-PORT-HOST-COFF-ABI-PASS')]:
   component=flow.read_json(directory/(name+'-report.json'))
   if component['status']!=status or component['build_host']!='yukabox' or flow.sha((directory/(name+'-report.json')).read_bytes())!=report[name+'_report_sha256'] or flow.sha((directory/(name+'-host.log')).read_bytes())!=component['host_log_sha256']:raise ValueError('exact RAM component gates required')
   for path,expected in component['source_sha256'].items():
    if reproduction['inputs'].get(path)!=expected:raise ValueError('RAM gate source differs: '+path)
  asset_port=flow.read_json(directory/'asset-port-report.json');asset_channel=flow.read_json(directory/'asset-channel-report.json')
  if asset_port.get('fresh_setup_rejections')!=143 or asset_port.get('fresh_setup_gate') is not True or asset_channel.get('handle_bases')!=[11,13]:raise ValueError('fresh/relocated receiver fixtures missing')
  for sub in ('actors-qemu','actors-empty-boot-qemu'):
   if b'INTEGRATED RAM SERVICE13..19; TARGET ABSENT WRITE REJECTED; CITY RETAINED' not in (directory/sub/'observed.log').read_bytes():raise ValueError('integrated UEFI ATT receiver gate missing')
 if report['status']==BOOT_STATUS:
  if report.get('two_lifetimes_verified') is not True or report.get('permanent_otp_programming') is not False or report.get('wifi_connected') is not False or report.get('boot_decode_rejections')!=96:raise ValueError('exact boot trial scope required')
  for name,status,cases in [('boot-core','EXACT-BOARD-CALIBRATION-MAIN-BMI-BOOT-CORE-HOST-COFF-PASS',42),('boot-lifetimes','NATIVE-EXACT-BOOT-TWO-LIFETIME-HOST-MOCK-PASS',8)]:
   component=flow.read_json(directory/(name+'-report.json'))
   if component['status']!=status or component['scenarios']!=cases or component['build_host']!='yukabox' or flow.sha((directory/(name+'-report.json')).read_bytes())!=report[name+'_report_sha256'] or flow.sha((directory/(name+'-host.log')).read_bytes())!=component['host_log_sha256']:raise ValueError('boot component proof missing')
   for path,expected in component['source_sha256'].items():
    if reproduction['inputs'].get('experiments/native-wifi-qca9377-v1/'+path)!=expected:raise ValueError('boot component sources changed: '+path)
   for path,expected in component.get('dependency_sha256',{}).items():
    if reproduction['inputs'].get(path)!=expected:raise ValueError('boot component dependencies changed')
  for sub in ('actors-qemu','actors-empty-boot-qemu'):
   if b'BOOT SERVICE20..22 READ ONLY; RAM SERVICE PRESERVED; CITY RETAINED' not in (directory/sub/'observed.log').read_bytes():raise ValueError('boot read-only ATT gate missing')
 if report['status']==BOARD_STATUS:
  import board_build
  policy=board_build.policy()
  if report.get('board_policy')!=policy or report.get('board_policy_sha256')!=flow.sha(board_build.POLICY.read_bytes()) or report.get('helper_ram_upload') is not True or report.get('helper_execute_parameter')!=0x10 or report.get('main_firmware_execution') is not False or report.get('permanent_otp_programming') is not False:raise ValueError('exact helper query-only policy required')
  component=flow.read_json(directory/'board-core-report.json')
  if component['status']!='BOUNDED-BOARD-HELPER-BMI-SMBIOS-HOST-COFF-PASS' or component['build_host']!='yukabox' or flow.sha((directory/'board-core-report.json').read_bytes())!=report['board_core_report_sha256'] or flow.sha((directory/'board-core-host.log').read_bytes())!=component['host_log_sha256']:raise ValueError('exact board component gates required')
  for path,expected in component['source_sha256'].items():
   if reproduction['inputs'].get('experiments/native-wifi-qca9377-v1/'+path)!=expected:raise ValueError('board core source differs: '+path)
  probe=flow.read_json(directory/'probe-report.json')
  if any(probe.get(k) is not True for k in ('board_query_integrated','exact_helper_bytes_fixture','helper_timeout_cancel_cleanup')):raise ValueError('integrated helper fixture required')
  for sub in ('actors-qemu','actors-empty-boot-qemu'):
   if b'READ-ONLY BOARD SERVICE13..15; WRITE REJECTED; CITY RETAINED' not in (directory/sub/'observed.log').read_bytes():raise ValueError('board ATT gate required')
 for sub,empty in [('actors-qemu',False),('actors-empty-boot-qemu',True)]:
  gate=flow.read_json(directory/sub/'report.json');log=(directory/sub/'observed.log').read_bytes()
  if (gate not in report['gates'] or gate['empty_boot']!=empty or gate['payload_sha256']!=flow.sha(payload)
   or gate['status']!='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS'
   or flow.sha(log)!=gate['observed_log_sha256']
   or b'ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES' not in log):
   raise ValueError('exact UEFI PCI and city evidence required')
 return {'report_sha256':flow.sha((directory/'report.json').read_bytes()),
  'reproduction_sha256':flow.sha((directory/'reproduction.json').read_bytes()),'profile_status':report['status']}
def prepare(state_path,state,checked,private_path):
 if state['pending'] or state.get('native_pending') or state.get('recovery_pending') or state.get('hardware_trial_pending'):raise ValueError('pending operation exists')
 flow.current(state);installed=engine.gate_check(Path(state['engine']['installed_gate']))
 if flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256']:raise ValueError('installed gate changed')
 world=Path(state['package']).read_bytes();payload=(checked/'payload.efi').read_bytes();gate=gates(checked,payload,world)
 public=private_path.with_suffix('.pub').read_bytes()
 if flow.sha(public)!=installed['owner_public_sha256']:raise ValueError('owner identity differs')
 counter=state['engine']['native_counter']+1
 if gate['profile_status'] in (RECEIVER_STATUS,BOOT_STATUS):
  if gate['profile_status']==BOOT_STATUS:import boot_build as receiver_build
  else:import receiver_build
  policy=receiver_build.policy()
  if policy['owner']!=public.hex() or policy['target']!=installed['target_sha256'] or policy['generation']!=counter:raise ValueError('installed owner/target/next generation receiver binding required')
 # Secrets first touched here, after all source, VM and current-world checks.
 private=engine.load_private(private_path)
 if private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)!=public:raise ValueError('owner key mismatch')
 packet=engine.pack(payload,private=private,target=bytes.fromhex(installed['target_sha256']),
  base_runtime=bytes.fromhex(state['engine']['payload_sha256']),world=world,counter=counter)
 engine.verify(packet,target=bytes.fromhex(installed['target_sha256']),owner=public,
  base_runtime=bytes.fromhex(state['engine']['payload_sha256']),world=world,counter=state['engine']['native_counter'])
 directory=Path(tempfile.mkdtemp(prefix='pci-native-',dir=state_path.parent))
 (directory/'native.rrt').write_bytes(packet);(directory/'payload.efi').write_bytes(payload)
 flow.save(directory/'session.json',flow.bundle(packet,2,counter))
 report={'kind':'native-read-only-pci','status':'CHECKED-NOT-SENT','counter':counter,
  'base_runtime_sha256':state['engine']['payload_sha256'],'base_world_sha256':state['world_sha256'],
  'world_package_sha256':state['package_sha256'],'payload_sha256':flow.sha(payload),'package_sha256':flow.sha(packet),
  'session_sha256':flow.sha((directory/'session.json').read_bytes()),'checked_directory':str(checked),'gate':gate,
  'sender_steps':[],'receiver_reported_applied':False}
 flow.save(directory/'report.json',report);state['native_pending']=str(directory);flow.save(state_path,state)
 return directory
def deliver(state_path,state,private_path):
 directory=Path(state['native_pending']);report=flow.read_json(directory/'report.json')
 payload=(directory/'payload.efi').read_bytes();packet=(directory/'native.rrt').read_bytes()
 world=Path(state['package']).read_bytes();session=flow.validate_session(flow.read_json(directory/'session.json'))
 installed=engine.gate_check(Path(state['engine']['installed_gate']))
 if (report['kind']!='native-read-only-pci' or gates(Path(report['checked_directory']),payload,world)!=report['gate']
  or flow.sha((directory/'session.json').read_bytes())!=report['session_sha256'] or session['kind']!=2
  or session['counter']!=report['counter'] or report['counter']!=state['engine']['native_counter']+1
  or base64.b64decode(session['stream_base64'])[32:]!=packet or flow.sha(packet)!=report['package_sha256']
  or flow.sha(payload)!=report['payload_sha256'] or state['engine']['payload_sha256']!=report['base_runtime_sha256']
  or state['world_sha256']!=report['base_world_sha256'] or state['package_sha256']!=report['world_package_sha256']):
  raise ValueError('source/session/base binding changed; no radio')
 verified=engine.verify(packet,target=bytes.fromhex(installed['target_sha256']),owner=private_path.with_suffix('.pub').read_bytes(),
  base_runtime=bytes.fromhex(state['engine']['payload_sha256']),world=world,counter=state['engine']['native_counter'])
 if verified.payload!=payload:raise ValueError('signed payload differs')
 flow.current(state)
 def applied():
  report.update(status='EXACT-APPLIED-RECEIPT',receiver_reported_applied=True);flow.save(directory/'report.json',report)
  state['engine'].update(native_counter=report['counter'],payload_sha256=report['payload_sha256'],
   last_release_report=str(directory/'report.json'),diagnostic_profile=report['gate']['profile_status'],
   basis='exact correlated applied receipt; PCI telemetry and physical scene observation separate')
  state['native_pending']=None;flow.save(state_path,state);return 0
 result=flow.deliver_session(directory,report,session,applied)
 if result==2:
  state['engine']['native_counter']=report['counter'];state['native_pending']=None;flow.save(state_path,state)
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','deliver'));p.add_argument('--state',type=Path,required=True)
 p.add_argument('--checked',type=Path);p.add_argument('--private',type=Path,required=True);a=p.parse_args()
 with flow.state_lock(a.state):
  state=flow.read_json(a.state)
  if a.action=='prepare':print(prepare(a.state,state,a.checked,a.private));return 0
  return deliver(a.state,state,a.private)
if __name__=='__main__':raise SystemExit(main())
