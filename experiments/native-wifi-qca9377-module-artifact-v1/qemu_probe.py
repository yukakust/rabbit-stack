from pathlib import Path
import subprocess,platform,os,json,hashlib,struct,time,shutil,sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
assert platform.system()=='Linux'
r=Path(__file__).resolve().parent;o=r/'runs/qemu';o.mkdir(parents=True,exist_ok=True);child=Path(sys.argv[1]);data=child.read_bytes();pe=struct.unpack_from('<I',data,60)[0];mapped=struct.unpack_from('<I',data,pe+24+56)[0];assert len(data)<=262144
key=Ed25519PrivateKey.from_private_bytes(bytes.fromhex('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60'));pub=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);digest=hashlib.sha256(data).digest();frames=[]
def cb(b):return '{'+','.join(map(str,b))+'}'
for off in range(0,len(data),65536):
 b=data[off:off+65536];h=b'RABMOD01'+pub+bytes([2])*32+bytes([3])*32+digest+hashlib.sha256(b).digest()+struct.pack('<QQIIIIIII',7,2,len(data),off,len(b),1,1,mapped,65536)+bytes(12);assert len(h)==224;frames.append(h+key.sign(h)+b)
text='static const ModPolicy fixture_policy={'+','.join([cb(pub),cb(bytes([2])*32),cb(bytes([3])*32),cb(digest),'7','2','1',str(len(data)),str(mapped),'1','1'])+'};\n'
for i,f in enumerate(frames):text+=f'static const uint8_t f{i}[]={cb(f)};\n'
text+='static const uint8_t*fixture_frames[]={'+','.join(f'f{i}' for i in range(len(frames)))+'};\nstatic const size_t fixture_sizes[]={'+','.join(str(len(f)) for f in frames)+'};\n#define FIXTURE_CHUNKS '+str(len(frames))+'\n';(o/'fixture.h').write_text(text)
cmd=['x86_64-w64-mingw32-gcc','-std=c11','-Os','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-ffunction-sections','-fdata-sections','-nostdlib','-I'+str(r),'-I'+str(o),*[str(r/p) for p in ['artifact.c','loader.c','qemu_parent.c','reference/sha256.c','reference/monocypher.c','reference/monocypher-ed25519.c','reference/memory_bridge.c']],'-Wl,--subsystem,10','-Wl,--entry,probe_entry','-Wl,--gc-sections','-Wl,--no-insert-timestamp','-Wl,--image-base,0','-o',str(o/'parent.efi')]
p=subprocess.run(cmd,text=True,capture_output=True,env=dict(os.environ,TMPDIR=str(o)));(o/'compile.log').write_text(json.dumps(cmd)+'\n'+p.stdout+p.stderr);assert p.returncode==0,p.stderr
# Mature frozen FAT media builder only for QEMU disk; pinned as provenance.
repo=Path('/home/yuka/rabbit-world/parallel-filter64-native-v1/source');media=repo/'experiments/x86-64-uefi-v0/build_image.py';import importlib.util
spec=importlib.util.spec_from_file_location('fixture_media',media);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);(o/'disk.img').write_bytes(m.build_image((o/'parent.efi').read_bytes()))
vars=Path('/usr/share/OVMF/OVMF_VARS_4M.fd');code=Path('/usr/share/OVMF/OVMF_CODE_4M.fd');shutil.copyfile(vars,o/'vars.fd');log=o/'debug.log';log.write_text('')
command=['qemu-system-x86_64','-machine','q35','-m','256M','-nic','none','-display','none','-debugcon','file:'+str(log),'-drive','if=pflash,format=raw,unit=0,readonly=on,file='+str(code),'-drive','if=pflash,format=raw,unit=1,file='+str(o/'vars.fd'),'-drive','file='+str(o/'disk.img')+',format=raw,snapshot=on']
with (o/'stderr.log').open('wb') as err:
 proc=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=err)
 try:
  deadline=time.monotonic()+40
  while time.monotonic()<deadline and 'MODULE CHILD QEMU PASS' not in log.read_text():
   if proc.poll() is not None:break
   time.sleep(.1)
  actual=log.read_text();assert 'MODULE CHILD QEMU PASS' in actual,actual
 finally:proc.terminate();proc.wait(timeout=10)
report={'status':'ACTUAL-QEMU-UEFI-SIGNED-TLS-CHILD-LOAD-START-OPTIONS-UNLOAD-PASS','physical_admission':False,'qemu_only':True,'entropy_calls':0,'tls_calls':0,'private_fixture_only':'RFC8032-public-seed','child_payload_sha256':digest.hex(),'child_payload_bytes':len(data),'child_mapped_bytes':mapped,'conservative_parent_projection_mapped':2224128,'aggregate_projection':mapped+2224128,'source_sha256':{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in r.rglob('*') if p.is_file() and 'runs' not in p.parts and 'evidence' not in p.parts},'media_builder_sha256':hashlib.sha256(media.read_bytes()).hexdigest(),'ovmf_code_sha256':hashlib.sha256(code.read_bytes()).hexdigest(),'ovmf_initial_vars_sha256':hashlib.sha256(vars.read_bytes()).hexdigest(),'qemu_version':subprocess.check_output(['qemu-system-x86_64','--version'],text=True).splitlines()[0],'artifacts':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in o.iterdir() if p.is_file() and p.name!='report.json'},'command':command};(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(actual)
