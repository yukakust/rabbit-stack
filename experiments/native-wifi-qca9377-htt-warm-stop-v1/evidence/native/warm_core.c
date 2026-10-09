/* SPDX-License-Identifier: GPL-2.0-only
 * Cooperative QCA6174/QCA9377 warm sequence adapted from pinned ath10k pci.c.
 * Used by the separately gated one-shot native init profile.
 */
#include "warm_core.h"
static int fail(QcaWarm*w,unsigned e){
 if(!w->failure_phase&&w->phase!=QCA_WARM_FAULT){
  w->failure_phase=w->phase;
  uint64_t elapsed=w->last>=w->operation?w->last-w->operation:0;
  w->failure_elapsed_us=elapsed>UINT32_MAX?UINT32_MAX:(uint32_t)elapsed;
 }
 if(!w->error)w->error=(uint8_t)e;
 w->phase=QCA_WARM_FAULT;return -1;
}
static int read32(QcaWarm*w,uint32_t a,uint32_t*v){
 if(w->read(w->context,a,v)||*v==UINT32_MAX)return -1;
 if(a==0x800)w->last_reset_read=*v;
 w->reads++;return 0;
}
static int write32(QcaWarm*w,uint32_t a,uint32_t v){
 w->writes++;return w->write(w->context,a,v)?-1:0;
}
static int cpu(QcaWarm*w,uint64_t now){
 uint32_t v=0;
 if(write32(w,0x3a028,0)||read32(w,0x800,&v)||write32(w,0x800,v|0x40))return fail(w,QCA_WARM_IO);
 w->cpu_resets++;w->operation=w->next=now;return 0;
}
static int deassert_ce(QcaWarm*w,uint64_t now){
 if(now-w->operation<10000)return 0;
 uint32_t v=0;
 /* Preserve the pre-assert value exactly as upstream. Write failure is
  * ambiguous: retain ce_owned, including when device may have accepted it. */
 if(write32(w,0x800,w->reset_value&~1u)||read32(w,0x800,&v)||(v&1))return fail(w,QCA_WARM_IO);
 w->ce_owned=0;
 if(w->cancelled)return fail(w,QCA_WARM_CANCELLED);
 if(w->error)return fail(w,w->error);
 w->phase=QCA_WARM_CPU_SECOND;return 0;
}
int qca_warm_begin(QcaWarm*w,QcaRead32 r,QcaWrite32 wr,QcaWarmCheck check,QcaWarmPipes pipes,void*c,uint64_t now){
 if(!w||!r||!wr||!check||!pipes||w->owned||w->phase||now>UINT64_MAX-20000000||check(c))return -1;
 w->read=r;w->write=wr;w->check=check;w->pipes=pipes;w->context=c;
 w->started=w->last=w->operation=w->next=now;w->owned=1;w->phase=QCA_WARM_SI_ASSERT;return 0;
}
int qca_warm_poll(QcaWarm*w,uint64_t now){
 if(!w)return -1;
 if(w->phase==QCA_WARM_DONE)return 1;
 if(!w->owned||w->phase==QCA_WARM_FAULT)return -1;
 if(now<w->last)return fail(w,QCA_WARM_CLOCK);
 w->last=now;
 if(w->check(w->context))return fail(w,QCA_WARM_GUARD);
 if(now-w->started>=20000000){w->error=QCA_WARM_TIMEOUT;w->cancelled=1;}
 if(w->cancelled&&!w->ce_owned)return fail(w,w->error?w->error:QCA_WARM_CANCELLED);
 if(w->ce_owned)return deassert_ce(w,now);
 uint32_t v=0;
 switch(w->phase){
 case QCA_WARM_SI_ASSERT:
  /* SI0 mask is zero for this chip. Retain source read/write/read and waits. */
  if(read32(w,0x800,&v)||(v&1)||write32(w,0x800,v)||read32(w,0x800,&v))return fail(w,QCA_WARM_IO);
  w->operation=now;w->phase=QCA_WARM_SI_CLEAR;return 0;
 case QCA_WARM_SI_CLEAR:
  if(now-w->operation<10000)return 0;
  if(read32(w,0x800,&v)||write32(w,0x800,v)||read32(w,0x800,&v))return fail(w,QCA_WARM_IO);
  w->operation=now;w->phase=QCA_WARM_CPU_FIRST;return 0;
 case QCA_WARM_CPU_FIRST:
  if(now-w->operation<10000)return 0;
  if(cpu(w,now))return -1;
  w->phase=QCA_WARM_PIPES_FIRST;return 0;
 case QCA_WARM_PIPES_FIRST:case QCA_WARM_PIPES_SECOND:
  {
  int rc=w->pipes(w->context);
  if(rc<0)return fail(w,QCA_WARM_GUARD);
  if(!rc)return 0;
  w->pipe_inits++;w->operation=w->next=now;
  w->phase=w->phase==QCA_WARM_PIPES_FIRST?QCA_WARM_ROM_FIRST:QCA_WARM_ROM_SECOND;return 0;
  }
 case QCA_WARM_ROM_FIRST:case QCA_WARM_ROM_SECOND:
  if(now-w->operation>=3000000)return fail(w,QCA_WARM_TIMEOUT);
  if(now<w->next)return 0;
  w->next=now+10000;
  if(w->phase==QCA_WARM_ROM_FIRST)w->first_rom_polls++;else w->second_rom_polls++;
  if(read32(w,0x3a028,&w->indicator))return fail(w,QCA_WARM_IO);
  if(w->indicator&1)return fail(w,QCA_WARM_ROM_ERROR);
  if(!(w->indicator&2))return 0;
  if(w->phase==QCA_WARM_ROM_FIRST){w->phase=QCA_WARM_LF;return 0;}
  w->owned=0;w->phase=QCA_WARM_DONE;return 1;
 case QCA_WARM_LF:
  if(read32(w,0x850,&v)||write32(w,0x850,v&~4u))return fail(w,QCA_WARM_IO);
  w->phase=QCA_WARM_CE_ASSERT;return 0;
 case QCA_WARM_CE_ASSERT:
  if(read32(w,0x800,&v)||(v&1))return fail(w,QCA_WARM_IO);
  w->reset_value=v;w->ce_owned=1;w->operation=now;w->phase=QCA_WARM_CE_CLEAR;
  if(write32(w,0x800,v|1))return fail(w,QCA_WARM_IO);
  return 0;
 case QCA_WARM_CPU_SECOND:
  if(cpu(w,now))return -1;
  w->phase=QCA_WARM_PIPES_SECOND;return 0;
 default:return fail(w,QCA_WARM_GUARD);
 }
}
void qca_warm_cancel(QcaWarm*w){if(w&&w->owned)w->cancelled=1;}
int qca_warm_recover_ce(QcaWarm*w,uint64_t now){
 /* Caller bounds retry count. This path can only remove CE reset, never
  * continue normal initialization or release exclusive device ownership. */
 if(!w||!w->owned||!w->ce_owned||now<w->last||w->check(w->context))return -1;
 w->last=now;w->cancelled=1;return deassert_ce(w,now);
}
