import hashlib,json,re,subprocess
from pathlib import Path
import make_oracle
R=Path(__file__).resolve().parent
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=R/'runs/host';out.mkdir(parents=True,exist_ok=True)
 oracle=out/'original_oracle.c';oracle.write_text(make_oracle.oracle())
 sources=[R/p for p in ['pn.c','copied/rx_decode.c','copied/station.c','copied/codec/htc_wire.c']]
 flags=['-Wall','-Wextra','-Werror','-I'+str(R),'-I'+str(R/'copied/abi'),'-I'+str(R/'copied/codec')]
 subprocess.run([CC,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,*map(str,sources),str(R/'test_pn.c'),str(oracle),'-o',str(out/'test')],check=True)
 p=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=90);(out/'host.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
 for s in sources:subprocess.run([CC,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(s),'-o',str(out/(s.stem+'.obj'))],check=True)
 report={'status':'OWNED-PN-METADATA-ASAN-COFF-PASS','build_host':'yukabox','checks':int(re.search(r'checks=(\d+)',p.stdout)[1]),'source_sha256':{str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and 'runs' not in p.relative_to(R).parts and '__pycache__' not in p.parts},'original_oracle_sha256':sha(oracle),'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','host_log_sha256':sha(out/'host.log'),'coff_sha256':{p.name:sha(p) for p in out.glob('*.obj')},'physical_verified':False,'native_integrated':False,'counter_metadata_only':True,'frame_authentication_proven':False,'protected_quarantine_required':True,'rf_admission_granted':False,'credential_reads':0}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(p.stdout.strip())
if __name__=='__main__':main()
