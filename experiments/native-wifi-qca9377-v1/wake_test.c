#include "wake_core.h"
#include <assert.h>
#include <stdio.h>
typedef struct {unsigned reads,writes,fail_read,fail_write;uint32_t state,chip,last_write;} Mock;
static int read32(void*context,uint32_t address,uint32_t*out){
 Mock*m=context;m->reads++;assert(address==0x80000||address==0x8f0);
 if(m->fail_read)return -1;
 *out=address==0x80000?m->state:m->chip;return 0;
}
static int write32(void*context,uint32_t address,uint32_t value){
 Mock*m=context;m->writes++;assert(address==0x80004&&value<=1);m->last_write=value;return m->fail_write?-1:0;
}
int main(void){
 QcaWakeTarget target={0x80000,0x80004,0x8f0,3,1000000};
 QcaWake w={0};Mock m={0};m.chip=0x100;
 assert(!qca_wake_begin(&w,&target,read32,write32,&m,100));
 assert(w.owned&&m.writes==1&&m.last_write==1);
 assert(qca_wake_begin(&w,&target,read32,write32,&m,100)==-1);
 assert(!qca_wake_poll(&w,101)&&m.reads==1);
 m.state=3;assert(qca_wake_poll(&w,102)==1&&w.chip_id==0x100&&m.reads==3);
 assert(qca_wake_poll(&w,103)==1&&m.reads==3);
 assert(!qca_wake_close(&w)&&!w.owned&&m.last_write==0);
 unsigned writes=m.writes;assert(!qca_wake_close(&w)&&m.writes==writes);
 for(unsigned mode=0;mode<7;mode++){
  w=(QcaWake){0};m=(Mock){0};m.chip=0x100;
  if(mode==0)m.fail_write=1;
  int begin=qca_wake_begin(&w,&target,read32,write32,&m,100);
  if(mode==0)assert(begin==-1&&w.owned);
  else{
   assert(!begin);
   if(mode==1)m.fail_read=1;
   if(mode==2)m.state=0xffffffff;
   if(mode==3){m.state=3;m.chip=0xffffffff;}
   if(mode==4){m.state=3;m.chip=0x200;}
   uint64_t time=mode==5?1000100:mode==6?99:101;
   assert(qca_wake_poll(&w,time)==-1&&w.owned);
  }
  m.fail_write=1;assert(qca_wake_close(&w)==-1&&w.owned);
  m.fail_write=0;assert(!qca_wake_close(&w)&&!w.owned);
 }
 QcaWakeTarget invalid=target;invalid.timeout_us=1000001;
 w=(QcaWake){0};writes=m.writes;
 assert(qca_wake_begin(&w,&invalid,read32,write32,&m,0)==-1&&m.writes==writes);
 invalid=target;invalid.wake++;
 assert(qca_wake_begin(&w,&invalid,read32,write32,&m,0)==-1&&m.writes==writes);
 puts("Cooperative QCA wake: bounded poll, timeout/backwards clock, chip revision, ambiguous write ownership, close retry PASS; MOCK MMIO ONLY");
 return 0;
}
