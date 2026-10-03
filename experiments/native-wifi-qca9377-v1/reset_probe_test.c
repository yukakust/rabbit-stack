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
uint8_t qca_diagnostic[196];void*qca_controller;
static unsigned scenario,reset_writes,reset_cleared;static uint32_t reset_register;
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
 if(off==0x3a028){mem_reads++;*(uint32_t*)out=2;return 0;}
 if(off==0x8f0){mem_reads++;*(uint32_t*)out=scenario==2?0x200:scenario==1&&!reset_cleared?0:scenario==6?0:0x100;return 0;}
 return old_mem_read(p,width,bar,off,count,out);
}
static Status EFIAPI mem_write(void*p,uint32_t width,uint8_t bar,uint64_t off,uint64_t count,void*in){
 if(reset_writes)assert(now_us-last_reset_write>=20000);
 if(off!=0x80008)return old_mem_write(p,width,bar,off,count,in);
 assert(p==pci&&width==2&&!bar&&count==1);uint32_t value=*(uint32_t*)in;assert(value<=1);
 reset_writes++;last_reset_write=now_us;
 if(scenario!=4||value)reset_register=value;
 if(!value&&scenario!=4){reset_cleared=1;if(scenario==5)config[1]&=~2u;}
 return scenario==7?EFI_ERROR(7):0;
}
static void tick(unsigned ms){now_us=(uint64_t)ms*1000;qca_poll(ms);}
int main(int argc,char**argv){
 assert(argc==2);scenario=(unsigned)atoi(argv[1]);assert(scenario<=10);unsigned initial=scenario;
 assert(!port_previous_main());baseline();config[1]|=0x00100000;
 pci[48/8]=read_config;pci[16/8]=mem_read;pci[24/8]=mem_write;
 qca_image=&port_system;qca_controller=scenario==8?0:pci;qca_diagnostic[4]=15;
 qca_start(&port_system,0);tick(1);
 if(scenario==9||scenario==10){
  if(scenario==10)tick(21);
  unsigned n=mem_writes+reset_writes,closed=closes;
  assert(qca_stop()&&get(168)==1&&mem_writes+reset_writes==n&&closes==closed);
 }
 if(scenario==3||scenario==8)assert(!mem_writes&&!reset_writes);
 for(unsigned ms=initial==10?22:2;ms<200;ms++)tick(ms);
 if(scenario==4||scenario==7){assert(get(168)==1&&get(140)==2&&qca_stop());scenario=0;for(unsigned ms=200;ms<300;ms++)tick(ms);}
 assert(!qca_stop()&&get(140)==1&&!attributes&&opens==closes&&(config[1]&65535)==0x100);
 if(initial==0||initial==1||initial==5)assert(reset_cleared&&get(132)==0x100);
 if(scenario==2)assert(!reset_writes&&get(128)==6);
 if(scenario==6)assert(get(132)==0&&get(172)==2&&get(128)==6);
 unsigned n=reset_writes+mem_writes;qca_start(&port_system,500);tick(501);assert(n==reset_writes+mem_writes);
 printf("Integrated reset probe scenario %u: PCI D0, timed access, command repair, cleanup/cancel/reattach PASS; MOCK ONLY\n",initial);return 0;
}
