import hashlib,json,shutil,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;A=R.parent/'native-wifi-qca9377-htt-authenticated-ll-rx-v1'
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sys.platform=='linux'
base=A/'runs/native-auth';out=R/'runs/native';out.mkdir(parents=True,exist_ok=True)
report=json.loads((base/'report.json').read_text())
assert sha(base/'report.json')=='92cd754e6fb60483fe67308942fbc4647dd4382bb2025d34d036358920baacf2'
for p in base.iterdir():
 if p.suffix in {'.c','.h'}:shutil.copy2(p,out/p.name)
s=(out/'fixture.c').read_text();s='#include "stop.h"\nstatic unsigned stop_started,stop_fault;\nint stop_model_active(void);\nvoid stop_model_tick(uint64_t);\n'+s
s=s.replace('static void data_tick(void){','static void data_tick(void){if(stop_model_active())return;')
s=s.replace('static unsigned auth_sent;', (R/'model.inc').read_text()+'\nstatic unsigned auth_sent;')
marker='puts("ACTUAL PRODUCER OWNED47+REAL KEY DMA/SEC+OFFICIAL ASSET+RAW HW FLAGS+ATOMIC OUTPUT PN COMMIT+REPLAY PASS; CORE CALLBACK STATE SYNTHETIC; NO PORT/IP");exit(0);'
assert marker in s
s=s.replace(marker,'qsg_revoke(&glue_model,201);d->runtime->phase=HTT_RUNTIME_ACTIVE;stop_started=1;assert(!qstop_begin(&stop_model,d,now));return 1;')
s=s.replace('assert(argc==11);data_case=','assert(argc==12);stop_fault=(unsigned)atoi(argv[11]);assert(stop_fault<=8);data_case=')
needle='if(off==0x3a028){assert(!v);fw=0;}'
assert needle in s;s=s.replace(needle,'if(off==0x3a028){assert(!v);if(!(stop_started&&stop_fault==1))fw=0;}')
s=s.replace('else{warm_register=v&~0x40u;if(v&0x40){','else{if(stop_started&&stop_fault==2)return 0;warm_register=v&~0x40u;if(v&0x40){')
s=s.replace('return scenario==16?EFI_ERROR(7):0;','return (scenario==16||(stop_started&&stop_fault==3))?EFI_ERROR(7):0;')
s=s.replace('if(off==4){uint16_t v=*(uint16_t*)in;','if(off==4){uint16_t v=*(uint16_t*)in;if(stop_started&&stop_fault==4&&!(v&4))return 0;')
s=s.replace('if(index==0x18)registers[id][index/4]=value?9:0;','if(index==0x18){if(stop_started&&stop_fault==5&&value)return 0;registers[id][index/4]=value?9:0;}')
head,tail=s.split('static Status EFIAPI mem_write(',1)
tail=tail.replace('if(off>=0x3a000&&off<=0x3a014){','if(stop_started&&stop_fault==6&&off==0x3a008&&!*(uint32_t*)in)return 0;\n if(off>=0x3a000&&off<=0x3a014){',1)
s=head+'static Status EFIAPI mem_write('+tail
s=s.replace('unmaps++;return 0;','unmaps++;return stop_started&&stop_fault==7?EFI_ERROR(7):0;')
s=s.replace('assert(pci==pci)','assert(pci==pci)') # no mutation of baseline helper semantics
s=s.replace('static Status EFIAPI free_buffer(void*p,uint64_t pages,void*host){','static Status EFIAPI free_buffer(void*p,uint64_t pages,void*host){if(stop_started&&stop_fault==8)return EFI_ERROR(7);')
(out/'fixture.c').write_text(s)
p=out/'init_probe.c';s=p.read_text()
s=s.replace('void qca_poll(uint64_t ms){','int stop_model_active(void);void stop_model_tick(uint64_t);\nvoid qca_poll(uint64_t ms){if(stop_model_active()){stop_model_tick(ms*1000);return;}')
s=s.replace('static int runtime_extra_stop(void*context){','int stop_model_dma_guard(QcaHttRuntime*);\nstatic int runtime_extra_stop(void*context){if(stop_model_active())return stop_model_dma_guard(context);')
s=s.replace('int runtime_extra_retained(QcaChannels*c){','int stop_model_retained(QcaChannels*);\nint runtime_extra_retained(QcaChannels*c){if(stop_model_active())return stop_model_retained(c);')
p.write_text(s)
flags=['-I'+str(R),'-I'+str(A),'-I'+str(A/'glue_inputs'),'-I'+str(out),'-I'+str(A/'copied/abi'),'-I'+str(A/'copied/codec')]
sources=[p for p in out.glob('*.c') if p.name not in {'fixture.c','port_test.c','scene_module.c','runtime_core.c','city_display.c','actor_clock.c'}]+[A/n for n in ['auth_native.c','auth_raw.c','pn.c','glue_inputs/glue.c','glue_inputs/eapol_wire.c','glue_inputs/key_operation.c','glue_inputs/copied/wire.c','glue_inputs/copied/coordinator.c','copied/station.c']]+[R/'stop.c']
cmd=[CC,'-DRABBIT_PREFIX_DRIVER_MODEL','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-DSCENE_REVISION=1','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,str(out/'fixture.c'),*map(str,sources),'-o',str(out/'test')]
subprocess.run(cmd,check=True)
assets=R.parent/'native-wifi-qca9377-filter64-native-v1/runs/native-host/fixture-assets';world=R.parent/'native-wifi-qca9377-scan61-native-v1/runs/world19.rup'
logs={}
for fault in [0,1,2,3,4,5,6,7,8]:
 argv=[str(out/'test'),'0',str(assets),'35','0','0','0','0',str(world),'0','30',str(fault)]
 p=subprocess.run(argv,capture_output=True,text=True,timeout=180);log=out/('case'+str(fault)+'.log');log.write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
 assert ('CE14 RETAINED' if fault==0 else 'EXACT ALLOCATION47' if fault>=7 else 'FAULT RETAINS47') in p.stdout,p.stdout;logs[str(fault)]=sha(log);print(p.stdout.strip())
subprocess.run([CC,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*flags,'-c',str(R/'stop.c'),'-o',str(out/'stop.obj')],check=True)
(out/'report.json').write_text(json.dumps({'status':'ACTUAL-WARM-TARGET-STOP-47TO14-ASAN-COFF-PASS','compiled_sources_sha256':{str(p):sha(p) for p in sources+[out/'fixture.c']},'logs':logs,'stop_obj_sha256':sha(out/'stop.obj'),'physical_verified':False,'native_integrated':False,'remaining_CE14_retained':True,'flash_OTP_USB_host_reboot':False},indent=2)+'\n')
