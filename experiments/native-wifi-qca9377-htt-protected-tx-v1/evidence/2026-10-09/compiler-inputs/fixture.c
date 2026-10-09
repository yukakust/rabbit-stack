#include "ether_tx.h"
int ethernet_mmio(unsigned,unsigned,uint32_t);
int glue_key_mmio(unsigned,unsigned,uint32_t);
#include "data_path.h"
QcaHttDataPath*data_model_view(void);
unsigned data_model_uncertain(void);
static void data_tick(void);
static unsigned tx_delay,data_case;
#include "primary_oracle.h"
#include "phase_arena.h"
void qca_filter64_status(unsigned char[544]);
#include "prefix.h"
#include "usb_port.h"
#include "scene_abi.h"
QcaPrefix*qca_prefix_view(void);
void qca_prefix_status(uint8_t[240]);
void prefix_driver_model_bind(void*);
int prefix_driver_model_poll(uint32_t);
void prefix_driver_model_display(uint32_t*,unsigned,unsigned,unsigned);
int prefix_driver_model_world(const uint8_t*,uint32_t,Surface*);
int prefix_driver_model_frame(Surface*);
#include "scan_native.h"
const QcaNativeScan*qca_scan_native_view(void);
void qca_scan_status(uint8_t[416]);
size_t qca_scan_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);
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
static unsigned fault;static void*usb_methods[16];static uint32_t*model_surface,*model_physical;static Surface model_sf;static unsigned active_status_reads;static unsigned startup_fault,init_posts;static unsigned persistent_fault,active_ticks,stopped;static unsigned rx_scenario;static unsigned native_scenario,scan_posts,credit_pending,emitted,regression_emitted;static unsigned filter_scenario,overflow_emitted,mixed_emitted,early_credit_delivered;static unsigned filter_posts,echo_pending,echo_delivered,htt_posts,htt_delivered;static uint32_t commands[8];static unsigned control_tx,rx_ready_sent,available_delivered;
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
   assert(allocations==47&&boot_regs[2]==0&&!(boot_regs[0]&0x800)&&!tx[6]&&!tx[7]);
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






  if(ethernet_mmio(id,index,value)||glue_key_mmio(id,index,value))return 0;
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==3&&index==0x3c){
   uint8_t status[544];qca_filter64_status(status);
   if(bw(status+8)==1){
    const QcaNativeScan*sc=qca_scan_native_view();assert(sc->tx.phase==QCA_TX_POSTED&&filter_posts<3);
    const uint32_t expected[3]={0x5001,0x5002,0x1d001};assert(bw(hosts[7]+8)==expected[filter_posts]);
    filter_posts++;if(filter_scenario!=9||filter_posts<3)registers[3][0x44/4]=value;
    credit_pending+=(sc->tx.bytes+sc->tx.credit->size-1)/sc->tx.credit->size;
    if(filter_posts==3)echo_pending=1;
    return 0;
   }
  }
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==4&&index==0x3c){
   const uint8_t*b=hosts[9];QcaHttDataPath*dp=data_model_view();
   if(dp&&dp->phase==QDP_CFG_POSTED){assert(b[0]==2&&b[2]==40&&b[8]==2&&b[9]==1);if(data_case==2){unsigned slot=(value-1)&7;hosts[8][slot*8+4]=47;}if(data_case!=3)registers[4][0x44/4]=value;return 0;}
   if(dp&&dp->phase==QDP_AGGR_POSTED){assert(b[0]==2&&b[2]==3&&b[8]==5&&b[9]==1&&b[10]==1);registers[4][0x44/4]=value;return 0;}
   if(dp&&dp->tx_posted){assert(b[16]==2&&b[24]==1);if(!tx_delay)registers[4][0x44/4]=value;return 0;}
   assert(!htt_posts&&b[0]==2&&!b[1]&&b[2]==4&&!b[3]&&!bw(b+8));
   htt_posts++;registers[4][0x44/4]=value;return 0;
  }
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==3&&index==0x3c&&qca_scan_native_view()->tx.phase==QCA_TX_POSTED){
   const QcaNativeScan*s=qca_scan_native_view();assert(scan_posts<8);commands[scan_posts++]=bw(hosts[7]+8);
   const uint8_t*body=hosts[7]+8;unsigned command=bw(body);
   if(command==0x3003){assert(bw(body+8)==13&&s->tx.bytes==388);for(unsigned j=0;j<13;j++){const uint8_t*c=body+16+28*j;assert(bw(c+4)==2412+5*j&&bw(c+8)==2412+5*j&&!bw(c+12)&&bw(c+16)==129);}}
   if(command==0x4001)assert(bw(body+12)==108&&bw(body+16)==108&&bw(body+20)==108);
   if(command==0x3001){assert(s->tx.bytes==184&&bw(body+64)==0x21&&bw(body+72)==13);for(unsigned j=0;j<13;j++)assert(bw(body+112+4*j)==2412+5*j);assert(bw(body+164)==(19u<<16)&&bw(body+168)==(19u<<16)&&bw(body+172)==(17u<<16));}

   assert(!s->tx.credit->reserved&&s->tx.credit->outstanding);
   if(native_scenario!=5)registers[3][0x44/4]=value;
   credit_pending+=(s->tx.bytes+s->tx.credit->size-1)/s->tx.credit->size;
   if(native_scenario==6)return 1;
   return 0;
  }
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&(id==1||id==2)&&index==0x40){
   if(rx_scenario==13&&active_ticks>=20&&id==2)return 1;
   return 0;
  }
  if(main_done&&qca_wmi_startup_view()->phase==1){
   if(id==0&&index==0x3c)assert(!"WMI INIT incorrectly sent on CE0");
   if(id==1&&index==0x40){
    if(filter_scenario==4&&!early_credit_delivered&&qca_wmi_startup_view()->transaction.ready_seen){unsigned ri=(value-1)&7;uint8_t*p=hosts[3];memset(p,0,2048);p[1]=2;p[2]=8;p[4]=8;p[8]=1;p[9]=4;p[12]=1;p[13]=1;hosts[2][ri*8+4]=16;hosts[2][ri*8+5]=0;registers[1][0x48/4]=value;early_credit_delivered=1;}return 0;}
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
     const uint8_t captured[256]={1,0,56,1,0,4,0,0,1,0,0,0,128,0,32,0,21,0,0,0,0,0,0,1,62,2,0,0,81,67,65,95,77,76,0,0,0,0,0,0,0,0,0,0,3,0,0,0,10,0,0,0,1,0,0,0,91,8,0,0,178,17,144,51,254,255,0,0,63,0,0,0,63,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,68,0,0,0,1,0,0,0,0,0,0,0,6,64,1,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,189,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,36,0,33,0,108,0,0,0,63,0,0,0,7,0,0,0,192,11,0,0,13,248,127,0,8,9,0,0,172,10,0,0,56,19,0,0,212,23,0,0,128,0,16,0,13,0,0,0,7,0,0,0,15,0,0,0,3,0,0,0,15,0,0,0,15,0,0,0,11,0,0,0,15,0,0,0,11,0,0,0,11,0,0,0,0,0,0,0,10,0,0,0,0,0,0,0,4,0,0,0,7,0,0,0,14,0,0,0,10,0,0,0};memcpy(p,captured,256);memset(p+256,0,64);bp(p+252,data_case==1?0:2);bp(p+316,18u<<16);
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
    hosts[3][10]=(uint8_t)service;hosts[3][11]=(uint8_t)(service>>8);hosts[3][13]=control_tx==1?1:2;hosts[3][14]=0xf8;hosts[3][15]=0x06;
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
     const uint8_t captured[256]={1,0,56,1,0,4,0,0,1,0,0,0,128,0,32,0,21,0,0,0,0,0,0,1,62,2,0,0,81,67,65,95,77,76,0,0,0,0,0,0,0,0,0,0,3,0,0,0,10,0,0,0,1,0,0,0,91,8,0,0,178,17,144,51,254,255,0,0,63,0,0,0,63,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,68,0,0,0,1,0,0,0,0,0,0,0,6,64,1,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,189,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,36,0,33,0,108,0,0,0,63,0,0,0,7,0,0,0,192,11,0,0,13,248,127,0,8,9,0,0,172,10,0,0,56,19,0,0,212,23,0,0,128,0,16,0,13,0,0,0,7,0,0,0,15,0,0,0,3,0,0,0,15,0,0,0,15,0,0,0,11,0,0,0,15,0,0,0,11,0,0,0,11,0,0,0,0,0,0,0,10,0,0,0,0,0,0,0,4,0,0,0,7,0,0,0,14,0,0,0,10,0,0,0};memcpy(p,captured,256);memset(p+256,0,64);bp(p+252,data_case==1?0:2);bp(p+316,18u<<16);
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
   assert(get(296)==31&&cpu_issued&&allocations==47);const uint8_t*tx=hosts[1];uint32_t op=bw(tx);unsigned reply_n=0;
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
   unsigned ri=(value-1)&7;memset(hosts[3],0,20);hosts[3][2]=12;hosts[3][8]=fault==2?2:1;hosts[3][10]=2;hosts[3][12]=0;hosts[3][13]=7;hosts[3][14]=4;hosts[3][16]=1;hosts[3][17]=1;
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
static void tick(unsigned ms){now_us=(uint64_t)ms*1000;assert(!prefix_driver_model_poll(ms));data_tick();}

static void*extra_hosts[33];static uint64_t extra_sizes[33];
static Status EFIAPI allocate(void*p,uint32_t type,uint32_t memory,uint64_t pages,void**out,uint64_t attrs){
 assert(p==pci&&!type&&memory==4&&!attrs&&!(config[1]&4)&&allocations<47);
 if(allocations<14){assert(pages==1);*out=hosts[allocations];}
 else{unsigned j=allocations-14;assert(pages==(j==32?3:16));assert(!extra_hosts[j]);*out=extra_hosts[j]=aligned_alloc(4096,(size_t)pages*4096);extra_sizes[j]=pages*4096;assert(*out);}
 allocations++;return 0;
}
static Status EFIAPI map(void*p,uint32_t op,void*host,uint64_t*n,uint64_t*addr,void**token){
 assert(p==pci&&op==2&&!(config[1]&4));unsigned i;
 for(i=0;i<14;i++)if(host==hosts[i]){assert(*n==4096);*addr=0x100000+i*4096;*token=host;return 0;}
 for(i=0;i<33;i++)if(host==extra_hosts[i]){assert(*n==extra_sizes[i]);*addr=0x200000+i*0x20000;*token=host;return 0;}
 assert(!"unowned map");return EFI_ERROR(7);
}
static Status EFIAPI unmap(void*p,void*token){assert(p==pci&&token&&!(config[1]&4));unmaps++;return 0;}
static Status EFIAPI free_buffer(void*p,uint64_t pages,void*host){
 assert(p==pci&&host&&!(config[1]&4));unsigned i;
 for(i=0;i<14;i++)if(host==hosts[i]){assert(pages==1);dma_frees++;return 0;}
 for(i=0;i<33;i++)if(host==extra_hosts[i]){assert(pages*4096==extra_sizes[i]);free(host);extra_hosts[i]=0;extra_sizes[i]=0;dma_frees++;return 0;}
 assert(!"unowned free");return EFI_ERROR(7);
}
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
 assert(guard.value[248]==64&&guard.value[8]==s->phase);
 uint8_t req[5]={10,34,0},reply[247];assert(qca_scan_att(247,req,3,reply,247)==247&&!memcmp(reply+1,guard.value,246));
 req[0]=12;req[3]=246;assert(qca_scan_att(247,req,5,reply,247)==171&&!memcmp(reply+1,guard.value+246,170));
 assert(!memcmp(s,&before,sizeof(before))&&!memcmp(qca_persistent_view(),&radio,sizeof(radio))&&!memcmp(qca_prefix_view(),&telemetry,sizeof(telemetry)));active_status_reads++;
}

static void*ram_blocks[2];static unsigned ram_allocs,ram_frees;
static Status EFIAPI ram_allocate(uint32_t kind,uint64_t n,void**out){
 assert(kind==4&&n>0&&ram_allocs<2&&!(config[1]&4)&&allocations==47&&dma_frees==47&&unmaps==47&&opens==closes);
 *out=ram_blocks[ram_allocs++]=malloc((size_t)n);assert(*out);return 0;
}
static Status EFIAPI ram_release(void*p){
 if(p==resource)return free_pool(p);
 unsigned slot=p==ram_blocks[0]?0:1;assert(p&&p==ram_blocks[slot]);free(p);ram_blocks[slot]=0;ram_frees++;return 0;
}

static void*phase_pool,*inventory_pool,*data_pool;static unsigned phase_allocs,phase_frees,inventory_allocs,inventory_frees,info_calls,rng_calls,locate_calls;
static RngStatus EFIAPI public_info(RngProtocol*p,size_t*n,RngGuid*out);
static RngStatus EFIAPI forbidden_rng(RngProtocol*p,RngGuid*g,size_t n,uint8_t*out){(void)p;(void)g;(void)n;(void)out;rng_calls++;assert(!"GetRNG forbidden");return EFI_ERROR(7);}
static RngProtocol inventory_protocol={public_info,forbidden_rng};
static RngStatus EFIAPI public_info(RngProtocol*p,size_t*n,RngGuid*out){assert(p==&inventory_protocol&&n);info_calls++;if(!out){*n=16;return EFI_ERROR(5);}assert(*n==16);*out=rng_ctr_guid;return 0;}
static RngStatus EFIAPI public_locate(RngGuid*g,void*r,void**out){assert(g&&!r&&out&&!memcmp(g,&rng_protocol_guid,16));locate_calls++;*out=&inventory_protocol;return 0;}
extern int runtime_rng_public(RngPublicDiagnostic*);
static Status EFIAPI pool_dispatch(uint32_t kind,uint64_t n,void**out){
 if(kind==4)return ram_allocate(kind,n,out);
 if(kind==2&&n==sizeof(QcaHttDataPath)+_Alignof(QcaHttDataPath)-1){assert(!data_pool);if(data_case==15){*out=data_pool=hosts[7];return 0;}*out=data_pool=malloc((size_t)n);assert(*out);if(data_case==16){memset(*out,0xa5,(size_t)n);return EFI_ERROR(7);}return 0;}
 if(kind==2&&n<=256){assert(n==16&&!inventory_pool&&!inventory_allocs);*out=inventory_pool=malloc((size_t)n);assert(*out);inventory_allocs++;return 0;}
 assert(kind==2&&!phase_pool&&!phase_allocs&&!allocations&&n>94016&&n<200000);
 *out=phase_pool=malloc((size_t)n);assert(*out);phase_allocs++;return 0;
}
static Status EFIAPI pool_release(void*p){
 if(p==inventory_pool){assert(p&&inventory_allocs==1&&!inventory_frees);free(p);inventory_pool=0;inventory_frees++;return 0;}
 if(p==phase_pool){assert(p&&phase_allocs==1&&!phase_frees&&(allocations==47&&dma_frees==47&&unmaps==47)||(allocations==0&&!dma_frees&&!unmaps));free(p);phase_pool=0;phase_frees++;return 0;}
 return ram_release(p);
}
extern int runtime_phase_retire(void);
extern const QcaHttPhaseOwner*runtime_phase_model(void);
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


static void emit_htt(const uint8_t*p,unsigned n){
 const QcaPersistentNative*r=qca_persistent_view();QcaInitAdapter*a=r->startup->operating->boot->board->setup->read.full.adapter;
 assert(r->rx.posted[0]&&registers[1][0x48/4]==a->channels.rings[1].read);unsigned ri=a->channels.rings[1].read;
 uint8_t*raw=hosts[3];memset(raw,0,2048);raw[0]=2;raw[2]=(uint8_t)n;memcpy(raw+8,p,n);hosts[2][ri*8+4]=(uint8_t)(n+8);hosts[2][ri*8+5]=(uint8_t)((n+8)>>8);registers[1][0x48/4]=(ri+1)&7;
}
static unsigned data_step,tx_delay;static uint8_t public_mgmt[24]={0xb0};
static void glue_tick(void);
static int ethernet_failure_tick(void);
static void data_tick(void){if(data_case>=31&&ethernet_failure_tick())return;if(data_case>=23){glue_tick();return;}
 QcaHttDataPath*s=data_model_view();if(!s){if(data_case==15||data_case==16){uint8_t status[544];qca_filter64_status(status);if(bw(status+8)==5){const QcaHttPhaseOwner*po=runtime_phase_model();assert(bw(status+12)==190&&data_model_uncertain()&&!runtime_phase_retire()&&po->arena->runtime.port->dma_users==47);puts("ACTUAL AUX POOL ALIAS/ERROR POINTER RETAINS47 WITHOUT WRITE/FREE PASS");exit(0);}}return;}
 if(s->phase==QDP_QUARANTINED){
  assert(data_case>=2&&data_case<=18&&s->runtime->port->dma_users==47&&s->runtime->callback_owners==1&&!qca_radio_accepts_work(&s->radio->life)&&!qca_htt_runtime_close_one(s->runtime)&&!runtime_phase_retire());
  if(data_case==2)assert(s->error==4&&s->runtime->ring.fill==1023);
  if(data_case==3||data_case==9||data_case==10)assert(s->error==20);
  if(data_case==4||data_case==6)assert(s->error==13&&s->runtime->ring.fill==1023&&s->runtime->owners[0].state==1);
  if(data_case==5)assert(s->error==17&&s->pending_valid&&s->runtime->rx_copy_owners==1&&s->rejected_bytes==2048&&!s->output_count);
  if(data_case==8||data_case==11)assert(s->error==11);
  if(data_case==17||data_case==18)assert(s->error==21&&s->rejected_bytes==2048&&!s->output_count&&s->runtime->rx_copy_owners==1);
  printf("ACTUAL PRODUCER NEGATIVE CASE%u retained47/error%u PASS; SYNTHETIC ONLY\n",data_case,s->error);exit(0);
 }
 if(data_case==1){uint8_t status[544];qca_filter64_status(status);if(bw(status+8)==5){assert(bw(status+12)==191);const QcaHttPhaseOwner*po=runtime_phase_model();assert(!po->arena->runtime.ring.cfg_posted&&!po->arena->runtime.callback_owners&&htt_posts==1);puts("ACTUAL SERVICE65 MISSING FAILS BEFORE RING/PUBLISH PASS; SYNTHETIC ONLY");exit(0);}return;}
 if(s->phase!=QDP_RX_ACTIVE||!s->aggr_done)return;
 if(data_case==22&&qca_scan_native_view()->phase!=QCA_NATIVE_SCAN_LIVE_DONE)return;
 if(data_case==22)assert(qca_radio_accepts_work(&s->radio->life)&&s->runtime->port->dma_users==47&&!qca_scan_native_view()->quiesce_requested);
 assert(s->radio==qca_persistent_view()&&s->runtime->port->dma_users==47&&s->runtime->ring.cfg_posted&&s->runtime->callback_owners==1);
 if(data_case==7){
  static unsigned sent,drained;const QcaPersistentNative*pr=s->radio;QcaInitAdapter*a=pr->startup->operating->boot->board->setup->read.full.adapter;
  if(sent<5&&s->output_count==(sent<4?sent:4)&&pr->rx.posted[0]&&registers[1][0x48/4]==a->channels.rings[1].read){
   uint8_t*raw=(uint8_t*)s->runtime->extra[0].host+sent*2048;memset(raw,0,2048);bp(raw+4,0x80000000u);bp(raw+12,0x70000000u);bp(raw+24,24);bp(raw+56,0xc000);raw[300]=8;raw[302]=(uint8_t)sent;
   uint8_t ind[16]={0x12,16,1,0,0,0,1,0};bp(ind+8,s->runtime->owners[sent].paddr);ind[12]=24;emit_htt(ind,16);sent++;return;
  }
  if(sent==5&&!drained&&s->output_count==4&&pr->rx.count&&pr->rx.events[pr->rx.head].pipe==1&&pr->rx.events[pr->rx.head].payload[0]==0x12){
   const QcaRxEvent*e=&pr->rx.events[pr->rx.head];assert(e->payload[0]==0x12&&bw(e->payload+8)==s->runtime->owners[4].paddr&&s->runtime->owners[4].state==1&&!s->pending_valid&&s->runtime->ring.fill==1023);
   QRxFrame f;uint64_t id;assert(qdp_take_frame(s,&f,&id)&&f.payload[2]==0);drained=1;return;
  }
  if(drained&&s->output_count==4&&!pr->rx.count){
   for(unsigned i=1;i<5;i++){QRxFrame f;uint64_t id;assert(qdp_take_frame(s,&f,&id)&&f.payload[2]==i);}
   assert(s->runtime->ring.fill==1023&&!s->runtime->rx_copy_owners);qdp_quarantine(s,91);assert(!qca_htt_runtime_close_one(s->runtime)&&s->runtime->port->dma_users==47);
   puts("ACTUAL RX OUTPUT BACKPRESSURE RETAINS OWNED CE EVENT; DRAIN RESUMES COPY/REFILL WITHOUT DROP PASS");exit(0);
  }return;
 }
 if(data_step==0){
  uint8_t*raw=s->runtime->extra[0].host;memset(raw,0,2048);bp(raw+4,data_case==5?0:0x80000000u);bp(raw+12,0x70000000u);bp(raw+24,24);bp(raw+56,0xc000);raw[300]=8;if(data_case==17)bp(raw+12,0x60002000u);if(data_case==18)raw[301]=0x40;
  uint8_t inord[24]={0x12,16,1,0,0,0,1,0};bp(inord+8,s->runtime->owners[0].paddr+(data_case==4?8:0));inord[12]=24;
  if(data_case==6){inord[6]=2;memcpy(inord+16,inord+8,8);}emit_htt(inord,data_case==6?24:16);data_step=1;return;
 }
 if(data_step==1&&s->output_count){
  QRxFrame frame;uint64_t completion;assert(qdp_take_frame(s,&frame,&completion)&&frame.bytes==24&&frame.payload[0]==8&&completion>s->floor);
  assert(s->runtime->ring.fill==1023&&s->runtime->owners[0].state==1&&*(uint32_t*)((uint8_t*)s->runtime->extra[0].host+4)==0);
  if(data_case==9)tx_delay=1;if(data_case==14){uint8_t raw_data[24]={8};assert(qdp_submit_raw(s,raw_data,24,1,0,16,now_us)==1);primary_tx_assert(hosts[9],(uint32_t)s->runtime->ce[9].address,raw_data,24,1,0,16);assert(hosts[9][25]==7&&bw(hosts[9]+32)==s->runtime->ce[9].address&&bw(hosts[9])==s->runtime->ce[9].address+1024&&bw(hosts[9]+4)==24);}else{assert(qdp_submit_mgmt(s,public_mgmt,24,1,0,now_us)==1);primary_tx_assert(hosts[9],(uint32_t)s->runtime->ce[9].address,public_mgmt,24,1,3,17);assert(hosts[9][25]==0x67&&bw(hosts[9]+32)==s->runtime->ce[9].address+1024);}assert(s->tx_posted&&s->runtime->tx_owners==1);data_step=2;return;
 }
 if(data_step==2&&s->tx_dma_done){
  assert(!s->tx_htt_done&&s->runtime->tx_owners==1&&!qdp_submit_mgmt(s,public_mgmt,24,2,0,now_us));if(data_case==10)return;uint8_t done[6]={7,128,1,0,1,0};if(data_case==8)done[4]=99;emit_htt(done,6);data_step=3;return;
 }
 if(data_step==3&&!s->tx_posted){
  assert(s->tx_dma_done&&s->tx_htt_done&&!s->tx_status&&!s->runtime->tx_owners);
  if(data_case==11){uint8_t done[6]={7,128,1,0,1,0};emit_htt(done,6);data_step=99;return;}tx_delay=1;assert(qdp_submit_mgmt(s,public_mgmt,24,2,0,now_us));uint8_t done[6]={7,130,1,0,2,0};emit_htt(done,6);data_step=4;return;
 }
 if(data_step==4&&s->tx_htt_done){
  assert(!s->tx_dma_done&&s->tx_posted&&s->runtime->tx_owners==1&&!qdp_submit_mgmt(s,public_mgmt,24,3,0,now_us));QcaInitAdapter*a=s->radio->startup->operating->boot->board->setup->read.full.adapter;registers[4][0x44/4]=a->channels.rings[4].write;data_step=5;return;
 }
 if(data_step==5&&!s->tx_posted){
  assert(s->tx_dma_done&&s->tx_htt_done&&s->tx_status==2&&!s->runtime->tx_owners);
  assert(!qdp_submit_mgmt(s,public_mgmt,24,2,0,now_us));public_mgmt[1]=0x40;assert(!qdp_submit_mgmt(s,public_mgmt,24,3,0,now_us));public_mgmt[1]=0;
  qdp_quarantine(s,90);assert(s->phase==QDP_QUARANTINED&&!qca_htt_runtime_close_one(s->runtime)&&s->runtime->port->dma_users==47&&!runtime_phase_retire());
  printf("DATA_PATH_BYTES=%zu aligned_pool=%zu maps=%u\n",sizeof(*s),sizeof(*s)+_Alignof(QcaHttDataPath)-1,s->runtime->port->dma_users);
  puts("ACTUAL NEW PRODUCER: SERVICE65+47DMA+CFG+OWNED_INORD+COPY+REFILL+MGMT_TYPE3+DMA_FIRST+HTT_FIRST+NOACK+RETAINED_TARGET_STOP_GAP PASS; SYNTHETIC ONLY");exit(0);
 }
}
#include "primary_htt.h"
#include "primary_wmi_generator.h"
static QethPolicy ethernet_policy;static void ethernet_tick(void);
static QsgKeyOp key_operations[2],key_model;static QcaPersistentTx*key_tx;static QpnLedger key_pn;static QcaRxEvent key_confirmations[2];static unsigned key_setup,key_sent;
static void glue_key_tick(void);
static QsgNative glue_model;static StaJoin glue_station;static unsigned glue_setup,glue_sent_map,glue_sent_status,glue_sent_response;
static const uint8_t glue_peer[6]={2,3,4,5,6,7};
static void emit_scan_payload(const uint8_t*,unsigned);
int glue_model_active(void){return glue_model.epoch!=0;}
int glue_model_dispatch(const QcaRxEvent*e,uint64_t now){QcaHttDataPath*d=data_model_view();if(key_model.phase&&e->pipe==1&&e->bytes&&e->payload[0]==11)return qsk_receive(&key_model,e,now);if(glue_model.epoch)return qsg_receive(&glue_model,e,now);if(glue_setup&&e->pipe==1&&e->bytes&&e->payload[0]==3){QcaHttVersion v={0};v.major=3;v.minor=56;return sta_observe_owned(&glue_station,d->epoch,e,2412,0xfff,&d->binding,&v);}return qdp_receive(d,e,now);}
static void glue_tick(void){
 QcaHttDataPath*d=data_model_view();if(d&&glue_model.fault){fprintf(stderr,"GLUE fault=%u phase=%u step=%u posted=%u DMA=%u status=%u response=%u dp_error=%u station_watermark=%u\n",glue_model.fault,glue_model.mgmt.phase,glue_model.mgmt.step,glue_model.mgmt.posted,glue_model.mgmt.dma_closed,glue_model.mgmt.status_seen,glue_model.mgmt.response_seen,d->error,glue_station.watermark);assert((data_case==24||data_case>=26)&&d->runtime->port->dma_users==47&&!qca_radio_accepts_work(&d->radio->life)&&!runtime_phase_retire());if(data_case==26)assert(glue_model.fault==45&&key_model.rejected.raw_bytes==36&&!key_model.sec_seen);if(data_case==28)assert(key_model.sec_seen&&!key_model.dma_seen&&!key_model.dma_serial);if(data_case==29)assert(key_model.dma_seen&&!key_model.sec_seen);printf("ACTUAL STATION GLUE FAULTCASE%u ERROR%u REVOKES/RETAINS47 PASS SYNTHETIC\n",data_case,glue_model.fault);exit(0);}if(!d||d->phase!=QDP_RX_ACTIVE||!d->aggr_done)return;
 const QcaNativeScan*sc=qca_scan_native_view();if(!sc||sc->phase!=QCA_NATIVE_SCAN_LIVE_DONE)return;
 if(!glue_setup){const uint8_t*own=d->radio->startup->transaction.ready.mac;assert(sta_begin(&glue_station,d->epoch,(uint32_t)d->radio->rx.completed,0,glue_peer,own,1,2));glue_setup=1;}
 if(!glue_sent_map){uint8_t map[12]={3,0,7};memcpy(map+4,glue_peer,6);emit_htt(map,12);glue_sent_map=1;return;}
 if(!glue_station.mapped)return;
 if(!glue_model.epoch){StaWireBss b={0};b.epoch=d->epoch;b.observed_us=now_us;b.ttl_us=5000000;b.completion=(uint32_t)d->radio->rx.completed;b.rx_floor=b.completion-1;b.frequency=2412;b.interval=100;b.dtim=1;b.native_rates=0xfff;b.basic_rates=15;memcpy(b.peer,glue_peer,6);memcpy(b.own,glue_station.own_mac,6);b.policy_digest[0]=1;b.native_source[0]=2;b.ssid_bytes=10;memcpy(b.ssid,"iPhone (9)",10);b.mode=1;b.max_power=b.reg_power=20;uint8_t source[32]={1};assert(qsg_begin(&glue_model,d,&glue_station,&b,0xfff,10,source,now_us));}
 if(glue_model.fault){assert(data_case==24&&glue_station.quarantined&&d->runtime->port->dma_users==47&&!qca_radio_accepts_work(&d->radio->life)&&!runtime_phase_retire());if(data_case==26)assert(glue_model.fault==45&&key_model.rejected.raw_bytes==36&&!key_model.sec_seen);if(data_case==28)assert(key_model.sec_seen&&!key_model.dma_seen&&!key_model.dma_serial);if(data_case==29)assert(key_model.dma_seen&&!key_model.sec_seen);printf("ACTUAL STATION GLUE FAULTCASE%u ERROR%u REVOKES/RETAINS47 PASS SYNTHETIC\n",data_case,glue_model.fault);exit(0);}
 if(data_case>=31&&key_operations[1].phase==QSK_CONFIRMED){ethernet_tick();return;}
 int rc=qsg_poll(&glue_model,now_us);
 if(glue_model.fault)return;
 if(rc==1&&data_case>=31&&key_operations[1].phase==QSK_CONFIRMED){ethernet_tick();return;}if(rc==1&&data_case>=25){glue_key_tick();return;}
 if(rc==1){assert(data_case==23&&glue_station.authenticated&&glue_station.associated&&glue_station.aid==1&&!glue_station.ptk&&!glue_station.gtk&&!glue_station.core_completed&&!d->tx_posted&&!d->runtime->tx_owners&&d->runtime->port->dma_users==47);qsg_revoke(&glue_model,99);assert(!qca_radio_accepts_work(&d->radio->life)&&!runtime_phase_retire());puts("ACTUAL STATION GLUE CE4+OWNED_HTT_ACK+OWNED_AUTH_ASSOC+AID PASS; NO KEYS/PORT/IP; SYNTHETIC");exit(0);}
 if(glue_model.mgmt.posted&&d->tx_dma_done&&!d->tx_htt_done&&glue_sent_status!=d->tx_id){uint8_t done[6]={7,128,1,0};if(data_case==24)done[1]=130;done[4]=(uint8_t)d->tx_id;done[5]=d->tx_id>>8;emit_htt(done,6);glue_sent_status=d->tx_id;return;}
 if(glue_model.mgmt.posted&&glue_model.mgmt.status_seen&&!glue_model.mgmt.response_seen&&glue_sent_response!=d->tx_id){uint8_t payload[100]={0};bp(payload,0x7001);bp(payload+4,40|(44u<<16));bp(payload+8,1);uint8_t*f=payload+52;memcpy(f+4,glue_station.own_mac,6);memcpy(f+10,glue_peer,6);memcpy(f+16,glue_peer,6);unsigned n=30;if(!glue_model.mgmt.step){f[0]=0xb0;f[26]=2;}else{f[0]=0x10;f[24]=0x11;f[28]=1;f[29]=0xc0;f[30]=1;f[31]=4;f[32]=0x82;f[33]=0x84;f[34]=0x8b;f[35]=0x96;n=36;}bp(payload+24,n);unsigned pad=(n+3)&~3u;bp(payload+48,pad|(17u<<16));emit_scan_payload(payload,52+pad);glue_sent_response=d->tx_id;return;}
}

int glue_key_mmio(unsigned id,unsigned index,uint32_t value){if(id!=3||index!=0x3c||!key_tx||!key_model.phase||key_tx->phase!=QCA_TX_POSTED)return 0;assert(key_model.phase&&bw(hosts[7]+8)==0x5009&&key_tx->radio==glue_model.data->radio&&key_tx->request==key_model.request&&key_tx->credit->outstanding&&!key_tx->credit->reserved);if(data_case!=28)registers[3][0x44/4]=value;credit_pending+=(key_tx->bytes+key_tx->credit->size-1)/key_tx->credit->size;return 1;}
static void glue_key_tick(void){QcaHttDataPath*d=glue_model.data;
 if(!key_setup){QcaHttVersion v={0};v.major=3;v.minor=56;assert(qpn_begin(&key_pn,d->epoch,glue_station.peer_id,glue_station.vdev,glue_station.peer,glue_station.own_mac,&d->binding,&v));key_tx=(QcaPersistentTx*)&qca_scan_native_view()->tx;assert(key_tx->phase==QCA_TX_IDLE);key_setup=1;}
 if(!key_model.phase){uint8_t public_key[16];memset(public_key,0x42,sizeof public_key);uint8_t rsc[6]={7,6,5,4,3,2};unsigned index=glue_station.ptk?1:0;assert(qsk_begin(&key_model,&glue_model,key_tx,&key_pn,index,public_key,16,rsc,6,now_us));memset(public_key,0,sizeof public_key);key_sent=0;}
 unsigned before_phase=key_model.phase;int rc=qsk_poll(&key_model,now_us);if(rc<0){fprintf(stderr,"KEYFAIL prior=%u index=%u now=%llu deadline=%llu txphase=%u txepoch=%llu epoch=%llu pnepoch=%llu pnq=%u pending=%u sec=%u dma=%u sq=%u\n",before_phase,key_model.index,(unsigned long long)now_us,(unsigned long long)key_model.deadline,key_tx->phase,(unsigned long long)key_tx->epoch,(unsigned long long)key_model.epoch,(unsigned long long)key_pn.epoch,key_pn.quarantined,key_pn.pending,key_model.sec_seen,key_model.dma_seen,glue_station.quarantined);return;}
 if(key_model.phase==QSK_POSTED&&!key_sent&&data_case!=29){uint8_t sec[28]={11,6,7};if(!key_model.index)sec[1]|=128;if(data_case==26)sec[2]=8;emit_htt(sec,28);key_sent=1;return;}
 if(rc==1){assert(key_model.dma_seen&&key_model.sec_seen&&key_tx->phase==QCA_TX_IDLE);for(unsigned j=0;j<4096;j++)assert(!key_tx->frame[j]&&!hosts[7][j]);key_confirmations[key_model.index]=key_model.sec_raw;key_operations[key_model.index]=key_model;assert(key_model.pub_cookie==key_tx->cookie&&key_model.dma_serial==key_tx->completed);uint8_t rsc[6]={1};assert(!qpn_key_posted(&key_pn,d->epoch,key_model.index,rsc,6,(uint32_t)d->radio->rx.completed,99));if(!key_model.index){memset(&key_model,0,sizeof key_model);return;}assert((data_case==25||data_case>=31)&&glue_station.ptk&&glue_station.gtk&&!glue_station.pending&&!glue_station.core_completed&&!sta_local_eligibility(&glue_station,d->epoch));for(unsigned j=0;j<17;j++)assert(key_pn.key[1].last[j]==0x020304050607ULL);assert(key_confirmations[0].completion<key_confirmations[1].completion&&key_confirmations[0].raw_bytes==36&&key_confirmations[1].raw_bytes==36);if(data_case>=31){ethernet_tick();return;}qsg_revoke(&glue_model,100);puts("ACTUAL CE3 KEY PUBLICATION+DMA+OWNED SEC/PTK/GTK+NONZERO_RSC17+WIPE PASS; NO AUTHENTICATED DATA/PORT/IP; SYNTHETIC");exit(0);}
}

int ethernet_mmio(unsigned id,unsigned index,uint32_t value){if(id!=3||index!=0x3c||!ethernet_policy.phase||key_tx->phase!=QCA_TX_POSTED)return 0;assert(bw(hosts[7]+8)==0x5008&&bw(hosts[7]+16)==0&&bw(hosts[7]+24)==1&&key_tx==ethernet_policy.publisher);struct ath10k primary={0};struct sk_buff*oracle=ath10k_wmi_tlv_op_gen_vdev_set_param(&primary,glue_station.vdev,WMI_TLV_VDEV_PARAM_TX_ENCAP_TYPE,1);assert(bw(hosts[7]+8)==WMI_TLV_VDEV_SET_PARAM_CMDID&&!memcmp(hosts[7]+12,oracle->data,16));registers[3][0x44/4]=value;credit_pending+=(key_tx->bytes+key_tx->credit->size-1)/key_tx->credit->size;return 1;}
static void ethernet_tick(void){static unsigned step;QcaHttDataPath*d=glue_model.data;if(!ethernet_policy.phase){assert(qeth_policy_begin(&ethernet_policy,&glue_model,now_us));return;}if(ethernet_policy.phase!=QETH_CONFIG_DMA_DONE){assert(qeth_policy_poll(&ethernet_policy,now_us)>=0);return;}if(step==0){uint8_t ether[113]={0};memcpy(ether,glue_station.peer,6);memcpy(ether+6,glue_station.own_mac,6);ether[12]=0x88;ether[13]=0x8e;ether[14]=2;ether[15]=3;ether[17]=95;
 QsgKeyOp bad=key_operations[0];bad.epoch++;assert(!qeth_submit(&ethernet_policy,&bad,&key_operations[1],ether,sizeof ether,3,now_us));bad=key_operations[0];bad.pub_cookie=ethernet_policy.cookie;assert(!qeth_submit(&ethernet_policy,&bad,&key_operations[1],ether,sizeof ether,3,now_us));bad=key_operations[0];bad.sec_seen=0;assert(!qeth_submit(&ethernet_policy,&bad,&key_operations[1],ether,sizeof ether,3,now_us));bad=key_operations[0];bad.pub_floor=bad.sec_raw.completion;assert(!qeth_submit(&ethernet_policy,&bad,&key_operations[1],ether,sizeof ether,3,now_us));bad=key_operations[0];bad.dma_seen=0;assert(!qeth_submit(&ethernet_policy,&bad,&key_operations[1],ether,sizeof ether,3,now_us));bad=key_operations[0];bad.sec_raw.raw[9]=5;assert(!qeth_submit(&ethernet_policy,&bad,&key_operations[1],ether,sizeof ether,3,now_us));ether[12]=8;ether[13]=0;assert(!qeth_submit(&ethernet_policy,&key_operations[0],&key_operations[1],ether,sizeof ether,3,now_us));ether[12]=0x88;ether[13]=0x8e;assert(!qeth_submit(&ethernet_policy,&key_operations[0],&key_operations[1],hosts[9],sizeof ether,3,now_us));
 if(data_case==33)tx_delay=1;assert(qeth_submit(&ethernet_policy,&key_operations[0],&key_operations[1],ether,sizeof ether,3,now_us)==1);assert(hosts[9][25]==0x42&&(hosts[9][26]|(hosts[9][27]<<8))==0xc00&&bw(hosts[9]+32)==d->runtime->ce[9].address&&!memcmp(hosts[9]+1024,ether,sizeof ether));assert(!glue_station.core_completed&&!sta_local_eligibility(&glue_station,d->epoch));struct peth_data_tx_desc oracle={0};oracle.flags0=PETH_DATA_TX_DESC_FLAGS0_NO_AGGR|(2<<PETH_DATA_TX_DESC_FLAGS0_PKT_TYPE_LSB);oracle.flags1=glue_station.vdev|(PETH_DATA_TX_EXT_TID_NON_QOS_MCAST_BCAST<<PETH_DATA_TX_DESC_FLAGS1_EXT_TID_LSB)|PETH_DATA_TX_DESC_FLAGS1_POSTPONED;oracle.len=sizeof ether;oracle.id=3;oracle.frags_paddr=(uint32_t)d->runtime->ce[9].address;oracle.peerid=65535;assert(sizeof oracle==15&&!memcmp(hosts[9]+25,&oracle,sizeof oracle));assert(!(oracle.flags0&(PETH_DATA_TX_DESC_FLAGS0_MAC_HDR_PRESENT|PETH_DATA_TX_DESC_FLAGS0_NO_ENCRYPT)));step=1;return;}
 int result=qeth_poll_result(&ethernet_policy,now_us);if(result<0){if(data_case==32||data_case==35||data_case==36){assert(d->phase==QDP_QUARANTINED&&d->error==206&&d->tx_status==(data_case==32?2u:data_case==35?1u:3u)&&d->tx_dma_done&&d->tx_htt_done&&!d->runtime->tx_owners&&d->runtime->port->dma_users==47);printf("ACTUAL ETHERNET NON_OK CASE%u STATUS%u REVOKES/RETAINS47 PASS SYNTHETIC\n",data_case,d->tx_status);exit(0);}return;}if(step==1&&(d->tx_dma_done||data_case==33)){if(data_case==34)return;assert(!d->tx_htt_done&&d->runtime->tx_owners);uint8_t done[6]={7,128,1,0,3};if(data_case==32)done[1]=130;if(data_case==35)done[1]=129;if(data_case==36)done[1]=131;emit_htt(done,6);step=2;return;}if(step==2&&!d->tx_posted){assert(d->tx_dma_done&&d->tx_htt_done&&d->tx_status==(data_case==32?2u:0u)&&!d->runtime->tx_owners&&d->runtime->port->dma_users==47);uint8_t replay[113];memcpy(replay,hosts[9]+1024,sizeof replay);assert(!qeth_submit(&ethernet_policy,&key_operations[0],&key_operations[1],replay,sizeof replay,3,now_us));qsg_revoke(&glue_model,99);printf("CASE%u STATUS%u ",data_case,d->tx_status);puts("ACTUAL EXPERIMENTAL ETHERNET2/TID16/NO_ENCRYPT0 +CE3_POLICY_NATIVE1+PTK_GTK_SEC+REALDMA_HTT+EAPOL_BEFORE_PORT+IP_CLOSED_REJECT PASS; NO PHYSICAL ENCRYPTION CLAIM");exit(0);}}

int ethernet_model_dispatch(const QcaRxEvent*e,uint64_t now){if(ethernet_policy.phase&&e->pipe==1&&e->bytes&&e->payload[0]==7)return qdp_receive(glue_model.data,e,now);return glue_model_dispatch(e,now);}

static int ethernet_failure_tick(void){QcaHttDataPath*d=data_model_view();if(!d||d->phase!=QDP_QUARANTINED)return 0;fprintf(stderr,"ETHFAULT case=%u error=%u pol=%u txid=%u posted=%u DMA=%u HTT=%u gsg=%u\n",data_case,d->error,ethernet_policy.phase,d->tx_id,d->tx_posted,d->tx_dma_done,d->tx_htt_done,glue_model.fault);assert((data_case==33||data_case==34)&&d->error==20&&d->tx_posted&&d->runtime->tx_owners==1&&d->runtime->port->dma_users==47&&!runtime_phase_retire());if(data_case==33)assert(d->tx_htt_done&&!d->tx_dma_done);else assert(d->tx_dma_done&&!d->tx_htt_done);printf("ACTUAL ETHERNET MISSING OWNER CASE%u ERROR20 RETAINS47 PASS SYNTHETIC\n",data_case);exit(0);}

static const uint8_t physical54_0[]={17,208,1,0,112,0,17,0,0,0,0,0,33,112,39,3,4,253,0,230,205,171,0,0,1,123,39,3,4,252,93,166,4,234,1,0,39,126,39,3,4,253,54,166,2,16,0,0,39,126,39,3,4,253,54,166,23,0,0,0,39,126,39,3,4,253,12,180,1,0,0,0,40,126,39,3,4,253,51,142,88,0,0,0,41,126,39,3,8,253,58,142,24,171,154,0,0,0,0,0,47,126,39,3,12,253,35,166,1,0,0,0,1,0,0,0,1,0,0,0};
static const uint8_t physical54_1[]={25,208,1,0,4,0,93,2,0,0,0,0};
static const uint8_t physical54_2[]={6,96,1,0,4,0,162,1,34,0,0,0,136,0,16,0,87,24,1,0,154,24,1,0,241,24,1,0,242,24,1,0,123,6,0,0,124,6,0,0,125,6,0,0,126,6,0,0,202,9,0,0,203,9,0,0,3,10,0,0,4,10,0,0,19,10,0,0,20,10,0,0,142,10,0,0,143,10,0,0,144,10,0,0,145,10,0,0,146,10,0,0,147,10,0,0,148,10,0,0,149,10,0,0,150,10,0,0,151,10,0,0,152,10,0,0,153,10,0,0,154,10,0,0,155,10,0,0,156,10,0,0,157,10,0,0,163,10,0,0,164,10,0,0,165,10,0,0,166,10,6,0};
static const uint8_t physical54_3[]={17,208,1,0,104,2,17,0,0,0,0,0,47,126,39,0,4,0,0,0,21,0,0,0,47,126,39,3,16,252,3,128,0,0,0,0,136,167,66,0,128,165,70,0,124,90,1,0,47,126,39,3,16,252,4,128,0,0,0,0,224,32,65,0,252,33,65,0,4,0,0,0,47,126,39,3,16,252,4,128,1,0,0,0,92,61,65,0,112,61,65,0,4,0,0,0,47,126,39,3,16,252,4,128,2,0,0,0,80,160,64,0,188,162,64,0,4,0,0,0,47,126,39,3,16,252,4,128,3,0,0,0,144,56,65,0,88,61,65,0,4,0,0,0,47,126,39,3,16,252,4,128,4,0,0,0,12,137,64,0,68,160,64,0,1,0,0,0,47,126,39,3,16,252,4,128,5,0,0,0,160,26,65,0,188,32,65,0,4,0,0,0,47,126,39,3,16,252,4,128,6,0,0,0,40,76,64,0,140,76,64,0,4,0,0,0,47,126,39,3,16,252,4,128,7,0,0,0,0,128,73,0,252,255,73,0,4,0,0,0,47,126,39,3,16,252,3,128,1,0,0,0,216,254,160,0,216,254,160,0,40,1,0,0,47,126,39,3,16,252,3,128,2,0,0,0,128,115,11,0,172,121,11,0,84,6,0,0,48,126,39,3,16,252,6,128,51,0,0,0,68,2,0,0,159,178,159,0,162,160,155,0,48,126,39,3,16,252,6,128,51,0,0,0,44,5,0,0,159,178,159,0,162,160,155,0,48,126,39,3,16,252,6,128,51,0,0,0,100,45,0,0,159,178,159,0,162,160,155,0,48,126,39,3,16,252,6,128,51,0,0,0,156,52,0,0,159,178,159,0,162,160,155,0,48,126,39,3,16,252,6,128,32,0,0,0,156,52,0,0,159,178,159,0,72,179,159,0,48,126,39,3,16,252,6,128,51,0,0,0,68,1,0,0,159,178,159,0,162,160,155,0,48,126,39,3,16,252,6,128,51,0,0,0,4,64,0,0,159,178,159,0,162,160,155,0,48,126,39,3,16,252,6,128,32,0,0,0,4,64,0,0,159,178,159,0,72,179,159,0,48,126,39,3,16,252,6,128,51,0,0,0,4,72,0,0,159,178,159,0,162,160,155,0,48,126,39,3,16,252,6,128,32,0,0,0,4,72,0,0,159,178,159,0,72,179,159,0,49,126,39,3,16,252,6,128,51,0,0,0,108,2,0,0,159,178,159,0,162,160,155,0,49,126,39,3,16,252,6,128,51,0,0,0,100,0,0,0,159,178,159,0,162,160,155,0,49,126,39,3,16,252,6,128,51,0,0,0,0,7,0,0,159,178,159,0,162,160,155,0,49,126,39,3,16,252,6,128,51,0,0,0,100,2,0,0,159,178,159,0,162,160,155,0};
static const uint8_t physical54_4[]={1,48,0,0,28,0,36,0,1,0,0,0,6,0,0,0,0,0,0,0,8,160,0,0,7,160,0,0,0,0,0,0,0,0,0,0};
static const uint8_t physical54_5[]={1,48,0,0,28,0,36,0,8,0,0,0,6,0,0,0,108,9,0,0,8,160,0,0,7,160,0,0,0,0,0,0,0,0,0,0};

static void emit_scan_payload(const uint8_t*p,unsigned n){
 const QcaPersistentNative*r=qca_persistent_view();QcaInitAdapter*a=r->startup->operating->boot->board->setup->read.full.adapter;
 assert(r->rx.posted[1]&&registers[2][0x48/4]==a->channels.rings[2].read);unsigned ri=a->channels.rings[2].read;
 uint8_t*b=hosts[5];memset(b,0,2048);b[0]=1;b[2]=(uint8_t)n;b[3]=(uint8_t)(n>>8);memcpy(b+8,p,n);
 hosts[4][ri*8+4]=(uint8_t)(n+8);hosts[4][ri*8+5]=(uint8_t)((n+8)>>8);registers[2][0x48/4]=(ri+1)&7;
}
static void emit_scan_event(unsigned type,unsigned reason,unsigned request){
 uint8_t b[32]={0};bp(b,0x3001);bp(b+4,24|(36u<<16));bp(b+8,type);bp(b+12,reason);
 bp(b+16,type==8?2412:0);bp(b+20,0xa000|request);bp(b+24,0xa007);emit_scan_payload(b,32);
}
static void emit_beacon(void){
 uint8_t b[112]={0};bp(b,0x7001);bp(b+4,40|(44u<<16));bp(b+8,native_scenario==3?6:1);bp(b+24,51);bp(b+48,52|(17u<<16));
 uint8_t*f=b+52;f[0]=0x80;for(unsigned j=0;j<6;j++){f[4+j]=255;f[10+j]=f[16+j]=(uint8_t)(j+2);}f[32]=100;f[34]=0x11;
 f[36]=0;f[37]=10;memcpy(f+38,"iPhone (9)",10);f[48]=3;f[49]=1;f[50]=native_scenario==3?6:1;
 if(native_scenario==4)b[4]=39;emit_scan_payload(b,104);
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

 assert(allocations==47&&dma_frees==47&&unmaps==47&&opens==closes&&!(config[1]&4));
 allocations=dma_frees=unmaps=0;memset(hosts,0,sizeof(hosts));unsigned cancel_called=0;
 for(unsigned ms=15001;ms<60000;){
  if(fault==16&&qca_operating_view()->phase==1){
   /* RX first, TX hardware index delayed until the next cooperative poll. */
   if(qca_operating_view()->control.deferred_bytes)registers[0][0x44/4]=registers[0][0x3c/4];
  }

  const QcaWmiStartup*w=qca_wmi_startup_view();

  if(filter_scenario==4&&!early_credit_delivered&&w->transaction.ready_seen&&w->rx1_posted){
   QcaInitAdapter*a=w->operating->boot->board->setup->read.full.adapter;unsigned ri=a->channels.rings[1].read;uint8_t*p=hosts[3];memset(p,0,2048);p[1]=2;p[2]=8;p[4]=8;p[8]=1;p[9]=4;p[12]=1;p[13]=1;hosts[2][ri*8+4]=16;hosts[2][ri*8+5]=0;registers[1][0x48/4]=(ri+1)&7;early_credit_delivered=1;
  }
  if(startup_fault==1&&w->transaction.ready_seen&&(filter_scenario!=4||early_credit_delivered))registers[FW_WMI_TX][0x44/4]=registers[FW_WMI_TX][0x3c/4];
  if(startup_fault==10&&w->tx_posted)qca_wmi_startup_cancel((QcaWmiStartup*)w);
  if(startup_fault==18&&w->transaction.phase==QCA_INIT_RESERVED)qca_wmi_startup_cancel((QcaWmiStartup*)w);
  if(startup_fault==19&&w->tx_posted)((QcaWmiStartup*)w)->last=UINT64_MAX;
  if(startup_fault==21&&w->tx_posted)assert(qca_stop());
  if(startup_fault==20&&w->tx_posted)((QcaWmiStartup*)w)->operating->boot->asset->poisoned=1;

  const QcaPersistentNative*p=qca_persistent_view();
  if(p->life.phase==QCA_RADIO_ACTIVE){
   active_ticks++;
   QcaInitAdapter*a=p->startup->operating->boot->board->setup->read.full.adapter;
   assert(allocations==47&&!dma_frees&&!unmaps&&r->asset.pinned&&a->mapped.irq->port->dma_users==47);
   assert(a->channels.rings[3].owned&&a->bus.owned&&qca_radio_accepts_work(&p->life));

   assert(!qca_rx_clear((QcaPersistentRx*)&p->rx,&p->life));


   if(echo_pending&&!echo_delivered&&filter_scenario!=2&&filter_scenario!=6&&p->rx.posted[1]&&registers[2][0x48/4]==a->channels.rings[2].read){
    uint8_t b[12]={0};bp(b,0x1d001);bp(b+4,4|(54u<<16));bp(b+8,filter_scenario==1?0x64000002:0x64000001);emit_scan_payload(b,12);echo_delivered=1;
   }
   if(filter_scenario==6&&echo_pending&&overflow_emitted<17&&p->rx.posted[1]&&registers[2][0x48/4]==a->channels.rings[2].read){uint8_t unknown[8]={0x22,0x22,0x22};emit_scan_payload(unknown,8);overflow_emitted++;}
   if(htt_posts&&!htt_delivered&&p->rx.posted[0]&&registers[1][0x48/4]==a->channels.rings[1].read){
    deliver_rx(1,1);unsigned ri=a->channels.rings[1].read;uint8_t*b=hosts[3];memset(b,0,24);b[0]=2;b[2]=4;b[8]=0;b[9]=56;b[10]=filter_scenario==3?2:3;hosts[2][ri*8+4]=12;hosts[2][ri*8+5]=0;htt_delivered=1;
   }
   const QcaNativeScan*sc=qca_scan_native_view();scan_observe_active();
   if(filter_scenario==7&&!mixed_emitted&&sc->scan.pending.started&&p->rx.posted[0]&&registers[1][0x48/4]==a->channels.rings[1].read){
    deliver_rx(1,1);unsigned ri=a->channels.rings[1].read;uint8_t*b=hosts[3];memset(b,0,24);b[0]=2;b[2]=4;b[8]=99;hosts[2][ri*8+4]=12;hosts[2][ri*8+5]=0;mixed_emitted=1;
   }

   if(native_scenario==7&&sc->scan.stop_begun)((QcaNativeScan*)sc)->last=UINT64_MAX;
   if(credit_pending&&native_scenario!=2&&p->rx.posted[0]&&registers[1][0x48/4]==a->channels.rings[1].read){
    deliver_rx(1,2);hosts[3][13]=(uint8_t)credit_pending;credit_pending=0;
   }

   if(native_scenario>=10&&p->rx.posted[1]&&registers[2][0x48/4]==a->channels.rings[2].read){
    unsigned burst=native_scenario==11?17:4;
    if(regression_emitted<burst){
     const uint8_t*packets[4]={physical54_0,physical54_1,physical54_2,physical54_3};unsigned sizes[4]={sizeof physical54_0,sizeof physical54_1,sizeof physical54_2,sizeof physical54_3};
     unsigned which=regression_emitted%4;emit_scan_payload(packets[which],sizes[which]);regression_emitted++;
    }else if(sc->scan.stop_begun){
     if(emitted==0){uint8_t b[40];memcpy(b,physical54_4,sizeof physical54_4);
      if(native_scenario==12)bp(b+12,0xffffffff);
      if(native_scenario==14)bp(b+32,0xdeadbeef);
      if(native_scenario==15){bp(b+4,20|(36u<<16));emit_scan_payload(b,28);}
      else if(native_scenario==16){memcpy(b+36,b+4,4);bp(b+36,0|(36u<<16));emit_scan_payload(b,40);}
      else emit_scan_payload(b,sizeof physical54_4);emitted=1;
     }else if(emitted==1&&sc->scan.pending.started){emit_scan_payload(physical54_5,sizeof physical54_5);emitted=2;}
     else if(emitted==2&&sc->scan.live_frequency==2412){emit_beacon();if(native_scenario==17){hosts[5][8+52+38]='X';emitted=30;}else emitted=3;}
     else if(emitted==30&&sc->archive_count==5){emit_beacon();emitted=3;}
     else if(emitted==3&&native_scenario==18&&sc->scan.has_observation&&sc->scan.stop.stop.phase>=QCA_STOP_POSTED){emit_beacon();emitted=31;}
     else if(emitted==31&&sc->archive_count==5&&sc->scan.stop.stop.phase>=QCA_STOP_POSTED){emit_scan_event(2,1,8);emitted=4;}
     else if((emitted==3||native_scenario==11)&&sc->scan.stop.stop.phase>=QCA_STOP_POSTED){emit_scan_event(2,native_scenario==13?6:1,8);emitted=4;}
    }
   }
   if(native_scenario<10&&sc->scan.stop_begun&&p->rx.posted[1]&&registers[2][0x48/4]==a->channels.rings[2].read){
    if(emitted==0){if(native_scenario==1||native_scenario==9){uint8_t b[8]={0x56,0x34,0x12};emit_scan_payload(b,8);emitted=10;}
     else if(native_scenario==8){emit_scan_event(1,0,9);emitted=10;}
     else {emit_scan_event(1,0,8);emitted=1;}}
    else if(emitted==10&&sc->archive_count){if(native_scenario==9){uint8_t b[8]={0x22,0x22,0x22};emit_scan_payload(b,8);emitted=11;}else {emit_scan_event(1,0,8);emitted=1;}}
    else if(emitted==11&&sc->archive_count==2){emit_scan_event(1,0,8);emitted=1;}
    else if(emitted==1&&sc->scan.pending.started){emit_scan_event(8,0,8);emitted=2;}
    else if(emitted==2&&sc->scan.live_frequency==2412){emit_beacon();emitted=3;}
    else if(emitted==3&&(sc->scan.ssid_seen||sc->archive_count)){emit_scan_event(2,sc->scan.stop.stop.phase>=QCA_STOP_POSTED?1:0,8);emitted=4;}
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
   if(active_ticks==200&&persistent_fault){
    if(persistent_fault==1)a->channels.rings[3].fault=1;
    else if(persistent_fault==2)a->channels.buffers[7].valid=0;
    else if(persistent_fault==3)((QcaFirmwarePort*)r)->asset.poisoned=1;
    else if(persistent_fault==4)a->channels.routes[3].pipe=0;
    else if(persistent_fault==5)((QcaPersistentNative*)p)->life.last=UINT64_MAX;
    else {assert(qca_stop());stopped=1;assert(!qca_radio_accepts_work(&p->life));}
   }
  }
  {uint8_t fs[544];qca_filter64_status(fs);unsigned delta=((filter_scenario==8||filter_scenario==9)&&bw(fs+8)==1)?500:1;tick(ms);ms+=delta;}const QcaBootNative*b=qca_boot_view();
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
 assert(qca_boot_round()&&get(128)==6u&&allocations==47&&dma_frees==47&&unmaps==47&&opens==closes&&!r->asset.pinned);
 if(!fault||fault==16||fault==24||fault==32||fault==35)assert(b->phase==5&&b->plan.phase==20&&!b->error&&b->ready_bytes==20&&executions==2&&streams==3&&main_done==1);
 else if(fault<=5)assert(b->phase==6&&b->error);
 else if(fault<=7)assert(b->phase==1&&!b->error&&!main_done);
 else assert(b->phase==5&&!b->error);
 const QcaOperating*o=qca_operating_view();
 if(startup_fault==20)assert(o->phase==3&&o->error==2);else if(!fault||fault==16||fault==24||fault==32||fault==35)assert((persistent_fault||rx_scenario||(o->phase==2&&!o->error))&&o->service_valid&&o->service.build==(fault==35?21u:1234u)&&o->control.session.phase==QCA_HTC_RUNNING&&o->tx_count==3&&o->rx_count==(fault==32?3u:4u));
 else if(fault>=8&&fault!=15&&fault!=24)assert(o->phase==3&&o->error);
 
 if(fault==10||fault==18||fault==19||fault==22||fault==23||fault==25||fault==26){assert(o->error==4&&o->rx_diagnostic[0]==1&&o->rx_diagnostic[1]==5&&o->rx_diagnostic[7]==(fault==23?18u:20u)&&o->rx_descriptor[4]==(fault==23?18u:20u));}
 if(fault==17){assert(o->error==4&&o->rx_diagnostic[1]==4&&o->rx_diagnostic[7]==7&&o->rx_prefix[7]==0);}
 if(fault==20){assert(o->error==4&&o->rx_diagnostic[1]==2&&o->rx_diagnostic[8]);}
 if(fault==21){assert(o->error==4&&o->rx_diagnostic[1]==1);}

 const QcaWmiStartup*w=qca_wmi_startup_view();
 if(startup_fault==0||startup_fault==1||startup_fault==15||startup_fault==22){
  fprintf(stderr,"STARTUP phase=%u err=%u transaction=%u ready=%u tx=%u rx=%u early=%u\n",w->phase,w->error,w->transaction.phase,w->transaction.ready_seen,w->transaction.tx_complete,w->rx_count,early_credit_delivered);assert((persistent_fault||rx_scenario||(w->phase==2&&!w->error&&w->transaction.phase==QCA_INIT_RUNNING))&&w->transaction.ready_seen&&w->transaction.tx_complete);
  assert(w->transaction.ready.mac[0]==2&&w->transaction.ready.mac[5]==1&&w->transaction.ready.abi_minor==(startup_fault==15?53u:574u));
  fprintf(stderr,"INIT COUNTS tx=%u rx=%u posted=%u available=%u outstanding=%u\n",w->tx_count,w->rx_count,w->tx_posted,o->control.credit.available,o->control.credit.outstanding);
  assert(w->tx_count==1&&w->rx_count==(filter_scenario==4?2u:1u)&&!w->tx_posted&&(filter_posts||scan_posts||rx_scenario||((o->control.credit.available==(o->control.credit.total-(startup_fault==0?0u:1u)))&&o->control.credit.outstanding==(startup_fault==0?0u:1u))));
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
  assert(active_ticks>0);
  if(!persistent_fault&&(rx_scenario<3||rx_scenario==10||rx_scenario==11)){
   assert(p->life.phase==QCA_RADIO_CLOSED&&qca_persistent_unload_safe(p));

  }
  else {assert(p->life.phase==QCA_RADIO_RETAINED&&!qca_persistent_unload_safe(p)&&!qca_radio_accepts_work(&p->life));}
 }else assert(!active_ticks&&!p->life.phase);
 
 if((rx_scenario>=3&&rx_scenario<=9)||rx_scenario==12||rx_scenario==13){
  assert(p->rx.phase==QCA_RX_FAULT&&p->rx.error&&!qca_rx_clear((QcaPersistentRx*)&p->rx,&p->life));
  assert(p->rx.completed==(rx_scenario==13?1u:0u));
  assert(o->control.credit.available==o->control.credit.total-(startup_fault==1?1u:0u));
  assert(o->control.credit.outstanding==(startup_fault==1?1u:0u));
 }


 {tick(60001);const QcaNativeScan*sc=qca_scan_native_view();uint8_t f[544];qca_filter64_status(f);
  assert(bw(f+8+44*4)==1);
  unsigned success=(native_scenario==0||native_scenario==1||native_scenario==8)&&(filter_scenario==0||filter_scenario==4||filter_scenario==7||filter_scenario==8);
  if(native_scenario==3&&!filter_scenario){assert(bw(f+8)==4&&!sc->error&&!sc->scan.ssid_seen);}
  else if(success){assert(filter_posts==3&&echo_delivered&&htt_posts==1&&htt_delivered);assert(bw(f+8)==4&&!bw(f+12));assert(sc->scan.ssid_seen&&sc->scan.has_observation&&sc->scan.stop.stop.terminal_seen);}
  else {assert(bw(f+8)==5&&sc->error);if(filter_scenario)assert(!sc->scan.ssid_seen);}
  if(filter_scenario==4){const QcaWmiStartup*w=qca_wmi_startup_view();assert(early_credit_delivered&&w->rx_count==2&&w->ready_frame_bytes==52&&bw(w->prefix+8)==2&&w->frame_bytes==16);}
  if(filter_scenario==6)assert(sc->archive_count==16);
  if(filter_scenario==7)assert(mixed_emitted);
  if(filter_scenario==8){uint64_t began=0,dma=0,gap=0;for(unsigned k=0;k<8;k++){began|=(uint64_t)f[448+k]<<(8*k);dma|=(uint64_t)f[512+k]<<(8*k);gap|=(uint64_t)f[504+k]<<(8*k);}assert(dma-began>3000000&&gap>=500000);}
  if(filter_scenario==9)assert(echo_delivered&&!bw(f+8+7*4)&&!htt_posts&&!sc->scan.ssid_seen&&sc->tx.error==3);
  if(success){
  assert(sc->tx.serial==sc->tx.attempted&&sc->tx.completed==sc->tx.attempted&&sc->tx.completed>=7);
  assert(bw(f+8+31*4)==3&&bw(f+8+32*4)==56&&bw(f+8+34*4));
  }
  uint8_t page[512],copy[512];for(unsigned i=0;i<110;i++){unsigned n=qca_native_scan_export(sc,i,page,512);assert(n==(i%5==4?56u:512u));assert(qca_native_scan_export(sc,i,copy,512)==n&&!memcmp(page,copy,n));}
  if(success)assert(!memcmp(sc->scan.observation.parsed.bss.ssid,"iPhone (9)",10)&&sc->scan.observation.parsed.bss.ssid_bytes==10);
  for(unsigned slot=0;slot<sc->archive_count;slot++){
   uint8_t full[2104];unsigned used=0;for(unsigned part=0;part<5;part++){uint8_t part_bytes[512];unsigned n=qca_native_scan_export(sc,slot*5+part,part_bytes,512);assert(n==(part==4?56u:512u));memcpy(full+used,part_bytes,n);used+=n;}
   const QcaRxEvent*e=&sc->archive[slot];assert(!memcmp(full,"QFEX0001",8)&&bw(full+20)==e->completion&&bw(full+44)==e->raw_bytes);
   assert(!memcmp(full+56,e->raw,e->raw_bytes));for(unsigned j=e->raw_bytes;j<2048;j++)assert(!full[56+j]);
  }
  assert(active_status_reads);assert(!prefix_driver_model_frame(&model_sf));free(model_surface);free(model_physical);prefix_driver_model_display(0,0,0,0);
  printf("FILTER64_ACTUAL_PRODUCER_SYNTHETIC filter3/ECHO/HTT3.56/passiveSSID/raw22/all14 PASS\n");}
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
 assert(argc==11);data_case=(unsigned)atoi(argv[10]);filter_scenario=(unsigned)atoi(argv[9]);native_scenario=(unsigned)atoi(argv[7]);assert(native_scenario<=18);rx_scenario=(unsigned)atoi(argv[6]);assert(rx_scenario<=13);persistent_fault=(unsigned)atoi(argv[5]);assert(persistent_fault<=5);startup_fault=(unsigned)atoi(argv[4]);assert(startup_fault<=22);fault=(unsigned)atoi(argv[3]);assert(fault<=40);scenario=(unsigned)atoi(argv[1]);assert(scenario<=18||(scenario>=100&&scenario<=110)||(scenario>=200&&scenario<=244));unsigned initial=scenario;
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
 boot[64/8]=pool_dispatch;boot[72/8]=pool_release;boot[320/8]=public_locate;
 sm_fixture();usb_fixture();
 if(data_case==13){qca_controller=0;qca_start(&port_system,0);const QcaHttPhaseOwner*po=runtime_phase_model();assert(po->arena&&!po->arena->runtime.phase&&!allocations);QcaHttRuntime*rt=(QcaHttRuntime*)&po->arena->runtime;rt->allocated=1;assert(!runtime_phase_retire()&&phase_pool&&!phase_frees);rt->allocated=0;assert(runtime_phase_retire()&&phase_frees==1&&!phase_pool&&!qca_scan_native_view());puts("ACTUAL ABSENT RADIO UNUSED POOL + NONCANONICAL RETAIN + CANONICAL DETACH FREE PASS");exit(0);}qca_start(&port_system,0);tick(1);
 if(scenario==9||scenario==10){if(scenario==10)tick(21);assert(qca_stop()&&get(168)==1);}
 for(unsigned ms=initial==10?22:2;ms<((initial==18||initial>=100)?60000u:15000u);ms+=(initial==18&&get(128)==18&&get(800)==3)?600u:((initial==100&&get(888)==1)?4000u:((initial==244&&get(316)==1)?4000u:1u))){tick(ms);if(initial>=230&&initial<=239&&get(280)==1&&get(288)==(unsigned)(initial-230))(void)qca_stop();}
 assert(initial==0&&get(128)==5&&!(config[1]&4));
 FILE*wf=fopen(argv[8],"rb");assert(wf&&!fseek(wf,0,SEEK_END));long wn=ftell(wf);assert(wn>0&&wn<65536);rewind(wf);uint8_t*wp=malloc((size_t)wn);assert(wp&&fread(wp,1,(size_t)wn,wf)==(size_t)wn);fclose(wf);
 model_surface=malloc((480*270+32)*4);model_physical=malloc((1280*720+32)*4);assert(model_surface&&model_physical);
 for(unsigned i=0;i<480*270+32;i++)model_surface[i]=0xdeadbeef;for(unsigned i=0;i<1280*720+32;i++)model_physical[i]=0xdeadbeef;
 model_sf=(Surface){model_surface+16,480,270,480,1};prefix_driver_model_display(model_physical+16,1280,720,1280);
 assert(!prefix_driver_model_world(wp,(uint32_t)wn,&model_sf));assert(!prefix_driver_model_frame(&model_sf));free(wp);
upload_fixture(argv[2]);
 assert(phase_allocs==1&&!phase_frees&&phase_pool&&qca_scan_native_view());
 assert(locate_calls==1&&info_calls==2&&rng_calls==0&&inventory_allocs==1&&inventory_frees==1&&!inventory_pool);
 RngPublicDiagnostic rd;assert(runtime_rng_public(&rd)&&rd.phase==2&&rd.algorithm_count==1&&!rd.owned_pool_count&&!rd.uncertain_pool_count);
 uint8_t captured[544];qca_filter64_status(captured);assert(captured[244]==64);
 const QcaHttPhaseOwner*po=runtime_phase_model();const QcaHttRuntime*rt=&po->arena->runtime;const QcaPersistentNative*pp=qca_persistent_view();
 fprintf(stderr,"RETIRE phase%u runtime%u detachable%d port claimed%u dma%u wake%u link%u irq%u scanRadio%p life%u ticket%llu reserved%u queryOwner%p epoch%llu/%llu\n",po->phase,rt->phase,qca_htt_runtime_detachable(rt),rt->port->claimed,rt->port->dma_users,rt->port->wake_owned,rt->port->link_owned,rt->port->boot_irq_owned,(void*)po->arena->scan.radio,pp->life.phase,(unsigned long long)po->arena->scan.tx.ticket,po->arena->scan.tx.credit?po->arena->scan.tx.credit->reserved:0,(void*)pp->htt_owner,(unsigned long long)rt->epoch,(unsigned long long)po->epoch);
 assert(runtime_phase_retire()&&phase_frees==1&&!phase_pool&&!qca_scan_native_view());
 uint8_t absent[544];qca_filter64_status(absent);assert(absent[244]==64&&!absent[8]);
 assert(runtime_phase_retire());puts("ACTUAL TWO ACQUISITIONS 47 MAPS EACH; CAPTURE RETAINED; DETACH BEFORE POOL FREE PASS");return 0;
}
