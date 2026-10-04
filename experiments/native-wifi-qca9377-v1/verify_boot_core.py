#!/usr/bin/env python3
"""Pinned official assets, bounded boot planner/transport, Yukabox only."""
import hashlib,json,os,subprocess
from pathlib import Path
from firmware_preflight import container,elements,firmware
from verify_port import CC
ROOT=Path(__file__).resolve().parent
VENDOR=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor')
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/boot-core';out.mkdir(parents=True,exist_ok=True)
 files=tuple(sorted(p.name for p in ROOT.iterdir() if p.suffix in ('.c','.h','.py','.json')))
 inputs={n:sha((ROOT/n).read_bytes()) for n in files}
 policy=json.loads((ROOT/'boot-reference-policy.json').read_text())
 refs=VENDOR/'linux/drivers/net/wireless/ath/ath10k'
 for name,expected in policy['reference_sha256'].items():assert sha((refs/name).read_bytes())==expected,name
 blob=(VENDOR/'firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes()
 info=firmware(blob)
 assert info['container_sha256']=='8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01' and not info['code_swap_present']
 images=dict(container(blob,b'QCA-ATH10K'))
 catalog=(VENDOR/'firmware/ath10k/QCA9377/hw1.0/board-2.bin').read_bytes()
 assert sha(catalog)=='0fdcc7838f478da81704de88f7b33e28862110c6d5decf7818543f8e37e6cd98'
 name=b'bus=pci,vendor=168c,device=0042,subsystem-vendor=1028,subsystem-device=1810'
 matches=[]
 for kind,body in container(catalog,b'QCA-ATH10K-BOARD'):
  items=elements(body)
  if kind==0 and (0,name) in items:matches.extend(data for tag,data in items if tag==1)
 assert len(matches)==1 and len(matches[0])==8124 and sha(matches[0])=='b2713b77c725b0ff81af75c85c3aeba97885d0f40174f715b1e39d5a9d50f4e7'
 assets=(out/'board.bin',out/'helper.bin',out/'main.bin')
 for path,data in zip(assets,(matches[0],images[4],images[3])):path.write_bytes(data)
 (out/'container.bin').write_bytes(blob)
 native=ROOT.parent/'x86-64-uefi-runtime-supervisor-v1'
 import board_build
 provenance=json.loads((board_build.actors.engine.old.V1/'crypto-provenance.json').read_text())
 crypto=ROOT/'runs/board-profile'
 for name,expected in provenance['files'].items():assert sha((crypto/Path(name).name).read_bytes())==expected,name
 inc=['-I'+str(p) for p in (ROOT,ROOT.parent/'x86-64-uefi-wireless-supervisor-v1',native)]
 log=''
 for name,names,cases,args in (
  ('boot-image',('boot_image.c','boot_image_test.c'),range(14),[str(p) for p in assets]),
  ('boot-transport',('boot_transport.c','boot_image.c','boot_transport_test.c','bmi_transport.c','rom_ready.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','boot_irq.c','power_core.c','pci_identity.c'),range(10),[]),
  ('boot-native',('boot_native.c','boot_image.c','boot_native_test.c','firmware_chunks.c'),range(18),[str(out/'container.bin'),str(out/'board.bin')])):
  exe=out/name
  extra=['-I'+str(crypto),str(crypto/'monocypher.c'),str(crypto/'monocypher-ed25519.c')] if name=='boot-native' else []
  subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,*extra,*[str(ROOT/n) for n in names],str(native/'sha256.c'),'-o',str(exe)],check=True)
  for i in cases:
   r=subprocess.run([str(exe),*args,str(i)],capture_output=True,text=True,timeout=45,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'});log+=r.stdout+r.stderr
   if r.returncode:
    (out/'failure.log').write_text(log)
    raise RuntimeError(f'{name} scenario{i}: {r.stdout[-1000:]}\n{r.stderr[-4000:]}')
 for name in ('boot_image','boot_transport','boot_native'):
  subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*inc,'-c',str(ROOT/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 assert inputs=={n:sha((ROOT/n).read_bytes()) for n in files}
 (out/'host.log').write_text(log)
 dependencies={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in (native/'sha256.c',native/'sha256.h',ROOT.parent/'x86-64-uefi-wireless-supervisor-v1/scene_abi.h',native/'abi.h')}
 report={'status':'EXACT-BOARD-CALIBRATION-MAIN-BMI-BOOT-CORE-HOST-COFF-PASS','source_sha256':inputs,'dependency_sha256':dependencies,'crypto_provenance':provenance,'reference_policy':policy,'assets':{p.name:sha(p.read_bytes()) for p in assets},'firmware':info,'catalog_sha256':sha(catalog),'scenarios':42,'host_log_sha256':sha(log.encode()),'build_host':'yukabox','physical_verified':False,'integrated_native_profile':False,'htc_ready':False,'wifi_connected':False,'permanent_programming':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
