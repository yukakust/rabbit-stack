#include "bmi_transport.h"
#include "rom_ready.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
static void*methods[20];static uint32_t reg[8][32],indicator;static uint16_t command=0x102;
static unsigned rom_error,post_error,publications[2],order,flushes;
static _Alignas(4096) uint8_t hosts[4][4096];
static Status EFIAPI memread(void*p,uint32_t w,uint8_t bar,uint64_t addr,uint64_t n,void*out){
 assert(p==methods&&w==2&&!bar&&n==1);
 if(addr==0x3a028){if(rom_error)return 1;*(uint32_t*)out=indicator;return 0;}
 unsigned id=(unsigned)(addr-0x34400)/0x400,off=(unsigned)(addr-0x34400)%0x400;assert(id<8&&off<=0x50);
 *(uint32_t*)out=reg[id][off/4];return 0;
}
static Status EFIAPI memwrite(void*p,uint32_t w,uint8_t bar,uint64_t addr,uint64_t n,void*in){
 assert(p==methods&&w==2&&!bar&&n==1);unsigned id=(unsigned)(addr-0x34400)/0x400,off=(unsigned)(addr-0x34400)%0x400;assert(id<8&&off<=0x50);
 uint32_t v=*(uint32_t*)in;
 if(command&4){if(id==1&&off==0x40){assert(!order);order=1;publications[1]++;if(post_error)return 1;}if(!id&&off==0x3c){assert(order==1);order=2;publications[0]++;}}
 if(off==0x18)reg[id][off/4]=v?9:0;else if(off==0x30||off==0x38)reg[id][off/4]&=~v;else reg[id][off/4]=v;return 0;
}
static Status EFIAPI configread(void*p,uint32_t w,uint32_t off,uint64_t n,void*out){assert(p==methods&&w==1&&off==4&&n==1);*(uint16_t*)out=command;return 0;}
static Status EFIAPI configwrite(void*p,uint32_t w,uint32_t off,uint64_t n,void*in){assert(p==methods&&w==1&&off==4&&n==1);command=*(uint16_t*)in;return 0;}
static Status EFIAPI flush(void*p){assert(p==methods&&!(command&4));flushes++;return 0;}
static void put32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static void rom_tests(QcaUefiPort*p){
 QcaRomReady r={0};assert(!qca_rom_begin(&r,p,0));assert(!qca_rom_poll(&r,0)&&r.reads==1);assert(!qca_rom_poll(&r,9999)&&r.reads==1);
 indicator=UINT32_MAX;assert(!qca_rom_poll(&r,10000));indicator=2;assert(qca_rom_poll(&r,20000)==1&&r.reads==3);
 assert(!qca_rom_begin(&r,p,0));indicator=3;assert(qca_rom_poll(&r,0)==-1&&r.error==6);
 assert(!qca_rom_begin(&r,p,0));indicator=UINT32_MAX;assert(!qca_rom_poll(&r,0));assert(qca_rom_poll(&r,3000000)==-1&&r.error==3);
 indicator=0;assert(!qca_rom_begin(&r,p,0));assert(qca_rom_poll(&r,3000000)==-1&&r.error==4);
 assert(!qca_rom_begin(&r,p,1));assert(qca_rom_poll(&r,0)==-1&&r.error==2);
 assert(!qca_rom_begin(&r,p,0));rom_error=1;assert(qca_rom_poll(&r,0)==-1&&r.error==5);rom_error=0;
 assert(!qca_rom_begin(&r,p,0));p->claimed=0;assert(qca_rom_poll(&r,0)==-1&&r.error==1);p->claimed=1;
 assert(qca_rom_begin(&r,p,UINT64_MAX)==-1);
 assert(!qca_rom_begin(&r,p,UINT64_MAX-3000000));assert(!qca_rom_poll(&r,UINT64_MAX-1)&&r.next==UINT64_MAX);assert(qca_rom_poll(&r,UINT64_MAX)==-1);
}
int main(int argc,char**argv){
 assert(argc==2);unsigned scenario=(unsigned)atoi(argv[1]);assert(scenario<=10);
 methods[2]=(void*)memread;methods[3]=(void*)memwrite;methods[6]=(void*)configread;methods[7]=(void*)configwrite;methods[13]=(void*)flush;
 QcaUefiPort p={.pci=methods,.bar_extent=0x200000,.claimed=1,.validated=1,.memory_ready=1,.wake_owned=1};rom_tests(&p);
 QcaCeAccess a={0};QcaCeBus bus={0};QcaDmaBuffer d[4]={0};assert(!qca_ce_access_init(&a,&p,255));
 for(unsigned i=0;i<4;i++){d[i]=(QcaDmaBuffer){.port=&p,.host=hosts[i],.address=0x100000+i*4096,.bytes=4096,.valid=1,.allocated=1,.mapped=1};assert(!qca_ce_access_buffer(&a,&d[i]));}
 assert(!qca_ce_bus_init(&bus,&a));assert(!qca_ce_bus_stop_begin(&bus,0));assert(qca_ce_bus_stop_poll(&bus,1)==1);
 QcaBmiPipe pipes[2]={{.bus=&bus,.receive=0},{.bus=&bus,.receive=1}};QcaCeRing rings[2]={0};
 for(unsigned i=0;i<2;i++)assert(!qca_ce_init(&rings[i],d[i].host,d[i].address,8,i,qca_bmi_publish,qca_bmi_ring_stop,&pipes[i]));
 reg[0][0x44/4]=3;reg[1][0x48/4]=5;
 assert(!qca_ce_hw_configure(&bus.engines[0],d[0].address,8,0,0,256));assert(!qca_ce_seed(&rings[0],bus.engines[0].src_index));
 assert(!qca_ce_hw_configure(&bus.engines[1],0,0,d[1].address,8,0));assert(!qca_ce_seed(&rings[1],bus.engines[1].dst_index));
 assert(!qca_ce_bus_start(&bus));QcaBmiExchange x={0};
 if(scenario==10){
  assert(qca_bmi_info_begin(&x,&bus,&rings[0],&rings[1],&d[0],&d[3],100)==-1&&!order);
  d[2].mapped=0;assert(qca_bmi_info_begin(&x,&bus,&rings[0],&rings[1],&d[2],&d[3],100)==-1&&!order);d[2].mapped=1;
  assert(qca_bmi_info_begin(&x,&bus,&rings[0],&rings[1],&d[2],&d[3],UINT64_MAX)==-1&&!order);
 }
 if(scenario==8)post_error=1;
 int started=qca_bmi_info_begin(&x,&bus,&rings[0],&rings[1],&d[2],&d[3],100);
 if(scenario==8)assert(started==-1&&rings[1].fault&&!publications[0]);
 else{
  assert(!started&&order==2&&publications[0]==1&&publications[1]==1&&hosts[2][0]==8&&!hosts[2][1]);
  assert(qca_bmi_info_begin(&x,&bus,&rings[0],&rings[1],&d[2],&d[3],101)==-1);
  if(scenario==5)assert(qca_bmi_poll(&x,3000100)==-1&&x.error==5);
  else if(scenario==6)assert(qca_bmi_poll(&x,99)==-1&&x.error==4);
  else if(scenario==7){d[3].closing=1;assert(qca_bmi_poll(&x,101)==-1&&x.error==6);}
  else{
   unsigned ti=rings[0].read,ri=rings[1].read;reg[0][0x44/4]=rings[0].write;reg[1][0x48/4]=rings[1].write;
   assert(qca_bmi_poll(&x,101)==0&&x.tx_done&&!x.rx_done); /* RX length race */
   put32(hosts[3],12);put32(hosts[3]+4,0x05020001);put32(hosts[3]+8,7);
   uint8_t*desc=hosts[1]+ri*8;desc[4]=scenario==1?8:scenario==2?13:12;desc[5]=0;
   if(scenario==3)desc[0]^=1;
   if(scenario==4)reg[1][0x48/4]=8;
   if(scenario==9)put32(hosts[3]+4,0);
   int rc=qca_bmi_poll(&x,102);
   if(scenario>=1&&scenario<=4)assert(rc==-1&&x.phase==QCA_BMI_FAULT);
   else if(scenario==9)assert(rc==-1&&x.error==11);
   else assert(rc==1&&x.version==0x05020001&&x.type==7&&x.info_length==12);
   assert(hosts[0][ti*8+4]==0); /* TX completed without descriptor re-use */
  }
 }
 post_error=0;assert(qca_ce_close(&rings[0])==-1&&rings[0].owned);
 assert(!qca_ce_bus_stop_begin(&bus,4000000));assert(qca_ce_bus_stop_poll(&bus,4000001)==1);
 assert(!qca_ce_close(&rings[0]));assert(!qca_ce_close(&rings[1]));assert(flushes==2);
 printf("ROM + BMI CE0/CE1 scenario %u PASS: actual production bus/ring callbacks, RX-before-TX, completion race/invalid response/error stop; MOCK ONLY\n",scenario);return 0;
}
