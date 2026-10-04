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
uint8_t qca_diagnostic[620];void*qca_controller;
static unsigned scenario,reset_writes,reset_cleared,allocations,dma_frees,unmaps,flushes;
static _Alignas(4096) uint8_t hosts[4][4096];
static uint32_t registers[8][32];static uint16_t link_control=0x143;static uint32_t boot_regs[6]={0x12300800};static unsigned mask_attempts,link_disables,msi_toggled;static uint32_t reset_register;
static uint64_t now_us,last_reset_write;
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
 if(off>=0x3a000&&off<=0x3a014){*(uint32_t*)out=boot_regs[(off-0x3a000)/4];return 0;}
 if(off==0x3a028){mem_reads++;*(uint32_t*)out=(scenario==11||scenario==33)?0:2;return 0;}
 if(off>=0x34400&&off<=0x36050){unsigned id=(unsigned)(off-0x34400)/0x400,index=(unsigned)(off-0x34400)%0x400;assert(id<8&&index<=0x50);if(scenario==35&&id==2&&index==8&&!registers[id][0x18/4])return EFI_ERROR(7);*(uint32_t*)out=scenario==36&&id==3&&index==8&&!registers[id][0x18/4]?0xffffffffu:registers[id][index/4];return 0;}
 if(off==0x8f0){mem_reads++;*(uint32_t*)out=scenario==2?0x200:scenario==1&&!reset_cleared?0:scenario==6?0:0x100;return 0;}
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
  if(!id&&index==0x3c&&(config[1]&4)&&scenario!=14){
   assert(hosts[2][0]==8&&!hosts[2][1]);registers[0][0x44/4]=value;if(scenario==34)return 0;registers[1][0x48/4]=registers[1][0x40/4];
   unsigned ri=(registers[1][0x40/4]-1)&7;hosts[1][ri*8+4]=scenario==13?13:12;
   const uint32_t info[3]={12,0x05020001,7};for(unsigned j=0;j<3;j++)for(unsigned k=0;k<4;k++)hosts[3][j*4+k]=(uint8_t)(info[j]>>(8*k));
  }
  return 0;
 }
 if(off!=0x80008)return old_mem_write(p,width,bar,off,count,in);
 assert(p==pci&&width==2&&!bar&&count==1);uint32_t value=*(uint32_t*)in;assert(value<=1);
 reset_writes++;last_reset_write=now_us;
 if(scenario!=4||value)reset_register=value;
 if(!value&&scenario!=4){reset_cleared=1;if(scenario==28||scenario==29)link_control=0x143;if(scenario==31)boot_regs[2]=0x7fc00;if(scenario==5)config[1]&=~2u;}
 return scenario==7?EFI_ERROR(7):0;
}
static void tick(unsigned ms){now_us=(uint64_t)ms*1000;qca_poll(ms);}
static Status EFIAPI allocate(void*p,uint32_t type,uint32_t memory,uint64_t pages,void**out,uint64_t attrs){assert(p==pci&&!type&&memory==4&&pages==1&&!attrs&&allocations<4);*out=hosts[allocations++];return 0;}
static Status EFIAPI map(void*p,uint32_t op,void*host,uint64_t*n,uint64_t*addr,void**token){assert(p==pci&&op==2&&*n==4096);unsigned i=(unsigned)(((uint8_t*)host-hosts[0])/4096);assert(i<4);*addr=scenario==12?0x100000000ull:0x100000+i*4096;*token=host;return 0;}
static Status EFIAPI unmap(void*p,void*token){assert(p==pci&&token&&!(config[1]&4));unmaps++;return 0;}
static Status EFIAPI free_buffer(void*p,uint64_t pages,void*host){assert(p==pci&&pages==1&&host&&!(config[1]&4));dma_frees++;return 0;}
static Status EFIAPI flush(void*p){assert(p==pci&&!(config[1]&4));flushes++;return scenario==16?EFI_ERROR(7):0;}
static Status EFIAPI bmi_config_write(void*p,uint32_t w,uint32_t off,uint64_t n,void*in){
 if(off==0x80){assert(p==pci&&w==1&&n==1);uint16_t v=*(uint16_t*)in;
  if(!(v&3)){link_disables++;if(scenario==18||(scenario==29&&link_disables>1))return 0;}
  if(scenario==19&&(v&3))return 0;
  link_control=v;return scenario==17&&!(v&3)?EFI_ERROR(7):0;
 }
 if(off==4){uint16_t v=*(uint16_t*)in;
  if(scenario==23&&(v&0x400))return 0;
  if(scenario==30&&!(v&0x400)&&(config[1]&0x400))return 0;
  if(scenario==25&&(v&0x400)&&!mask_attempts++){write_config(p,w,off,n,in);return EFI_ERROR(7);}
 }
 int rc=write_config(p,w,off,n,in);return scenario==15&&(*(uint16_t*)in&4)?EFI_ERROR(7):(Status)rc;}
int main(int argc,char**argv){
 assert(argc==2);scenario=(unsigned)atoi(argv[1]);assert(scenario<=37);unsigned initial=scenario;
 assert(!port_previous_main());baseline();config[1]|=0x00100000;
 pci[48/8]=read_config;pci[16/8]=mem_read;pci[24/8]=mem_write;pci[56/8]=bmi_config_write;
 pci[88/8]=allocate;pci[72/8]=map;pci[80/8]=unmap;pci[96/8]=free_buffer;pci[104/8]=flush;
 qca_image=&port_system;qca_controller=scenario==8?0:pci;qca_diagnostic[4]=15;
 for(unsigned i=0;i<8;i++){registers[i][0]=0x800000+i*4096;registers[i][1]=16;registers[i][2]=0x900000+i*4096;registers[i][3]=32;}
 qca_start(&port_system,0);tick(1);
 if(scenario==9||scenario==10){if(scenario==10)tick(21);assert(qca_stop()&&get(168)==1);}
 for(unsigned ms=initial==10?22:2;ms<4000;ms++){tick(ms);if(initial==37&&get(128)==13&&get(356)==1)assert(qca_stop());}
 if(initial==4||initial==7){assert(get(168)==1&&get(140)==2&&qca_stop());scenario=0;for(unsigned ms=4000;ms<4100;ms++)tick(ms);}
 if(initial==23||initial==26||initial==27||initial==30||initial==32||initial==33){assert(get(140)==2&&qca_stop()&&!allocations);scenario=0;assert(!qca_stop());}
 if(initial==19){assert(get(140)==2&&qca_stop()&&link_control==0x140);scenario=0;assert(!qca_stop());for(unsigned ms=4000;ms<4100;ms++)tick(ms);}
 if(initial==16){assert(get(220)==4&&get(236)==15&&qca_stop()&&!dma_frees&&!unmaps);scenario=0;for(unsigned ms=4000;ms<4100;ms++)tick(ms);}
 assert(link_control==0x143);assert(!(config[1]&0x400));assert(boot_regs[0]==0x12300800);assert(boot_regs[2]==(initial==31?0x7fc00u:0));
 assert(!qca_stop()&&get(140)==1&&!attributes&&opens==closes&&(config[1]&65535)==0x100);
 assert(!get(220)&&!get(236)&&allocations==dma_frees&&unmaps==allocations);
 if(initial==0||initial==1||initial==5||initial==28||initial==35||initial==36)assert(get(128)==5&&get(208)==0x05020001&&get(212)==7&&reset_cleared);
 else if(initial!=8)assert(get(128)==6);
 if(initial==2||initial==3||initial==6||initial==8||initial==9||initial==10||initial==11)assert(!allocations);
 if(initial==12)assert(allocations==1);
 if(initial==17||initial==18||initial==20||(initial>=21&&initial<=33&&initial!=28))assert(!allocations);
 if(initial==13||initial==14||initial==15)assert(allocations==4);
 if(initial==0||initial==1||initial==5||initial==28){
  assert(get(280)==127&&get(284)==3&&get(348)==8&&get(352)==12);
  assert(get(304)==0x102000&&get(312)==0x103000&&get(336)==12&&get(340)==0x05020001);
 }
 if(initial==14){assert(get(280)==121&&get(284)==3&&get(348)==8&&!get(352));assert(get(292)==0&&!get(336));}
 if(initial==34){assert(get(280)==123&&get(284)==3&&get(348)==8&&!get(352));assert((get(292)&65535)==1&&!get(336));}
 if(!allocations||initial==12)assert(!get(280));
 if(initial==0||initial==14||initial==34||initial==35||initial==36){
  assert(get(356)==(initial==35?251u:initial==36?247u:255u));assert(get(360)==(initial==35?4u:initial==36?8u:0u));
  for(unsigned i=0;i<8;i++){assert(get(364+i*32)==0x800000+i*4096);assert(get(368+i*32)==16);assert(!registers[i][0]&&!registers[i][2]);}
 }
 if(initial==37)assert(get(356)==1&&!get(360)&&!allocations);
 uint8_t pre_saved[264];memcpy(pre_saved,qca_diagnostic+356,264);
 uint8_t saved[76];memcpy(saved,qca_diagnostic+280,76);
 unsigned n=reset_writes+mem_writes;qca_start(&port_system,5000);tick(5001);assert(n==reset_writes+mem_writes);assert(!memcmp(saved,qca_diagnostic+280,76));assert(!memcmp(pre_saved,qca_diagnostic+356,264));
 if(initial==0||initial==14||initial==34){
  qca_diagnostic[0]='Q';qca_diagnostic[1]='P';qca_diagnostic[2]='D';qca_diagnostic[3]=9;
  printf("QPD9_MOCK=");for(unsigned i=0;i<sizeof(qca_diagnostic);i++)printf("%02x",qca_diagnostic[i]);puts("");
 }
 printf("Integrated native BMI probe scenario %u PASS: reset/D0/ROM/4DMA pages/CE0-1/query/stop/unmap/close; MOCK ONLY\n",initial);return 0;
}
