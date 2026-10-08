import hashlib,json,shutil,subprocess,sys
import source_contract
from pathlib import Path
R=Path(__file__).resolve().parent
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sys.platform=='linux'
primary=source_contract.check()
base=R/'runs/producer';out=R/'runs/native-auth';out.mkdir(parents=True,exist_ok=True)
pins=json.loads((base/'frozen-producer.json').read_text())
for n,h in pins.items():assert sha(base/n)==h,n;shutil.copyfile(base/n,out/n)
s=(out/'fixture.c').read_text();s='#include "auth_native.h"\nint glue_key_mmio(unsigned,unsigned,uint32_t);\n'+s
s=s.replace('static void data_tick(void){','static void glue_tick(void);\nstatic void data_tick(void){if(data_case>=23){glue_tick();return;}')
s=s.replace('static const uint8_t physical54_0[]=',(R/'key_model.inc').read_text()+'\n'+(R/'native_auth_model.inc').read_text()+'\nstatic const uint8_t physical54_0[]=')
s=s.replace('if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==3&&index==0x3c){','if(glue_key_mmio(id,index,value))return 0;\n  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==3&&index==0x3c){')
(out/'fixture.c').write_text(s)
p=out/'init_probe.c';s=p.read_text()
s=s.replace('static void data_native_step(uint64_t now){','int glue_model_active(void);\nint glue_model_dispatch(const QcaRxEvent*,uint64_t);\nint auth_model_copy(uint64_t);\nstatic void data_native_step(uint64_t now){')
s=s.replace('if(e->pipe==1&&e->endpoint==data_path->binding.endpoint&&e->bytes&&(e->payload[0]==7||e->payload[0]==0x12)){','if((glue_model_active()&&(e->pipe==2||!e->bytes))||(e->pipe==1&&e->endpoint==data_path->binding.endpoint&&e->bytes&&(e->payload[0]==3||e->payload[0]==4||e->payload[0]==11||e->payload[0]==7||e->payload[0]==0x12))){')
s=s.replace('int rc=qdp_receive(data_path,e,now);','int rc=glue_model_dispatch(e,now);')
needle='qdp_copy_one(data_path,now)';assert needle in s
s=s.replace(needle,'(auth_model_copy(now)?0:qdp_copy_one(data_path,now))')
p.write_text(s)
flags=['-I'+str(R),'-I'+str(R/'glue_inputs'),'-I'+str(out),'-I'+str(R/'copied/abi'),'-I'+str(R/'copied/codec')]
sources=[p for p in out.glob('*.c') if p.name not in {'fixture.c','port_test.c','scene_module.c','runtime_core.c','city_display.c','actor_clock.c'}]+[R/n for n in ['auth_native.c','auth_raw.c','pn.c','glue_inputs/glue.c','glue_inputs/eapol_wire.c','glue_inputs/key_operation.c','glue_inputs/copied/wire.c','glue_inputs/copied/coordinator.c','copied/station.c']]
cmd=[CC,'-DQAUTH_MODEL_TRACE','-DRABBIT_PREFIX_DRIVER_MODEL','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-DSCENE_REVISION=1','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,str(out/'fixture.c'),*map(str,sources),'-o',str(out/'test')]
subprocess.run(cmd,check=True)
assets=R.parent/'native-wifi-qca9377-filter64-native-v1/runs/native-host/fixture-assets'
world=R.parent/'native-wifi-qca9377-scan61-native-v1/runs/world19.rup'
argv=[str(out/'test'),'0',str(assets),'35','0','0','0','0',str(world),'0','30']
p=subprocess.run(argv,capture_output=True,text=True,timeout=180);(out/'host.log').write_text(p.stdout+p.stderr)
assert p.returncode==0,p.stdout+p.stderr
assert 'CORE CALLBACK STATE SYNTHETIC; NO PORT/IP' in p.stdout
objects={}
for name in ['auth_native','auth_raw','pn']:
 obj=out/(name+'.obj')
 subprocess.run([CC,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*flags,'-c',str(R/(name+'.c')),'-o',str(obj)],check=True)
 objects[name]=sha(obj)
report={'status':'NATIVE-OWNED-RAW-AUTH-OUTPUT-PN-COMMIT-ASAN-COFF-PASS','primary_source_contract':primary,'compiled_sources_sha256':{str(p.relative_to(R)):sha(p) for p in sources+[out/'fixture.c']},'textual_includes_sha256':{n:sha(out/n) for n in ['port_test.c','scene_module.c','runtime_core.c','city_display.c','actor_clock.c']},'original_producer_source_sha256':pins,'command':cmd,'argv':argv,'host_log_sha256':sha(out/'host.log'),'compiler_sha256':sha(Path(CC)),'executable_sha256':sha(out/'test'),'coff_sha256':objects,'fixture_kind':'synthetic-actual-C-producer-with-modeled-external-core-callback-state','physical_verified':False,'mature_handshake_exercised':False,'PN_original_committed_in_fixture':True,'controlled_port_created':False,'protected_quarantine_removed':False,'official_asset_and_real_dma_key_SEC_joins':True,'whole_EFI_fit_proven':False,'native_provider_glue_integrated':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(p.stdout.strip())
