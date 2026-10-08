from pathlib import Path
import subprocess,os,json,hashlib,struct
R=Path(__file__).resolve().parent;U=R/'vendor';O=R/'runs/checked';O.mkdir(exist_ok=True)
os.environ['TMPDIR']=str(O)
C='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
files=['core/init.c','core/def.c','core/ip.c','core/inet_chksum.c','core/mem.c','core/memp.c','core/netif.c','core/pbuf.c','core/timeouts.c','core/udp.c','core/ipv4/dhcp.c','core/ipv4/acd.c','core/ipv4/etharp.c','core/ipv4/ip4.c','core/ipv4/ip4_addr.c','netif/ethernet.c']
sources=[U/'src'/f for f in files]+[R/'network.c']
flags=['-std=c11','-Wall','-Wextra','-Werror','-I'+str(R/'include'),'-I'+str(U/'src/include')]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(R)):sha(p) for p in [*sources,R/'fixture.c',R/'network.h',R/'include/lwipopts.h',R/'include/arch/cc.h',*sorted((R/'freestanding').glob('*.h')),*sorted((U/'src/include').rglob('*.h'))]}
def run(a):subprocess.run(a,check=True)
run([C,*flags,'-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',*[str(p) for p in sources],str(R/'fixture.c'),'-o',str(O/'fixture')])
result=subprocess.run([str(O/'fixture')],check=True,text=True,capture_output=True);(O/'host.log').write_text(result.stdout+result.stderr)
run([C,*flags,'-O1','-g','-fsanitize=address,undefined','-DWRONG_SERVER_ONLY',*[str(x) for x in sources],str(R/'fixture.c'),'-o',str(O/'server-gap')])
gap=subprocess.run([str(O/'server-gap')],check=True,text=True,capture_output=True);(O/'server-gap.log').write_text(gap.stdout+gap.stderr)
for i,p in enumerate(sources):run([C,*flags,'-I'+str(R/'freestanding'),'--target=x86_64-pc-win32-coff','-ffreestanding','-fshort-wchar','-mno-red-zone','-fno-stack-protector','-Os','-c',str(p),'-o',str(O/f'{i}.obj')])

assert inputs=={name:sha(R/name) for name in inputs}
section_bytes={};objects={}
for i in range(len(sources)):
 f=O/f'{i}.obj';objects[f.name]=sha(f);raw=f.read_bytes();count=struct.unpack_from('<H',raw,2)[0];off=20+struct.unpack_from('<H',raw,16)[0]
 for j in range(count):
  h=raw[off+40*j:off+40*(j+1)];name=h[:8].rstrip(b'\0').decode();n=struct.unpack_from('<I',h,16)[0];section_bytes[name]=section_bytes.get(name,0)+n
report={'status':'SYNTHETIC-LWIP-NOSYS-ASAN-COFF-PASS','build_host':'yukabox','upstream_commit':'0a0452b2c39bdd91e252aef045c115f88f6ca773','source_sha256':inputs,'host_result':result.stdout.strip(),'host_log_sha256':sha(O/'host.log'),'coff_object_bytes':sum((O/f'{i}.obj').stat().st_size for i in range(len(sources))),'coff_section_bytes':section_bytes,'coff_object_sha256':objects,'compiler_sha256':sha(Path(C)),'native_efi_mapped_measurement':None,'physical_wifi':False,'physical_IP':False,'signing_admitted':False,'ACK_server_id_gap':gap.stdout.strip(),'ACK_server_id_gap_log_sha256':sha(O/'server-gap.log'),'key_loads':0,'actual_network_traffic':False}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.stdout);print(report['coff_object_bytes'])
