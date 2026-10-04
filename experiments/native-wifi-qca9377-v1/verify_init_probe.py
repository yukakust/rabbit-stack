#!/usr/bin/env python3
"""Exact native entrypoint/PCI fixture gate; no physical probe or signing."""
import hashlib,json,os,subprocess
from pathlib import Path
import init_build as build
ROOT=build.ROOT
FILES=('init_probe.c','init_adapter.c','boot_irq_mapped.c','channels_core.c','warm_core.c',
       'reset_core.c','rom_ready.c','boot_irq.c','pcie_link.c','uefi_port.c','wake_core.c',
       'pci_identity.c','power_core.c','ce_bus.c','ce_hw.c','ce_ring.c','ce_uefi.c','dma_buffer.c')
def main():
 if not __debug__:raise SystemExit('optimized Python is forbidden')
 sha=lambda b:hashlib.sha256(b).hexdigest()
 paths=sorted(p for p in ROOT.iterdir() if p.suffix in ('.c','.h','.py','.json'))
 inputs={p.name:sha(p.read_bytes()) for p in paths}
 dependencies=['experiments/x86-64-uefi-wireless-supervisor-v1/scene_abi.h','experiments/x86-64-uefi-runtime-supervisor-v1/abi.h']
 abi_inputs={n:sha((ROOT.parent.parent/n).read_bytes()) for n in dependencies}
 out=ROOT/'runs/init-probe-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 inc=['-I'+str(p) for p in (out,ROOT,build.actors.OLD,build.actors.NATIVE)]
 exe=out/'test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,
  str(ROOT/'init_probe_test.c'),*[str(out/n) for n in FILES],'-o',str(exe)],check=True)
 log=''
 for scenario in range(19):
  run=subprocess.run([str(exe),str(scenario)],capture_output=True,text=True,timeout=30,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  if run.returncode:raise RuntimeError(f'native probe scenario {scenario}: {run.stdout[-1000:]}\n{run.stderr}')
  log+=run.stdout+run.stderr
 (out/'host.log').write_text(log)
 assert inputs=={p.name:sha(p.read_bytes()) for p in paths},'native probe inputs changed'
 assert abi_inputs=={n:sha((ROOT.parent.parent/n).read_bytes()) for n in dependencies},'native probe ABI changed'
 report={'status':'NATIVE-WARM-FULL-CHANNEL-PROBE-ENTRYPOINT-HOST-PASS','scenarios':19,
  'host_log_sha256':sha(log.encode()),'native_entrypoints_integrated':True,'slow_cooperative_poll_fixture':True,'cold_reset_clears_ce_fixture':True,'build_host':'yukabox',
  'physical_warm_reset':False,'target_ram_writes':False,'firmware_uploaded':False,'wifi_association':False,
  'source_sha256':inputs,'dependency_sha256':abi_inputs}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
