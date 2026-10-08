import hashlib,json,re,subprocess
from pathlib import Path
import make_types,make_oracle
ROOT=Path(__file__).resolve().parent
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert (ROOT/'generated/primary_types.h').read_text()==make_types.types()
 out=ROOT/'runs/host';out.mkdir(parents=True,exist_ok=True);oracle=out/'oracle.c';oracle.write_text(make_oracle.oracle())
 flags=['-Wall','-Wextra','-Werror','-Wno-unused-parameter','-I'+str(ROOT),'-I'+str(ROOT/'copied/abi'),'-I'+str(ROOT/'copied/codec')]
 sources=[ROOT/n for n in ['wire.c','coordinator.c','copied/station.c','copied/codec/htc_wire.c']]
 subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,*map(str,sources),str(ROOT/'test_wire.c'),str(oracle),'-o',str(out/'test')],check=True)
 p=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=90);(out/'host.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stdout+p.stderr
 for s in sources:subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(s),'-o',str(out/(s.stem+'.obj'))],check=True)
 report={'status':'STATION-WIRE-ORIGINAL-GENERATORS-ASAN-COFF-PASS','build_host':'yukabox','checks':int(re.search(r'checks=(\d+)',p.stdout)[1]),'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and 'runs' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts},'oracle_sha256':sha(oracle),'host_log_sha256':sha(out/'host.log'),'physical_verified':False,'native_integrated':False,'native_radio_capability':'UNKNOWN','rf_admission_granted':False,'credential_reads':0,'nonzero_rx_sequence_supported':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(p.stdout.strip())
if __name__=='__main__':main()
