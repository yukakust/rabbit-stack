import hashlib,json,os,re,shutil,subprocess,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parent
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sys.platform=='linux'
TMP=R/'runs/tmp';TMP.mkdir(parents=True,exist_ok=True);os.environ['TMPDIR']=str(TMP);tempfile.tempdir=str(TMP)
base=R/'runs/producer';out=R/'runs/glue';out.mkdir(parents=True,exist_ok=True)
pins=json.loads((base/'frozen-producer.json').read_text())
for n,h in pins.items():assert sha(base/n)==h,n;shutil.copyfile(base/n,out/n)
s=(out/'fixture.c').read_text();s='#include "ether_tx.h"\nint ethernet_mmio(unsigned,unsigned,uint32_t);\nint glue_key_mmio(unsigned,unsigned,uint32_t);\n'+s;s=s.replace('static void data_tick(void){','static void glue_tick(void);\nstatic int ethernet_failure_tick(void);\nstatic void data_tick(void){if(data_case>=31&&ethernet_failure_tick())return;if(data_case>=23){glue_tick();return;}')
s=s.replace('static const uint8_t physical54_0[]=',(R/'model_hook.c.inc').read_text()+'\nstatic const uint8_t physical54_0[]=')
s=s.replace('if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==3&&index==0x3c){','if(ethernet_mmio(id,index,value)||glue_key_mmio(id,index,value))return 0;\n  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==3&&index==0x3c){')
(out/'fixture.c').write_text(s)
p=out/'init_probe.c';s=p.read_text();s='int glue_model_active(void);\nint glue_model_dispatch(const QcaRxEvent*,uint64_t);\n'+s if False else s
s=s.replace('static void data_native_step(uint64_t now){','int glue_model_active(void);\nint glue_model_dispatch(const QcaRxEvent*,uint64_t);\nstatic void data_native_step(uint64_t now){')
s=s.replace('if(e->pipe==1&&e->endpoint==data_path->binding.endpoint&&e->bytes&&(e->payload[0]==7||e->payload[0]==0x12)){','if((glue_model_active()&&(e->pipe==2||!e->bytes))||(e->pipe==1&&e->endpoint==data_path->binding.endpoint&&e->bytes&&(e->payload[0]==3||e->payload[0]==4||e->payload[0]==11||e->payload[0]==7||e->payload[0]==0x12))){')
s=s.replace('int rc=qdp_receive(data_path,e,now);','int rc=ethernet_model_dispatch(e,now);')
s=s.replace('int glue_model_dispatch(const QcaRxEvent*,uint64_t);','int ethernet_model_dispatch(const QcaRxEvent*,uint64_t);')
p.write_text(s)
flags=['-I'+str(R/'runs/glue-source'),'-I'+str(R),'-I'+str(out),'-I'+str(R/'runs/glue-source/copied/copied/abi'),'-I'+str(R/'runs/glue-source/copied/copied/codec')]
sources=[p for p in out.glob('*.c') if p.name not in {'fixture.c','port_test.c','scene_module.c','runtime_core.c','city_display.c','actor_clock.c','data_path.c'}]+[R/'ether_tx.c']+[R/'runs/glue-source'/n for n in ['glue.c','eapol_wire.c','key_operation.c','copied/wire.c','copied/coordinator.c','copied/copied/station.c','copied/pn/pn.c']]
subprocess.run([CC,'-DRABBIT_PREFIX_DRIVER_MODEL','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-DSCENE_REVISION=1','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,str(out/'fixture.c'),*map(str,sources),'-o',str(out/'test')],check=True)
log='';cases=[31,32,33,34,35,36]
for case in cases:
 p=subprocess.run([str(out/'test'),'0',str(R/'runs/fixture-assets'),'35','0','0','0','0',str(R/'runs/world19.rup'),'0',str(case)],capture_output=True,text=True,timeout=120)
 log+=f'CASE {case}\n'+p.stdout+p.stderr;(out/'host.log').write_text(log)
 assert p.returncode==0,log[-5000:]
for n in ['ether_tx.c']:
 subprocess.run([CC,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*flags,'-c',str(R/n),'-o',str(out/(n+'.obj'))],check=True)
report={'status':'EXPERIMENTAL-ETHERNET-TX-ACTUAL-PRODUCER-ASAN-COFF-PASS','build_host':'yukabox','fixture_kind':'synthetic-actual-C-producer','cases':cases,'source_sha256':{str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and 'runs' not in p.relative_to(R).parts and '__pycache__' not in p.parts},'frozen_producer_sha256':pins,'compiled_glue_sources_sha256':{str(p.relative_to(R)):sha(p) for p in (R/'runs/glue-source').rglob('*') if p.is_file() and p.suffix in {'.c','.h'}},'compiler_sha256':sha(Path(CC)),'compiled_sources_sha256':{p.name:sha(p) for p in out.glob('*') if p.suffix in {'.c','.h'}},'fixture_assets_sha256':{p.name:sha(p) for p in (R/'runs/fixture-assets').glob('*.bin')},'world19_fixture_sha256':sha(R/'runs/world19.rup'),'host_log_sha256':sha(out/'host.log'),'test_sha256':sha(out/'test'),'coff_sha256':{p.name:sha(p) for p in out.glob('*.obj')},'physical_verified':False,'native_candidate_integrated':False,'mature_handshake_in_this_producer':False,'authenticated_data_delivery':False,'controlled_port_authority':False,'protected_tx_software_profile':'EXPERIMENTAL-ETHERNET2-NONQOS16','physical_wire_encryption_verified':False,'policy_DMA_is_target_ACK':False,'all47_stop_backend':False,'rf_admission_granted':False,'credential_reads':0}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
