#!/usr/bin/env python3
"""Actual native entrypoints and CE DMA protocol with explicit simulated target."""
import hashlib,json,os,subprocess
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
import startup_build as build
from startup_fixture import fixture
from firmware_chunk_format import packets
import verify_setup_probe as prior
from verify_port import CC
ROOT=build.ROOT;BASE=build.BASE
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 paths=[p for folder,names in build.EXTRA_FILES.items() for p in folder.iterdir() if p.is_file()]+[build.LAYOUT/n for n in ('operating.c','operating.h','wmi_boot_info.c','htc_wire.c','operating_fixture.py','operating_build.py')]+[build.AVAILABLE/n for n in ('available.c','available.h','verify_available.py')]+list(ROOT.glob('*'))+[build.SESSION/n for n in build.layout.PROTOCOL]
 paths=[p for p in paths if p.is_file()]
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in paths}
 reference=Path('/home/yuka/rabbit-world/wmi-init-next/reference/pci.c');assert sha(reference.read_bytes())=='e5c8f5aec5312eb83bef7372706cdb7c979fcf81e423bb4fced3f18591e994fd'
 upstream=reference.read_text().split('static const struct ce_service_to_pipe pci_target_service_to_ce_map_wlan[] = {',1)[1].split('\n};',1)[0]
 import re
 routes=re.findall(r'__cpu_to_le32\(ATH10K_HTC_SVC_ID_WMI_CONTROL\),\s*__cpu_to_le32\(PIPEDIR_(OUT|IN)\).*?__cpu_to_le32\((\d+)\)',upstream,re.S)
 assert routes==[('OUT','3'),('IN','2')]
 out=ROOT/'runs/operating-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();p=build.policy();assert sha(data)==p['digest']
 key=Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
 for i,packet in enumerate(packets(data,key,target=bytes.fromhex(p['target']),generation=p['generation'],target_type=p['type'],target_version=p['version'],kind=p['kind'])):(assets/f'chunk-{i}.bin').write_bytes(packet)
 native=out/'init_probe.c';s=native.read_text();old='.owner={'+','.join(str(n) for n in bytes.fromhex(p['owner']))+'}';new='.owner={'+','.join(str(n) for n in public)+'}';assert s.count(old)==1;native.write_text(s.replace(old,new))
 (out/'fixture.c').write_text(fixture((BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(n) for n in (out,BASE,build.prior.actors.OLD,build.prior.actors.NATIVE,BASE/'runs/firmware-chunks')]
 files=prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','operating.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c')
 crypto=[BASE/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')]
 exe=out/'operating-test'
 subprocess.run([str(CC),'-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(exe)],check=True)
 log=''
 for scenario in range(22):
  r=subprocess.run([str(exe),'0',str(assets),'35',str(scenario)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr
  (out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'operating scenario{scenario}: {r.stdout[-1500:]}\n{r.stderr[-4000:]}')
 # Same actual model MUST reject the old CE0 transport despite valid wire.
 bad=(out/'startup.c').read_text().replace('a->bus.engines[3],0','a->bus.engines[0],0').replace('a->channels.rings[3]','a->channels.rings[0]').replace('a->channels.buffers[7]','a->channels.buffers[1]')
 (out/'startup-bad-route.c').write_text(bad)
 badexe=out/'bad-route-test';badfiles=[str(out/('startup-bad-route.c' if n=='startup.c' else n)) for n in files]
 subprocess.run([str(CC),'-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*badfiles,str(build.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(badexe)],check=True)
 badrun=subprocess.run([str(badexe),'0',str(assets),'35','0'],capture_output=True,text=True,timeout=90)
 assert badrun.returncode and 'WMI INIT incorrectly sent on CE0' in badrun.stderr
 log+=badrun.stdout+badrun.stderr; (out/'host.log').write_text(log)
 for name in ('startup','startup_gatt','init_probe'):
  subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 assert inputs=={n:sha((ROOT.parent.parent/n).read_bytes()) for n in inputs}
 report={'status':'NATIVE-WMI-INIT-DMA-READY-OWNER-RELEASE-ASAN-COFF-PASS','scenarios':22,'build_host':'yukabox','source_sha256':inputs,'derived_fixture_sha256':sha((out/'fixture.c').read_bytes()),'derived_probe_fixture_owner_sha256':sha((out/'init_probe.c').read_bytes()),'host_log_sha256':sha(log.encode()),'actual_native_entrypoints':True,'fixture_owner_override_only':True,'physical_verified':False,'physical_signing_admitted':False,'bounded_trial_teardown':True,'memory_requests_supported':0,'wmi_init_candidate':True,'station_profile_admitted':False,'new_dma_allocations':False,'ce3_route_pinned':True,'old_ce0_route_rejected':True,'pci_reference_sha256':sha(reference.read_bytes()),'persistent_operating_radio':False,'scan':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
