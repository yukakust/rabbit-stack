import hashlib,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=R/'runs/host';out.mkdir(parents=True,exist_ok=True)
 sources=[R/p for p in ['auth_raw.c','pn.c','copied/rx_decode.c','copied/station.c','copied/codec/htc_wire.c']]
 flags=['-Wall','-Wextra','-Werror','-I'+str(R),'-I'+str(R/'copied/abi'),'-I'+str(R/'copied/codec')]
 command=[CC,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,*map(str,sources),str(R/'test_auth.c'),'-o',str(out/'test')]
 subprocess.run(command,check=True)
 p=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=90)
 (out/'host.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
 for s in sources:subprocess.run([CC,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(s),'-o',str(out/(s.stem+'.obj'))],check=True)
 report={'status':'HW-RAW-CLASSIFICATION-STAGED-PN-ASAN-COFF-PASS','build_host':'yukabox','checks':int(re.search(r'checks=(\d+)',p.stdout)[1]),'source_sha256':{str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and 'runs' not in p.relative_to(R).parts and '__pycache__' not in p.parts},'command':command,'compiler_sha256':sha(Path(CC)),'host_log_sha256':sha(out/'host.log'),'coff_sha256':{p.name:sha(p) for p in out.glob('*.obj')},'physical_verified':False,'native_integrated':False,'PN_original_committed':False,'controlled_port_authority':False,'official_firmware_bridge_implemented':False,'protected_quarantine_required':True}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(p.stdout.strip())
if __name__=='__main__':main()
