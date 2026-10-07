"""Yukabox only: actual native/driver fullboot + WMI faults + transport telemetry."""
import sys,subprocess,json,hashlib,os,shutil
from pathlib import Path
import fullboot_build as build
from fullboot_fixture import fixture
sys.path.insert(0,str(build.BASE))
import verify_port,verify_setup_probe,receiver_fixture
from firmware_chunk_format import packets
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
ROOT=build.ROOT;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if sys.platform!='linux':raise SystemExit('Yukabox only')
 out=ROOT/'runs/native-host';out.mkdir(parents=True,exist_ok=True);build.driver_sources(out);assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();policy=build.policy();assert hashlib.sha256(data).hexdigest()==policy['digest']
 key=Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
 for i,p in enumerate(packets(data,key,target=bytes.fromhex(policy['target']),generation=60,target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])):(assets/f'chunk-{i}.bin').write_bytes(p)
 p=out/'init_probe.c';s=p.read_text();s=build.one(s,'.owner={'+','.join(str(n) for n in bytes.fromhex(policy['owner']))+'}', '.owner={'+','.join(str(n) for n in public)+'}');p.write_text(s)
 (out/'fixture.c').write_text(fixture((build.BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(x) for x in (out,build.BASE,build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE,build.BASE/'runs/firmware-chunks',build.checked.prior.actors.LINK,ROOT.parent/'x86-64-uefi-connected-supervisor-v1')]
 crypto=[]
 for n in ('monocypher.c','monocypher-ed25519.c','monocypher.h','monocypher-ed25519.h'):shutil.copyfile(build.BASE/'runs/firmware-chunks'/n,out/n)
 crypto=[out/n for n in ('monocypher.c','monocypher-ed25519.c')]
 for folder,n in [(build.checked.prior.actors.LINK,'file_core.c'),(build.checked.prior.actors.NATIVE,'sha256.c')]:shutil.copyfile(folder/n,out/n)
 files=list(build.FILES)+['driver.c','city_core.c','pci_identity.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c','diagnostic_gatt.c']
 command=[str(verify_port.CC),'-DRABBIT_PREFIX_DRIVER_MODEL','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-DSCENE_REVISION=1','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(out/'file_core.c'),str(out/'sha256.c'),*map(str,crypto),'-o',str(out/'test')]
 subprocess.run(command,check=True);log='';cases=[(35,s,0) for s in range(23)]+[(35,0,d) for d in (1,2,3,4,5,6,7,9)]+[(b,0,0) for b in range(1,8)]
 for boot,startup,diag in cases:
  r=subprocess.run([str(out/'test'),'0',str(assets),str(boot),str(startup),str(ROOT/'runs/world19.rup'),str(diag)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'boot{boot}/startup{startup}/diag{diag}: {r.stdout[-1000:]}\n{r.stderr[-3500:]}')
 initial_source=receiver_fixture.fixture((build.BASE/'init_probe_test.c').read_text())
 (out/'initial-fixture.c').write_text(initial_source+'\nvoid qca_collect(SystemTable*s){(void)s;}\n')
 initial_command=command.copy();initial_command[initial_command.index(str(out/'fixture.c'))]=str(out/'initial-fixture.c');initial_command[-1]=str(out/'initial-test')
 subprocess.run(initial_command,check=True)
 for initial in verify_setup_probe.CASES:
  r=subprocess.run([str(out/'initial-test'),str(initial),str(assets)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'initial{initial}: {r.stdout[-1000:]}\n{r.stderr[-3500:]}')
 # Reject wrong CE0 route using actual publication callbacks; no production edit.
 (out/'startup-bad-route.c').write_text((out/'startup.c').read_text().replace('a->bus.engines[3],0','a->bus.engines[0],0').replace('a->channels.rings[3]','a->channels.rings[0]').replace('a->channels.buffers[7]','a->channels.buffers[1]'))
 bad_command=command.copy();bad_command[bad_command.index(str(out/'startup.c'))]=str(out/'startup-bad-route.c');bad_command[-1]=str(out/'bad-route-test');subprocess.run(bad_command,check=True)
 bad=subprocess.run([str(out/'bad-route-test'),'0',str(assets),'35','0',str(ROOT/'runs/world19.rup'),'0'],capture_output=True,text=True,timeout=90)
 assert bad.returncode and 'WMI INIT incorrectly sent on CE0' in bad.stderr
 log+=bad.stdout+bad.stderr;(out/'host.log').write_text(log)
 for n in ('prefix','prefix_gatt','init_probe','driver','startup'):
  subprocess.run([str(verify_port.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(n+'.c')),'-o',str(out/(n+'.obj'))],check=True)
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p) for p in ROOT.iterdir() if p.is_file()}
 for module in list(sys.modules.values()):
  value=getattr(module,'__file__',None)
  if value:
   p=Path(value).resolve()
   if p.is_file() and p.is_relative_to(ROOT.parent.parent) and p.suffix=='.py':inputs[str(p.relative_to(ROOT.parent.parent))]=sha(p)
 report={'status':'FULLBOOT60-ACTUAL-DRIVER-PCI-CE-USB-WMI-READY-ASAN-COFF-PASS','scenarios':len(cases)+len(verify_setup_probe.CASES),'fullboot_scenarios':len(cases),'initial_scenarios':len(verify_setup_probe.CASES),'old_ce0_route_rejected':True,'scenario_ids':cases,'host_log_sha256':sha(out/'host.log'),'source_sha256':inputs,'compiled_fixture_sources_sha256':{p.name:sha(p) for p in [out/'fixture.c',out/'initial-fixture.c',out/'startup-bad-route.c',*[out/n for n in files],*crypto,out/'file_core.c',out/'sha256.c']},'actual_driver_poll':True,'actual_native_PCI_CE_DMA_model':True,'actual_driver_overlay_canary_test':True,'mocked_USB_backend':True,'driver_attach_not_modelled':True,'full_authenticated_container':True,'MAIN_bytes':727128,'BMI_DONE_commands':1,'WMI_INIT_commands':1,'WMI_READY_required_before_success':True,'deadline_us':5400000000,'device_operations':0,'private_key_loads':0,'physical_verified':False,'scan':False,'wifi_connected':False,'memory_requests_supported':0}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
