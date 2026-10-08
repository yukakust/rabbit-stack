import hashlib,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'runs/eapol';out.mkdir(parents=True,exist_ok=True)
flags=['-Wall','-Wextra','-Werror','-I'+str(R/'copied/copied/abi'),'-I'+str(R/'copied/copied/codec')]
subprocess.run([CC,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,str(R/'eapol_wire.c'),str(R/'test_eapol.c'),'-o',str(out/'test')],check=True)
p=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
subprocess.run([CC,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-Os',*flags,'-c',str(R/'eapol_wire.c'),'-o',str(out/'eapol.obj')],check=True)
report={'status':'EAPOL-WIRE-ASAN-COFF-PASS-GLUE-PENDING','build_host':'yukabox','checks':int(re.search(r'checks=(\d+)',p.stdout)[1]),'tested_sources_sha256':{n:sha(R/n) for n in ['eapol_wire.c','eapol_wire.h','test_eapol.c','verify_eapol.py']},'primary_tx_sha256':sha(R/'references/mac80211-tx.c'),'log_sha256':sha(out/'host.log'),'coff_sha256':sha(out/'eapol.obj'),'physical_verified':False,'native_integrated':False,'direct_backend_glue_compiled':False,'protected_tx_supported':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(p.stdout.strip())
