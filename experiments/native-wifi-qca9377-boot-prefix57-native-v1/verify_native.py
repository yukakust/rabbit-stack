"""Yukabox-only actual native PCI/CE/DMA + sole driver USB poll/overlay model."""
import sys,subprocess,json,hashlib,os
from pathlib import Path
import prefix_build as build
sys.path.insert(0,str(build.BASE));import boot_fixture,verify_setup_probe,verify_port
from firmware_chunk_format import packets
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
ROOT=build.ROOT;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fixture(source):
 s=boot_fixture.fixture(source);s='#include "prefix.h"\n#include "usb_port.h"\n#include "scene_abi.h"\nQcaPrefix*qca_prefix_view(void);\nvoid qca_prefix_status(uint8_t[240]);\nvoid prefix_driver_model_bind(void*);\nint prefix_driver_model_poll(uint32_t);\nvoid prefix_driver_model_display(uint32_t*,unsigned,unsigned,unsigned);\nint prefix_driver_model_world(const uint8_t*,uint32_t,Surface*);\nint prefix_driver_model_frame(Surface*);\n'+s
 s=build.one(s,'static unsigned fault;','static unsigned fault;static unsigned diag_scenario,usb_calls,usb_controls,frames_tested;static uint8_t usb_event[32];static unsigned usb_event_n;static void*usb_methods[16];static uint32_t*model_surface,*model_physical;static Surface model_sf;')
 s=build.one(s,'static void tick(unsigned ms){now_us=(uint64_t)ms*1000;qca_poll(ms);}', '''static void tick(unsigned ms){now_us=(uint64_t)ms*1000;int result=prefix_driver_model_poll(ms);assert(!result||diag_scenario==9);}''')
 insertion=r'''
void qca_collect(SystemTable*s){(void)s;assert(!"actual attach is not this model");}
static Status EFIAPI usb_control(void*io,void*request,uint32_t direction,uint32_t timeout,void*data,size_t n,uint32_t*result){
 assert(io==usb_methods&&direction==1&&timeout==200&&n==4);const uint8_t*p=data;assert(p[0]==0x0a&&p[1]==0x20&&p[2]==1&&p[3]==1);(void)request;usb_controls++;*result=0;
 const uint8_t e[6]={0x0e,4,1,0x0a,0x20,0};memcpy(usb_event,e,6);usb_event_n=6;return 0;
}
static Status EFIAPI usb_bulk(void*io,uint8_t endpoint,void*data,size_t*n,size_t timeout,uint32_t*result){assert(io==usb_methods&&endpoint==0x82&&timeout==1);(void)data;(void)n;*result=0;return EFI_ERROR(18);}
static Status EFIAPI usb_event_read(void*io,uint8_t endpoint,void*data,size_t*n,size_t timeout,uint32_t*result){
 assert(io==usb_methods&&endpoint==0x81&&*n==260&&timeout==20);usb_calls++;*result=0;QcaPrefix*p=qca_prefix_view();
 if(diag_scenario==9&&p->phase==1)return EFI_ERROR(7);
 if(usb_event_n){memcpy(data,usb_event,usb_event_n);*n=usb_event_n;usb_event_n=0;return 0;}
 if(diag_scenario==5&&p->phase==1&&usb_controls==0&&p->polls>5){const uint8_t e[6]={5,4,0,1,0,0x13};memcpy(data,e,6);*n=6;return 0;}
 if(diag_scenario==6&&p->phase==1){const uint8_t e[6]={0x0e,4,1,0xff,0xff,1};memcpy(data,e,6);*n=6;return 0;}
 if(diag_scenario==4&&p->phase==1)return EFI_ERROR(18); /* silent connected timeout */
 const uint8_t e[7]={0x13,5,1,1,0,0,0};memcpy(data,e,7);*n=7;return 0;
}
static void usb_fixture(void){usb_methods[0]=(void*)usb_control;usb_methods[1]=(void*)usb_bulk;usb_methods[3]=(void*)usb_event_read;prefix_driver_model_bind(usb_methods);}
'''
 s=build.one(s,'static void*ram_blocks[2];',insertion+'\nstatic void*ram_blocks[2];')
 # Prove exact real publication boundary, rather than fabricating an idle gap.
 s=build.one(s,'stream_bytes+=n;', '''stream_bytes+=n;
     if(streams==3)assert(stream_bytes<=32984); /* no134th MAIN descriptor */
''')
 s=build.one(s,'else{assert(op==1&&streams==3', 'else{assert(!"BMI_DONE forbidden in prefix57");assert(op==1&&streams==3')
 start=s.index(' unsigned cancel_called=0;') if ' unsigned cancel_called=0;' in s else s.index('unsigned cancel_called=0;')
 end=s.index(' uint8_t status[160];',start)
 s=s[:start]+r'''
 for(unsigned ms=15001;ms<700000;ms++){
  tick(ms);const QcaBootNative*b=qca_boot_view();QcaPrefix*p=qca_prefix_view();
  if(p->phase==1&&diag_scenario==1){tick(ms+600001);}
  if(p->phase==1&&diag_scenario==2){tick(0);}
  if(p->phase==1&&diag_scenario==3&&b->plan.phase==17)p->usb_fault=3;
    if(p->phase==1&&b->plan.phase==17&&b->plan.offset>=19592&&frames_tested==1){assert(!prefix_driver_model_frame(&model_sf));frames_tested++;}
  if(p->phase==3){assert(!prefix_driver_model_frame(&model_sf));frames_tested++;break;}
  if(diag_scenario==9&&p->usb_fault)break; /* resident fatal cannot promise cleanup */
 }
 QcaPrefix*p=qca_prefix_view();const QcaBootNative*b=qca_boot_view();
 fprintf(stderr,"PREFIXFINAL mode=%u phase=%u reason=%u offset=%u submitted=%u completed=%u streams=%u MAIN=%u OWNERS=%u frame=%u USB=%u/%u BLE=%u raw=%u overwrites=%u\n",diag_scenario,p->phase,p->reason,p->stop_offset,p->stop_submitted,p->stop_completed,streams,stream_bytes,get(240),p->frames,p->usb_reads,p->usb_timeouts,p->ble_state,p->raw_count,p->routine_overwritten);
 assert(!main_done&&!uart_off&&!b->ready_bytes&&stream_bytes<=32984);
 if(diag_scenario!=9){
  assert(p->phase==3&&allocations==14&&dma_frees==14&&unmaps==14&&opens==closes&&!r->asset.pinned&&!qca_fwp_owned(r));
  if(diag_scenario==0||diag_scenario==4||diag_scenario==5){assert(!p->reason&&p->stop_plan==17&&p->stop_offset==32984&&stream_bytes==32984&&p->stop_submitted==p->stop_completed);}
  if(diag_scenario==0)assert(p->routine_overwritten>100&&!p->raw_overflow);
  if(diag_scenario==4)assert(p->ble_state==RL_CONNECTED&&!p->pending&&p->usb_timeouts&&!p->raw_overflow);
  if(diag_scenario==5)assert(p->critical_count>=1&&usb_controls==1&&p->ble_state==RL_ADVERTISING);
  if(diag_scenario==1)assert(p->reason==1);
  if(diag_scenario==2)assert(p->reason==2);
  if(diag_scenario==3)assert(p->reason==6);
  if(diag_scenario==6)assert(p->reason==5&&p->critical_count==4&&p->raw_overflow);
 }else assert(p->usb_fault&&!qca_prefix_view()->raw_frozen);
 struct {uint8_t before[16],value[240],after[16];} guard;memset(&guard,0xa5,sizeof(guard));qca_prefix_status(guard.value);
 for(unsigned i=0;i<16;i++)assert(guard.before[i]==0xa5&&guard.after[i]==0xa5);
 assert(!memcmp(guard.value,"QPFX0001",8)&&guard.value[8]==57);
 if(diag_scenario!=9)assert(guard.value[24]==1&&!guard.value[96]&&!guard.value[100]);
 uint8_t req[5]={0x0a,31,0,0,0};extern size_t qca_prefix_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);
 assert(qca_prefix_att(247,req,3,reply,247)==241&&!memcmp(reply+1,guard.value,240));
 req[0]=0x12;assert(qca_prefix_att(247,req,3,reply,247)==5&&reply[4]==3);
 req[0]=0x0c;req[3]=240;assert(qca_prefix_att(247,req,5,reply,247)==1);req[3]=241;assert(qca_prefix_att(247,req,5,reply,247)==5&&reply[4]==7);
 uint8_t raw[4672];assert(qca_prefix_raw(p,raw,4672,0)==4672);
 for(unsigned page=0;page<10;page++){
  unsigned length=page==9?64:512;unsigned offset=0;uint8_t assembled[512];
  while(offset<length){req[0]=offset?0x0c:0x0a;req[1]=(uint8_t)(33+2*page);req[2]=0;req[3]=(uint8_t)offset;req[4]=(uint8_t)(offset>>8);size_t got=qca_prefix_att(247,req,offset?5:3,reply,247);assert(got>1&&got<=247&&got-1<=length-offset);memcpy(assembled+offset,reply+1,got-1);offset+=(unsigned)got-1;}
  assert(!memcmp(assembled,raw+page*512,length));
  req[0]=0x0c;req[3]=(uint8_t)length;req[4]=(uint8_t)(length>>8);assert(qca_prefix_att(247,req,5,reply,247)==1);
  req[3]=(uint8_t)(length+1);req[4]=(uint8_t)((length+1)>>8);assert(qca_prefix_att(247,req,5,reply,247)==5&&reply[4]==7);
 }

 if(diag_scenario!=9){
  tick(4294967);assert(p->poll_before==4294967000ull&&p->poll_after==4294967000ull);
  tick(4294968);assert(p->poll_before==4294968000ull&&p->poll_after==4294968000ull);
 }
''' +s[end:]
 # Old full-boot tail calls old assertion r phase. Replace it with our final,
 # actual driver overlay bounds/canary test and safe cleanup result.
 start=s.index(' /* Actual callback must return legacy writes');end=s.index('\n}\n',start)
 s=s[:start]+r'''
 assert(frames_tested);
 for(unsigned i=0;i<16;i++)assert(model_surface[i]==0xdeadbeef&&model_surface[480*270+16+i]==0xdeadbeef&&model_physical[i]==0xdeadbeef&&model_physical[1280*720+16+i]==0xdeadbeef);
 free(model_surface);free(model_physical);prefix_driver_model_display(0,0,0,0);
 if(diag_scenario!=9)assert(!qca_stop()&&ram_frees==2&&!qca_fwp_owned(r));
 else{(void)qca_stop();for(unsigned ms=700001;ms<720000;ms++)tick(ms);}
 puts("ACTUAL DRIVER POLL/USB/CE PREFIX NO134TH/BMI_DONE, OVERLAY/STATUS BOUNDS PASS");
''' +s[end:]
 s=build.one(s,'assert(argc==4);fault=(unsigned)atoi(argv[3]);assert(fault<=7);', 'assert(argc==5);fault=0;diag_scenario=(unsigned)atoi(argv[3]);assert(diag_scenario<=9);')
 s=build.one(s,' sm_fixture();\n qca_start(&port_system,0);',' sm_fixture();usb_fixture();\n qca_start(&port_system,0);')
 # Exercise real prefix_tick_frame with actualworld18 activation and real GOP
 # presentation; guards survive both surface and large physical framebuffer.
 marker='assert(initial==0&&get(128)==5&&!(config[1]&4));'
 code=r'''
 FILE*wf=fopen(argv[4],"rb");assert(wf&&!fseek(wf,0,SEEK_END));long wn=ftell(wf);assert(wn>0&&wn<65536);rewind(wf);uint8_t*wp=malloc((size_t)wn);assert(wp&&fread(wp,1,(size_t)wn,wf)==(size_t)wn);fclose(wf);
 model_surface=malloc((480*270+32)*4);model_physical=malloc((1280*720+32)*4);uint32_t*surface=model_surface,*physical=model_physical;assert(surface&&physical);
 for(unsigned i=0;i<480*270+32;i++)surface[i]=0xdeadbeef;for(unsigned i=0;i<1280*720+32;i++)physical[i]=0xdeadbeef;
 model_sf=(Surface){surface+16,480,270,480,1};Surface sf=model_sf;prefix_driver_model_display(physical+16,1280,720,1280);
 assert(!prefix_driver_model_world(wp,(uint32_t)wn,&sf));assert(!prefix_driver_model_frame(&sf));frames_tested++;
 for(unsigned i=0;i<16;i++)assert(surface[i]==0xdeadbeef&&surface[480*270+16+i]==0xdeadbeef&&physical[i]==0xdeadbeef&&physical[1280*720+16+i]==0xdeadbeef);
 free(wp);
'''
 s=build.one(s,marker,marker+code)
 return s

def main():
 if sys.platform!='linux':raise SystemExit('Yukabox only')
 out=ROOT/'runs/native-host';out.mkdir(parents=True,exist_ok=True);build.driver_sources(out);assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();policy=build.policy();assert hashlib.sha256(data).hexdigest()==policy['digest']
 key=Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
 for i,p in enumerate(packets(data,key,target=bytes.fromhex(policy['target']),generation=57,target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])):(assets/f'chunk-{i}.bin').write_bytes(p)
 p=out/'init_probe.c';s=p.read_text();s=build.one(s,'.owner={'+','.join(str(n) for n in bytes.fromhex(policy['owner']))+'}', '.owner={'+','.join(str(n) for n in public)+'}');p.write_text(s)
 (out/'fixture.c').write_text(fixture((build.BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(x) for x in (out,build.BASE,build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE,build.BASE/'runs/firmware-chunks',build.checked.prior.actors.LINK,ROOT.parent/'x86-64-uefi-connected-supervisor-v1')]
 crypto=[build.BASE/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')]
 files=list(build.FILES)+['driver.c','city_core.c','pci_identity.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c','diagnostic_gatt.c']
 command=[str(verify_port.CC),'-DRABBIT_PREFIX_DRIVER_MODEL','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-DSCENE_REVISION=1','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.checked.prior.actors.LINK/'file_core.c'),str(build.checked.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(out/'test')]
 subprocess.run(command,check=True);log=''
 for mode in (0,1,2,3,4,5,6,9):
  r=subprocess.run([str(out/'test'),'0',str(assets),str(mode),str(ROOT/'runs/world18.rup')],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'mode{mode}: {r.stdout[-1000:]}\n{r.stderr[-3500:]}')
 for n in ('prefix','prefix_gatt','init_probe','driver'):
  subprocess.run([str(verify_port.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(n+'.c')),'-o',str(out/(n+'.obj'))],check=True)
 report={'status':'BOOT-PREFIX57-ACTUAL-DRIVER-PCI-CE-USB-OVERLAY-ASAN-COFF-PASS','scenarios':8,'scenario_ids':[0,1,2,3,4,5,6,9],'host_log_sha256':sha(out/'host.log'),'source_sha256':{str(p.relative_to(ROOT.parent.parent)):sha(p) for p in ROOT.iterdir() if p.is_file()},'compiled_fixture_sources_sha256':{p.name:sha(p) for p in [out/'fixture.c',*[out/n for n in files],*crypto]},'actual_driver_poll':True,'actual_native_PCI_CE_DMA_model':True,'actual_driver_overlay_canary_test':True,'mocked_USB_backend':True,'driver_attach_not_modelled':True,'full_authenticated_container':True,'max_MAIN_bytes':32984,'max_MAIN_descriptors':133,'BMI_DONE_commands':0,'HTC_INIT_scan_commands':0,'device_operations':0,'private_key_loads':0,'physical_verified':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
