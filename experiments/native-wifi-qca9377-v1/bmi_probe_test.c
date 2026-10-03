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
#include <stdlib.h>
uint8_t qca_diagnostic[240];void*qca_controller;
static unsigned scenario,reset_writes,reset_cleared,allocations,dma_frees,unmaps,flushes;
static _Alignas(4096) uint8_t hosts[4][4096];
static uint32_t registers[8][32];static uint32_t reset_register;
static uint64_t now_us,last_reset_write;
static uint32_t get(unsigned i){return qca_diagnostic[i]|((uint32_t)qca_diagnostic[i+1]<<8)|((uint32_t)qca_diagnostic[i+2]<<16)|((uint32_t)qca_diagnostic[i+3]<<24);}
static Status EFIAPI read_config(void*p,uint32_t width,uint32_t offset,uint64_t count,void*out){
 if(count!=64)return old_read_config(p,width,offset,count,out);
 assert(p==pci&&width==2&&!offset);memset(out,0,256);memcpy(out,config,64);
 uint32_t*c=out;c[1]|=0x00100000;c[13]=0x40;c[16]=1;c[17]=scenario==3?3:0;return 0;
}
static Status EFIAPI mem_read(void*p,uint32_t width,uint8_t bar,uint64_t off,uint64_t count,void*out){
 assert(p==pci&&width==2&&!bar&&count==1);
 if(reset_writes)assert(now_us-last_reset_write>=20000);
 if(off==0x80008){mem_reads++;*(uint32_t*)out=reset_register;return 0;}
 if(off==0x3a028){mem_reads++;*(uint32_t*)out=scenario==11?0:2;return 0;}
 if(off>=0x34400&&off<=0x36050){unsigned id=(unsigned)(off-0x34400)/0x400,index=(unsigned)(off-0x34400)%0x400;assert(id<8&&index<=0x50);*(uint32_t*)out=registers[id][index/4];return 0;}
 if(off==0x8f0){mem_reads++;*(uint32_t*)out=scenario==2?0x200:scenario==1&&!reset_cleared?0:scenario==6?0:0x100;return 0;}
 return old_mem_read(p,width,bar,off,count,out);
}
static Status EFIAPI mem_write(void*p,uint32_t width,uint8_t bar,uint64_t off,uint64_t count,void*in){
 if(reset_writes)assert(now_us-last_reset_write>=20000);
 if(off>=0x34400&&off<=0x36050){
  assert(p==pci&&width==2&&!bar&&count==1);unsigned id=(unsigned)(off-0x34400)/0x400,index=(unsigned)(off-0x34400)%0x400;assert(id<8&&index<=0x50);
  uint32_t value=*(uint32_t*)in;
  if(index==0x18)registers[id][index/4]=value?9:0;
  else if(index==0x30||index==0x38)registers[id][index/4]&=~value;
  else registers[id][index/4]=value;
  if(!id&&index==0x3c&&(config[1]&4)&&scenario!=14){
   assert(hosts[2][0]==8&&!hosts[2][1]);registers[0][0x44/4]=value;registers[1][0x48/4]=registers[1][0x40/4];
   unsigned ri=(registers[1][0x40/4]-1)&7;hosts[1][ri*8+4]=scenario==13?13:12;
   const uint32_t info[3]={12,0x05020001,7};for(unsigned j=0;j<3;j++)for(unsigned k=0;k<4;k++)hosts[3][j*4+k]=(uint8_t)(info[j]>>(8*k));
  }
  return 0;
 }
 if(off!=0x80008)return old_mem_write(p,width,bar,off,count,in);
 assert(p==pci&&width==2&&!bar&&count==1);uint32_t value=*(uint32_t*)in;assert(value<=1);
 reset_writes++;last_reset_write=now_us;
 if(scenario!=4||value)reset_register=value;
 if(!value&&scenario!=4){reset_cleared=1;if(scenario==5)config[1]&=~2u;}
 return scenario==7?EFI_ERROR(7):0;
}
static void tick(unsigned ms){now_us=(uint64_t)ms*1000;qca_poll(ms);}
static Status EFIAPI allocate(void*p,uint32_t type,uint32_t memory,uint64_t pages,void**out,uint64_t attrs){assert(p==pci&&!type&&memory==4&&pages==1&&!attrs&&allocations<4);*out=hosts[allocations++];return 0;}
static Status EFIAPI map(void*p,uint32_t op,void*host,uint64_t*n,uint64_t*addr,void**token){assert(p==pci&&op==2&&*n==4096);unsigned i=(unsigned)(((uint8_t*)host-hosts[0])/4096);assert(i<4);*addr=scenario==12?0x100000000ull:0x100000+i*4096;*token=host;return 0;}
static Status EFIAPI unmap(void*p,void*token){assert(p==pci&&token&&!(config[1]&4));unmaps++;return 0;}
static Status EFIAPI free_buffer(void*p,uint64_t pages,void*host){assert(p==pci&&pages==1&&host&&!(config[1]&4));dma_frees++;return 0;}
static Status EFIAPI flush(void*p){assert(p==pci&&!(config[1]&4));flushes++;return scenario==16?EFI_ERROR(7):0;}
static Status EFIAPI bmi_config_write(void*p,uint32_t w,uint32_t off,uint64_t n,void*in){int rc=write_config(p,w,off,n,in);return scenario==15&&(*(uint16_t*)in&4)?EFI_ERROR(7):(Status)rc;}
int main(int argc,char**argv){
 assert(argc==2);scenario=(unsigned)atoi(argv[1]);assert(scenario<=16);unsigned initial=scenario;
 assert(!port_previous_main());baseline();config[1]|=0x00100000;
 pci[48/8]=read_config;pci[16/8]=mem_read;pci[24/8]=mem_write;pci[56/8]=bmi_config_write;
 pci[88/8]=allocate;pci[72/8]=map;pci[80/8]=unmap;pci[96/8]=free_buffer;pci[104/8]=flush;
 qca_image=&port_system;qca_controller=scenario==8?0:pci;qca_diagnostic[4]=15;
 qca_start(&port_system,0);tick(1);
 if(scenario==9||scenario==10){if(scenario==10)tick(21);assert(qca_stop()&&get(168)==1);}
 for(unsigned ms=initial==10?22:2;ms<4000;ms++)tick(ms);
 if(initial==4||initial==7){assert(get(168)==1&&get(140)==2&&qca_stop());scenario=0;for(unsigned ms=4000;ms<4100;ms++)tick(ms);}
 if(initial==16){assert(get(220)==4&&get(236)==15&&qca_stop()&&!dma_frees&&!unmaps);scenario=0;for(unsigned ms=4000;ms<4100;ms++)tick(ms);}
 assert(!qca_stop()&&get(140)==1&&!attributes&&opens==closes&&(config[1]&65535)==0x100);
 assert(!get(220)&&!get(236)&&allocations==dma_frees&&unmaps==allocations);
 if(initial==0||initial==1||initial==5)assert(get(128)==5&&get(208)==0x05020001&&get(212)==7&&reset_cleared);
 else if(initial!=8)assert(get(128)==6);
 if(initial==2||initial==3||initial==6||initial==8||initial==9||initial==10||initial==11)assert(!allocations);
 if(initial==12)assert(allocations==1);
 if(initial==13||initial==14||initial==15)assert(allocations==4);
 unsigned n=reset_writes+mem_writes;qca_start(&port_system,5000);tick(5001);assert(n==reset_writes+mem_writes);
 printf("Integrated native BMI probe scenario %u PASS: reset/D0/ROM/4DMA pages/CE0-1/query/stop/unmap/close; MOCK ONLY\n",initial);return 0;
}
