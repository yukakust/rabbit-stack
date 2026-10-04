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
#include "reset_core.h"
#include "diag_ce.h"
#include <stdlib.h>
uint8_t qca_diagnostic[888];void*qca_controller;
static unsigned scenario,reset_writes,reset_cleared,allocations,dma_frees,unmaps,flushes;
static _Alignas(4096) uint8_t hosts[14][4096];
static uint32_t registers[8][32];static uint16_t link_control=0x143;static uint32_t boot_regs[6]={0x12300e88};static unsigned mask_attempts,link_disables,msi_toggled;static uint32_t reset_register;
static uint64_t now_us,last_reset_write;
static uint32_t warm_register,warm_lf=0x14,fw=2,warm_cpus;static unsigned warm_write_failed;
static uint32_t get(unsigned i){return qca_diagnostic[i]|((uint32_t)qca_diagnostic[i+1]<<8)|((uint32_t)qca_diagnostic[i+2]<<16)|((uint32_t)qca_diagnostic[i+3]<<24);}
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
  boot_regs[index]=v;if(off==0x3a008&&v==0x7fc00){boot_regs[3]|=0x400;if(scenario==33)msi_toggled=1;}return 0;
 }
 if(off>=0x34400&&off<=0x36050){
  assert(p==pci&&width==2&&!bar&&count==1);unsigned id=(unsigned)(off-0x34400)/0x400,index=(unsigned)(off-0x34400)%0x400;assert(id<8&&index<=0x50);
  uint32_t value=*(uint32_t*)in;
  if(index==0x18)registers[id][index/4]=value?9:0;
  else if(index==0x30||index==0x38)registers[id][index/4]&=~value;
  else registers[id][index/4]=value;
  if(id==7&&index==0x3c&&(config[1]&4)){
   unsigned si=(value-1)&7,ri=(registers[7][0x40/4]-1)&7;
   const uint8_t*tx=hosts[0]+si*8,*rx=hosts[1]+ri*8;
   uint32_t addr=(uint32_t)tx[0]|((uint32_t)tx[1]<<8)|((uint32_t)tx[2]<<16)|((uint32_t)tx[3]<<24);
   assert(addr==0xd11008f8||addr==0xd1101ee0||addr==0xd1100900||addr==0xd11008cc);
   assert(tx[4]==(addr==0xd1101ee0?36:4)&&!tx[5]&&!tx[6]&&!tx[7]);
   assert(rx[0]==0&&rx[1]==0x30&&rx[2]==0x10&&!rx[3]&&!rx[4]&&!rx[5]&&!rx[6]&&!rx[7]);
  }
  if(id==7&&index==0x3c&&(config[1]&4)&&scenario!=38&&scenario!=50){
   unsigned si=(value-1)&7;const uint8_t*tx=hosts[0]+si*8;
   uint32_t addr=(uint32_t)tx[0]|((uint32_t)tx[1]<<8)|((uint32_t)tx[2]<<16)|((uint32_t)tx[3]<<24);
   if((scenario==53&&addr==0xd1101ee0)||(scenario==56&&addr==0xd1100900)||(scenario==57&&addr==0xd11008cc))return 0;
   registers[7][0x44/4]=value;if(scenario==39||scenario==51||(scenario==55&&addr==0xd1101ee0))return 0;
   registers[7][0x48/4]=registers[7][0x40/4];
   unsigned ri=(registers[7][0x40/4]-1)&7;hosts[1][ri*8+4]=scenario==40?5:scenario==44&&addr==0xd11008f8?0:scenario==54&&addr==0xd1101ee0?35:tx[4];
   const uint32_t state[9]={scenario==59?0xffffffffu:0x00402000u,0x00402400,1,1,0,0,0,0,1};
   unsigned nwords=addr==0xd1101ee0?9:1;
   for(unsigned j=0;j<nwords;j++){
    uint32_t v=addr==0xd11008f8?(scenario==52?0x00401000u:0x00401ee0u):addr==0xd1101ee0?state[j]:addr==0xd1100900?0x6d8a0000u:0;
    for(unsigned n=0;n<4;n++)hosts[3][4*j+n]=(uint8_t)(v>>(8*n));
   }
  }
  if(!id&&index==0x3c&&(config[1]&4)&&scenario!=14){
   assert(get(620)==2&&get(628)==15);assert(hosts[2][0]==8&&!hosts[2][1]);registers[0][0x44/4]=value;if(scenario==34)return 0;registers[1][0x48/4]=registers[1][0x40/4];
   unsigned ri=(registers[1][0x40/4]-1)&7;hosts[1][ri*8+4]=scenario==13?13:12;
   const uint32_t info[3]={12,0x05020001,7};for(unsigned j=0;j<3;j++)for(unsigned k=0;k<4;k++)hosts[3][j*4+k]=(uint8_t)(info[j]>>(8*k));
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
 if(!value&&scenario!=4){memset(registers,0,sizeof(registers));fw=scenario==14&&warm_cpus?0:2;reset_cleared=1;if(scenario==28||scenario==29)link_control=0x143;if(scenario==31)boot_regs[2]=0x7fc00;if(scenario==5)config[1]&=~2u;}
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
int main(int argc,char**argv){
 assert(argc==2);scenario=(unsigned)atoi(argv[1]);assert(scenario<=18);unsigned initial=scenario;
 assert(!port_previous_main());baseline();config[1]|=0x00100000;
 put(22,0x1fffff,8);put(38,0x200000,8);
 pci[48/8]=read_config;pci[16/8]=mem_read;pci[24/8]=mem_write;pci[56/8]=bmi_config_write;
 pci[88/8]=allocate;pci[72/8]=map;pci[80/8]=unmap;pci[96/8]=free_buffer;pci[104/8]=flush;
 qca_image=&port_system;qca_controller=scenario==8?0:pci;qca_diagnostic[4]=15;
 qca_start(&port_system,0);tick(1);
 if(scenario==9||scenario==10){if(scenario==10)tick(21);assert(qca_stop()&&get(168)==1);}
 for(unsigned ms=initial==10?22:2;ms<(initial==18?60000u:15000u);ms+=(initial==18&&get(128)==18&&get(800)==3)?600u:1u)tick(ms);
 if(initial==4||initial==7){assert(get(168)==1&&qca_stop());scenario=0;for(unsigned ms=15000;ms<15100;ms++)tick(ms);}
 if(initial==14||initial==16){
  assert(get(128)==20&&qca_stop()&&allocations==14&&!dma_frees&&!unmaps&&get(220)==14);
  assert(get(236)==0x3fff&&qca_diagnostic[250]==1&&qca_diagnostic[244]==1);
 }else{
  assert(!qca_stop()&&get(140)==1&&opens==closes&&!attributes);
  assert(!get(220)&&!get(236)&&allocations==dma_frees&&unmaps==allocations);
  assert(link_control==0x143&&!(config[1]&0x400)&&boot_regs[0]==0x12300e88);
  if(initial==18)fprintf(stderr,"SLOW-COOPERATIVE stage=%u error=%u failure_phase=%u elapsed=%u cpu=%u pipes=%u\n",get(128),get(136),get(864),get(872),get(824),get(828));
  if(initial==0||initial==1||initial==5||initial==18){assert(get(128)==5&&get(824)==2&&get(828)==2&&get(836)==14&&get(840)==14&&!get(816));}
  else if(initial!=8)assert(get(128)==6);
  if(initial==13||initial==15||initial==17){assert(get(844)==1&&get(856)==2&&!get(816)&&allocations==14);}
 }
 if(initial==17){assert(get(864)==11&&get(868)==0&&get(872)>=3000000&&get(876)>0&&get(880)>0);}
 if(initial==0){assert(!get(864)&&!get(872)&&get(868)==2&&get(876)>0&&get(880)>0);}
 assert(!(config[1]&4));
 qca_diagnostic[0]='Q';qca_diagnostic[1]='P';qca_diagnostic[2]='D';qca_diagnostic[3]=15;
 printf("QPD15_MOCK=");for(unsigned i=0;i<888;i++)printf("%02x",qca_diagnostic[i]);puts("");
 printf("Actual native init probe scenario %u PASS: outer PCI/cold/wake/ROM + mapped warm14 + cleanup/recovery; MOCK ONLY\n",initial);return 0;
}
