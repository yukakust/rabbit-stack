#include "htt_native.h"
#include "firmware_op.h"
const QcaHttNative*qca_htt_native_view(void);
const QcaHttFirmwareProof*qca_htt_firmware_view(void);
void qca_htt_status(uint8_t[320]);
unsigned qca_htt_profile_export(unsigned,uint8_t*,unsigned);
size_t qca_htt_profile_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);
#define query (*((QcaHttNative*)qca_htt_native_view()))
static unsigned htt_stale_injected,htt_response_delivered;static void deliver_htt(unsigned);static unsigned getle(const uint8_t*p){return p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24);}
#include "htt_native.h"
#include "persistent.h"
const QcaPersistentNative*qca_persistent_view(void);
#define FW_WMI_TX 3
#include "startup.h"
const QcaWmiStartup*qca_wmi_startup_view(void);
size_t qca_wmi_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);
#include "operating.h"
const QcaOperating*qca_operating_view(void);
#include "boot_native.h"
#include "boot_assets.h"
const QcaBootNative*qca_boot_view(void);
unsigned qca_boot_round(void);
void qca_boot_status(uint8_t[160]);
static unsigned fault;static unsigned startup_fault,init_posts;static unsigned persistent_fault,active_ticks,stopped;static unsigned rx_scenario;static unsigned htt_scenario,htt_started,htt_posts;static QcaHttNative rival;static unsigned control_tx,rx_ready_sent,available_delivered;
#include "sha256.h"
#define main port_previous_main
#define read_config old_read_config
#define mem_read old_mem_read
#define mem_write old_mem_write
#include "port_test.c"
#undef main
#undef read_config
#undef mem_read
#undef mem_write
#include "bringup.h"
#include "firmware_port.h"
#include <stdlib.h>
const QcaFirmwarePort*qca_ram_view(void);
size_t qca_ram_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);
#include "reset_core.h"
#include "diag_ce.h"
#include <stdlib.h>
uint8_t qca_diagnostic[924];void*qca_controller;
static unsigned scenario,reset_writes,reset_cleared,allocations,dma_frees,unmaps,flushes;
static _Alignas(4096) uint8_t hosts[14][4096];
static uint32_t registers[8][32];static uint16_t link_control=0x143;static uint32_t boot_regs[6]={0x12300e88};static unsigned mask_attempts,link_disables,msi_toggled;static uint32_t reset_register;
static uint64_t now_us,last_reset_write;
static uint32_t warm_register,warm_lf=0x14,fw=2,warm_cpus;static unsigned warm_write_failed;
static uint32_t get(unsigned i){return qca_diagnostic[i]|((uint32_t)qca_diagnostic[i+1]<<8)|((uint32_t)qca_diagnostic[i+2]<<16)|((uint32_t)qca_diagnostic[i+3]<<24);}
static uint32_t bw(const uint8_t*p){uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
static void bp(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static unsigned streams,stream_bytes,stream_open,executions,main_done,uart_off,board_written,board_read;
static uint8_t target_ram[65536];
static void reset_target(void){
 memset(target_ram,0,sizeof(target_ram));const uint32_t words[9]={0x404d90,0x404e50,8,0,0,0,0,3,1};
 for(unsigned i=0;i<9;i++){bp(target_ram+0x1ee0+4*i,words[i]);}
 bp(target_ram+0x8f8,0x401ee0);
 bp(target_ram+0x854,fault==4?0: fault==5?0x404d90:0x408000);
}static unsigned cpu_issued;
static Status EFIAPI read_config(void*p,uint32_t width,uint32_t offset,uint64_t count,void*out){
 if(count==1&&width==1&&(offset==0x52||offset==0xb2)){*(uint16_t*)out=offset==0x52?((scenario==21||(scenario==33&&msi_toggled))?1:0):(scenario==22?0x8000:0);return 0;}
 if(count==1&&width==1&&offset==0x80){*(uint16_t*)out=link_control;return 0;}
 if(count!=64)return old_read_config(p,width,offset,count,out);
 assert(p==pci&&width==2&&!offset);memset(out,0,256);memcpy(out,config,64);
 uint32_t*c=out;c[1]|=0x00100000;c[13]=0x40;c[16]=0x5001;c[20]=0x7005|((scenario==21?1u:0u)<<16);c[44]=0x11|((scenario==22?0x8000u:0u)<<16);c[17]=scenario==3?3:0;c[28]=scenario==20?0:0x0002b010;c[32]=0xabcd0000|link_control;return 0;
}
static Status EFIAPI mem_read(void*p,uint32_t width,uint8_t bar,uint64_t off,uint64_t count,void*out){
 if(htt_scenario==12&&!htt_stale_injected&&!query.attempted&&off==0x34848&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE){htt_stale_injected=1;deliver_htt(0);}

 assert(p==pci&&width==2&&!bar&&count==1);
 if(reset_writes)assert(now_us-last_reset_write>=20000);
 if(off==0x80008){mem_reads++;*(uint32_t*)out=reset_register;return 0;}
 if(off>=0x3a000&&off<=0x3a014){if(off==0x3a000&&allocations==4&&scenario==41)return EFI_ERROR(7);*(uint32_t*)out=(off==0x3a000&&allocations==4&&scenario==42)?0xffffffffu:(off==0x3a000&&allocations==4&&scenario==45)?0x12300e89:boot_regs[(off-0x3a000)/4];return 0;}
 if(off==0x800){*(uint32_t*)out=warm_register;return 0;}
 if(off==0x850){*(uint32_t*)out=warm_lf;return 0;}
 if(off==0x3a028){mem_reads++;*(uint32_t*)out=scenario==11?0:fw;return 0;}
 if(off>=0x34400&&off<=0x36050){unsigned id=(unsigned)(off-0x34400)/0x400,index=(unsigned)(off-0x34400)%0x400;assert(id<8&&index<=0x50);if(scenario==35&&id==2&&index==8&&!registers[id][0x18/4])return EFI_ERROR(7);*(uint32_t*)out=scenario==36&&id==3&&index==8&&!registers[id][0x18/4]?0xffffffffu:registers[id][index/4];return 0;}
 if(off==0x8f0){mem_reads++;*(uint32_t*)out=scenario==2?0x200:scenario==1&&!reset_cleared?0:scenario==6?0:0x003821ff;return 0;}
 return old_mem_read(p,width,bar,off,count,out);
}
static Status EFIAPI mem_write(void*p,uint32_t width,uint8_t bar,uint64_t off,uint64_t count,void*in){
 if(reset_writes)assert(now_us-last_reset_write>=20000);
 if(off>=0x3a000&&off<=0x3a014){
  assert(config[1]&0x400);uint32_t v=*(uint32_t*)in;unsigned index=(unsigned)(off-0x3a000)/4;
  if(scenario==24&&off==0x3a008&&v==0x7fc00)return 0;
  if(scenario==27&&off==0x3a000&&(v&0x800))return 0;
  if(off==0x3a014){assert(!boot_regs[2]);if(scenario!=32)boot_regs[3]&=~v;return scenario==26?EFI_ERROR(7):0;}
  if(off==0x3a000&&(v&0x2000)){cpu_issued=1;assert(get(292)==31&&get(296)==31);if(scenario==243)config[1]&=~4u;v&=~0x2000u;}boot_regs[index]=v;if(off==0x3a008&&v==0x7fc00){boot_regs[3]|=0x400;if(scenario==33)msi_toggled=1;}return 0;
 }
 if(off>=0x34400&&off<=0x36050){
  assert(p==pci&&width==2&&!bar&&count==1);unsigned id=(unsigned)(off-0x34400)/0x400,index=(unsigned)(off-0x34400)%0x400;assert(id<8&&index<=0x50);
  uint32_t value=*(uint32_t*)in;
  if(index==0x18)registers[id][index/4]=value?9:0;
  else if(index==0x30||index==0x38)registers[id][index/4]&=~value;
  else registers[id][index/4]=value;
  if(id==7&&index==0x3c&&(config[1]&4)){
   unsigned si=(value-1)&7,ri=(registers[7][0x40/4]-1)&7;
   const uint8_t*tx=hosts[10]+si*8;uint8_t*rx=hosts[12]+ri*8;
   uint32_t src=0,dst=0;for(unsigned j=0;j<4;j++){src|=(uint32_t)tx[j]<<(j*8);dst|=(uint32_t)rx[j]<<(j*8);}
   unsigned bytes=tx[4]|((unsigned)tx[5]<<8);int write=src==0x10b000;
   uint32_t address=(write?dst:src);assert(address>=0xd1100000&&address<0xd1110000);
   unsigned offset=address&0xffff;
   assert(allocations==14&&boot_regs[2]==0&&!(boot_regs[0]&0x800)&&!tx[6]&&!tx[7]);
   assert(write||dst==0x10d000);assert(bytes<=204);
   int setup=get(280)==1||write;unsigned op=get(288);
   if(write){
    assert(setup&&!(op&1)&&get(300)<=5);
    if(offset==0x8cc)assert(op==8&&get(292)==15&&get(296)==15);
    for(unsigned j=0;j<bytes;j++)target_ram[offset+j]=hosts[11][j];
   }
   int timeout=scenario==101||scenario==102||(scenario==106&&offset==0x1ee0)||(scenario==107&&offset==0x900)||(scenario==108&&offset==0x8cc)||(scenario>=200&&scenario<=209&&setup&&op==(unsigned)(scenario-200));
   if(scenario!=101)registers[7][0x44/4]=value;
   if(!timeout){
    registers[7][0x48/4]=registers[7][0x40/4];
    rx[4]=(scenario==103||(scenario==109&&offset==0x1ee0))?5:(uint8_t)bytes;
    if(!write){for(unsigned j=0;j<bytes;j++)hosts[13][j]=target_ram[offset+j];
     if(scenario==104&&offset==0x8f8)hosts[13][1]=0x20;
     if(scenario>=210&&scenario<=214&&setup&&op==(unsigned)(2*(scenario-210)+1))hosts[13][0]^=1;
    }
   }
   if(scenario==105||(scenario==110&&offset==0x1ee0))config[1]&=~4u;
  }






  if(main_done&&id==3&&index==0x3c&&htt_scenario>=21){
   const QcaBootNative*b=qca_boot_view();QcaFirmwareChunks*a=b->asset;
   if(htt_scenario==21)a->memory[0]^=1;
   if(htt_scenario==22){for(unsigned at=12;at<a->policy.total;){unsigned tag=getle(a->memory+at),n=getle(a->memory+at+4);at+=8;if(tag==6){a->memory[at]^=1;break;}at+=(n+3)&~3u;}}
   if(htt_scenario==23)((QcaBootNative*)b)->plan.assets.main++;
  }
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==4&&index==0x3c&&query.attempted){
   htt_posts++;assert(htt_posts==1&&query.attempted==1);
   const QcaPersistentNative*p=qca_persistent_view();const uint8_t*b=hosts[9];
   assert(b[0]==p->startup->operating->control.session.htt.endpoint&&!b[1]&&b[2]==4&&!b[3]);
   assert(!b[8]&&!b[9]&&!b[10]&&!b[11]);
   unsigned ri=(value-1)&7;assert((hosts[8][ri*8+6]|((unsigned)hosts[8][ri*8+7]<<8))==(unsigned)b[0]*4);
   if(htt_scenario!=1)registers[4][0x44/4]=value;
   if(htt_scenario==3){QcaInitAdapter*a=p->startup->operating->boot->board->setup->read.full.adapter;a->channels.rings[4].cookie[ri]^=1;}
   if(htt_scenario==4)hosts[8][ri*8]^=1;
   if(htt_scenario==5)hosts[8][ri*8+4]^=1;
   if(htt_scenario==6)registers[4][0x44/4]=(value+1)&7;
   if(htt_scenario==2)return 1;return 0;
  }
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&(id==1||id==2)&&index==0x40){
   if(rx_scenario==13&&active_ticks>=20&&id==2)return 1;
   return 0;
  }
  if(main_done&&qca_wmi_startup_view()->phase==1){
   if(id==0&&index==0x3c)assert(!"WMI INIT incorrectly sent on CE0");
   if(id==1&&index==0x40)return 0;
   if(id==2&&index==0x40){
    if(startup_fault==9)return 1;
    if(startup_fault==14&&qca_wmi_startup_view()->transaction.ready_seen){

   unsigned ri=(registers[2][0x40/4]-1)&7;uint8_t*p=hosts[5];memset(p,0,2048);
   p[0]=1;p[2]=44;bp(p+8,2);bp(p+12,36|(35u<<16));
   bp(p+16,startup_fault==4?0:0x01000000);bp(p+20,startup_fault==15?53:574);
   bp(p+24,startup_fault==16?0:0x5f414351);bp(p+28,0x4c4d);p[40]=startup_fault==6?1:2;p[45]=1;
   bp(p+48,startup_fault==5?1:0);
   unsigned length=52;
   if(startup_fault==22){bp(p+12,52|(35u<<16));p[2]=60;length=68;}
   if(startup_fault==0||startup_fault==13){
    p[1]=2;p[2]=52;p[4]=8;p[52]=1;p[53]=4;p[56]=1;p[57]=startup_fault==13?3:1;length=60;
   }
   if(startup_fault==17)p[0]=2;
   hosts[4][ri*8+4]=(uint8_t)length;hosts[4][ri*8+5]=0;registers[2][0x48/4]=registers[2][0x40/4];

    }
    return 0;
   }
   if(id==FW_WMI_TX&&index==0x3c){
    const uint8_t*t=hosts[7];init_posts++;assert(init_posts==1&&t[0]==1&&t[1]==1);
    assert((t[2]|((unsigned)t[3]<<8))==220&&t[8]==1&&!t[9]&&!t[10]&&!t[11]);
    unsigned ti=(value-1)&7;assert((hosts[6][ti*8+6]|((unsigned)hosts[6][ti*8+7]<<8))==4);
    /* Exact reference resource words and no extra mapped host chunks. */
    assert(t[48]==4&&t[52]==33&&t[40]==0&&t[41]==0&&t[42]==0&&t[43]==0);
    if(startup_fault!=1&&startup_fault!=3&&startup_fault!=14)registers[FW_WMI_TX][0x44/4]=value;
    if(startup_fault!=2){

   unsigned ri=(registers[2][0x40/4]-1)&7;uint8_t*p=hosts[5];memset(p,0,2048);
   p[0]=1;p[2]=44;bp(p+8,2);bp(p+12,36|(35u<<16));
   bp(p+16,startup_fault==4?0:0x01000000);bp(p+20,startup_fault==15?53:574);
   bp(p+24,startup_fault==16?0:0x5f414351);bp(p+28,0x4c4d);p[40]=startup_fault==6?1:2;p[45]=1;
   bp(p+48,startup_fault==5?1:0);
   unsigned length=52;
   if(startup_fault==22){bp(p+12,52|(35u<<16));p[2]=60;length=68;}
   if(startup_fault==0||startup_fault==13){
    p[1]=2;p[2]=52;p[4]=8;p[52]=1;p[53]=4;p[56]=1;p[57]=startup_fault==13?3:1;length=60;
   }
   if(startup_fault==17)p[0]=2;
   hosts[4][ri*8+4]=(uint8_t)length;hosts[4][ri*8+5]=0;registers[2][0x48/4]=registers[2][0x40/4];

    }
    if(startup_fault==7){QcaWmiStartup*w=(QcaWmiStartup*)qca_wmi_startup_view();w->operating->boot->board->setup->read.full.adapter->channels.rings[3].cookie[(value-1)&7]=0x999;}
    if(startup_fault==8)return 1; /* Ambiguous INIT TX doorbell. */
    return 0;
   }
  }
  if(main_done&&id==2&&index==0x40&&available_delivered){
   if(fault==34)return 1; /* Ambiguous rearm: retain DMA until actual stop. */
   if(fault==31)return 0; /* No READY after valid prelude. */
   if(fault==27){
    unsigned ri=(value-1)&7;uint8_t*p=hosts[5];memset(p,0,2048);p[0]=1;p[2]=28;
    bp(p+8,3);bp(p+12,20|(559u<<16));bp(p+16,128);
    hosts[4][ri*8+4]=36;registers[2][0x48/4]=value;return 0;
   }
     unsigned ri=(value-1)&7;uint8_t*p=hosts[5];memset(p,0,2048);p[0]=fault==12?2:1;p[2]=164;
    bp(p+8,1);bp(p+12,104|(32u<<16));bp(p+16,1234);bp(p+20,0x01000000);bp(p+24,53);bp(p+28,0x5f414351);bp(p+32,0x4c4d);bp(p+52,1);
    bp(p+120,36|(33u<<16));bp(p+124,0x60);bp(p+144,2412);bp(p+148,2472);bp(p+152,5180);bp(p+156,5825);
    bp(p+160,4|(16u<<16));bp(p+164,1);bp(p+168,18u<<16);
    if(fault==13)bp(p+20,0);
    hosts[4][ri*8+4]=172;hosts[4][ri*8+5]=0;registers[2][0x48/4]=registers[2][0x40/4];

    if(fault>=35){
     const uint8_t captured[256]={1,0,56,1,0,4,0,0,1,0,0,0,128,0,32,0,21,0,0,0,0,0,0,1,62,2,0,0,81,67,65,95,77,76,0,0,0,0,0,0,0,0,0,0,3,0,0,0,10,0,0,0,1,0,0,0,91,8,0,0,178,17,144,51,254,255,0,0,63,0,0,0,63,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,68,0,0,0,1,0,0,0,0,0,0,0,6,64,1,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,189,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,36,0,33,0,108,0,0,0,63,0,0,0,7,0,0,0,192,11,0,0,13,248,127,0,8,9,0,0,172,10,0,0,56,19,0,0,212,23,0,0,128,0,16,0,13,0,0,0,7,0,0,0,15,0,0,0,3,0,0,0,15,0,0,0,15,0,0,0,11,0,0,0,15,0,0,0,11,0,0,0,11,0,0,0,0,0,0,0,10,0,0,0,0,0,0,0,4,0,0,0,7,0,0,0,14,0,0,0,10,0,0,0};memcpy(p,captured,256);memset(p+256,0,64);bp(p+316,18u<<16);
     hosts[4][ri*8+4]=64;hosts[4][ri*8+5]=1;
     if(fault==36)bp(p+88,1);
     if(fault==37)bp(p+12,132|(32u<<16));
     if(fault==38)bp(p+172,2801);
     if(fault==39)bp(p+52,5);
     if(fault==40)bp(p+20,0);
     if(startup_fault==11){
      bp(p+88,1);bp(p+316,20|(18u<<16));bp(p+320,16|(34u<<16));
      bp(p+324,0);bp(p+328,8);bp(p+332,0);bp(p+336,1);
      p[2]=76;p[3]=1;hosts[4][ri*8+4]=84;hosts[4][ri*8+5]=1;
     }
     if(startup_fault==12){bp(p+184,4|(16u<<16));bp(p+192,18u<<16);p[2]=188;p[3]=0;hosts[4][ri*8+4]=196;hosts[4][ri*8+5]=0;}

    }
  return 0;
 }
  if(main_done&&id==0&&index==0x3c&&(config[1]&4)){
   const uint8_t*t=hosts[1];assert(!t[0]&&t[1]==0);unsigned msg=t[8]|((unsigned)t[9]<<8);control_tx++;
   assert(control_tx<=3&&msg==(control_tx==3?5u:2u));
   unsigned ti=(value-1)&7;assert((hosts[0][ti*8+6]|((unsigned)hosts[0][ti*8+7]<<8))==0);
   if(fault!=8&&(fault!=16||control_tx==3))registers[0][0x44/4]=value;
   if(control_tx<3&&fault!=9){
    unsigned service=t[10]|((unsigned)t[11]<<8);assert(service==(control_tx==1?0x100u:0x300u));
    unsigned ri=(registers[1][0x40/4]-1)&7;memset(hosts[3],0,20);hosts[3][2]=12;hosts[3][8]=3;
    hosts[3][10]=(uint8_t)service;hosts[3][11]=(uint8_t)(service>>8);hosts[3][13]=control_tx==1?1:2;hosts[3][14]=0xf8;hosts[3][15]=0x0f;
    if(fault==10)hosts[3][13]=0;
    hosts[2][ri*8+4]=20;hosts[2][ri*8+5]=0;registers[1][0x48/4]=registers[1][0x40/4];
    if(fault==17)hosts[2][ri*8+4]=7;
    if(fault==18)hosts[3][2]=13; /* Body length exceeds actual DMA completion. */
    if(fault==19)hosts[3][8]=1; /* Unexpected READY instead of CONNECT response. */
    if(fault==20)hosts[2][ri*8]^=4; /* Descriptor address disagreement. */
    if(fault==21)registers[1][0x48/4]=8; /* Invalid hardware index. */
    if(fault==22)hosts[3][16]=1; /* Unknown nonzero extension rejected. */
    if(fault==23){hosts[3][2]=10;hosts[2][ri*8+4]=18;}
    if(fault==24){hosts[3][2]=8;hosts[2][ri*8+4]=16;} /* Legacy8 remains valid. */
    if(fault==25)hosts[3][12]=1; /* Non-success status rejected. */
    if(fault==26)hosts[3][10]=1; /* Foreign service rejected. */
 
 
   }
   if(control_tx==1&&fault!=11){
    if(fault==32){
    unsigned ri=(registers[2][0x40/4]-1)&7;uint8_t*p=hosts[5];memset(p,0,2048);p[0]=fault==12?2:1;p[2]=164;
    bp(p+8,1);bp(p+12,104|(32u<<16));bp(p+16,1234);bp(p+20,0x01000000);bp(p+24,53);bp(p+28,0x5f414351);bp(p+32,0x4c4d);bp(p+52,1);
    bp(p+120,36|(33u<<16));bp(p+124,0x60);bp(p+144,2412);bp(p+148,2472);bp(p+152,5180);bp(p+156,5825);
    bp(p+160,4|(16u<<16));bp(p+164,1);bp(p+168,18u<<16);
    if(fault==13)bp(p+20,0);
    hosts[4][ri*8+4]=172;hosts[4][ri*8+5]=0;registers[2][0x48/4]=registers[2][0x40/4];

    if(fault>=35){
     const uint8_t captured[256]={1,0,56,1,0,4,0,0,1,0,0,0,128,0,32,0,21,0,0,0,0,0,0,1,62,2,0,0,81,67,65,95,77,76,0,0,0,0,0,0,0,0,0,0,3,0,0,0,10,0,0,0,1,0,0,0,91,8,0,0,178,17,144,51,254,255,0,0,63,0,0,0,63,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,68,0,0,0,1,0,0,0,0,0,0,0,6,64,1,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,189,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,36,0,33,0,108,0,0,0,63,0,0,0,7,0,0,0,192,11,0,0,13,248,127,0,8,9,0,0,172,10,0,0,56,19,0,0,212,23,0,0,128,0,16,0,13,0,0,0,7,0,0,0,15,0,0,0,3,0,0,0,15,0,0,0,15,0,0,0,11,0,0,0,15,0,0,0,11,0,0,0,11,0,0,0,0,0,0,0,10,0,0,0,0,0,0,0,4,0,0,0,7,0,0,0,14,0,0,0,10,0,0,0};memcpy(p,captured,256);memset(p+256,0,64);bp(p+316,18u<<16);
     hosts[4][ri*8+4]=64;hosts[4][ri*8+5]=1;
     if(fault==36)bp(p+88,1);
     if(fault==37)bp(p+12,132|(32u<<16));
     if(fault==38)bp(p+172,2801);
     if(fault==39)bp(p+52,5);
     if(fault==40)bp(p+20,0);
     if(startup_fault==11){
      bp(p+88,1);bp(p+316,20|(18u<<16));bp(p+320,16|(34u<<16));
      bp(p+324,0);bp(p+328,8);bp(p+332,0);bp(p+336,1);
      p[2]=76;p[3]=1;hosts[4][ri*8+4]=84;hosts[4][ri*8+5]=1;
     }
     if(startup_fault==12){bp(p+184,4|(16u<<16));bp(p+192,18u<<16);p[2]=188;p[3]=0;hosts[4][ri*8+4]=196;hosts[4][ri*8+5]=0;}

    }
    }else{

    unsigned ri=(registers[2][0x40/4]-1)&7;uint8_t*p=hosts[5];memset(p,0,2048);p[0]=1;p[2]=28;p[5]=3;
    bp(p+8,fault==30?4:3);bp(p+12,20|((fault==28?560u:559u)<<16));bp(p+16,fault==29?127:128);bp(p+20,0x08000000);
    unsigned length=36;
    if(fault==33){p[1]=2;p[2]=36;p[4]=8;p[36]=1;p[37]=4;p[40]=1;p[41]=1;length=44;}
    hosts[4][ri*8+4]=(uint8_t)length;hosts[4][ri*8+5]=0;registers[2][0x48/4]=registers[2][0x40/4];available_delivered=1;
     }
   }
   if(fault==14)return 1; /* Unknown doorbell outcome: ownership must remain. */
   return 0;
  }
  if(!id&&index==0x3c&&(config[1]&4)){
   assert(get(296)==31&&cpu_issued&&allocations==14);const uint8_t*tx=hosts[1];uint32_t op=bw(tx);unsigned reply_n=0;
   if(op==8){reply_n=12;bp(hosts[3],12);bp(hosts[3]+4,0x05020001);bp(hosts[3]+8,8);}
   else{
    assert(qca_boot_round());
    if(op==13){unsigned address=bw(tx+4);if(address){assert(address==0x1234&&!stream_open);streams++;stream_open=1;stream_bytes=0;}
     else{assert(stream_open&&stream_bytes==(streams<=2?24196:727128));stream_open=0;}}
    else if(op==14){
     assert(stream_open&&streams>=1&&streams<=3);unsigned n=bw(tx+4);assert(n&&n<=248&&!(n&3));
     const uint8_t*asset=streams<=2?boot_helper:qca_boot_view()->plan.assets.main;unsigned total=streams<=2?sizeof(boot_helper):727125;
     assert(asset&&stream_bytes+n<=((total+3)&~3u));for(unsigned i=0;i<n;i++)assert(tx[8+i]==(stream_bytes+i<total?asset[stream_bytes+i]:0));stream_bytes+=n;
    }else if(op==4){
     assert(!stream_open&&bw(tx+4)==0x1234&&executions<2);assert(bw(tx+8)==(executions?0:0x10));executions++;reply_n=4;bp(hosts[3],fault==1&&executions==2?1:0);
    }else if(op==2||op==3){
     unsigned addr=bw(tx+4),n=bw(tx+8);assert(addr>=0x400800&&addr<0x410000&&n&&n<=244&&addr-0x400000+n<=65536);unsigned off=addr-0x400000;
     if(op==3){memcpy(target_ram+off,tx+12,n);if(addr>=0x408000){assert(addr==0x408000+board_written&&n<=8124-board_written&&!memcmp(tx+12,boot_board+board_written,n));board_written+=n;}
      if(addr==0x400814){assert(streams==3&&!stream_open&&!bw(tx+12));uart_off++;}}
     else{reply_n=n;memcpy(hosts[3],target_ram+off,n);if(addr>=0x408000)board_read+=n;}
    }else{assert(op==1&&streams==3&&!stream_open&&uart_off==1&&board_written==8124&&board_read==8124);main_done++;}
   }
   registers[0][0x44/4]=value;
   if(reply_n){registers[1][0x48/4]=registers[1][0x40/4];unsigned ri=(registers[1][0x40/4]-1)&7;hosts[2][ri*8+4]=(uint8_t)reply_n;hosts[2][ri*8+5]=(uint8_t)(reply_n>>8);}
  }
  if(id==1&&index==0x40&&main_done&&!rx_ready_sent++&&fault!=3){
   unsigned ri=(value-1)&7;memset(hosts[3],0,20);hosts[3][2]=12;hosts[3][8]=fault==2?2:1;hosts[3][10]=8;hosts[3][12]=0;hosts[3][13]=1;hosts[3][14]=9;hosts[3][16]=1;hosts[3][17]=1;
   hosts[2][ri*8+4]=20;hosts[2][ri*8+5]=0;registers[1][0x48/4]=value;
  }
  return 0;
 }
 if(off==0x800||off==0x850||off==0x3a028){
  uint32_t v=*(uint32_t*)in;assert(!(config[1]&4));
  if(off==0x3a028){assert(!v);fw=0;}
  else if(off==0x850)warm_lf=v;
  else{warm_register=v&~0x40u;if(v&0x40){warm_cpus++;fw=(scenario==13||scenario==14||(scenario==17&&warm_cpus==2))?0:2;
    if(scenario==15&&!warm_write_failed++){return EFI_ERROR(7);}}}
  return 0;
 }
 if(off!=0x80008)return old_mem_write(p,width,bar,off,count,in);
 assert(p==pci&&width==2&&!bar&&count==1);uint32_t value=*(uint32_t*)in;assert(value<=1);
 reset_writes++;last_reset_write=now_us;
 if(scenario!=4||value)reset_register=value;
 if(!value&&scenario!=4){if(qca_boot_round())reset_target();memset(registers,0,sizeof(registers));fw=scenario==14&&warm_cpus?0:2;reset_cleared=1;if(scenario==28||scenario==29)link_control=0x143;if(scenario==31)boot_regs[2]=0x7fc00;if(scenario==5)config[1]&=~2u;}
 return scenario==7?EFI_ERROR(7):0;
}
static void tick(unsigned ms){now_us=(uint64_t)ms*1000;qca_poll(ms);}
static Status EFIAPI allocate(void*p,uint32_t type,uint32_t memory,uint64_t pages,void**out,uint64_t attrs){assert(p==pci&&!type&&memory==4&&pages==1&&!attrs&&allocations<14);*out=hosts[allocations++];return 0;}
static Status EFIAPI map(void*p,uint32_t op,void*host,uint64_t*n,uint64_t*addr,void**token){assert(p==pci&&op==2&&*n==4096);unsigned i=(unsigned)(((uint8_t*)host-hosts[0])/4096);assert(i<14);*addr=scenario==12?0x100000000ull:0x100000+i*4096;*token=host;return 0;}
static Status EFIAPI unmap(void*p,void*token){assert(p==pci&&token&&!(config[1]&4));unmaps++;return 0;}
static Status EFIAPI free_buffer(void*p,uint64_t pages,void*host){assert(p==pci&&pages==1&&host&&!(config[1]&4));dma_frees++;return 0;}
static Status EFIAPI flush(void*p){assert(p==pci&&!(config[1]&4));flushes++;return scenario==16?EFI_ERROR(7):0;}
static Status EFIAPI bmi_config_write(void*p,uint32_t w,uint32_t off,uint64_t n,void*in){
 if(off==0x80){assert(p==pci&&w==1&&n==1);uint16_t v=*(uint16_t*)in;
  if(!(v&3)){link_disables++;if(scenario==29&&link_disables>1)return 0;}
  if(scenario==19&&(v&3))return 0;
  link_control=v;return 0;
 }
 if(off==4){uint16_t v=*(uint16_t*)in;
  if(scenario==23&&(v&0x400))return 0;
  if(scenario==30&&!(v&0x400)&&(config[1]&0x400))return 0;
  if(scenario==25&&(v&0x400)&&!mask_attempts++){write_config(p,w,off,n,in);return EFI_ERROR(7);}
 }
 int rc=write_config(p,w,off,n,in);return scenario==15&&(*(uint16_t*)in&4)?EFI_ERROR(7):(Status)rc;}


static uint8_t sm_entry[24],sm_table[6]={127,4,0,0,0,0};
static struct {Guid guid;void*address;} sm_config;
static Status EFIAPI sm_map(uint64_t*n,void*p,uint64_t*k,uint64_t*d,uint32_t*v){
 assert(*n==65536);memset(p,0,40);*n=40;*d=40;*k=1;*v=1;uint64_t pages=UINT64_MAX/4096;memcpy((uint8_t*)p+24,&pages,8);return 0;
}
static void sm_fixture(void){
 const Guid g={0xf2fd1544,0x9794,0x4a2c,{0x99,0x2e,0xe5,0xbb,0xcf,0x20,0xe3,0x94}};
 sm_config.guid=g;sm_config.address=sm_entry;port_system.configuration=&sm_config;port_system.tables=1;boot[56/8]=(void*)sm_map;
 memcpy(sm_entry,"_SM3_",5);sm_entry[6]=24;sm_entry[7]=3;uint32_t n=sizeof(sm_table);memcpy(sm_entry+12,&n,4);uint64_t a=(uintptr_t)sm_table;memcpy(sm_entry+16,&a,8);
 unsigned sum=0;for(unsigned i=0;i<24;i++)sum+=sm_entry[i];sm_entry[5]=(uint8_t)(0u-sum);
}

static void*ram_blocks[2];static unsigned ram_allocs,ram_frees;
static Status EFIAPI ram_allocate(uint32_t kind,uint64_t n,void**out){
 assert(kind==4&&n>0&&ram_allocs<2&&!(config[1]&4)&&allocations==14&&dma_frees==14&&unmaps==14&&opens==closes);
 *out=ram_blocks[ram_allocs++]=malloc((size_t)n);assert(*out);return 0;
}
static Status EFIAPI ram_release(void*p){
 if(p==resource)return free_pool(p);
 unsigned slot=p==ram_blocks[0]?0:1;assert(p&&p==ram_blocks[slot]);free(p);ram_blocks[slot]=0;ram_frees++;return 0;
}
static uint8_t*packet_file(const char*dir,unsigned i,size_t*n){
 char path[4096];snprintf(path,sizeof(path),"%s/chunk-%u.bin",dir,i);FILE*f=fopen(path,"rb");assert(f&&!fseek(f,0,SEEK_END));long length=ftell(f);assert(length>224&&length<=65760);rewind(f);uint8_t*p=malloc((size_t)length);assert(p&&fread(p,1,(size_t)length,f)==(size_t)length);fclose(f);*n=(size_t)length;return p;
}

static void deliver_rx(unsigned pipe,unsigned kind){
 const QcaPersistentNative*p=qca_persistent_view();QcaPersistentRx*x=(QcaPersistentRx*)&p->rx;
 QcaInitAdapter*a=p->startup->operating->boot->board->setup->read.full.adapter;
 QcaCeRing*r=&a->channels.rings[pipe];assert(x->posted[pipe-1]);unsigned ri=r->read;
 uint8_t*b=hosts[2*pipe+1];memset(b,0,2048);unsigned n=16;
 b[0]=pipe==1?0:1;b[2]=8;bp(b+8,0x123456);bp(b+12,0xcafebabe);
 if(pipe==1){b[2]=2;b[8]=9;n=10;}
 if(kind==2||kind==5||kind==10){
  memset(b,0,24);b[1]=2;b[2]=8;b[4]=8;b[8]=1;b[9]=4;b[12]=1;b[13]=kind==5?3:1;n=16;
 }
 if(kind==3)b[2]=7;
 if(kind==4)b[0]=2;
 if(kind==6){b[2]=4;bp(b+8,2);n=12;}
 if(kind==7)r->cookie[ri]^=1;
 if(kind==8)hosts[2*pipe][ri*8]^=1;
 if(kind==9)n=2049;
 hosts[2*pipe][ri*8+4]=(uint8_t)n;hosts[2*pipe][ri*8+5]=(uint8_t)(n>>8);
 if(kind==10)hosts[2*pipe][ri*8+4]=hosts[2*pipe][ri*8+5]=0;
 registers[pipe][0x48/4]=kind==12?(ri+2)&7:(ri+1)&7;
}


static void deliver_htt(unsigned kind){
 deliver_rx(1,1);const QcaPersistentNative*p=qca_persistent_view();
 QcaInitAdapter*a=p->startup->operating->boot->board->setup->read.full.adapter;unsigned ri=a->channels.rings[1].read;
 uint8_t*b=hosts[3];memset(b,0,24);b[0]=p->startup->operating->control.session.htt.endpoint;b[2]=4;
 b[8]=0;b[9]=4;b[10]=3;
 if(kind==20)b[10]=2;if(kind==7)b[10]=9;if(kind==8)b[11]=1;if(kind==9)b[0]=3;
 if(kind==10)b[2]=12,b[1]=2,b[4]=8,b[12]=1,b[13]=4,b[16]=1,b[17]=1;
 if(kind==11)b[2]=12,b[1]=2,b[4]=8,b[12]=1,b[13]=4,b[16]=2,b[17]=1;
 unsigned n=(kind==10||kind==11)?20:12;
 hosts[2][ri*8+4]=(uint8_t)n;hosts[2][ri*8+5]=0;
}

static void upload_fixture(const char*dir){
 const QcaFirmwarePort*r=qca_ram_view();fprintf(stderr,"RAM phase=%u error=%u allocs=%u frees=%u setup=%u/%u bmi=%u/%u type=%u stage=%u\n",r->phase,r->error,ram_allocs,ram_frees,get(280),get(284),get(316),get(320),get(328),get(128));assert(r->phase==4&&ram_allocs==2&&!ram_frees);
 uint8_t request[247],reply[247];request[0]=0x0a;request[1]=19;request[2]=0;
 assert(qca_ram_att(247,request,3,reply,247)==65&&!memcmp(reply+1,"RFCS0001",8));
 /* Legacy file/diagnostic handles remain delegated. */
 for(unsigned h=1;h<=12;h++){request[1]=(uint8_t)h;assert(qca_ram_att(247,request,3,reply,247)==SIZE_MAX);}
 for(unsigned i=0;i<12;i++){
  size_t n;uint8_t*p=packet_file(dir,i,&n),cmd[44]={0};memcpy(cmd,"RFC1",4);cmd[4]=1;
  for(unsigned k=0;k<4;k++){cmd[8+k]=(uint8_t)(n>>(8*k));}rabbit_sha256(cmd+12,p,n);
  request[0]=0x12;request[1]=15;request[2]=0;memcpy(request+3,cmd,44);assert(qca_ram_att(247,request,47,reply,247)==1);
  for(size_t off=0;off<n;){size_t z=n-off;if(z>240)z=240;request[1]=17;for(unsigned k=0;k<4;k++)request[3+k]=(uint8_t)(off>>(8*k));memcpy(request+7,p+off,z);assert(qca_ram_att(247,request,z+7,reply,247)==1);off+=z;}
  cmd[4]=2;request[1]=15;memcpy(request+3,cmd,44);assert(qca_ram_att(247,request,47,reply,247)==1);assert(r->channel.state==QCA_FC_ACCEPTED&&!r->channel.error);free(p);
 }
 assert(r->asset.received==4095&&r->asset.ready&&!r->asset.poisoned);

 assert(allocations==14&&dma_frees==14&&unmaps==14&&opens==closes&&!(config[1]&4));
 allocations=dma_frees=unmaps=0;memset(hosts,0,sizeof(hosts));unsigned cancel_called=0;
 for(unsigned ms=15001;ms<60000;ms++){
  if(fault==16&&qca_operating_view()->phase==1){
   /* RX first, TX hardware index delayed until the next cooperative poll. */
   if(qca_operating_view()->control.deferred_bytes)registers[0][0x44/4]=registers[0][0x3c/4];
  }

  const QcaWmiStartup*w=qca_wmi_startup_view();
  if(startup_fault==1&&w->transaction.ready_seen)registers[FW_WMI_TX][0x44/4]=registers[FW_WMI_TX][0x3c/4];
  if(startup_fault==10&&w->tx_posted)qca_wmi_startup_cancel((QcaWmiStartup*)w);
  if(startup_fault==18&&w->transaction.phase==QCA_INIT_RESERVED)qca_wmi_startup_cancel((QcaWmiStartup*)w);
  if(startup_fault==19&&w->tx_posted)((QcaWmiStartup*)w)->last=UINT64_MAX;
  if(startup_fault==21&&w->tx_posted)assert(qca_stop());
  if(startup_fault==20&&w->tx_posted)((QcaWmiStartup*)w)->operating->boot->asset->poisoned=1;

  const QcaPersistentNative*p=qca_persistent_view();
  if(p->life.phase==QCA_RADIO_ACTIVE){
   active_ticks++;
   QcaInitAdapter*a=p->startup->operating->boot->board->setup->read.full.adapter;
   assert(allocations==14&&!dma_frees&&!unmaps&&r->asset.pinned&&a->mapped.irq->port->dma_users==14);
   assert(a->channels.rings[3].owned&&a->bus.owned&&qca_radio_accepts_work(&p->life));

   assert(!qca_rx_clear((QcaPersistentRx*)&p->rx,&p->life));

   htt_started=1;
   if(query.attempted)assert(!qca_htt_native_begin(&rival,(QcaPersistentNative*)p,3,ms*1000));
   if(htt_started&&!query.stop_requested){
    if(active_ticks>=12&&!htt_response_delivered&&htt_scenario!=15&&htt_scenario!=14&&p->rx.posted[0]){htt_response_delivered=1;deliver_htt(htt_scenario);}
    if(active_ticks==11&&(htt_scenario==13||htt_scenario==14)){deliver_rx(1,1);deliver_rx(2,1);}
    if(active_ticks==13&&htt_scenario==14){deliver_rx(1,1);deliver_rx(2,1);}
    if(active_ticks==14&&htt_scenario==14){deliver_rx(2,1);}
    if(active_ticks==12&&htt_scenario==16)a->channels.buffers[9].valid=0;
    if(active_ticks==12&&htt_scenario==18)((QcaPersistentNative*)p)->epoch++;
    if(active_ticks==12&&htt_scenario==19)((QcaHtcSession*)&p->startup->operating->control.session)->htt.max_bytes=128;
    /* Actual production qca_poll services the owner, not this fixture. */
   }
   if(active_ticks==20&&rx_scenario){
    if(rx_scenario==11){deliver_rx(1,1);deliver_rx(2,1);}
    else deliver_rx(rx_scenario==2||rx_scenario==5||rx_scenario==10?1:2,rx_scenario);
   }
   if(active_ticks==21&&rx_scenario==10){
    assert(!p->rx.completed);unsigned ri=a->channels.rings[1].read;
    hosts[2][ri*8+4]=16;hosts[2][ri*8+5]=0;
   }
   if(active_ticks==30&&(rx_scenario==1||rx_scenario==11)){
    assert(p->rx.count==(rx_scenario==11?2:1));
    const QcaRxEvent*e=&p->rx.events[p->rx.head];uint32_t id=e->completion;QcaRxEvent copy;
    assert(!qca_rx_take((QcaPersistentRx*)&p->rx,id+100,&copy,sizeof(copy)));
    assert(!qca_rx_take((QcaPersistentRx*)&p->rx,id,&copy,sizeof(copy)-1));
    uint32_t posts=p->rx.posted_count,done=p->rx.completed;
    if(rx_scenario==11){assert(p->rx.backpressure&&posts==1&&done==2);}
    assert(qca_rx_take((QcaPersistentRx*)&p->rx,id,&copy,sizeof(copy)));
    assert(copy.completion==id&&copy.payload[0]==(copy.pipe==1?9:0x56));
    assert(!qca_rx_take((QcaPersistentRx*)&p->rx,id,&copy,sizeof(copy)));
   }
   if(active_ticks==40&&rx_scenario==11){
    const QcaRxEvent*e=&p->rx.events[p->rx.head];QcaRxEvent copy;
    assert(p->rx.count==1&&e->pipe==2&&e->payload[0]==0x56);
    assert(qca_rx_take((QcaPersistentRx*)&p->rx,e->completion,&copy,sizeof(copy)));
   }
   if(active_ticks==50&&(rx_scenario==2||rx_scenario==10)){
    assert(p->rx.completed==1&&!p->rx.count);
    assert(p->startup->operating->control.credit.available==p->startup->operating->control.credit.total);
    assert(!p->startup->operating->control.credit.outstanding);
   }
   if(active_ticks==200000){
    if(persistent_fault==1)a->channels.rings[3].fault=1;
    else if(persistent_fault==2)a->channels.buffers[7].valid=0;
    else if(persistent_fault==3)((QcaFirmwarePort*)r)->asset.poisoned=1;
    else if(persistent_fault==4)a->channels.routes[3].pipe=0;
    else if(persistent_fault==5)((QcaPersistentNative*)p)->life.last=UINT64_MAX;
    else {assert(qca_stop());stopped=1;assert(!qca_radio_accepts_work(&p->life));}
   }
  }
  if(htt_scenario==17&&active_ticks==12)tick(ms-2);else tick(ms);const QcaBootNative*b=qca_boot_view();
  if(qca_persistent_view()->error)fprintf(stderr,"PERSISTENT_BEGIN_ERROR=%u\n",qca_persistent_view()->error);

  if((fault==6&&b->plan.phase==7)||(fault==7&&b->plan.phase==17)||(fault==15&&qca_operating_view()->control.posted)){if(!cancel_called++){assert(qca_stop()&&!ram_frees&&r->asset.pinned);}}
  if(get(128)==18&&b->plan.submitted&&b->phase!=6&&b->phase!=5){
   assert(r->asset.pinned);
   uint8_t request[4]={0x12,6,0,0},reply[8]={0};
   assert(qca_ram_att(247,request,4,reply,8)==5&&reply[4]==3);
   request[0]=0x52;assert(qca_ram_att(247,request,4,reply,8)==0);
  }
  if(qca_boot_round()&&(get(128)==5||get(128)==6))break;
 }
 const QcaBootNative*b=qca_boot_view();fprintf(stderr,"SECOND phase=%u error=%u plan=%u/%u streams=%u exec=%u stage=%u/%u pins=%u alloc=%u free=%u open=%u close=%u\n",b->phase,b->error,b->plan.phase,b->plan.error,streams,executions,get(128),get(136),r->asset.pinned,allocations,dma_frees,opens,closes);
 assert(qca_boot_round()&&get(128)==6u&&allocations==14&&dma_frees==14&&unmaps==14&&opens==closes&&!r->asset.pinned);
 if(!fault||fault==16||fault==24||fault==32||fault==35)assert(b->phase==5&&b->plan.phase==20&&!b->error&&b->ready_bytes==20&&executions==2&&streams==3&&main_done==1);
 else if(fault<=5)assert(b->phase==6&&b->error);
 else if(fault<=7)assert(b->phase==1&&!b->error&&!main_done);
 else assert(b->phase==5&&!b->error);
 const QcaOperating*o=qca_operating_view();
 if(startup_fault==20)assert(o->phase==3&&o->error==2);else if(!fault||fault==16||fault==24||fault==32||fault==35)assert((htt_started||persistent_fault||rx_scenario||(o->phase==2&&!o->error))&&o->service_valid&&o->service.build==(fault==35?21u:1234u)&&o->control.session.phase==QCA_HTC_RUNNING&&o->tx_count==3&&o->rx_count==(fault==32?3u:4u));
 else if(fault>=8&&fault!=15&&fault!=24)assert(o->phase==3&&o->error);
 
 if(fault==10||fault==18||fault==19||fault==22||fault==23||fault==25||fault==26){assert(o->error==4&&o->rx_diagnostic[0]==1&&o->rx_diagnostic[1]==5&&o->rx_diagnostic[7]==(fault==23?18u:20u)&&o->rx_descriptor[4]==(fault==23?18u:20u));}
 if(fault==17){assert(o->error==4&&o->rx_diagnostic[1]==4&&o->rx_diagnostic[7]==7&&o->rx_prefix[7]==0);}
 if(fault==20){assert(o->error==4&&o->rx_diagnostic[1]==2&&o->rx_diagnostic[8]);}
 if(fault==21){assert(o->error==4&&o->rx_diagnostic[1]==1);}

 const QcaWmiStartup*w=qca_wmi_startup_view();
 if(startup_fault==0||startup_fault==1||startup_fault==15||startup_fault==22){
  assert((htt_started||persistent_fault||rx_scenario||(w->phase==2&&!w->error&&w->transaction.phase==QCA_INIT_RUNNING))&&w->transaction.ready_seen&&w->transaction.tx_complete);
  assert(w->transaction.ready.mac[0]==2&&w->transaction.ready.mac[5]==1&&w->transaction.ready.abi_minor==(startup_fault==15?53u:574u));
  fprintf(stderr,"INIT COUNTS tx=%u rx=%u posted=%u available=%u outstanding=%u\n",w->tx_count,w->rx_count,w->tx_posted,o->control.credit.available,o->control.credit.outstanding);
  assert(w->tx_count==1&&w->rx_count==1&&!w->tx_posted&&(htt_started||rx_scenario||((o->control.credit.available==(o->control.credit.total-(startup_fault==0?0u:1u)))&&o->control.credit.outstanding==(startup_fault==0?0u:1u))));
 }else{
  assert(w->phase==3&&w->error);
  if(startup_fault==11||startup_fault==12)assert(!w->transaction.phase&&!init_posts);
  if(startup_fault==18)assert(w->transaction.phase==QCA_INIT_CANCELLED&&!init_posts&&o->control.credit.available==o->control.credit.total);
  if(startup_fault==8||startup_fault==9)assert(w->error==(startup_fault==8?18u:14u));
 }
 uint8_t init_request[7]={0x10,26,0,255,255,0,0x28},init_reply[247];
 assert(qca_wmi_att(247,init_request,7,init_reply,sizeof(init_reply))==22&&init_reply[2]==26&&init_reply[4]==28&&init_reply[6]==0x26);
 init_request[0]=8;init_request[1]=27;init_request[6]=0x28;init_request[5]=3;
 assert(qca_wmi_att(247,init_request,7,init_reply,sizeof(init_reply))==23&&init_reply[2]==27&&init_reply[5]==28&&init_reply[7]==0x27);
 init_request[0]=0x0a;init_request[1]=28;
 assert(qca_wmi_att(247,init_request,3,init_reply,sizeof(init_reply))==245&&!memcmp(init_reply+1,"QWIN0002",8));
 assert(!memcmp(init_reply+117,w->prefix,128));
 assert(init_reply[97]==w->reject_reason&&init_reply[105]==w->prefix_bytes);
 if(startup_fault==4||startup_fault==5||startup_fault==6||startup_fault==14)assert(w->reject_reason);
 assert(init_reply[9]==w->phase&&init_reply[13]==w->error&&init_reply[57]==w->transaction.ready.mac[0]);
 init_request[0]=0x0c;init_request[3]=244;init_request[4]=0;
 assert(qca_wmi_att(247,init_request,5,init_reply,sizeof(init_reply))==1);
 init_request[3]=245;assert(qca_wmi_att(247,init_request,5,init_reply,sizeof(init_reply))==5&&init_reply[4]==7);
 init_request[0]=0x12;assert(qca_wmi_att(247,init_request,3,init_reply,sizeof(init_reply))==5&&init_reply[4]==3);
 init_request[0]=0x52;assert(!qca_wmi_att(247,init_request,3,init_reply,sizeof(init_reply)));

 const QcaPersistentNative*p=qca_persistent_view();
 fprintf(stderr,"PERSISTENT_FINAL phase=%u error=%u life_error=%u active=%u stop=%u polls=%u\n",p->life.phase,p->error,p->life.error,active_ticks,p->stop_latched,p->polls);
 if(startup_fault==0||startup_fault==1||startup_fault==15||startup_fault==22){
  assert(query.attempted==1||htt_scenario>=21);
  if(qca_persistent_unload_safe(p)){
   assert(query.stop_requested&&p->life.phase==QCA_RADIO_CLOSED&&qca_persistent_unload_safe(p));
   QcaRadioLifecycle other=p->life;
   assert(!qca_rx_clear((QcaPersistentRx*)&p->rx,&other));
   assert(query.stop_requested);
   assert(qca_rx_poll((QcaPersistentRx*)&p->rx,&p->life,60000000)==0);
  }
  else {assert(p->life.phase==QCA_RADIO_RETAINED&&!qca_persistent_unload_safe(p)&&!qca_radio_accepts_work(&p->life));}
 }else assert(!active_ticks&&!p->life.phase);
 
 if((rx_scenario>=3&&rx_scenario<=9)||rx_scenario==12||rx_scenario==13){
  assert(p->rx.phase==QCA_RX_FAULT&&p->rx.error&&!qca_rx_clear((QcaPersistentRx*)&p->rx,&p->life));
  assert(p->rx.completed==(rx_scenario==13?1u:0u));
  assert(o->control.credit.available==o->control.credit.total-(startup_fault==1?1u:0u));
  assert(o->control.credit.outstanding==(startup_fault==1?1u:0u));
 }

 assert(query.stop_requested&&htt_posts==(htt_scenario>=21?0u:1u)&&query.attempted==(htt_scenario>=21?0u:1u));
 assert(!qca_htt_native_begin(&query,(QcaPersistentNative*)p,3,60000000));
 (void)qca_htt_native_poll(&query,60000000);
 if(htt_scenario==0||htt_scenario==10||htt_scenario==13||htt_scenario==20){assert(query.phase==QCA_HTTN_RELEASED&&query.version_seen&&query.dma_completed&&query.version.major==(htt_scenario==20?2:3)&&query.version.minor==4);}
 else {assert(query.error&&query.phase==QCA_HTTN_FAULT);}
 if(htt_scenario==1||htt_scenario==15)assert(query.error==7);
 if(htt_scenario==12)assert(query.error==10&&query.response.completion<=query.watermark);
 if(htt_scenario==13)assert(query.archive_count==2&&query.archive[0].endpoint==0&&query.archive[1].endpoint==1);
 if(htt_scenario==16||htt_scenario==18||htt_scenario==19)assert(!qca_persistent_unload_safe(p));
 if(htt_scenario==18)assert(query.error==4);
 if(htt_scenario>=21)assert(query.error==30&&!qca_htt_firmware_view()->valid);
 if(htt_scenario==19)assert(query.error==6);
 if(htt_scenario==1)assert(query.version_seen&&!query.dma_completed);
 assert(o->control.credit.available==o->control.credit.total-(htt_scenario==10?0u:(startup_fault==1?1u:0u))&&!o->control.credit.reserved);
 assert(o->control.credit.outstanding==(htt_scenario==10?0u:(startup_fault==1?1u:0u)));
 for(unsigned slot=0;slot<6;slot++){
  QcaRxEvent before,after;int present=qca_htt_native_export(&query,slot,&before,sizeof before);
  assert(!qca_htt_native_export(&query,slot,&after,sizeof after-1));
  assert(!qca_htt_native_export(&query,slot,(QcaRxEvent*)&query,sizeof before));
  assert(!qca_htt_native_export(&query,slot,(QcaRxEvent*)&p->rx,sizeof before));
  if(present){assert(before.completion&&before.bytes<=2040&&before.raw_bytes>=8&&before.raw_bytes<=2048);assert(qca_htt_native_export(&query,slot,&after,sizeof after));assert(!memcmp(&before,&after,sizeof before));}
 }
 assert(!qca_htt_native_export(&query,6,(QcaRxEvent*)&query.response,sizeof(QcaRxEvent)));

 {
  uint8_t status[320],request[7]={0x10,29,0,255,255,0,0x28},reply[247],page[512],again[512];
  qca_htt_status(status);assert(!memcmp(status,"QHTT0001",8)&&getle(status+224)==56&&getle(status+24)==1);
  assert(getle(status+8)==query.phase&&getle(status+12)==query.error);
  if(htt_scenario<21){assert(qca_htt_firmware_view()->valid&&getle(status+80)==3&&getle(status+100)==56);}
  else assert(qca_htt_firmware_view()->error==(htt_scenario==23?8u:2u));
  assert(qca_htt_profile_att(247,request,7,reply,sizeof(reply))==22&&reply[2]==29&&reply[4]==31&&reply[6]==0x2e);
  request[0]=0x0a;request[1]=31;assert(qca_htt_profile_att(247,request,3,reply,sizeof(reply))==247&&!memcmp(reply+1,status,246));
  request[0]=0x0c;request[3]=246;request[4]=0;assert(qca_htt_profile_att(247,request,5,reply,sizeof(reply))==75&&!memcmp(reply+1,status+246,74));
  request[3]=65;request[4]=1;assert(qca_htt_profile_att(247,request,5,reply,sizeof(reply))==5&&reply[4]==7);
  for(unsigned index=0;index<30;index++){
   unsigned n=qca_htt_profile_export(index,page,sizeof(page));assert(n==((index%5)==4?56:512));
   assert(qca_htt_profile_export(index,again,sizeof(again))==n&&!memcmp(page,again,n));
   assert(!qca_htt_profile_export(index,again,511));
   request[0]=0x0a;request[1]=(uint8_t)(34+2*index);request[2]=0;
   assert(qca_htt_profile_att(247,request,3,reply,sizeof(reply))==(n>246?247:n+1)&&!memcmp(reply+1,page,n>246?246:n));
   request[0]=0x12;assert(qca_htt_profile_att(247,request,3,reply,sizeof(reply))==5&&reply[4]==3);
   request[0]=0x52;assert(!qca_htt_profile_att(247,request,3,reply,sizeof(reply)));
   for(unsigned offset=0;offset<n;offset+=246){request[0]=0x0c;request[3]=(uint8_t)offset;request[4]=(uint8_t)(offset>>8);unsigned take=n-offset;if(take>246)take=246;
    assert(qca_htt_profile_att(247,request,5,reply,sizeof(reply))==take+1&&!memcmp(reply+1,page+offset,take));}
  }
  assert(!qca_htt_profile_export(30,page,sizeof(page)));
 }
 printf("HTT_NATIVE scenario=%u posts=%u DMA=%u version=%u error=%u archive=%u all14released=%u\n",htt_scenario,htt_posts,query.dma_completed,query.version_seen,query.error,query.archive_count,qca_init_adapter_released(p->startup->operating->boot->board->setup->read.full.adapter));
 printf("PERSISTENT_MOCK active_ticks=%u fault=%u startup=%u phase=%u polls=%u ALL14 RELEASE PASS\n",active_ticks,persistent_fault,startup_fault,p->life.phase,p->polls);
 printf("WMI_INIT_MOCK phase%u/error%u transaction%u tx%u rx%u fault%u ALL14 RELEASED PASS\n",w->phase,w->error,w->transaction.phase,w->tx_count,w->rx_count,startup_fault);
 printf("OPERATING_MOCK phase%u/error%u tx%u rx%u fault%u SAFE RELEASE PASS\n",o->phase,o->error,o->tx_count,o->rx_count,fault);
 uint8_t status[160];qca_boot_status(status);printf("QWBT_MOCK=");for(unsigned i=0;i<160;i++)printf("%02x",status[i]);puts("");
 /* Actual callback must return legacy writes to the resident after cleanup,
    including fault/cancellation paths; the completed RAM asset stays sealed. */
 for(unsigned opcode=0x12;opcode<=0x52;opcode+=0x40){
  uint8_t request[4]={(uint8_t)opcode,0,0,0},reply[247]={0};
  for(unsigned handle=1;handle<=12;handle++){
   request[1]=(uint8_t)handle;assert(qca_ram_att(247,request,4,reply,247)==SIZE_MAX);
  }
  for(unsigned handle=13;handle<=19;handle++){
   request[1]=(uint8_t)handle;size_t n=qca_ram_att(247,request,4,reply,247);
   assert(n==(opcode==0x12?5u:0u));if(n)assert(reply[4]==3);
  }
 }
 puts("LEGACY WRITES BLOCKED WHILE OWNED; DELEGATED AFTER COMPLETE CLEANUP; ASSET SEALED PASS");
 assert(!qca_stop()&&ram_frees==2&&!qca_fwp_owned(r));
 printf("ACTUAL ENTRYPOINT TWO LIFETIMES fault%u PASS; SYNTHETIC RADIO/HTC ONLY\n",fault);

}

int main(int argc,char**argv){
 assert(argc==8);htt_scenario=(unsigned)atoi(argv[7]);assert(htt_scenario<=23);rx_scenario=(unsigned)atoi(argv[6]);assert(rx_scenario<=13);persistent_fault=(unsigned)atoi(argv[5]);assert(persistent_fault<=5);startup_fault=(unsigned)atoi(argv[4]);assert(startup_fault<=22);fault=(unsigned)atoi(argv[3]);assert(fault<=40);scenario=(unsigned)atoi(argv[1]);assert(scenario<=18||(scenario>=100&&scenario<=110)||(scenario>=200&&scenario<=244));unsigned initial=scenario;
 assert(!port_previous_main());baseline();
 const uint32_t initial_state[9]={initial==220?0:initial==221?0x401ee0:initial==222?0x404d91:0x404d90,initial==223?0x404d90:0x404e50,8,0,0,0,0,3,1};
 for(unsigned k=0;k<36;k++)target_ram[0x1ee0+k]=(uint8_t)(initial_state[k/4]>>(8*(k%4)));
 target_ram[0x8cc]=initial==224?0x10:0;
 target_ram[0x8f8]=0xe0;target_ram[0x8f9]=0x1e;target_ram[0x8fa]=0x40;
 config[1]|=0x00100000;
 put(22,0x1fffff,8);put(38,0x200000,8);
 pci[48/8]=read_config;pci[16/8]=mem_read;pci[24/8]=mem_write;pci[56/8]=bmi_config_write;
 pci[88/8]=allocate;pci[72/8]=map;pci[80/8]=unmap;pci[96/8]=free_buffer;pci[104/8]=flush;
 qca_image=&port_system;qca_controller=scenario==8?0:pci;qca_diagnostic[4]=15;
 port_system.header.signature=0x5453595320494249ull;port_system.header.size=sizeof(port_system);
 ((TableHeader*)boot)->signature=0x56524553544f4f42ull;((TableHeader*)boot)->size=sizeof(boot);
 boot[64/8]=ram_allocate;boot[72/8]=ram_release;
 sm_fixture();
 qca_start(&port_system,0);tick(1);
 if(scenario==9||scenario==10){if(scenario==10)tick(21);assert(qca_stop()&&get(168)==1);}
 for(unsigned ms=initial==10?22:2;ms<((initial==18||initial>=100)?60000u:15000u);ms+=(initial==18&&get(128)==18&&get(800)==3)?600u:((initial==100&&get(888)==1)?4000u:((initial==244&&get(316)==1)?4000u:1u))){tick(ms);if(initial>=230&&initial<=239&&get(280)==1&&get(288)==(unsigned)(initial-230))(void)qca_stop();}
 assert(initial==0&&get(128)==5&&!(config[1]&4));upload_fixture(argv[2]);return 0;
}
