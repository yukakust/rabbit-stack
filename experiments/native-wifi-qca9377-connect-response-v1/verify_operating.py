#!/usr/bin/env python3
"""Actual native entrypoints and CE DMA protocol with explicit simulated target."""
import hashlib,json,os,subprocess
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
import operating_build as build
from operating_fixture import fixture
from firmware_chunk_format import packets
import verify_setup_probe as prior
from verify_port import CC
ROOT=build.ROOT;BASE=build.BASE
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 paths=list(ROOT.glob('*'))+[build.SESSION/n for n in build.PROTOCOL]
 paths=[p for p in paths if p.is_file()]
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in paths}
 out=ROOT/'runs/operating-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();p=build.policy();assert sha(data)==p['digest']
 key=Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
 for i,packet in enumerate(packets(data,key,target=bytes.fromhex(p['target']),generation=p['generation'],target_type=p['type'],target_version=p['version'],kind=p['kind'])):(assets/f'chunk-{i}.bin').write_bytes(packet)
 native=out/'init_probe.c';s=native.read_text();old='.owner={'+','.join(str(n) for n in bytes.fromhex(p['owner']))+'}';new='.owner={'+','.join(str(n) for n in public)+'}';assert s.count(old)==1;native.write_text(s.replace(old,new))
 (out/'fixture.c').write_text(fixture((BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(n) for n in (out,BASE,build.prior.actors.OLD,build.prior.actors.NATIVE,BASE/'runs/firmware-chunks')]
 files=prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','operating.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c')
 crypto=[BASE/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')]
 exe=out/'operating-test'
 subprocess.run([str(CC),'-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(exe)],check=True)
 log=''
 for scenario in range(27):
  r=subprocess.run([str(exe),'0',str(assets),str(scenario)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr
  (out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'operating scenario{scenario}: {r.stdout[-1500:]}\n{r.stderr[-4000:]}')
 for name in ('operating','init_probe'):
  subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 assert inputs=={n:sha((ROOT.parent.parent/n).read_bytes()) for n in inputs}
 report={'status':'NATIVE-OPERATING-CE-HANDSHAKE-SERVICE-READY-ASAN-COFF-PASS','scenarios':27,'build_host':'yukabox','source_sha256':inputs,'derived_fixture_sha256':sha((out/'fixture.c').read_bytes()),'derived_probe_fixture_owner_sha256':sha((out/'init_probe.c').read_bytes()),'host_log_sha256':sha(log.encode()),'actual_native_entrypoints':True,'fixture_owner_override_only':True,'physical_verified':False,'physical_signing_admitted':False,'bounded_trial_teardown':True,'persistent_operating_radio':False,'scan':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
