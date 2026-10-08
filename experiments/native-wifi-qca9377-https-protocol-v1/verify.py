from pathlib import Path
import subprocess,json,hashlib,platform
assert platform.system()=='Linux','Native compile only Yukabox'
R=Path(__file__).resolve().parent;O=R/'runs';O.mkdir(exist_ok=True)
C='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=['-std=c11','-Wall','-Wextra','-Werror','-I'+str(R)]
subprocess.run([C,*f,'-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(R/'probe_protocol.c'),str(R/'test_protocol.c'),'-o',str(O/'test')],check=True)
r=subprocess.run([str(O/'test')],text=True,capture_output=True,check=True)
subprocess.run([C,*f,'-I'+str(R/'freestanding'),'--target=x86_64-pc-win32-coff','-Os','-ffreestanding','-fno-stack-protector','-mno-red-zone','-c',str(R/'probe_protocol.c'),'-o',str(O/'protocol.obj')],check=True)
a={'status':'BOUNDED-SYNTHETIC-HTTP-NONCE-FRAMING-ASAN-UBSAN-COFF-PASS','build_host':'yukabox','source_sha256':{str(p.relative_to(R)):sha(p) for p in [R/'probe_protocol.c',R/'probe_protocol.h',R/'test_protocol.c',R/'verify.py',R/'freestanding/string.h']},'compiler_sha256':sha(Path(C)),'result':r.stdout.strip(),'object_sha256':sha(O/'protocol.obj'),'physical_network':False,'TLS_authenticated':False,'fresh_entropy_proved':False};(O/'report.json').write_text(json.dumps(a,indent=2)+'\n');print(r.stdout)
