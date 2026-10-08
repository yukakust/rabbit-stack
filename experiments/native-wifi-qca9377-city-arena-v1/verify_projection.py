"""Real OVMF normal/EMPTY world19 gate for the NEW unsigned projection.
USB/radio are existing synthetic fixtures. No owner keys or device operations.
"""
from pathlib import Path
import importlib.util,sys,tempfile,os,json,hashlib,time
import native_projection as project
assert sys.platform.startswith('linux'),'QEMU only Yukabox'
R=project.R;O=R/'runs/native-projection';tmp=Path('/home/yuka/rabbit-world/ca-qmp');tmp.mkdir(parents=True,exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
S=R.parent/'native-wifi-qca9377-filter64-native-v1'
sys.path.insert(0,str(S))
spec=importlib.util.spec_from_file_location('city_inherited_world_gate',S/'prove_filter.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
packet=(S/'runs/checked-candidate/world19.rup').read_bytes();assert g.sha(packet)==g.WORLD_PACKAGE
payload=(O/'payload.efi').read_bytes();original_report=json.loads((O/'report.json').read_text());assert g.sha(payload)==original_report['payload_sha256']
Q=O/('qemu-attempt-'+str(time.time_ns()));Q.mkdir()
qemu=g.checked.verify_init_profile.prior.actors_gate
original_city=qemu.compile_scene;original_world=qemu.flow.compile_world;original_temp=tempfile.TemporaryDirectory
def projection_fixture(source):
 s=g.fixture(source)
 s=project.one(s,'if(stage(legacy_city_stream,sizeof(legacy_city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=3)return 1;', 'if(stage(legacy_city_stream,sizeof(legacy_city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=3){say("CITYARENA LEGACY STAGE FAIL");return 1;} say("CITYARENA LEGACY STAGE PASS");')
 s=project.one(s,'if(stage(upgrade_stream,sizeof(upgrade_stream),2)||rabbit_test_finish()||pump())return 1;', 'if(stage(upgrade_stream,sizeof(upgrade_stream),2)){say("CITYARENA UPGRADE STAGE FAIL");return 1;} if(rabbit_test_finish()){say("CITYARENA UPGRADE FINISH FAIL");return 1;} if(pump()){say("CITYARENA UPGRADE PUMP FAIL");return 1;} say("CITYARENA UPGRADE PUMP PASS");')
 return s
def exact_city(world,counter,*args,**kwargs):
 assert counter==4;return packet
def later_restore(path,counter,*args,**kwargs):return original_world(path,20 if counter==5 else counter,*args,**kwargs)
def bounded_temp(*args,**kwargs):
 if kwargs.get('dir')=='/tmp':kwargs['dir']=str(tmp)
 return original_temp(*args,**kwargs)
try:
 qemu.compile_scene=exact_city;qemu.flow.compile_world=later_restore;tempfile.TemporaryDirectory=bounded_temp
 gates=[qemu.qemu_gate(Q,payload,test_transform=projection_fixture),qemu.qemu_gate(Q,payload,True,test_transform=projection_fixture)]
finally:qemu.compile_scene=original_city;qemu.flow.compile_world=original_world;tempfile.TemporaryDirectory=original_temp
for gate in gates:assert gate['payload_sha256']==g.sha(payload) and gate['physical_verified'] is False
report={'status':'UNSIGNED-CITY-ARENA-NORMAL-EMPTY-QEMU-WORLD19-PASS','build_host':'yukabox','gates':gates,'payload_sha256':g.sha(payload),'world19_sha256':g.sha(packet),'test_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inherited_fixture_sha256':hashlib.sha256((S/'prove_filter.py').read_bytes()).hexdigest(),'physical_proved':False,'signing_admitted':False,'radio_backend':'MOCK USB ONLY'}
(O/'qemu-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
