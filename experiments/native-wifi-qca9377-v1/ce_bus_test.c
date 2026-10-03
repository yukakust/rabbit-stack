#include "ce_bus.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
static void*methods[20];static uint32_t reg[8][32];static uint16_t command=0x102;
static unsigned mode,flushes,unmaps,frees;static QcaCeBus bus;
static _Alignas(4096) uint8_t hosts[2][4096];
static Status EFIAPI memread(void*p,uint32_t w,uint8_t bar,uint64_t addr,uint64_t n,void*out){
 assert(p==methods&&w==2&&!bar&&n==1);unsigned id=(unsigned)(addr-0x34400)/0x400,off=(unsigned)(addr-0x34400)%0x400;assert(id<8&&off<=0x50);
 *(uint32_t*)out=reg[id][off/4];return 0;
}
static Status EFIAPI memwrite(void*p,uint32_t w,uint8_t bar,uint64_t addr,uint64_t n,void*in){
 assert(p==methods&&w==2&&!bar&&n==1);unsigned id=(unsigned)(addr-0x34400)/0x400,off=(unsigned)(addr-0x34400)%0x400;assert(id<8&&off<=0x50);
 uint32_t v=*(uint32_t*)in;
 if(mode==9&&!id&&!off&&!v)return 0;
 if(off==0x18)reg[id][off/4]=v?((mode==4&&id==7)?1:9):0;
 else if(off==0x30||off==0x38)reg[id][off/4]&=~v;
 else reg[id][off/4]=v;
 return 0;
}
static Status EFIAPI configread(void*p,uint32_t w,uint32_t off,uint64_t n,void*out){
 assert(p==methods&&w==1&&off==4&&n==1);if(mode==7)return 1;*(uint16_t*)out=command;return 0;
}
static Status EFIAPI configwrite(void*p,uint32_t w,uint32_t off,uint64_t n,void*in){
 assert(p==methods&&w==1&&off==4&&n==1);uint16_t v=*(uint16_t*)in;
 if(mode==2&&(v&4))return 0;
 command=v;
 return (mode==1&&(v&4))||(mode==3&&!(v&4))?1:0;
}
static Status EFIAPI flush(void*p){assert(p==methods&&!(command&4));flushes++;return mode==5?1:0;}
static Status EFIAPI unmap(void*p,void*token){assert(p==methods&&token&&flushes);unmaps++;return mode==6?1:0;}
static Status EFIAPI freebuffer(void*p,uint64_t pages,void*host){assert(p==methods&&pages==1&&(host==hosts[0]||host==hosts[1])&&unmaps);assert(!qca_ce_bus_released(&bus));frees++;return 0;}
int main(int argc,char**argv){
 assert(argc==2);unsigned scenario=(unsigned)atoi(argv[1]);assert(scenario<=9);
 methods[2]=(void*)memread;methods[3]=(void*)memwrite;methods[6]=(void*)configread;methods[7]=(void*)configwrite;methods[10]=(void*)unmap;methods[12]=(void*)freebuffer;methods[13]=(void*)flush;
 QcaUefiPort p={.pci=methods,.bar_extent=0x200000,.claimed=1,.validated=1,.memory_ready=1,.wake_owned=1,.dma_users=2};
 QcaDmaBuffer buffers[2]={0};QcaCeAccess a={0};assert(!qca_ce_access_init(&a,&p,255));
 for(unsigned i=0;i<2;i++){
  buffers[i]=(QcaDmaBuffer){.port=&p,.host=hosts[i],.mapping=&hosts[i],.address=0x100000+i*4096,.bytes=4096,.pages=1,.valid=1,.allocated=1,.mapped=1,.stop=qca_ce_bus_released,.context=&bus};
  assert(!qca_ce_access_buffer(&a,&buffers[i]));
 }
 assert(!qca_ce_bus_init(&bus,&a));assert(qca_ce_bus_start(&bus)==-1);
 assert(!qca_ce_bus_stop_begin(&bus,0));assert(qca_ce_bus_stop_poll(&bus,1)==1);assert(!qca_ce_bus_released(&bus));
 assert(!qca_ce_hw_configure(&bus.engines[0],buffers[0].address,8,0,0,256));
 assert(!qca_ce_hw_configure(&bus.engines[1],0,0,buffers[1].address,8,0));
 assert(qca_ce_bus_released(&bus)==-1);mode=(scenario<=2)?scenario:0;
 int started=qca_ce_bus_start(&bus);
 if(scenario==1||scenario==2)assert(started==-1&&bus.owned&&buffers[0].exposed&&buffers[1].exposed);
 else assert(!started&&bus.phase==QCA_BUS_ACTIVE&&command==0x106);
 assert(qca_dma_close(&buffers[0])==-1&&!frees&&!unmaps&&buffers[0].closing);
 mode=scenario;
 assert(!qca_ce_bus_stop_begin(&bus,2));int stopped=qca_ce_bus_stop_poll(&bus,3);
 if(scenario==4){assert(stopped==0&&bus.owned);assert(qca_ce_bus_stop_poll(&bus,1000002)==-1&&bus.owned&&!(command&4));}
 else if(scenario==3||scenario==7||scenario==9)assert(stopped==-1&&bus.owned);
 else assert(stopped==1&&!bus.owned&&!(command&4));
 if(scenario==3||scenario==4||scenario==7||scenario==9){assert(qca_dma_close(&buffers[0])==-1&&!frees&&!unmaps);mode=0;assert(!qca_ce_bus_stop_begin(&bus,1000003));assert(qca_ce_bus_stop_poll(&bus,1000004)==1);}
 if(scenario==5||scenario==6){assert(qca_dma_close(&buffers[0])==-1&&buffers[0].allocated&&buffers[0].mapped&&!frees);mode=0;}
 assert(!qca_dma_close(&buffers[0]));assert(!qca_dma_close(&buffers[1]));assert(frees==2&&!p.dma_users);
 p.claimed=0;assert(qca_ce_bus_released(&bus)==-1);
 printf("CE bus scenario %u: all-eight halt, command16 readback, ambiguous enable/stop retention, DMA close order PASS; MOCK ONLY\n",scenario);return 0;
}
