from pathlib import Path
import os,subprocess,json,hashlib,re,struct
import derive_layout
R=Path(__file__).resolve().parent;O=R/'runs/checked';O.mkdir(parents=True,exist_ok=True);os.environ['TMPDIR']=str(O)
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
refs=derive_layout.generate(O/'oracle');oracle=O/'oracle';text=(oracle/'oracle.c').read_text();(oracle/'oracle_types.h').write_text(text[:text.index('int main(void)')])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inputs={str(p.relative_to(R)):sha(p) for p in [R/'ring.c',R/'ring.h',R/'ring_test.c',R/'derive_layout.py',R/'verify_remote.py',R/'references.json',*[R/'runs/reference'/n for n in refs['files']]]}
flags=['-std=c11','-Wall','-Wextra','-Werror','-I'+str(R),'-I'+str(oracle)]
subprocess.run([CC,*flags,str(oracle/'oracle.c'),'-o',str(oracle/'oracle')],check=True);layout=json.loads(subprocess.check_output([str(oracle/'oracle')],text=True));assert layout=={'descriptor_bytes':300,'payload_bytes':40,'ring32_bytes':36,'offsets_words':[59,75,21,31,3,20,6,10,1,2]}
subprocess.run([CC,*flags,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(R/'ring.c'),str(R/'ring_test.c'),'-o',str(O/'test')],check=True);p=subprocess.run([str(O/'test')],text=True,capture_output=True);(O/'host.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
subprocess.run([CC,*flags,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-c',str(R/'ring.c'),'-o',str(O/'ring.obj')],check=True)
assert inputs=={n:sha(R/n) for n in inputs}
raw=(O/'ring.obj').read_bytes();count=struct.unpack_from('<H',raw,2)[0];sections={}
for i in range(count):
 h=raw[20+i*40:60+i*40];sections[h[:8].rstrip(b'\0').decode()]=struct.unpack_from('<I',h,16)[0]
report={'status':'HTT-RING-DEFAULT-UPSTREAM-WIRE-OWNER-ASAN-COFF-PASS','build_host':'yukabox','checks':int(re.search(r'checks=(\d+)',p.stdout)[1]),'layout':layout,'source_sha256':inputs,'compiler_sha256':sha(Path(CC)),'oracle_source_sha256':sha(oracle/'oracle.c'),'rx_desc_header_sha256':sha(oracle/'rx_desc.h'),'coff_sha256':sha(O/'ring.obj'),'coff_sections':sections,'host_log_sha256':sha(O/'host.log'),'proposed_extra_HTT_maps':33,'proposed_total_with_CE':47,'allocated_DMA_maps':0,'physical_verified':False,'native_integrated':False,'device_operations':0,'credential_reads':0,'RX_dataplane_ready':False}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(p.stdout.strip())
