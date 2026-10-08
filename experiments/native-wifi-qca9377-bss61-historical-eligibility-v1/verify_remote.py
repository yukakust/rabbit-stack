from pathlib import Path
import os,subprocess,hashlib,json,re,struct
R=Path(__file__).resolve().parent;O=R/'runs/checked';O.mkdir(parents=True,exist_ok=True);os.environ['TMPDIR']=str(O)
C='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=[R/'historical.c',*[R/'copied'/n for n in ('bss_security.c','rsn_core.c','beacon_rx.c','beacon_info.c')]]
inputs={str(p.relative_to(R)):sha(p) for p in [*sources,*sorted((R/'copied').glob('*.h')),R/'historical.h',R/'historical_test.c',R/'verify_remote.py',R/'copied-pin.json']}
flags=['-Wall','-Wextra','-Werror','-I'+str(R),'-I'+str(R/'copied')]
subprocess.run([C,*flags,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*[str(p) for p in sources],str(R/'historical_test.c'),'-o',str(O/'test')],check=True)
p=subprocess.run([str(O/'test')],capture_output=True,text=True);(O/'host.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
sections={};objects={}
for i,src in enumerate(sources):
 dst=O/f'{i}.obj';subprocess.run([C,*flags,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-c',str(src),'-o',str(dst)],check=True);objects[dst.name]=sha(dst);raw=dst.read_bytes();count=struct.unpack_from('<H',raw,2)[0]
 for j in range(count):
  h=raw[20+j*40:60+j*40];name=h[:8].rstrip(b'\0').decode();sections[name]=sections.get(name,0)+struct.unpack_from('<I',h,16)[0]
assert inputs=={n:sha(R/n) for n in inputs}
r={'status':'HISTORICAL61-COPIED-MATURE-GRAMMAR-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',p.stdout)[1]),'build_host':'yukabox','source_sha256':inputs,'coff_object_sha256':objects,'coff_sections':sections,'compiler_sha256':sha(Path(C)),'host_log_sha256':sha(O/'host.log'),'positive_fixtures':'SYNTHETIC-NOT-PHYSICAL','physical_scan_verified':False,'native_capabilities':'UNKNOWN','fresh_live_BSS_required':True,'association_authority':False,'controlled_port_authority':False,'credential_reads':0,'native_operations':0};(O/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(p.stdout.strip())
