"""Reuse frozen55 regression target fixture with actual61 production C + driver."""
import importlib.util,sys
from pathlib import Path
import scan_build as build
OLD=build.E/'native-wifi-qca9377-scan-native-profile-v2'
spec=importlib.util.spec_from_file_location('frozen_scan55_build',OLD/'scan_build.py');old_build=importlib.util.module_from_spec(spec);spec.loader.exec_module(old_build)
saved=sys.modules['scan_build'];sys.modules['scan_build']=old_build
try:
 spec=importlib.util.spec_from_file_location('frozen_scan55_native_fixture',OLD/'verify_native.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
finally:sys.modules['scan_build']=saved
one=build.one
def fixture(source):
 s=old.fixture(source)
 s=s.replace('status[248]==55','status[248]==61')
 marker='uint8_t req[7]={10,34,0},reply[247];'
 s=one(s,marker,marker+r'''
  uint8_t gap[7]={0x10,29,0,255,0,0,0x28};assert(qca_scan_att(247,gap,7,reply,247)==22&&reply[2]==32&&reply[4]==34);
  gap[0]=8;gap[5]=3;assert(qca_scan_att(247,gap,7,reply,247)==23&&reply[2]==33&&reply[5]==34);
  gap[0]=4;assert(qca_scan_att(247,gap,5,reply,247)==6&&reply[2]==32);gap[3]=31;assert(qca_scan_att(247,gap,5,reply,247)==5&&reply[4]==10);
  gap[0]=10;assert(qca_scan_att(247,gap,3,reply,247)==SIZE_MAX);
''')

 marker='commands[scan_posts++]=bw(hosts[7]+8);'
 s=one(s,marker,marker+r'''
   const uint8_t*body=hosts[7]+8;unsigned command=bw(body);
   if(command==0x3003){assert(bw(body+8)==13&&s->tx.bytes==388);for(unsigned j=0;j<13;j++){const uint8_t*c=body+16+28*j;assert(bw(c+4)==2412+5*j&&bw(c+8)==2412+5*j&&!bw(c+12)&&bw(c+16)==129);}}
   if(command==0x4001)assert(bw(body+12)==108&&bw(body+16)==108&&bw(body+20)==108);
   if(command==0x3001){assert(s->tx.bytes==184&&bw(body+64)==0x21&&bw(body+72)==13);for(unsigned j=0;j<13;j++)assert(bw(body+112+4*j)==2412+5*j);assert(bw(body+164)==(19u<<16)&&bw(body+168)==(19u<<16)&&bw(body+172)==(17u<<16));}
''')

 s='#include "prefix.h"\n#include "usb_port.h"\n#include "scene_abi.h"\nQcaPrefix*qca_prefix_view(void);\nvoid qca_prefix_status(uint8_t[240]);\nvoid prefix_driver_model_bind(void*);\nint prefix_driver_model_poll(uint32_t);\nvoid prefix_driver_model_display(uint32_t*,unsigned,unsigned,unsigned);\nint prefix_driver_model_world(const uint8_t*,uint32_t,Surface*);\nint prefix_driver_model_frame(Surface*);\n'+s
 s=one(s,'static unsigned fault;','static unsigned fault;static void*usb_methods[16];static uint32_t*model_surface,*model_physical;static Surface model_sf;static unsigned active_status_reads;')
 s=one(s,'static void tick(unsigned ms){now_us=(uint64_t)ms*1000;qca_poll(ms);}', 'static void tick(unsigned ms){now_us=(uint64_t)ms*1000;assert(!prefix_driver_model_poll(ms));}')
 insertion=r'''
void qca_collect(SystemTable*s){(void)s;assert(!"actual attach is not this model");}
static Status EFIAPI usb_control(void*io,void*request,uint32_t direction,uint32_t timeout,void*data,size_t n,uint32_t*result){(void)io;(void)request;(void)direction;(void)timeout;(void)data;(void)n;(void)result;assert(!"no modeled disconnect");return 0;}
static Status EFIAPI usb_bulk(void*io,uint8_t endpoint,void*data,size_t*n,size_t timeout,uint32_t*result){assert(io==usb_methods&&endpoint==0x82&&timeout==1);(void)data;(void)n;*result=0;return EFI_ERROR(18);}
static Status EFIAPI usb_event_read(void*io,uint8_t endpoint,void*data,size_t*n,size_t timeout,uint32_t*result){
 assert(io==usb_methods&&endpoint==0x81&&*n==260&&timeout==20);*result=0;
 const uint8_t e[7]={0x13,5,1,1,0,0,0};memcpy(data,e,7);*n=7;return 0;
}
static void usb_fixture(void){usb_methods[0]=(void*)usb_control;usb_methods[1]=(void*)usb_bulk;usb_methods[3]=(void*)usb_event_read;prefix_driver_model_bind(usb_methods);}
static void scan_observe_active(void){
 const QcaNativeScan*s=qca_scan_native_view();QcaNativeScan before=*s;QcaPersistentNative radio=*qca_persistent_view();QcaPrefix telemetry=*qca_prefix_view();
 struct{uint8_t before[16],value[416],after[16];}guard;memset(&guard,0xa5,sizeof(guard));qca_scan_status(guard.value);
 for(unsigned i=0;i<16;i++)assert(guard.before[i]==0xa5&&guard.after[i]==0xa5);
 assert(guard.value[248]==61&&guard.value[8]==s->phase);
 uint8_t req[5]={10,34,0},reply[247];assert(qca_scan_att(247,req,3,reply,247)==247&&!memcmp(reply+1,guard.value,246));
 req[0]=12;req[3]=246;assert(qca_scan_att(247,req,5,reply,247)==171&&!memcmp(reply+1,guard.value+246,170));
 assert(!memcmp(s,&before,sizeof(before))&&!memcmp(qca_persistent_view(),&radio,sizeof(radio))&&!memcmp(qca_prefix_view(),&telemetry,sizeof(telemetry)));active_status_reads++;
}
'''
 s=one(s,'static void*ram_blocks[2];',insertion+'\nstatic void*ram_blocks[2];')
 s=one(s,'assert(argc==8);','assert(argc==9);')
 s=one(s,' sm_fixture();\n qca_start(&port_system,0);',' sm_fixture();usb_fixture();\n qca_start(&port_system,0);')
 marker='assert(initial==0&&get(128)==5&&!(config[1]&4));'
 code=r'''
 FILE*wf=fopen(argv[8],"rb");assert(wf&&!fseek(wf,0,SEEK_END));long wn=ftell(wf);assert(wn>0&&wn<65536);rewind(wf);uint8_t*wp=malloc((size_t)wn);assert(wp&&fread(wp,1,(size_t)wn,wf)==(size_t)wn);fclose(wf);
 model_surface=malloc((480*270+32)*4);model_physical=malloc((1280*720+32)*4);assert(model_surface&&model_physical);
 for(unsigned i=0;i<480*270+32;i++)model_surface[i]=0xdeadbeef;for(unsigned i=0;i<1280*720+32;i++)model_physical[i]=0xdeadbeef;
 model_sf=(Surface){model_surface+16,480,270,480,1};prefix_driver_model_display(model_physical+16,1280,720,1280);
 assert(!prefix_driver_model_world(wp,(uint32_t)wn,&model_sf));assert(!prefix_driver_model_frame(&model_sf));free(wp);
'''
 s=one(s,marker,marker+code)
 s=one(s,'   const QcaNativeScan*sc=qca_scan_native_view();','   const QcaNativeScan*sc=qca_scan_native_view();scan_observe_active();')
 marker=' printf("PERSISTENT_MOCK active_ticks='
 code=r'''
 {assert(active_status_reads);QcaPrefix*p=qca_prefix_view();assert(p->phase==3&&p->raw_frozen&&!p->usb_fault&&!p->raw_overflow);
  assert(!prefix_driver_model_frame(&model_sf));
  for(unsigned i=0;i<16;i++)assert(model_surface[i]==0xdeadbeef&&model_surface[480*270+16+i]==0xdeadbeef&&model_physical[i]==0xdeadbeef&&model_physical[1280*720+16+i]==0xdeadbeef);
  free(model_surface);free(model_physical);prefix_driver_model_display(0,0,0,0);
 }
'''
 s=one(s,marker,code+marker)
 return s
