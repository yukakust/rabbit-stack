#define MAPPED_IRQ_NO_MAIN
#include "boot_irq_mapped_test.c"
#undef MAPPED_IRQ_NO_MAIN
#include "init_adapter.h"
static QcaInitAdapter adapter;
static uint64_t adapter_now,cold_operation_time;
static uint32_t reset800,lf850=0x14,fw_indicator=2,cold80008;
static unsigned cold_asserts,cold_clears,cpu_resets,adapter_fault,warm_failed;
static unsigned selector,allocation_failure,guard_lost;
static Status EFIAPI adapter_memread(void*p,uint32_t w,uint8_t bar,uint64_t a,uint64_t n,void*out){
 if(a==0x800||a==0x850||a==0x3a028||a==0x80008){
  assert(p==methods&&w==2&&!bar&&n==1);
  if(cold_asserts&&!cold_clears&&a!=0x80008)assert(adapter_now-cold_operation_time>=20000);
  if(a==0x80008){*(uint32_t*)out=cold80008;return 0;}
  if(a==0x800&&selector==3&&!warm_failed){warm_failed=1;return 1;}
  *(uint32_t*)out=a==0x800?reset800:a==0x850?lf850:fw_indicator;return 0;
 }
 return irq_memread(p,w,bar,a,n,out);
}
static Status EFIAPI adapter_memwrite(void*p,uint32_t w,uint8_t bar,uint64_t a,uint64_t n,void*in){
 if(a==0x800||a==0x850||a==0x3a028||a==0x80008){
  assert(p==methods&&w==2&&!bar&&n==1&&!(command&4));uint32_t v=*(uint32_t*)in;
  if(a==0x80008){
   if(v&1){cold_asserts++;cold_operation_time=adapter_now;}
   else{assert(adapter_now-cold_operation_time>=20000);cold_clears++;fw_indicator=selector==9?0:2;}
   cold80008=v;
   return selector==6?1:0;
  }
  if(a==0x3a028){assert(!v);fw_indicator=0;}
  else if(a==0x850)lf850=v;
  else{
   reset800=v&~0x40u;
   if(v&0x40){cpu_resets++;fw_indicator=selector==4||selector==6||selector==9?0:2;core[0]|=0x800;}
   if((v&1)&&selector==5&&!warm_failed){warm_failed=1;adapter_fault=1;return 1;}
   if(!(v&1)&&adapter_fault&&selector==5)return 1;
  }
  return 0;
 }
 return irq_memwrite(p,w,bar,a,n,in);
}
static Status EFIAPI adapter_allocate(void*p,uint32_t t,uint32_t m,uint64_t pages,void**out,uint64_t attrs){
 if(allocation_failure){allocation_failure=0;return 1;}
 return allocate(p,t,m,pages,out,attrs);
}
int main(int argc,char**argv){
 assert(argc==2);selector=(unsigned)atoi(argv[1]);assert(selector<=12);
 methods[2]=(void*)adapter_memread;methods[3]=(void*)adapter_memwrite;methods[6]=(void*)irq_configread;methods[7]=(void*)configwrite;
 methods[9]=(void*)map;methods[10]=(void*)unmap;methods[11]=(void*)adapter_allocate;
 /* The inherited free fixture binds the separate legacy bus. Replace below. */
 methods[12]=0;methods[13]=(void*)flush;
 QcaUefiPort port={.pci=methods,.bar_extent=0x200000,.claimed=1,.validated=1,.memory_ready=1,.wake_owned=1,.link_owned=1};
 QcaBootIrq irq={0};assert(!qca_boot_irq_begin(&irq,&port));
 extern Status EFIAPI adapter_free(void*,uint64_t,void*);methods[12]=(void*)adapter_free;
 assert(!qca_init_adapter_begin(&adapter,&irq,0xd1000000,0x80,0));
 if(selector==1)qca_init_adapter_cancel(&adapter);
 if(selector==2)allocation_failure=1;
 for(adapter_now=0;adapter_now<15000000;adapter_now+=1000){
  if(selector==7&&adapter.phase==QCA_INIT_WARM&&!guard_lost){port.wake_owned=0;guard_lost=1;}
  if(selector==8&&adapter.phase==QCA_INIT_WARM)qca_init_adapter_cancel(&adapter);
  if(selector==10&&adapter.phase==QCA_INIT_CLEANUP)mode=17;
  if(selector==11&&adapter.phase==QCA_INIT_READY){
   assert(adapter.channels.allocated==14&&adapter.warm.cpu_resets==2&&adapter.warm.pipe_inits==2);
   qca_init_adapter_cancel(&adapter);
  }
  if(selector==12&&adapter.phase==QCA_INIT_WARM){assert(qca_init_adapter_poll(&adapter,adapter.last-1)==-1);break;}
  int rc=qca_init_adapter_poll(&adapter,adapter_now);
  if(rc==1){
   assert(adapter.phase==QCA_INIT_READY&&!adapter.warm.owned&&!frees&&!unmaps);
   assert(cpu_resets==2&&adapter.warm.pipe_inits==2&&allocations==14&&!cold_asserts);
   assert(!qca_channels_prepared(&adapter.channels));qca_init_adapter_cancel(&adapter);
  }
  if(adapter.phase==QCA_INIT_CLOSED||adapter.phase==QCA_INIT_RETAINED)break;
 }
 assert(adapter_now<15000000&&!(command&4));
 if(selector==5||selector==6||selector==7||selector==9||selector==10||selector==12){
  assert(adapter.phase==QCA_INIT_RETAINED&&!qca_init_adapter_released(&adapter));
  assert(!frees&&!unmaps&&irq.owned&&port.dma_users==14);
  if(selector==5)assert(adapter.warm.ce_owned);
  if(selector==6||selector==9)assert(adapter.warm.owned&&!adapter.recovery_verified);
 }else{
  assert(adapter.phase==QCA_INIT_CLOSED&&qca_init_adapter_released(&adapter));
  assert(frees==allocations&&unmaps==allocations&&!port.dma_users);
  if(selector==3||selector==4||selector==8){assert(adapter.recovery_verified&&cold_asserts==1&&cold_clears==1&&!adapter.warm.owned);}
  assert(!qca_boot_irq_close(&irq)&&!irq.owned&&command==0x102);
 }
 printf("Native init adapter scenario %u PASS: borrowed PCI/IRQ, warm/full channels, cold-proof recovery or retained ownership; MOCK ONLY\n",selector);return 0;
}
Status EFIAPI adapter_free(void*p,uint64_t pages,void*host){
 assert(p==methods&&pages==1&&host&&!(command&4)&&unmaps);
 assert(!qca_ce_bus_released(&adapter.bus)&&!adapter.warm.owned&&!adapter.recovery.owned);
 frees++;return 0;
}
