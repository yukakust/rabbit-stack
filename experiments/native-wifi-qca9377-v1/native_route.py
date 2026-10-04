"""Exact PCI diagnostic delivery; Yukabox gates precede local owner signing."""
import argparse,base64,tempfile
from pathlib import Path
import diagnostic_build as build
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
engine=build.actors.engine
flow=engine.flow
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
def gates(directory,payload,world):
 report=flow.read_json(directory/'report.json')
 reproduction=flow.read_json(directory/'reproduction.json',8*1024*1024)
 if report['status'] not in ('READ-ONLY-PCI-CITY-PROFILE-GATES-PASS','REVERSIBLE-PCI-WAKE-CITY-PROFILE-GATES-PASS','READ-ONLY-PCI-POWER-CITY-PROFILE-GATES-PASS','REVERSIBLE-PCI-RESET-CITY-PROFILE-GATES-PASS','QCA-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-BOOTIRQ-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS') or report['payload_sha256']!=flow.sha(payload):
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
 if report['status'] in ('REVERSIBLE-PCI-WAKE-CITY-PROFILE-GATES-PASS','REVERSIBLE-PCI-RESET-CITY-PROFILE-GATES-PASS','QCA-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-BOOTIRQ-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS'):
  port=flow.read_json(directory/'port-report.json')
  if (port['status']!='INITIAL-UEFI-PCI-WAKE-PORT-HOST-MOCK-AND-COFF-ABI-PASS'
   or flow.sha((directory/'port-report.json').read_bytes())!=report['port_report_sha256']
   or flow.sha((directory/'port-host.log').read_bytes())!=port['host_log_sha256']):raise ValueError('exact port gates required')
  for name,expected in port['source_sha256'].items():
   if reproduction['inputs'].get('experiments/native-wifi-qca9377-v1/'+name)!=expected:raise ValueError('port gate sources changed')
 if report['status'] in ('REVERSIBLE-PCI-RESET-CITY-PROFILE-GATES-PASS','QCA-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','QCA-BOOTIRQ-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS'):
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
  for component,status in components:
   subreport=flow.read_json(directory/(component+'-report.json'))
   if (subreport['status']!=status or flow.sha((directory/(component+'-report.json')).read_bytes())!=report[component+'_report_sha256']
    or flow.sha((directory/(component+'-host.log')).read_bytes())!=subreport['host_log_sha256']):raise ValueError('component gate mismatch: '+component)
   for name,expected in subreport['source_sha256'].items():
    if reproduction['inputs'].get('experiments/native-wifi-qca9377-v1/'+name)!=expected:raise ValueError('component sources changed: '+name)
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
 if state['pending'] or state.get('native_pending') or state.get('recovery_pending'):raise ValueError('pending operation exists')
 flow.current(state);installed=engine.gate_check(Path(state['engine']['installed_gate']))
 if flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256']:raise ValueError('installed gate changed')
 world=Path(state['package']).read_bytes();payload=(checked/'payload.efi').read_bytes();gate=gates(checked,payload,world)
 public=private_path.with_suffix('.pub').read_bytes()
 if flow.sha(public)!=installed['owner_public_sha256']:raise ValueError('owner identity differs')
 counter=state['engine']['native_counter']+1
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
