"""Normal/EMPTY actual OVMF world19; inherited USB is synthetic, no Dell."""
from pathlib import Path
import importlib.util,sys,tempfile,os,json,hashlib,time
import native_build as project
assert sys.platform.startswith('linux')
R=project.R;O=R/'runs/checked-candidate';tmp=Path('/home/yuka/rabbit-world/i65-qmp');tmp.mkdir(parents=True,exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
S=project.BASE;sys.path.insert(0,str(S));spec=importlib.util.spec_from_file_location('i65_inherited_world',S/'prove_filter.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
packet=(S/'runs/checked-candidate/world19.rup').read_bytes();assert g.sha(packet)==g.WORLD_PACKAGE
payload=(O/'payload.efi').read_bytes();n=json.loads((O/'report.json').read_text());assert g.sha(payload)==n['payload_sha256'];qemu=g.checked.verify_init_profile.prior.actors_gate
old_city=qemu.compile_scene;old_world=qemu.flow.compile_world;old_temp=tempfile.TemporaryDirectory
Q=O/('qemu-attempt-'+str(time.time_ns()));Q.mkdir()
def fixture(s):
 s=project.one(s,'stage(city_stream,sizeof(city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=4','stage(city_stream,sizeof(city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=19')
 s=project.one(s,'before[36]!=5||le32(before+12)!=4','before[36]!=5||le32(before+12)!=19')
 return project.one(s,'stage(restored_stream,sizeof(restored_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=5','stage(restored_stream,sizeof(restored_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=20')
def exact_city(w,c,*a,**k):assert c==4;return packet
def restore(p,c,*a,**k):return old_world(p,20 if c==5 else c,*a,**k)
def temp(*a,**k):
 if k.get('dir')=='/tmp':k['dir']=str(tmp)
 return old_temp(*a,**k)
try:
 qemu.compile_scene=exact_city;qemu.flow.compile_world=restore;tempfile.TemporaryDirectory=temp
 gates=[qemu.qemu_gate(Q,payload,test_transform=fixture),qemu.qemu_gate(Q,payload,True,test_transform=fixture)]
finally:qemu.compile_scene=old_city;qemu.flow.compile_world=old_world;tempfile.TemporaryDirectory=old_temp
report={'status':'INVENTORY65-EXACT-WORLD19-NORMAL-EMPTY-QEMU-PASS','gates':gates,'payload_sha256':g.sha(payload),'world_package_sha256':g.sha(packet),'test_source_sha256':g.sha(Path(__file__).read_bytes()),'physical_admission':False,'RNG_entropy_approved':False,'USB_backend':'SYNTHETIC-QEMU-FIXTURE'};(O/'qemu-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
