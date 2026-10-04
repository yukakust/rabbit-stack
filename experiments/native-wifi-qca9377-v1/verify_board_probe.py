#!/usr/bin/env python3
"""Actual init/board-query entrypoints; synthetic hardware, no owner key."""
import hashlib,json,os,subprocess
import board_build as build
from board_fixture import fixture
import verify_setup_probe as prior
ROOT=build.ROOT
CASES=prior.CASES+tuple(range(500,508))
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 paths=sorted(p for p in ROOT.iterdir() if p.suffix in ('.c','.h','.py','.json'));inputs={p.name:sha(p.read_bytes()) for p in paths}
 out=ROOT/'runs/full-read-probe-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 (out/'fixture.c').write_text(fixture((ROOT/'init_probe_test.c').read_text()))
 inc=['-I'+str(p) for p in (out,ROOT,build.actors.OLD,build.actors.NATIVE)]
 files=prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','bmi_loader.c','board_query.c','board_smbios.c')
 exe=out/'board-test';subprocess.run(['gcc','-DQCA_CONFIG_SETUP=1','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.actors.NATIVE/'sha256.c'),'-o',str(exe)],check=True)
 log=''
 for scenario in CASES:
  r=subprocess.run([str(exe),str(scenario)],capture_output=True,text=True,timeout=45,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  if r.returncode:raise RuntimeError(f'board scenario{scenario}: {r.stdout[-2000:]}\n{r.stderr[-4000:]}')
  log+=r.stdout+r.stderr
 (out/'host.log').write_text(log)
 assert inputs=={p.name:sha(p.read_bytes()) for p in paths}
 dependencies=['experiments/x86-64-uefi-wireless-supervisor-v1/scene_abi.h','experiments/x86-64-uefi-runtime-supervisor-v1/abi.h']
 report={'status':'NATIVE-FULL-CHANNEL-CONFIG-SETUP-BMI-PROBE-HOST-PASS','scenarios':len(CASES),'scenario_ids':CASES,'host_log_sha256':sha(log.encode()),'native_entrypoints_integrated':True,'cold_reset_clears_ce_fixture':True,'slow_cooperative_poll_fixture':True,'full_channel_ce7_read':True,'active_dma_guard':True,'completion_before_timeout':True,'full_channel_config_read':True,'config_write_readback':True,'config_done_last':True,'cpu_wake_and_bmi':True,'board_query_integrated':True,'exact_helper_bytes_fixture':True,'helper_timeout_cancel_cleanup':True,'build_host':'yukabox','physical_verified':False,'target_ram_writes':True,'firmware_uploaded':False,'wifi_association':False,'source_sha256':inputs,'dependency_sha256':{n:sha((ROOT.parent.parent/n).read_bytes()) for n in dependencies}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('NATIVE BOARD73 + EXACT HELPER STREAM/CANCEL/CLOSE PASS')
if __name__=='__main__':main()
