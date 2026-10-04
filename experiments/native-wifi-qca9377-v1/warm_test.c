#include "warm_core.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef struct {
 QcaWarm*w;uint64_t now,ce_assert_time;uint32_t reset,lf,indicator;
 unsigned operations,fail_operation,guard_error,pipes_error,rom_timeout,rom_error;
 unsigned cpu,ce_asserts,ce_clears,pipes,lf_clears,allones;
 unsigned trace[64],count,pipe_waits;
} Mock;
static int operation(Mock*m){return ++m->operations==m->fail_operation;}
static void trace(Mock*m,unsigned v){assert(m->count<64);m->trace[m->count++]=v;}
static int read32(void*c,uint32_t a,uint32_t*v){
 Mock*m=c;assert(a==0x800||a==0x850||a==0x3a028);
 if(operation(m))return -1;
 if(m->allones){*v=UINT32_MAX;return 0;}
 *v=a==0x800?m->reset:a==0x850?m->lf:m->indicator;return 0;
}
static int write32(void*c,uint32_t a,uint32_t v){
 Mock*m=c;assert(a==0x800||a==0x850||a==0x3a028);
 int error=operation(m);
 /* Simulate an ambiguous failure: device accepted write but host got error. */
 if(a==0x3a028){assert(v==0);m->indicator=0;trace(m,10);}
 else if(a==0x850){assert(v==(m->lf&~4u));m->lf=v;m->lf_clears++;trace(m,30);}
 else{
  if((v&1)&&!(m->reset&1)){
   assert(m->cpu==1&&m->pipes==1&&m->lf_clears==1&&m->w->indicator==2);
   m->ce_asserts++;m->ce_assert_time=m->now;trace(m,40);
  }else if(!(v&1)&&(m->reset&1)){
   assert(m->now-m->ce_assert_time>=10000);m->ce_clears++;trace(m,50);
  }else if(v&0x40){
   assert(m->cpu<2);m->cpu++;trace(m,20);
   /* CPU reset self clears in this fixture. */
   m->indicator=m->rom_timeout==m->cpu?0:m->rom_error==m->cpu?1:2;
  }else trace(m,1);
  m->reset=v&~0x40u;
 }
 return error?-1:0;
}
static int guard(void*c){Mock*m=c;return m->guard_error?-1:0;}
static int pipes(void*c){Mock*m=c;assert(m->cpu==m->pipes+1);if(m->pipe_waits){m->pipe_waits--;return 0;}m->pipes++;trace(m,25);return m->pipes_error==m->pipes?-1:1;}
static void setup(QcaWarm*w,Mock*m){memset(w,0,sizeof(*w));memset(m,0,sizeof(*m));m->w=w;m->reset=0x100;m->lf=0x14;m->indicator=2;}
static int step(QcaWarm*w,Mock*m,uint64_t now){m->now=now;return qca_warm_poll(w,now);}
static void run(QcaWarm*w,Mock*m){
 for(uint64_t t=m->now;t<7100000;t+=1000)if(step(w,m,t))return;
 assert(0);
}
int main(void){
 QcaWarm w;Mock m;setup(&w,&m);
 assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));run(&w,&m);
 assert(w.phase==QCA_WARM_DONE&&!w.owned&&!w.ce_owned&&w.cpu_resets==2&&w.pipe_inits==2);
 assert(m.cpu==2&&m.ce_asserts==1&&m.ce_clears==1&&m.pipes==2&&m.lf==0x10);
 const unsigned expected[]={1,1,10,20,25,30,40,50,10,20,25};
 assert(m.count==sizeof(expected)/sizeof(*expected));for(unsigned i=0;i<m.count;i++)assert(m.trace[i]==expected[i]);
 assert(!w.failure_phase&&!w.failure_elapsed_us&&w.first_rom_polls&&w.second_rom_polls&&w.indicator==2);
 unsigned operations=m.operations;
 assert(qca_warm_poll(&w,7000000)==1&&m.operations==operations);
 /* Fault injection at EVERY read/write; fail closed and keep ownership. */
 for(unsigned failure=1;failure<=operations;failure++){
  setup(&w,&m);m.fail_operation=failure;assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));run(&w,&m);
  assert(w.phase==QCA_WARM_FAULT&&w.owned&&w.error);
  unsigned held=w.ce_owned,old_asserts=m.ce_asserts;
  if(held){m.fail_operation=0;m.now+=10000;assert(qca_warm_recover_ce(&w,m.now)==-1);assert(!w.ce_owned&&w.owned&&m.ce_asserts==old_asserts);}
  assert(qca_warm_poll(&w,m.now)==-1);
 }
 /* Cancel at each phase, including the interval while CE reset is asserted. */
 for(unsigned phase=QCA_WARM_SI_ASSERT;phase<QCA_WARM_DONE;phase++){
  setup(&w,&m);assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));
  for(unsigned t=0;w.phase!=phase&&t<100000;t+=1000)assert(step(&w,&m,t)==0);
  assert(w.phase==phase);qca_warm_cancel(&w);run(&w,&m);
  assert(w.phase==QCA_WARM_FAULT&&w.error==QCA_WARM_CANCELLED&&w.owned&&!w.ce_owned);
 }
 for(unsigned phase=QCA_WARM_SI_ASSERT;phase<QCA_WARM_DONE;phase++){
  setup(&w,&m);assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));
  for(unsigned t=0;w.phase!=phase&&t<100000;t+=1000)assert(step(&w,&m,t)==0);
  assert(w.phase==phase);m.guard_error=1;unsigned before=m.operations;
  assert(step(&w,&m,m.now)==-1&&w.error==QCA_WARM_GUARD&&w.owned&&m.operations==before);
  if(w.ce_owned){m.guard_error=0;m.now+=10000;assert(qca_warm_recover_ce(&w,m.now)==-1&&!w.ce_owned&&w.owned);}
 }
 setup(&w,&m);m.guard_error=1;assert(qca_warm_begin(&w,read32,write32,guard,pipes,&m,0)==-1&&!w.owned&&!m.operations);
 setup(&w,&m);assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));m.guard_error=1;assert(step(&w,&m,1)==-1&&w.error==QCA_WARM_GUARD&&!m.operations);
 setup(&w,&m);m.pipes_error=1;assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));run(&w,&m);assert(w.error==QCA_WARM_GUARD&&!m.ce_asserts);
 setup(&w,&m);m.pipe_waits=20;assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));run(&w,&m);assert(w.phase==QCA_WARM_DONE&&w.pipe_inits==2);
 setup(&w,&m);m.pipe_waits=8000;assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));run(&w,&m);assert(w.error==QCA_WARM_TIMEOUT&&!m.ce_asserts);
 setup(&w,&m);m.rom_timeout=1;assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));run(&w,&m);assert(w.error==QCA_WARM_TIMEOUT&&!m.ce_asserts);
 setup(&w,&m);m.rom_error=1;assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));run(&w,&m);assert(w.error==QCA_WARM_ROM_ERROR&&!m.ce_asserts);
 for(unsigned kind=0;kind<3;kind++){
  setup(&w,&m);if(!kind)m.pipes_error=2;else if(kind==1)m.rom_timeout=2;else m.rom_error=2;
  assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));run(&w,&m);
  assert(w.phase==QCA_WARM_FAULT&&w.owned&&!w.ce_owned&&m.cpu==2);
  if(kind==1){assert(w.failure_phase==QCA_WARM_ROM_SECOND&&w.failure_elapsed_us>=3000000&&w.indicator==0&&w.first_rom_polls&&w.second_rom_polls);}
 }
 setup(&w,&m);m.allones=1;assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));run(&w,&m);assert(w.error==QCA_WARM_IO&&!w.writes);
 setup(&w,&m);assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,10));assert(step(&w,&m,9)==-1&&w.error==QCA_WARM_CLOCK);
 setup(&w,&m);assert(qca_warm_begin(&w,read32,write32,guard,pipes,&m,UINT64_MAX)==-1&&!w.owned);
 /* Recovery cannot write after guard/clock failure. */
 setup(&w,&m);assert(!qca_warm_begin(&w,read32,write32,guard,pipes,&m,0));
 for(unsigned t=0;!w.ce_owned&&t<100000;t+=1000)assert(step(&w,&m,t)==0);
 assert(w.ce_owned);m.guard_error=1;operations=m.operations;
 assert(qca_warm_recover_ce(&w,m.now+10000)==-1&&m.operations==operations&&w.ce_owned);
 m.guard_error=0;assert(qca_warm_recover_ce(&w,m.now-1)==-1&&m.operations==operations&&w.ce_owned);
 assert(step(&w,&m,7000000)==-1&&w.error==QCA_WARM_TIMEOUT&&!w.ce_owned&&w.owned);
 printf("WARM-ORDER-CANCELLATION-IO-OWNERSHIP-PASS\n");return 0;
}
