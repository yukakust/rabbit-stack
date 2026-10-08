"""Run only on Yukabox; no device, keys, state or RF interface."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'runs/host';out.mkdir(parents=True,exist_ok=True)
 inputs=[p for p in ROOT.rglob('*') if p.is_file() and 'runs' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts]
 pins={str(p.relative_to(ROOT)):sha(p) for p in inputs}
 sources=[ROOT/'selection.c',ROOT/'live_adapter.c']+[ROOT/'copied'/n for n in ['bss_security.c','rsn_core.c','beacon_rx.c','beacon_info.c','htc_wire.c']]
 flags=['-Wall','-Wextra','-Werror','-I'+str(ROOT/'abi'),'-I'+str(ROOT/'copied')]
 subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,*map(str,sources),str(ROOT/'test_selection.c'),'-o',str(out/'test')],check=True)
 p=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=90);(out/'host.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stdout+p.stderr
 for s in sources:subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(s),'-o',str(out/(s.stem+'.obj'))],check=True)
 assert all(sha(ROOT/n)==h for n,h in pins.items())
 report={'status':'OWNED-WMI-BSS-SELECTION-ASAN-UBSAN-COFF-PASS','build_host':'yukabox','checks':int(re.search(r'checks=(\d+)',p.stdout)[1]),'source_sha256':pins,'compiler_sha256':sha(CC),'host_log_sha256':sha(out/'host.log'),'executable_sha256':sha(out/'test'),'coff_sha256':{p.name:sha(p) for p in out.glob('*.obj')},'native_integrated':False,'native_capabilities_currently_proven':False,'physical_verified':False,'rf_admission_granted':False,'credential_reads':0,'association_authority':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(p.stdout.strip());print(report['status'])
if __name__=='__main__':main()
