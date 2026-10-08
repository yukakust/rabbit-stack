from pathlib import Path
import subprocess,hashlib,json,platform
assert platform.system()=='Linux','C/ASAN/COFF only Yukabox'
R=Path(__file__).resolve().parent;O=R/'runs';O.mkdir(exist_ok=True)
C='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=['-std=c11','-Wall','-Wextra','-Werror','-I'+str(R)]
subprocess.run([C,*f,'-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(R/'city_arena.c'),str(R/'test_arena.c'),'-o',str(O/'test')],check=True)
a=subprocess.run([str(O/'test')],capture_output=True,text=True,check=True)
subprocess.run([C,*f,'--target=x86_64-pc-win32-coff','-Os','-ffreestanding','-fno-stack-protector','-mno-red-zone','-c',str(R/'city_arena.c'),'-o',str(O/'arena.obj')],check=True)
report={'status':'SYNTHETIC-CITY-ARENA-ASAN-UBSAN-COFF-PASS','build_host':'yukabox','source_sha256':{p.name:sha(p) for p in [R/'city_arena.c',R/'city_arena.h',R/'test_arena.c',R/'verify.py']},'result':a.stdout.strip(),'compiler_sha256':sha(Path(C)),'object_sha256':sha(O/'arena.obj'),'allocation_bytes':1958415,'depth_bytes':1440000,'legacy_picture_bytes':518400,'physical_proved':False,'integrated':False};(O/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(a.stdout)
