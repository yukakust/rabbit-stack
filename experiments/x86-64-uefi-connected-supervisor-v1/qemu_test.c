/* Actual UEFI LoadImage/StartImage/unload with a MOCK USB controller.
 * No emulated QCA/radio or physical performance claim. */
#include "connected_abi.h"
#include "test_data.h"
void EFIAPI rabbit_supervisor_entry(void*,SystemTable*);
Status EFIAPI rabbit_connected_run(void*,SystemTable*);
int EFIAPI rabbit_scene_tick(void*);
int rabbit_test_connected_boot(SystemTable*);
int rabbit_test_radio_poll(void);
int rabbit_test_control(const uint8_t*,uint32_t);
int rabbit_test_data(const uint8_t*,uint32_t);
void rabbit_test_status(uint8_t*);
int rabbit_test_finish(void);
int rabbit_test_snapshot(uint8_t*,uint32_t*);
const uint8_t *rabbit_test_base(void);
static uint8_t before[SNAPSHOT_MAX],after[SNAPSHOT_MAX],status[60];
static void*mock_io[13];static uint16_t pending;static int conn_event,connected,advertising,disconn_event;
static unsigned resets,disconnects,violations;
static uint8_t incoming[260],last_att;static size_t incoming_length;static uint16_t completed_packets;
static const Guid usb_guid={0x2b2f68d6,0x0cd2,0x44cf,{0x8e,0x8b,0xbb,0xa2,0x0b,0x1b,0x5b,0x75}};
static void copy(uint8_t*d,const uint8_t*s,size_t n){for(size_t i=0;i<n;i++)d[i]=s[i];}
static void put32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=v>>(8*i);}
static int same(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
static uint32_t le32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void say(const char*s){for(unsigned i=0;s[i];i++)__asm__ volatile("outb %0,%1"::"a"((uint8_t)s[i]),"Nd"((uint16_t)0xe9));__asm__ volatile("outb %0,%1"::"a"((uint8_t)'\n'),"Nd"((uint16_t)0xe9));}
#ifdef RABBIT_FAULT_TEST
/* Fixture-only forwarding ConOut proxy records actual screen diagnostics.
 * This is never compiled into the physical candidate. */
static void*diagnostic_io[10],*original_output;
typedef Status(EFIAPI *TextOutput)(void*,const uint16_t*);
static Status EFIAPI record_output(void*io,const uint16_t*text){
 (void)io;char ascii[160];unsigned i=0;
 while(text[i]&&i<159){ascii[i]=(char)text[i];i++;}ascii[i]=0;say(ascii);
 return ((TextOutput)*(void**)((uint8_t*)original_output+8))(original_output,text);
}
#endif
static Status EFIAPI descriptor(void*this,void*out){
 (void)this;uint8_t*p=out;for(unsigned i=0;i<18;i++)p[i]=0;
 p[0]=18;p[1]=1;p[8]=0xf3;p[9]=0x0c;p[10]=9;p[11]=0xe0;return 0;
}
static Status EFIAPI iface(void*this,void*out){
 (void)this;uint8_t*p=out;for(unsigned i=0;i<9;i++)p[i]=0;
 p[0]=9;p[1]=4;p[4]=3;p[5]=0xe0;p[6]=p[7]=1;return 0;
}
static Status EFIAPI endpoint(void*this,uint8_t i,void*out){
 (void)this;uint8_t*p=out;for(unsigned j=0;j<7;j++)p[j]=0;
 p[0]=7;p[1]=5;p[2]=i==0?0x81:i==1?0x82:2;p[3]=i==0?3:2;p[4]=64;return i>2?EFI_ERROR(2):0;
}
static Status EFIAPI control(void*this,void*request,uint32_t dir,uint32_t ms,void*data,size_t n,uint32_t*result){
 (void)this;(void)request;(void)ms;if(dir!=1||n<3||pending)return EFI_ERROR(2);
 uint8_t*p=data;pending=p[0]|((uint16_t)p[1]<<8);*result=0;
 if(pending==0x0c03){if(connected||advertising)violations++;resets++;completed_packets=0;incoming_length=0;}
 if(pending==0x200a){advertising=p[3];if(advertising)conn_event=1;}
 return 0;
}
static Status EFIAPI interrupt(void*this,uint8_t ep,void*out,size_t*n,size_t ms,uint32_t*result){
 (void)this;(void)ms;if(ep!=0x81)return EFI_ERROR(2);*result=0;uint8_t*p=out;
 if(pending){
  if(pending==0x0406){uint8_t e[6]={0x0f,4,0,1,6,4};copy(p,e,6);*n=6;disconn_event=1;pending=0;return 0;}
  uint8_t e[9]={0x0e,4,1,(uint8_t)pending,(uint8_t)(pending>>8),0,0xfb,0,4};
  if(pending==0x2002){e[1]=7;*n=9;}else *n=6;
  copy(p,e,*n);pending=0;return 0;
 }
 if(disconn_event){uint8_t e[6]={5,4,0,0x40,0,0x13};copy(p,e,6);*n=6;disconn_event=0;connected=0;disconnects++;return 0;}
 if(conn_event){uint8_t e[21]={0x3e,19,1,0,0x40,0,1,0,0,0,0,0,0,0,24,0,0,0,200,0,0};copy(p,e,21);*n=21;conn_event=0;connected=1;advertising=0;return 0;}
 if(completed_packets){uint8_t e[7]={0x13,5,1,0x40,0,(uint8_t)completed_packets,(uint8_t)(completed_packets>>8)};copy(p,e,7);*n=7;completed_packets=0;return 0;}
 return EFI_ERROR(18);
}
static Status EFIAPI bulk(void*this,uint8_t ep,void*out,size_t*n,size_t ms,uint32_t*result){
 (void)this;(void)ms;*result=0;
#ifdef RABBIT_FAULT_TEST
 if(ep==0x82&&connected)return EFI_ERROR(7); /* Deliberate read failure. */
#endif
 /* These fixture replies fit one ACL packet: strict LE H->C first PB=00,
  * BC=00, exact connection handle. Never accept PB=10 like the old mock. */
 if(ep==2){uint8_t*p=out;if(*n<9||p[0]!=0x40||p[1]!=0||p[6]!=4||p[7])return EFI_ERROR(2);last_att=p[8];completed_packets++;return 0;}
 if(ep!=0x82||!incoming_length)return EFI_ERROR(18);
 if(*n<incoming_length)return EFI_ERROR(2);
 copy(out,incoming,incoming_length);*n=incoming_length;incoming_length=0;return 0;
}
static int install_mock(SystemTable*st){
 typedef Status(EFIAPI *Install)(void**,const Guid*,uint32_t,void*);void*handle=0;
 mock_io[0]=(void*)control;mock_io[1]=(void*)bulk;mock_io[3]=(void*)interrupt;
 mock_io[6]=(void*)descriptor;mock_io[8]=(void*)iface;mock_io[9]=(void*)endpoint;
 return ((Install)service(st,128))(&handle,&usb_guid,0,mock_io)!=0;
}
static int pump(void){for(unsigned i=0;i<20;i++)if(rabbit_test_radio_poll())return 1;return 0;}
static int att(const uint8_t*p,uint32_t n,uint8_t expected){
 if(n>247||incoming_length)return 1;
 incoming[0]=0x40;incoming[1]=0x20;incoming[2]=(uint8_t)(n+4);incoming[3]=(n+4)>>8;
 incoming[4]=(uint8_t)n;incoming[5]=n>>8;incoming[6]=4;incoming[7]=0;
 copy(incoming+8,p,n);incoming_length=n+8;last_att=0;
 return rabbit_test_radio_poll()||incoming_length||last_att!=expected;
}
static int write(uint8_t handle,const uint8_t*p,uint32_t n){
 uint8_t request[247]={0x12,handle,0};if(n>244)return 1;copy(request+3,p,n);return att(request,n+3,0x13);
}
static unsigned session_number;
static int stage(const uint8_t*stream,uint32_t n,uint8_t kind){
 uint8_t begin[16]={1,1,kind,0},chunk[244],commit[9]={2};
 begin[4]=++session_number;put32(begin+12,n);copy(commit+1,begin+4,8);
 uint8_t mtu[3]={2,247,0};
 if(att(mtu,3,3)||write(3,begin,16))return 1;
 for(uint32_t i=0;i<n;){uint32_t count=n-i;if(count>240)count=240;put32(chunk,i);copy(chunk+4,stream+i,count);
  if(write(5,chunk,count+4))return 1;
  i+=count;
 }
 if(write(3,commit,9))return 1;
 rabbit_test_status(status);return 0;
}
static int reject_unchanged(const uint8_t*stream,uint32_t n){
 uint32_t a=0,b=0;if(rabbit_test_snapshot(before,&a)||stage(stream,n,2)||status[20]!=RF_PENDING||rabbit_test_finish())return 1;
 rabbit_test_status(status);
 return status[20]!=RF_REJECTED||rabbit_test_snapshot(after,&b)||a!=b||!same(before,after,a)||!same(rabbit_test_base(),base_hash,32);
}
static int test(SystemTable*st){
 if(pump()||!connected||stage(world_stream,sizeof(world_stream),1)||status[20]!=RF_APPLIED)return 1;
 for(unsigned i=0;i<120;i++)if(rabbit_scene_tick(st))return 1;
 uint32_t a=0,b=0;if(rabbit_test_snapshot(before,&a))return 1;
 if(stage(a_stream,sizeof(a_stream),2)||status[20]!=RF_PENDING||!same(rabbit_test_base(),base_hash,32))return 1;
 if(rabbit_test_finish())return 1;
 rabbit_test_status(status);
 if(status[20]!=RF_APPLIED||le32(status+24)!=1||!same(rabbit_test_base(),a_hash,32)||disconnects!=1||pump())return 1;
 say("CONNECTED DRIVER A COMMITTED VIA MOCK USB ACL ATT; OLD CONNECTION CONFIRMED CLOSED; RECEIPT RETAINED");
 if(rabbit_test_snapshot(before,&a)||stage(a_stream,sizeof(a_stream),2)||rabbit_test_finish()||rabbit_test_snapshot(after,&b)||a!=b||!same(before,after,a)||disconnects!=1)return 1;
 say("EXACT NATIVE RETRY RECEIPT ONLY; NO SECOND APPLY OR DISCONNECT");
 if(stage(b_stream,sizeof(b_stream),2)||rabbit_test_finish())return 1;
 rabbit_test_status(status);
 if(status[20]!=RF_APPLIED||le32(status+24)!=2||!same(rabbit_test_base(),base_hash,32)||disconnects!=2||pump())return 1;
 say("CONNECTED DRIVER B COMMITTED IN SAME BOOT; WORLD AND COUNTER RETAINED");
 if(reject_unchanged(bad_stream,sizeof(bad_stream))||reject_unchanged(tampered_stream,sizeof(tampered_stream))||disconnects!=2||violations)return 1;
 say("FAILED HEALTH AND BAD OWNER SIGNATURE RETAIN EXACT WORLD AND LIVE DRIVER");
 return 0;
}
Status EFIAPI rabbit_entry(void*h,SystemTable*st){
 rabbit_supervisor_entry(h,st);
 if(install_mock(st)){say("FAIL MOCK INSTALL");return EFI_ERROR(2);}
#ifdef RABBIT_FAULT_TEST
 original_output=st->output;copy((uint8_t*)diagnostic_io,original_output,sizeof(diagnostic_io));
 diagnostic_io[1]=(void*)record_output;st->output=diagnostic_io;
 say("ACTUAL ROOT LOOP FAULT TEST; MOCK USB ONLY");
 rabbit_connected_run(h,st);say("FAIL FAULT LOOP RETURNED");return EFI_ERROR(2);
#endif
#ifdef RABBIT_LOOP_TEST
 say("ACTUAL ROOT LOOP STARTING; MOCK USB ONLY");
 if(rabbit_connected_run(h,st)||connected||advertising||violations){say("FAIL ROOT LOOP CLEANUP");return EFI_ERROR(2);}
 say("ACTUAL ROOT LOOP ESC CLEANUP PASS");
 typedef Status(EFIAPI *LoopStall)(uint64_t);
 for(;;)((LoopStall)service(st,248))(10000);
#endif
 if(rabbit_test_connected_boot(st)){say("FAIL CONNECTED BOOT");return EFI_ERROR(2);}
 say("CONNECTED BOOTSTRAP FALLBACK ACTIVE; MOCK USB ONLY");
 typedef Status(EFIAPI *ReadKey)(void*,void*);typedef Status(EFIAPI *Stall)(uint64_t);
 for(;;){
  uint16_t key[2]={0,0};
  if(!((ReadKey)*(void**)((uint8_t*)st->input+8))(st->input,key)){
   if(key[1]=='t'){if(test(st)){say("FAIL CONNECTED TEST");return EFI_ERROR(2);}say("CONNECTED NATIVE INTEGRATION PASS");}
   if(key[1]=='h'){say("STARTING SIGNED CONNECTED HUNG INIT");if(stage(hung_stream,sizeof(hung_stream),2)||rabbit_test_finish()){say("FAIL HUNG STAGE");return EFI_ERROR(2);}}
  }
  ((Stall)service(st,248))(10000);
 }
}
