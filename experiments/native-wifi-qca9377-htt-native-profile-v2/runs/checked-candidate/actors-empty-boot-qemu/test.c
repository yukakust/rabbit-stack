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
static unsigned lost_event;
static uint8_t diagnostic_reply[247];static size_t diagnostic_reply_size;
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
 p[0]=7;p[1]=5;p[2]=i==0?0x81:i==1?0x82:2;p[3]=i==0?3:2;p[4]=i==0?16:64;p[6]=i==0?1:0;return i>2?EFI_ERROR(2):0;
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
#ifdef RABBIT_FAULT_TEST
 /* Fixture-only malformed and unsupported events must remain visible even
  * though the existing parser ignores them. Do not "repair" parsing here. */
 static unsigned raw_probe;
 if(conn_event&&raw_probe<2){uint8_t e[4]={0x3e,raw_probe?2:19,raw_probe?10:1,0};
  copy(p,e,4);*n=4;raw_probe++;return 0;}
#endif


 if(conn_event&&resets>=3&&*n){
  uint8_t connection[21]={0x3e,19,1,0,0x40,0,1,0,0,0,0,0,0,0,24,0,0,0,200,0,0};
  if(!lost_event){copy(p,connection,16);*n=16;lost_event=1;return 0;}
  if(lost_event==1){copy(p,connection+16,5);*n=5;lost_event=2;connected=1;advertising=0;return 0;}
  if(lost_event==2){uint8_t e[6]={5,4,0,0x40,0,0x13};copy(p,e,6);*n=6;lost_event=3;conn_event=0;connected=advertising=0;return 0;}
 }
 if(conn_event){
  /* Synthetic latency threshold, not measured Dell firmware behavior. */
  if(ms<2){violations++;return EFI_ERROR(18);}
  uint8_t e[21]={0x3e,19,1,0,0x40,0,1,0,0,0,0,0,0,0,24,0,0,0,200,0,0};copy(p,e,21);*n=21;conn_event=0;connected=1;advertising=0;return 0;}
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
 if(ep==2){uint8_t*p=out;if(*n<9||p[0]!=0x40||p[1]!=0||p[6]!=4||p[7])return EFI_ERROR(2);last_att=p[8];diagnostic_reply_size=*n-8;if(diagnostic_reply_size>247)return EFI_ERROR(2);copy(diagnostic_reply,p+8,diagnostic_reply_size);completed_packets++;return 0;}
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
uint32_t rabbit_test_background(void); int rabbit_test_city_display(void); uint32_t rabbit_test_display_hash(void);
static int test(SystemTable*st){
 if(pump()||!connected)return 1;
 for(unsigned i=0;i<120;i++)if(rabbit_scene_tick(st))return 1;
 uint32_t a=0,b=0;if(rabbit_test_snapshot(before,&a))return 1;
 if(stage(a_stream,sizeof(a_stream),2)||status[20]!=RF_PENDING||!same(rabbit_test_base(),base_hash,32))return 1;
 if(rabbit_test_finish())return 1;
 rabbit_test_status(status);
 if(status[20]!=RF_APPLIED||le32(status+24)!=1||!same(rabbit_test_base(),a_hash,32)||disconnects!=1||pump())return 1;
 if(rabbit_scene_tick(st)||rabbit_test_background()!=0x121826)return 1;
 say("CONNECTED DRIVER A COMMITTED VIA MOCK USB ACL ATT; OLD CONNECTION CONFIRMED CLOSED; RECEIPT RETAINED");
 if(rabbit_test_snapshot(before,&a)||stage(a_stream,sizeof(a_stream),2)||rabbit_test_finish()||rabbit_test_snapshot(after,&b)||a!=b||!same(before,after,a)||disconnects!=1)return 1;
 if(lost_event!=3)return 1;
 say("FRAGMENTED16+5 CONNECTION AND MATCHED DISCONNECTION VERIFIED THROUGH ACTUAL UEFI USB; NO ORPHAN GUESSING");
 say("EXACT NATIVE RETRY RECEIPT ONLY; NO SECOND APPLY OR DISCONNECT");
 if(stage(legacy_city_stream,sizeof(legacy_city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=3)return 1;
 if(stage(upgrade_stream,sizeof(upgrade_stream),2)||rabbit_test_finish()||pump())return 1;
 rabbit_test_status(status);if(status[20]!=RF_APPLIED||le32(status+24)!=2||disconnects!=2)return 1;
 say("ACTOR DRIVER RESTORED ACTUAL CITY4 SNAPSHOT");
 if(stage(city_stream,sizeof(city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=4)return 1;
 if(rabbit_scene_tick(st))return 1;
 uint32_t hash=rabbit_test_display_hash();
 typedef Status(EFIAPI *ActorStall)(uint64_t);((ActorStall)service(st,248))(600000);
 if(rabbit_scene_tick(st)||hash==rabbit_test_display_hash())return 1;
 say("ACTOR MOTION ADVANCED BY TARGET CLOCK WITHOUT FRAME COUNT TIMING");
 ((ActorStall)service(st,248))(9450000);
 if(rabbit_scene_tick(st)||rabbit_test_city_display())return 1;
 if(rabbit_test_snapshot(before,&a)||before[20]||before[36]!=5||le32(before+12)!=4)return 1;
 
 uint8_t request_pci[3]={0x0a,10,0};
 if(att(request_pci,3,0x0b)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QPD\22",4))return 1;
 /* Actual OVMF enumerator, QCA absent: positive flags/count, no guessed device. */
 if(le32(diagnostic_reply+5)!=1||!le32(diagnostic_reply+17)||le32(diagnostic_reply+21))return 1;
 
 uint8_t joined_prefix[716];copy(joined_prefix,diagnostic_reply+1,246);
 if(le32(diagnostic_reply+129)!=7||le32(diagnostic_reply+141)!=1)return 1;
 uint8_t blob[5]={0x0c,10,0,246,0};
 if(att(blob,5,0x0d)||diagnostic_reply_size!=247)return 1;
 for(unsigned i=0;i<246;i++)if(diagnostic_reply[i+1])return 1;
 copy(joined_prefix+246,diagnostic_reply+1,246);
 uint8_t final_blob[5]={0x0c,10,0,236,1};
 if(att(final_blob,5,0x0d)||diagnostic_reply_size!=225)return 1;
 for(unsigned i=0;i<224;i++)if(diagnostic_reply[i+1])return 1;
 copy(joined_prefix+492,diagnostic_reply+1,224);
 uint8_t extension[3]={0x0a,12,0};if(att(extension,3,0x0b)||diagnostic_reply_size!=245)return 1;
 if(!same(diagnostic_reply+1,(const uint8_t*)"QIC\1",4))return 1;
 void rabbit_sha256(uint8_t*,const uint8_t*,size_t);uint8_t expected_hash[32];rabbit_sha256(expected_hash,joined_prefix,716);
 if(!same(diagnostic_reply+5,expected_hash,32))return 1;
 for(unsigned i=0;i<208;i++)if(diagnostic_reply[37+i])return 1;
 uint8_t bad_blob[5]={0x0c,10,0,205,2};if(att(bad_blob,5,1))return 1;
 uint8_t bad_extension[5]={0x0c,12,0,245,0};if(att(bad_extension,5,1))return 1;
 
 uint8_t ram_service[7]={0x10,13,0,255,255,0,0x28};
 if(att(ram_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=13||diagnostic_reply[4]!=19||diagnostic_reply[6]!=7)return 1;
 uint8_t ram_status[3]={0x0a,19,0};if(att(ram_status,3,0x0b)||diagnostic_reply_size!=65||!same(diagnostic_reply+1,(const uint8_t*)"RFCS0001",8))return 1;
 for(unsigned i=9;i<65;i++)if(diagnostic_reply[i])return 1;
 uint8_t no_ram_write[47]={0x12,15,0,'R','F','C','1',1};if(att(no_ram_write,47,1))return 1;
 
 uint8_t boot_service[7]={0x10,20,0,255,255,0,0x28};
 if(att(boot_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=20||diagnostic_reply[4]!=22||diagnostic_reply[6]!=0x22)return 1;
 uint8_t boot_status[3]={0x0a,22,0};if(att(boot_status,3,0x0b)||diagnostic_reply_size!=161||!same(diagnostic_reply+1,(const uint8_t*)"QWBT0001",8))return 1;
 uint8_t boot_write[4]={0x12,22,0,0};if(att(boot_write,4,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
 
 uint8_t init_service[7]={0x10,26,0,255,255,0,0x28};
 if(att(init_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=26||diagnostic_reply[4]!=28||diagnostic_reply[6]!=0x26)return 1;
 uint8_t init_status[3]={0x0a,28,0};if(att(init_status,3,0x0b)||diagnostic_reply_size!=245||!same(diagnostic_reply+1,(const uint8_t*)"QWIN0002",8))return 1;
 for(unsigned i=9;i<245;i++)if(diagnostic_reply[i])return 1;
 uint8_t init_write[4]={0x12,28,0,0};if(att(init_write,4,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
 
 uint8_t hs[7]={0x10,29,0,255,255,0,0x28};
 if(att(hs,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=29||diagnostic_reply[4]!=31||diagnostic_reply[6]!=0x2e)return 1;
 uint8_t hr[5]={0x0a,31,0,0,0};
 if(att(hr,3,0x0b)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QHTT0001",8))return 1;
 for(unsigned j=9;j<247;j++)if(diagnostic_reply[j]!=(j==225?56:0))return 1;
 hr[0]=0x0c;hr[3]=246;if(att(hr,5,0x0d)||diagnostic_reply_size!=75)return 1;
 for(unsigned j=1;j<75;j++)if(diagnostic_reply[j])return 1;
 hr[3]=65;hr[4]=1;if(att(hr,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
 hs[1]=32;if(att(hs,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=32||diagnostic_reply[4]!=92||diagnostic_reply[6]!=0x30)return 1;
 for(unsigned slot=0;slot<6;slot++){
  hr[0]=0x0a;hr[1]=(uint8_t)(34+10*slot);hr[3]=hr[4]=0;
  if(att(hr,3,0x0b)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QHTX0001",8)||diagnostic_reply[9]!=slot)return 1;
  for(unsigned j=10;j<247;j++)if(diagnostic_reply[j])return 1;
  hr[0]=0x0c;hr[3]=0;hr[4]=2;if(att(hr,5,0x0d)||diagnostic_reply_size!=1)return 1;
  hr[3]=1;if(att(hr,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
  for(unsigned page=1;page<5;page++){hr[0]=0x0a;hr[1]=(uint8_t)(34+10*slot+2*page);
   if(att(hr,3,0x0b)||diagnostic_reply_size!=(page==4?57u:247u))return 1;
   for(unsigned j=1;j<diagnostic_reply_size;j++)if(diagnostic_reply[j])return 1;
   hr[0]=0x12;if(att(hr,3,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
  }
 }
 say("HTT56 READ-ONLY STATUS29..31 RAW32..92; ABSENT RADIO NO VERSION OR DATA-PLANE CLAIM");
say("WMI INIT SERVICE26..28 READ ONLY; ABSENT RADIO CLAIMS NO READY/MAC/IP");

 uint8_t op_service[7]={0x10,23,0,255,255,0,0x28};
 if(att(op_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=23||diagnostic_reply[4]!=25||diagnostic_reply[6]!=0x24)return 1;
 uint8_t op_status[3]={0x0a,25,0};if(att(op_status,3,0x0b)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QWOP0003",8))return 1;
 for(unsigned i=9;i<247;i++)if(diagnostic_reply[i])return 1;
 uint8_t op_write[4]={0x12,25,0,0};if(att(op_write,4,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
 uint8_t op_second[5]={0x0c,25,0,246,0};if(att(op_second,5,0x0d)||diagnostic_reply_size!=243)return 1;
 for(unsigned i=1;i<243;i++)if(diagnostic_reply[i])return 1;
 uint8_t op_blob[5]={0x0c,25,0,232,1};if(att(op_blob,5,0x0d)||diagnostic_reply_size!=1)return 1;
 op_blob[3]=233;if(att(op_blob,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
 say("OPERATING SERVICE23..25 READ ONLY; ABSENT TARGET DOES NOT CLAIM SERVICE READY OR WIFI");
 say("BOOT SERVICE20..22 READ ONLY; RAM SERVICE PRESERVED; CITY RETAINED");
 say("INTEGRATED RAM SERVICE13..19; TARGET ABSENT WRITE REJECTED; CITY RETAINED");
 say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");
 say("LONG QPD17 READ/BLOB BOUNDS PASS; QCA ABSENT; NO IRQ WRITES");
 say("ONE-SHOT WIFI RESET PROBE TARGET ABSENT; CLEAN CLOSE AND CITY RETAINED");
 
 say("CITY FULLSCREEN QEMU READY");
 
 typedef Status(EFIAPI *CityRead)(void*,void*);
 for(;;){uint16_t key[2]={0,0};if(!((CityRead)*(void**)((uint8_t*)st->input+8))(st->input,key)&&key[1]=='g')break;((ActorStall)service(st,248))(10000);}
 if(stage(actor_restore_stream,sizeof(actor_restore_stream),2)||rabbit_test_finish()||pump())return 1;
 rabbit_test_status(status);if(status[20]!=RF_APPLIED||le32(status+24)!=3||disconnects!=3)return 1;
 say("ACTOR DRIVER RESTORED ACTUAL CITY5 SNAPSHOT");
 if(stage(restored_stream,sizeof(restored_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=5)return 1;
 for(unsigned i=0;i<10;i++)if(rabbit_scene_tick(st))return 1;
 say("CITY DATA APPLIED AND LEGACY DATA RESTORED BEFORE ENGINE ROLLBACK");

 if(stage(b_stream,sizeof(b_stream),2)||rabbit_test_finish())return 1;
 rabbit_test_status(status);
 if(status[20]!=RF_APPLIED||le32(status+24)!=4||!same(rabbit_test_base(),base_hash,32)||disconnects!=4||pump())return 1;
 say("CONNECTED DRIVER B COMMITTED IN SAME BOOT; WORLD AND COUNTER RETAINED");
 if(reject_unchanged(bad_stream,sizeof(bad_stream))||reject_unchanged(tampered_stream,sizeof(tampered_stream))||disconnects!=4||violations)return 1;
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
