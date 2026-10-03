#include "reset_core.h"
#include <assert.h>
#include <stdio.h>
static uint32_t reg;static unsigned reads,writes,mode;static uint64_t clock_us,write_time;
static int read32(void*c,uint32_t a,uint32_t*out){
 (void)c;assert(a==0x80008);if(writes)assert(clock_us-write_time>=20000);
 reads++;if(mode==3)return -1;*out=mode==4?0xffffffffu:reg;return 0;
}
static int write32(void*c,uint32_t a,uint32_t v){
 (void)c;assert(a==0x80008);if(writes)assert(clock_us-write_time>=20000);
 assert((v&~1u)==0x20);writes++;write_time=clock_us;
 if(mode!=2)reg=v;
 return mode==1?-1:0;
}
static int poll(QcaReset*r,uint64_t t){clock_us=t;return qca_reset_poll(r,t);}
static void baseline(void){reg=0x20;reads=writes=mode=0;clock_us=write_time=0;}
int main(void){
 QcaResetTarget t={0x80008,20000,1000000};QcaReset r={0};
 baseline();assert(!qca_reset_begin(&r,&t,read32,write32,0,0));
 assert(r.owned&&reg==0x21&&reads==1&&writes==1);
 assert(qca_reset_begin(&r,&t,read32,write32,0,0)==-1);
 assert(!poll(&r,19999)&&reads==1&&writes==1);
 assert(!poll(&r,20000)&&r.owned&&reg==0x20&&reads==1&&writes==2);
 assert(!poll(&r,39999)&&reads==1);assert(poll(&r,40000)==1&&!r.owned&&reads==2);
 assert(poll(&r,50000)==1&&reads==2&&writes==2);
 for(unsigned fault=1;fault<=7;fault++){
  baseline();r=(QcaReset){0};mode=fault==1?1:0;
  int begun=qca_reset_begin(&r,&t,read32,write32,0,0);assert((fault==1)==(begun<0));
  if(fault==1)mode=0;
  if(fault==2)mode=1; /* ambiguous deassert, retries retain ownership */
  if(fault==3){assert(!poll(&r,100));assert(poll(&r,99)==-1&&r.owned&&writes==1);}
  if(fault==4){assert(!poll(&r,1000000));assert(poll(&r,1020000)==-1&&!r.owned);continue;}
  poll(&r,20000);
  if(fault==5)mode=3; /* read error after settle */
  if(fault==7)mode=4;
  if(fault==6)reg|=1; /* dropped clear: must not release ownership */
  poll(&r,40000);poll(&r,60000);poll(&r,80000);
  if(fault==2||fault==5||fault==6||fault==7){
   assert(r.owned&&r.phase==QCA_RESET_FAULT);unsigned n=reads+writes;
   assert(poll(&r,100000)==-1&&reads+writes==n);
   mode=0;assert(!qca_reset_recover(&r,100000));poll(&r,120000);poll(&r,140000);
  }
  assert(!r.owned&&reg==0x20&&r.error);
 }
 baseline();r=(QcaReset){0};reg=1;assert(qca_reset_begin(&r,&t,read32,write32,0,0)==-1&&!writes&&!r.owned);
 reg=0xffffffffu;assert(qca_reset_begin(&r,&t,read32,write32,0,0)==-1&&!writes);
 t.settle_us=19999;assert(qca_reset_begin(&r,&t,read32,write32,0,0)==-1&&!writes);
 puts("Cold reset core: 20ms access exclusion, ambiguous writes, bounded retry/recovery, verified deassertion, clock and deadline PASS; MOCK ONLY");return 0;
}
