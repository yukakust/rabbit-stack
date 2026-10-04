#!/usr/bin/env python3
"""Actual entrypoints plus full signed RAM fixture, never owner signing."""
import hashlib,json,os,subprocess
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
import boot_build as build
from boot_fixture import fixture
from firmware_chunk_format import packets
import verify_setup_probe as prior
ROOT=build.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 paths=sorted(p for p in ROOT.iterdir() if p.suffix in ('.c','.h','.py','.json'));inputs={p.name:sha(p.read_bytes()) for p in paths}
 out=ROOT/'runs/boot-two-lifetime-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();p=build.policy();assert sha(data)==p['digest']
 key=Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
 for i,packet in enumerate(packets(data,key,target=bytes.fromhex(p['target']),generation=p['generation'],target_type=p['type'],target_version=p['version'],kind=p['kind'])):(assets/f'chunk-{i}.bin').write_bytes(packet)
 native=out/'init_probe.c';s=native.read_text();old='.owner={'+','.join(str(n) for n in bytes.fromhex(p['owner']))+'}';new='.owner={'+','.join(str(n) for n in public)+'}';assert s.count(old)==1;native.write_text(s.replace(old,new))
 (out/'fixture.c').write_text(fixture((ROOT/'init_probe_test.c').read_text()))
 inc=['-I'+str(n) for n in (out,ROOT,build.actors.OLD,build.actors.NATIVE,ROOT/'runs/firmware-chunks')]
 files=prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c')
 crypto=[ROOT/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')]
 exe=out/'boot-test';subprocess.run(['gcc','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(exe)],check=True)
 log=''
 for scenario in range(8):
  r=subprocess.run([str(exe),"0",str(assets),str(scenario)],capture_output=True,text=True,timeout=60,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  if r.returncode:raise RuntimeError(f'receiver scenario{scenario}: {r.stdout[-1500:]}\n{r.stderr[-4000:]}')
  log+=r.stdout+r.stderr
 (out/'host.log').write_text(log)
 assert inputs=={p.name:sha(p.read_bytes()) for p in paths}
 dependencies=['experiments/x86-64-uefi-wireless-supervisor-v1/scene_abi.h','experiments/x86-64-uefi-runtime-supervisor-v1/abi.h']
 report={'status':'NATIVE-EXACT-BOOT-TWO-LIFETIME-HOST-MOCK-PASS','scenarios':8,'scenario_ids':list(range(8)),'scenarios_description':['complete_main_ready','calibration_failure','invalid_htc','htc_timeout','null_board_pointer','board_config_overlap','cancel_calibration_stream','cancel_main_stream'],'host_log_sha256':sha(log.encode()),'native_entrypoints_integrated':True,'cold_reset_clears_ce_fixture':True,'slow_cooperative_poll_fixture':True,'full_channel_ce7_read':True,'active_dma_guard':True,'full_channel_config_read':True,'config_write_readback':True,'config_done_last':True,'cpu_wake_and_bmi':True,'completion_before_timeout':True,'boot_receiver_first_lifetime':True,'second_lifetime_verified':True,'signed_ram_receiver_integrated':True,'full_asset_fixture':True,'pinned_unload_retained':True,'fixture_owner_override_only':True,'build_host':'yukabox','physical_verified':False,'target_ram_writes':True,'firmware_uploaded':True,'wifi_association':False,'source_sha256':inputs,'dependency_sha256':{n:sha((ROOT.parent.parent/n).read_bytes()) for n in dependencies}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('BOOT TWO LIFETIME8 HOST MOCK PASS')
if __name__=='__main__':main()
