from pathlib import Path
import platform,subprocess,json,hashlib
assert platform.system()=='Linux','Native C only Yukabox'
R=Path(__file__).resolve().parent;O=R/'runs';O.mkdir(exist_ok=True)
C='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
f=['-std=c11','-Wall','-Wextra','-Werror','-I'+str(R)]
subprocess.run([C,*f,'-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(R/'presentation.c'),str(R/'test_presentation.c'),'-o',str(O/'test')],check=True)
a=subprocess.run([str(O/'test')],capture_output=True,text=True,check=True)
subprocess.run([C,*f,'--target=x86_64-pc-win32-coff','-Os','-ffreestanding','-fno-stack-protector','-mno-red-zone','-c',str(R/'presentation.c'),'-o',str(O/'presentation.obj')],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'ORIGINAL-CACHED-PRESENTATION-SERVICE-SYNTHETIC-ASAN-UBSAN-COFF-PASS','build_host':'yukabox','source_sha256':{p.name:sha(p) for p in [R/'presentation.c',R/'presentation.h',R/'test_presentation.c',R/'verify.py']},'result':a.stdout.strip(),'object_sha256':sha(O/'presentation.obj'),'physical_proved':False,'network_service_integrated':False};(O/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(a.stdout)
