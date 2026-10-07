"""Actual production native/driver entrypoints; explicit PCI/CE/USB target mock."""
import sys
import fullboot_build as build
sys.path.insert(0,str(build.CHECKED))
import startup_fixture
one=build.one

def fixture(source):
 s=startup_fixture.fixture(source)
 s='#include "prefix.h"\n#include "usb_port.h"\n#include "scene_abi.h"\nQcaPrefix*qca_prefix_view(void);\nvoid qca_prefix_status(uint8_t[240]);\nvoid prefix_driver_model_bind(void*);\nint prefix_driver_model_poll(uint32_t);\nvoid prefix_driver_model_display(uint32_t*,unsigned,unsigned,unsigned);\nint prefix_driver_model_world(const uint8_t*,uint32_t,Surface*);\nint prefix_driver_model_frame(Surface*);\n'+s
 s=one(s,'static unsigned fault;','static unsigned fault;static unsigned diag_scenario,usb_calls,usb_controls,frames_tested;static uint8_t usb_event[32];static unsigned usb_event_n;static void*usb_methods[16];static uint32_t*model_surface,*model_physical;static Surface model_sf;')
 s=one(s,'static void tick(unsigned ms){now_us=(uint64_t)ms*1000;qca_poll(ms);}','static void tick(unsigned ms){now_us=(uint64_t)ms*1000;int result=prefix_driver_model_poll(ms);assert(!result||diag_scenario==9);}')
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
 if(diag_scenario==4&&p->phase==1)return EFI_ERROR(18);
 const uint8_t e[7]={0x13,5,1,1,0,0,0};memcpy(data,e,7);*n=7;return 0;
}
static void usb_fixture(void){usb_methods[0]=(void*)usb_control;usb_methods[1]=(void*)usb_bulk;usb_methods[3]=(void*)usb_event_read;prefix_driver_model_bind(usb_methods);}
static void prefix_boundaries(void){
 QcaPrefix p={0};qca_prefix_arm(&p,1000);
 assert(!qca_prefix_tick(&p,1000+QCA_PREFIX_DEADLINE_US-1,5,20,727128,3200,3200,0,0,0)&&p.phase==1);
 assert(qca_prefix_tick(&p,1000+QCA_PREFIX_DEADLINE_US,5,20,727128,3200,3200,0,0,0)&&p.phase==2&&p.reason==1);
 assert(!qca_prefix_tick(&p,1000+QCA_PREFIX_DEADLINE_US,5,20,727128,3200,3200,0,0,1)&&p.phase==3&&p.raw_frozen);
 QcaPrefix q={0};qca_prefix_arm(&q,5000);assert(qca_prefix_tick(&q,4999,1,17,32984,312,312,0,0,0)&&q.reason==2);
 QcaPrefix full={0};qca_prefix_arm(&full,1);
 for(unsigned phase=1;phase<=5;phase++){if(phase==4)continue;assert(!qca_prefix_tick(&full,phase,phase,17,32984,312,312,0,0,0)&&full.phase==1);}
}
static void observe_active(void){
 QcaPrefix*p=qca_prefix_view();QcaPrefix before=*p;QcaBootNative boot=*qca_boot_view();QcaWmiStartup startup=*qca_wmi_startup_view();
 struct{uint8_t before[16],status[240],after[16];} guard;memset(&guard,0xa5,sizeof(guard));qca_prefix_status(guard.status);
 for(unsigned i=0;i<16;i++)assert(guard.before[i]==0xa5&&guard.after[i]==0xa5);
 assert(guard.status[8]==60&&guard.status[12]==1);
 uint8_t req[3]={10,31,0},reply[247];extern size_t qca_prefix_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);
 assert(qca_prefix_att(247,req,3,reply,247)==241&&!memcmp(reply+1,guard.status,240));
 req[1]=33;assert(qca_prefix_att(247,req,3,reply,247)==247);req[1]=51;assert(qca_prefix_att(247,req,3,reply,247)==65);
 assert(!memcmp(&before,p,sizeof(before))&&!memcmp(&boot,qca_boot_view(),sizeof(boot))&&!memcmp(&startup,qca_wmi_startup_view(),sizeof(startup)));
}
static void finish_diag(void){
 QcaPrefix*p=qca_prefix_view();const QcaBootNative*b=qca_boot_view();
 struct {uint8_t before[16],value[240],after[16];} guard;memset(&guard,0xa5,sizeof(guard));qca_prefix_status(guard.value);
 for(unsigned i=0;i<16;i++)assert(guard.before[i]==0xa5&&guard.after[i]==0xa5);
 assert(!memcmp(guard.value,"QPFX0001",8)&&guard.value[8]==60);
 if(diag_scenario!=9){
  assert(p->phase==3&&p->raw_frozen&&guard.value[24]==1&&!guard.value[96]&&!guard.value[100]);
  assert(allocations==14&&dma_frees==14&&unmaps==14&&opens==closes&&!qca_ram_view()->asset.pinned&&!qca_fwp_owned(qca_ram_view()));
  if(diag_scenario==1)assert(p->reason==1);
  if(diag_scenario==2)assert(p->reason==2);
  if(diag_scenario==3)assert(p->reason==6);
  if(diag_scenario==6)assert(p->reason==5&&p->critical_count==4&&p->raw_overflow);
  if(diag_scenario==7)assert(p->reason==7);
  if(fault!=35){assert(p->reason==(fault>=6?7u:3u)&&!init_posts);}
  else if(!diag_scenario||diag_scenario==4||diag_scenario==5){
   unsigned success=startup_fault==0||startup_fault==1||startup_fault==15||startup_fault==22;
   assert(p->reason==(success?0u:startup_fault==21?7u:3u));
   assert(main_done==1&&uart_off==1&&streams==3&&stream_bytes==727128&&b->plan.phase==20);
   if(success){const QcaWmiStartup*w=qca_wmi_startup_view();assert(w->phase==2&&w->transaction.ready_seen&&w->transaction.tx_complete&&init_posts==1);}
  }
 }else assert(p->usb_fault&&!p->raw_frozen);
 uint8_t req[5]={0x0a,31,0,0,0},reply[247];extern size_t qca_prefix_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);
 assert(qca_prefix_att(247,req,3,reply,247)==241&&!memcmp(reply+1,guard.value,240));
 req[0]=0x12;assert(qca_prefix_att(247,req,3,reply,247)==5&&reply[4]==3);
 req[0]=0x0c;req[3]=240;assert(qca_prefix_att(247,req,5,reply,247)==1);req[3]=241;assert(qca_prefix_att(247,req,5,reply,247)==5&&reply[4]==7);
 uint8_t raw[4672];assert(qca_prefix_raw(p,raw,4672,0)==4672&&raw[8]==60);
 for(unsigned page=0;page<10;page++){
  unsigned length=page==9?64:512,offset=0;uint8_t assembled[512];
  while(offset<length){req[0]=offset?0x0c:0x0a;req[1]=(uint8_t)(33+2*page);req[2]=0;req[3]=(uint8_t)offset;req[4]=(uint8_t)(offset>>8);size_t got=qca_prefix_att(247,req,offset?5:3,reply,247);assert(got>1&&got<=247&&got-1<=length-offset);memcpy(assembled+offset,reply+1,got-1);offset+=(unsigned)got-1;}
  assert(!memcmp(assembled,raw+page*512,length));req[0]=0x0c;req[3]=(uint8_t)length;req[4]=(uint8_t)(length>>8);assert(qca_prefix_att(247,req,5,reply,247)==1);
  req[3]=(uint8_t)(length+1);req[4]=(uint8_t)((length+1)>>8);assert(qca_prefix_att(247,req,5,reply,247)==5&&reply[4]==7);
 }
 assert(!prefix_driver_model_frame(&model_sf));frames_tested++;
 for(unsigned i=0;i<16;i++)assert(model_surface[i]==0xdeadbeef&&model_surface[480*270+16+i]==0xdeadbeef&&model_physical[i]==0xdeadbeef&&model_physical[1280*720+16+i]==0xdeadbeef);
 free(model_surface);free(model_physical);prefix_driver_model_display(0,0,0,0);
 if(diag_scenario==9){(void)qca_stop();for(unsigned ms=700001;ms<720000;ms++)tick(ms);assert(!qca_stop()&&!qca_fwp_owned(qca_ram_view()));}
 if(diag_scenario!=9){tick(4294967);assert(p->poll_before==4294967000ull);tick(4294968);assert(p->poll_before==4294968000ull);}
 fprintf(stderr,"FULL60 diag=%u startup=%u phase=%u reason=%u released=%u MAIN=%u BMI_DONE=%u INIT=%u USB=%u/%u raw=%u overwrite=%u\n",diag_scenario,startup_fault,p->phase,p->reason,guard.value[24],stream_bytes,main_done,init_posts,p->usb_reads,p->usb_timeouts,p->raw_count,p->routine_overwritten);
}
'''
 s=one(s,'static void*ram_blocks[2];',insertion+'\nstatic void*ram_blocks[2];')
 s=one(s,'assert(argc==5);','assert(argc==7);diag_scenario=(unsigned)atoi(argv[6]);assert(diag_scenario<=9);')
 s=one(s,' sm_fixture();\n qca_start(&port_system,0);',' prefix_boundaries();sm_fixture();usb_fixture();\n qca_start(&port_system,0);')
 marker='assert(initial==0&&get(128)==5&&!(config[1]&4));'
 code=r'''
 FILE*wf=fopen(argv[5],"rb");assert(wf&&!fseek(wf,0,SEEK_END));long wn=ftell(wf);assert(wn>0&&wn<65536);rewind(wf);uint8_t*wp=malloc((size_t)wn);assert(wp&&fread(wp,1,(size_t)wn,wf)==(size_t)wn);fclose(wf);
 model_surface=malloc((480*270+32)*4);model_physical=malloc((1280*720+32)*4);assert(model_surface&&model_physical);
 for(unsigned i=0;i<480*270+32;i++)model_surface[i]=0xdeadbeef;for(unsigned i=0;i<1280*720+32;i++)model_physical[i]=0xdeadbeef;
 model_sf=(Surface){model_surface+16,480,270,480,1};prefix_driver_model_display(model_physical+16,1280,720,1280);
 assert(!prefix_driver_model_world(wp,(uint32_t)wn,&model_sf));assert(!prefix_driver_model_frame(&model_sf));frames_tested++;free(wp);
'''
 s=one(s,marker,marker+code)
 s=one(s,'ms<60000','ms<700000')
 marker='  tick(ms);const QcaBootNative*b=qca_boot_view();'
 code=r'''
  QcaPrefix*diag=qca_prefix_view();
  if(diag->phase==1&&diag_scenario==1)tick(ms+5400001);
  if(diag->phase==1&&diag_scenario==2)tick(0);
  if(diag->phase==1&&diag_scenario==3)diag->usb_fault=3;
  if(diag->phase==1&&diag_scenario==7)(void)qca_stop();
'''
 s=one(s,marker,code+marker+'\n  if(qca_prefix_view()->phase==1&&(!(ms%1000)||qca_wmi_startup_view()->phase==1))observe_active();')
 marker=' const QcaBootNative*b=qca_boot_view();fprintf(stderr,"SECOND'
 s=one(s,marker,' finish_diag();if(diag_scenario||fault!=35)return;\n'+marker)
 # Resident fatal result cannot promise cleanup; stop the actual model at that
 # boundary and prove explicit retained/unfrozen diagnostics, rather than claim.
 s=one(s,'  if(qca_boot_round()&&(get(128)==5||get(128)==6))break;','  if(diag_scenario==9&&qca_prefix_view()->usb_fault)break;\n  if(qca_boot_round()&&(get(128)==5||get(128)==6))break;')
 return s
