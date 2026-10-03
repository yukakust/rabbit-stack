#include "ce_hw.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
static uint32_t registers[32];static unsigned mode,reads,writes,failing_offset=~0u;
static int read32(void*c,uint32_t address,uint32_t*out){
 assert(c==registers&&address>=0x34400&&address<0x34480&&!(address&3));reads++;
 unsigned off=address-0x34400;if(mode==1)return -1;
 *out=mode==2?0xffffffffu:registers[off/4];return 0;
}
static int write32(void*c,uint32_t address,uint32_t value){
 assert(c==registers&&address>=0x34400&&address<0x34480&&!(address&3));writes++;
 unsigned off=address-0x34400;
 if(mode==3)return -1;
 if(mode==4||off==failing_offset)return 0; /* acknowledged but dropped */
 if(off==0x18){registers[off/4]=value|(mode==5?0:value?8:0);return 0;}
 if(off==0x30||off==0x38)registers[off/4]&=~value;else registers[off/4]=value;
 return 0;
}
static void ready(QcaCeHw*c){assert(!qca_ce_hw_init(c,0,read32,write32,registers));assert(!qca_ce_hw_stop_begin(c,0));assert(qca_ce_hw_stop_poll(c,1)==1&&!c->owned);}
int main(int argc,char**argv){
 assert(argc==2);unsigned scenario=(unsigned)atoi(argv[1]);assert(scenario<=9);QcaCeHw c={0};unsigned index;
 if(scenario<=4){
  mode=scenario;assert(!qca_ce_hw_init(&c,0,read32,write32,registers));int start=qca_ce_hw_stop_begin(&c,0);
  if(scenario==3)assert(start==-1&&c.owned);else assert(!start);
  int stopped=qca_ce_hw_stop_poll(&c,1);
  if(scenario==0)assert(stopped==1&&!c.owned);else{assert(stopped==-1&&c.owned);mode=0;assert(!qca_ce_hw_stop_begin(&c,2));assert(qca_ce_hw_stop_poll(&c,3)==1&&!c.owned);}return 0;
 }
 if(scenario==5){mode=5;assert(!qca_ce_hw_init(&c,0,read32,write32,registers));assert(!qca_ce_hw_stop_begin(&c,0));assert(!qca_ce_hw_stop_poll(&c,1)&&c.owned);assert(qca_ce_hw_stop_poll(&c,1000000)==-1&&c.owned);return 0;}
 ready(&c);
 if(scenario==6){registers[0x44/4]=5;registers[0x48/4]=6;}
 if(scenario==7)failing_offset=0;
 if(scenario==8)registers[0x18/4]=0;
 int configured=qca_ce_hw_configure(&c,0x100000,8,0x200000,8,256);
 if(scenario==7){assert(configured==-1&&c.owned);failing_offset=~0u;assert(!qca_ce_hw_stop_begin(&c,2));assert(qca_ce_hw_stop_poll(&c,3)==1&&!c.owned);return 0;}
 if(scenario==8){assert(configured==-1&&!c.owned);return 0;}
 assert(!configured&&c.owned&&registers[0]==0x100000&&registers[2]==0x200000&&registers[0x10/4]==256);
 assert(registers[0x4c/4]==8&&registers[0x50/4]==8);
 if(scenario==6)assert(c.src_index==5&&c.dst_index==6&&registers[0x3c/4]==5);
 assert(!qca_ce_hw_run(&c));assert(!qca_ce_hw_publish(&c,0,7));assert(qca_ce_hw_publish(&c,0,8)==-1);
 registers[0x44/4]=7;assert(!qca_ce_hw_index(&c,0,&index)&&index==7);
 if(scenario==9){registers[0x44/4]=8;assert(qca_ce_hw_index(&c,0,&index)==-1&&c.owned);}
 assert(!qca_ce_hw_stop_begin(&c,100));assert(qca_ce_hw_stop_poll(&c,101)==1&&!c.owned&&!registers[0]&&!registers[1]&&!registers[2]&&!registers[3]);
 assert(qca_ce_hw_publish(&c,0,0)==-1);assert(qca_ce_hw_init(&c,8,read32,write32,registers)==-1);
 unsigned n=writes;assert(qca_ce_hw_configure(&c,UINT32_MAX,8,0,0,256)==-1&&writes==n);
 printf("CE MMIO scenario %u: halt ACK/readback, setup/index/stop, drop/error/timeout retention PASS; MOCK ONLY\n",scenario);return 0;
}
