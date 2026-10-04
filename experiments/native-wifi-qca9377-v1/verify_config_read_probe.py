#!/usr/bin/env python3
"""Actual full initialization/CE7 native entrypoints, fault/cleanup fixtures."""
import hashlib,json,os,subprocess
import config_read_build as build
import verify_init_probe as prior
from config_read_fixture import fixture
ROOT=build.ROOT
CASES=tuple(range(19))+tuple(range(100,111))
def main():
 if not __debug__:raise SystemExit('optimized Python forbidden')
 sha=lambda b:hashlib.sha256(b).hexdigest()
 paths=sorted(p for p in ROOT.iterdir() if p.suffix in ('.c','.h','.py','.json'))
 inputs={p.name:sha(p.read_bytes()) for p in paths}
 dependencies=['experiments/x86-64-uefi-wireless-supervisor-v1/scene_abi.h','experiments/x86-64-uefi-runtime-supervisor-v1/abi.h']
 abi_inputs={n:sha((ROOT.parent.parent/n).read_bytes()) for n in dependencies}
 out=ROOT/'runs/full-read-probe-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 (out/'fixture.c').write_text(fixture((ROOT/'init_probe_test.c').read_text()))
 inc=['-I'+str(p) for p in (out,ROOT,build.actors.OLD,build.actors.NATIVE)]
 files=prior.FILES+('full_read.c','config_read.c','diag_ce.c')
 exe=out/'test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],'-o',str(exe)],check=True)
 log=''
 for scenario in CASES:
  r=subprocess.run([str(exe),str(scenario)],capture_output=True,text=True,timeout=30,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  if r.returncode:raise RuntimeError(f'full read scenario{scenario}: {r.stdout[-2000:]}\n{r.stderr}')
  log+=r.stdout+r.stderr
 (out/'host.log').write_text(log)
 assert inputs=={p.name:sha(p.read_bytes()) for p in paths}
 assert abi_inputs=={n:sha((ROOT.parent.parent/n).read_bytes()) for n in dependencies}
 report={'status':'NATIVE-FULL-CHANNEL-CONFIG-READ-PROBE-HOST-PASS','scenarios':len(CASES),
  'scenario_ids':CASES,'host_log_sha256':sha(log.encode()),'native_entrypoints_integrated':True,
  'cold_reset_clears_ce_fixture':True,'slow_cooperative_poll_fixture':True,'full_channel_ce7_read':True,
  'active_dma_guard':True,'full_channel_config_read':True,'completion_before_timeout':True,'build_host':'yukabox',
  'physical_verified':False,'target_ram_writes':False,'firmware_uploaded':False,'wifi_association':False,
  'source_sha256':inputs,'dependency_sha256':abi_inputs}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
