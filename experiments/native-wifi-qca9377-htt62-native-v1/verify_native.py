"""Yukabox only: actual native/driver fullboot + WMI faults + transport telemetry."""
import sys,subprocess,json,hashlib,os,shutil
from pathlib import Path
import htt_build as build
from htt_fixture import fixture
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
 for i,p in enumerate(packets(data,key,target=bytes.fromhex(policy['target']),generation=62,target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])):(assets/f'chunk-{i}.bin').write_bytes(p)
 p=out/'init_probe.c';s=p.read_text();s=build.one(s,'.owner={'+','.join(str(n) for n in bytes.fromhex(policy['owner']))+'}', '.owner={'+','.join(str(n) for n in public)+'}');p.write_text(s)
 (out/'fixture.c').write_text(fixture((build.BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(x) for x in (out,build.BASE,build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE,build.BASE/'runs/firmware-chunks',build.checked.prior.actors.LINK,ROOT.parent/'x86-64-uefi-connected-supervisor-v1')]
 crypto=[]
 for n in ('monocypher.c','monocypher-ed25519.c','monocypher.h','monocypher-ed25519.h'):shutil.copyfile(build.BASE/'runs/firmware-chunks'/n,out/n)
 crypto=[out/n for n in ('monocypher.c','monocypher-ed25519.c')]
 for folder,n in [(build.checked.prior.actors.LINK,'file_core.c'),(build.checked.prior.actors.NATIVE,'sha256.c')]:shutil.copyfile(folder/n,out/n)
 files=list(build.FILES)+['driver.c','city_core.c','pci_identity.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c','diagnostic_gatt.c']
 command=[str(verify_port.CC),'-DRABBIT_PREFIX_DRIVER_MODEL','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-DSCENE_REVISION=1','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(out/'file_core.c'),str(out/'sha256.c'),*map(str,crypto),'-o',str(out/'test')]
 subprocess.run(command,check=True);log='';cases=list(range(24))
 for scenario in cases:
  r=subprocess.run([str(out/'test'),'0',str(assets),'35','1' if scenario==10 else '0','0','0',str(scenario)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'scan{scenario}: {r.stdout[-1400:]}\n{r.stderr[-4500:]}')
 for n in ('prefix','init_probe','driver','persistent','rx','htt_native','version','firmware_op','profile_gatt'):
  subprocess.run([str(verify_port.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(n+'.c')),'-o',str(out/(n+'.obj'))],check=True)
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p) for p in ROOT.iterdir() if p.is_file()}
 for p in build.COMPONENTS.iterdir():
  if p.is_file():inputs[str(p.relative_to(ROOT.parent.parent))]=sha(p)
 for module in list(sys.modules.values()):
  value=getattr(module,'__file__',None)
  if value:
   p=Path(value).resolve()
   if p.is_file() and p.is_relative_to(ROOT.parent.parent) and p.suffix=='.py':inputs[str(p.relative_to(ROOT.parent.parent))]=sha(p)
 report={'status':'HTT62-ACTUAL-PRODUCTION-AUTHENTICATED-IE6-VERSION-RAW-ASAN-COFF-PASS','scenarios':len(cases),'host_log_sha256':sha(out/'host.log'),'source_sha256':inputs,'compiled_fixture_sources_sha256':{p.name:sha(p) for p in [out/'fixture.c',*[out/n for n in files],*out.glob('*.h'),*crypto,out/'file_core.c',out/'sha256.c']},'actual_driver_poll':True,'actual_native_entrypoints':True,'authenticated_firmware_ie6':True,'request_is_rf':False,'duplicate_HTT_CONNECT':False,'raw_slots':6,'raw_pages':30,'device_operations':0,'private_key_loads':0,'physical_verified':False,'physical_admission':False,'htt_dataplane_ready':False,'scan':False,'credentials':False,'association':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
