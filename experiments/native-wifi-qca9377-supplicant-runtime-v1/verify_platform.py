"""Actual runtime/adapter ASAN tests, on Yukabox with fresh mature ELF objects."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'runs/platform';out.mkdir(parents=True,exist_ok=True)
 src=ROOT.parent/'reference/wpa_supplicant-2.11/src'
 flags=['-O1','-g','-fno-builtin','-DOS_NO_C_LIB_DEFINES','-DCONFIG_NO_STDOUT_DEBUG','-DCONFIG_NO_WPA_MSG','-fsanitize=address,undefined','-fno-sanitize-recover=all','-Wall','-Wextra','-Werror','-isystem',str(src),'-isystem',str(src/'utils')]
 interop=json.loads((ROOT/'runs/interop/report.json').read_text())
 assert interop['local_sources']=={n:sha(ROOT/n) for n in interop['local_sources']}
 objects=sorted((ROOT/'runs/interop/objects').glob('*.o'),key=lambda p:int(p.stem))[1:]
 for n,h in interop['object_sha256'].items():assert sha(ROOT/'runs/interop'/n)==h
 logs={};checks={}
 for name,sources in [('runtime',['runtime.c','primitives.c','runtime_test.c']),('adapter',['adapter.c','adapter_test.c'])]:
  command=[str(CC),*flags,*[str(ROOT/n) for n in sources],*([str(p) for p in objects] if name=='adapter' else []),'-Wl,--gc-sections','-o',str(out/name)]
  subprocess.run(command,check=True)
  p=subprocess.run([str(out/name)],capture_output=True,text=True,timeout=30);(out/(name+'.log')).write_text(p.stdout+p.stderr);assert not p.returncode,p.stdout+p.stderr
  logs[name]=sha(out/(name+'.log'));checks[name]=int(re.search(r'checks=(\d+)',p.stdout)[1]);print(p.stdout.strip())
 report={'status':'FREESTANDING-PLATFORM-ASAN-UBSAN-PROVIDER-TIMER-REVOKE-PASS','build_host':'yukabox','checks':checks,'host_log_sha256':logs,'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and (p.suffix in ('.c','.h','.py','.json','.md','.patch','.txt') or p.name=='.gitignore') and 'runs' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts},'interop_report_sha256':sha(ROOT/'runs/interop/report.json'),'native_admitted':False,'physical_verified':False,'credential_reads':0,'native_radio_capability':'UNKNOWN','production_providers_approved':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
