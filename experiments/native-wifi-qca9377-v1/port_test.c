#include "uefi_port.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
static void*boot[44],*pci[18];
static SystemTable port_system;
static uint8_t resource[48];
static uint32_t config[16];
static unsigned mode,opens,closes,frees,mem_reads,mem_writes,attr_writes,config_writes;
static uint64_t attributes;
static void put(unsigned offset,uint64_t value,unsigned bytes){for(unsigned i=0;i<bytes;i++)resource[offset+i]=(uint8_t)(value>>(8*i));}
static Status EFIAPI open_protocol(void*h,const Guid*g,void**out,void*agent,void*controller,uint32_t flags){
 assert(h==pci&&controller==pci&&agent==&port_system&&g->a==0x4cf5b200&&flags==0x30);
 if(mode==1)return EFI_ERROR(15);
 opens++;*out=pci;return 0;
}
static Status EFIAPI close_protocol(void*h,const Guid*g,void*agent,void*controller){
 assert(h==pci&&controller==pci&&agent==&port_system&&g->a==0x4cf5b200);
 if(mode==8)return EFI_ERROR(7);
 closes++;return 0;
}
static Status EFIAPI free_pool(void*p){assert(p==resource);if(mode==7)return EFI_ERROR(7);frees++;return 0;}
static Status EFIAPI read_config(void*p,uint32_t width,uint32_t offset,uint64_t count,void*out){
 assert(p==pci);
 if(width==1){assert(offset==4&&count==1);if(mode==15)return EFI_ERROR(7);*(uint16_t*)out=(uint16_t)config[1];}
 else{assert(width==2&&!offset&&count==16);memcpy(out,config,sizeof(config));}return 0;
}
static Status EFIAPI write_config(void*p,uint32_t width,uint32_t offset,uint64_t count,void*in){
 assert(p==pci&&width==1&&offset==4&&count==1);config_writes++;
 if(mode==16)return EFI_ERROR(7);
 if(mode!=17&&mode!=19)config[1]=(config[1]&0xffff0000u)|*(uint16_t*)in;
 return mode==20?EFI_ERROR(7):0;
}
static Status EFIAPI bar_attributes(void*p,uint8_t bar,uint64_t*support,void**out){
 assert(p==pci&&!bar);*support=0;*out=resource;return 0;
}
static Status EFIAPI attr(void*p,uint32_t operation,uint64_t value,uint64_t*out){
 assert(p==pci);if(operation==0){*out=attributes;return 0;}
 if(operation==4){*out=mode==3?0:0x200;return 0;}
 assert(operation==1||operation==2);attr_writes++;
 if(operation==2){assert(value==0x200);attributes|=value;if(mode<18)config[1]|=2;else if(mode==21)config[1]|=4;return mode==5?EFI_ERROR(7):0;}
 assert(!value||value==0x200);if(mode==6)return EFI_ERROR(7);attributes=value;if(mode!=12&&mode!=16&&mode!=17){if(value&0x200)config[1]|=2;else config[1]&=~2u;}return 0;
}
static Status EFIAPI mem_read(void*p,uint32_t width,uint8_t bar,uint64_t offset,uint64_t count,void*out){
 assert(p==pci&&width==2&&!bar&&count==1&&(attributes&0x200));mem_reads++;
 assert(offset==0x80000||offset==0x8f0);
 *(uint32_t*)out=offset==0x80000?(mode==10?0:3):(mode==11?0x200:0x100);return 0;
}
static Status EFIAPI mem_write(void*p,uint32_t width,uint8_t bar,uint64_t offset,uint64_t count,void*in){
 assert(p==pci&&width==2&&!bar&&count==1&&offset==0x80004&&(attributes&0x200));
 assert(*(uint32_t*)in<=1);mem_writes++;return mode==9?EFI_ERROR(7):0;
}
static void baseline(void){
 mode=opens=closes=frees=mem_reads=mem_writes=attr_writes=config_writes=0;attributes=0;
 memset(config,0,sizeof(config));config[0]=0x0042168c;config[1]=0x100;config[2]=0x02800031;config[4]=0xd1000004;config[11]=0x18101028;
 memset(resource,0,sizeof(resource));resource[0]=0x8a;put(1,43,2);put(6,64,8);put(14,0xd1000000,8);
 put(22,0xfffff,8);put(38,0x100000,8);resource[46]=0x79;
}
int main(void){
 port_system.boot=boot;boot[280/8]=open_protocol;boot[288/8]=close_protocol;boot[72/8]=free_pool;
 pci[48/8]=read_config;pci[56/8]=write_config;pci[128/8]=bar_attributes;pci[120/8]=attr;pci[16/8]=mem_read;pci[24/8]=mem_write;
 QcaPciTarget target={0x1028,0x1810,0x31};QcaWakeTarget wake_target={0x80000,0x80004,0x8f0,3,1000000};
 baseline();QcaUefiPort port={0};QcaWake wake={0};uint32_t value=0;
 assert(!qca_port_open(&port,&port_system,&port_system,pci,&target)&&port.claimed&&frees==1&&!attr_writes);
 assert(qca_port_read32(&port,0x80000,&value)==-1&&!mem_reads);
 assert(!qca_port_enable_memory(&port)&&attributes==0x200);
 port.link_owned=1;assert(qca_port_close(&port,0)==-1&&port.claimed);assert(qca_port_open(&port,&port_system,&port_system,pci,&target)==-1);port.link_owned=0;port.boot_irq_owned=1;assert(qca_port_close(&port,0)==-1&&port.claimed);port.boot_irq_owned=0;
 assert(qca_port_read32(&port,0x80004,&value)==-1&&!mem_reads);
 assert(qca_port_write32(&port,0x80004,2)==-1&&!mem_writes);
 assert(!qca_wake_begin(&wake,&wake_target,qca_port_read32,qca_port_write32,&port,0));
 assert(qca_port_close(&port,0)==-1&&port.claimed);
 assert(qca_wake_poll(&wake,1)==1&&mem_reads==2);
 assert(!qca_port_close(&port,&wake)&&!port.claimed&&!wake.owned&&!attributes&&closes==1&&mem_writes==2);
 assert(!qca_port_close(&port,&wake)&&closes==1);
 for(unsigned failure=1;failure<=9;failure++){
  baseline();port=(QcaUefiPort){0};wake=(QcaWake){0};mode=failure;
  if(failure==2)config[11]=0x18111028;
  if(failure==4)put(38,0x80000,8);
  int result=qca_port_open(&port,&port_system,&port_system,pci,&target);
  if(failure<=4||failure==7)assert(result==-1&&!attr_writes&&!mem_reads&&!mem_writes);
  else{
   assert(!result);
   result=qca_port_enable_memory(&port);
   if(failure==5)assert(result==-1&&port.memory_attempted&&port.claimed);
   else{
    assert(!result);
    if(failure==9){
     assert(qca_wake_begin(&wake,&wake_target,qca_port_read32,qca_port_write32,&port,0)==-1&&wake.owned);
     assert(qca_port_close(&port,&wake)==-1&&wake.owned&&port.claimed);
    }
   }
  }
  if(failure==6||failure==7||failure==8)assert(qca_port_close(&port,&wake)==-1&&port.claimed);
  mode=0;assert(!qca_port_close(&port,&wake)&&!port.claimed&&!wake.owned&&!attributes);
 }
 for(unsigned corrupt=0;corrupt<6;corrupt++){
  baseline();port=(QcaUefiPort){0};
  if(corrupt==0)config[1]|=4;
  if(corrupt==1)resource[0]=0;
  if(corrupt==2)resource[3]=1;
  if(corrupt==3)put(30,1,8);
  if(corrupt==4)put(14,0xd2000000,8);
  if(corrupt==5)resource[46]=0;
  assert(qca_port_open(&port,&port_system,&port_system,pci,&target)==-1&&!attr_writes&&!mem_reads&&!mem_writes);
  assert(!qca_port_close(&port,0));
 }
 for(unsigned failure=12;failure<=17;failure++){
  if(failure==13||failure==14)continue;
  baseline();config[1]|=0x00100000u;port=(QcaUefiPort){0};wake=(QcaWake){0};
  assert(!qca_port_open(&port,&port_system,&port_system,pci,&target));
  assert(!qca_port_enable_memory(&port)&&((config[1]&65535)==0x102));mode=failure;
  int closed=qca_port_close(&port,&wake);
  if(failure==12)assert(!closed&&config_writes==1&&!port.claimed);
  else assert(closed==-1&&port.claimed&&port.memory_attempted&&!closes);
  mode=0;assert(!qca_port_close(&port,&wake)&&config[1]==0x00100100u&&!port.claimed);
 }
 /* Preserve initial hardware MEM even if cached Attributes says zero. */
 baseline();config[1]|=2;port=(QcaUefiPort){0};wake=(QcaWake){0};
 assert(!qca_port_open(&port,&port_system,&port_system,pci,&target));
 assert(!qca_port_enable_memory(&port));assert(!qca_port_close(&port,&wake));assert((config[1]&65535)==0x102&&config_writes==1);
 /* Fresh actual MEM-off with cached Attributes MEM-on, as physical QPD8.
  * Successful repair, dropped write, ambiguous applied write, foreign command.
  * Never perform MMIO or allow uncertain ownership to be silently discarded. */
 for(unsigned cached=18;cached<=21;cached++){
  baseline();attributes=0x200;config[1]|=0x00100000;port=(QcaUefiPort){0};wake=(QcaWake){0};
  assert(!qca_port_open(&port,&port_system,&port_system,pci,&target));mode=cached;
  int enabled=qca_port_enable_memory(&port);
  assert(port.claimed&&port.memory_attempted&&!mem_reads&&!mem_writes);
  if(cached==18)assert(!enabled&&port.memory_ready&&config[1]==0x00100102&&config_writes==1);
  else assert(enabled==-1&&!port.memory_ready);
  if(cached==19)assert(port.error==0x1000&&config[1]==0x00100100);
  if(cached==20)assert(port.error==0xf07&&config[1]==0x00100102);
  if(cached==21)assert(port.error==0xb00&&!config_writes);
  mode=0;assert(!qca_port_close(&port,&wake)&&!port.claimed&&attributes==0x200&&config[1]==0x00100100);
 }
 puts("UEFI PCI port: exclusive claim, fresh identity, BAR descriptor/bounds, memory-only enable, allowlisted IO, wake-before-release, ambiguous-write/cleanup retries, actual Command readback/Write16 fallback/stale API/drop-write retention PASS; MOCK HARDWARE ONLY");
 return 0;
}
