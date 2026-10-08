/* SPDX-License-Identifier: GPL-2.0-only
 * Cooperative cold-reset ordering adapted from pinned ath10k pci.c.
 * This component is not yet linked into a physical native profile. */
#include "reset_core.h"
int qca_reset_begin(QcaReset*r,const QcaResetTarget*t,QcaRead32 read,QcaWrite32 write,void*context,uint64_t now){
 if(!r||!t||!read||!write||r->owned||(t->address&3)||t->settle_us<20000||t->settle_us>100000
  ||t->deadline_us<2*t->settle_us||t->deadline_us>2000000)return -1;
 uint32_t value=0;
 if(read(context,t->address,&value)||value==0xffffffffu||(value&1))return -1;
 r->target=*t;r->read=read;r->write=write;r->context=context;
 r->started=r->last_time=r->operation_time=now;r->original=value;r->readback=0;
 r->phase=QCA_RESET_ASSERT_WAIT;r->owned=1;r->error=r->attempts=r->deasserted=0;
 /* Mark ownership BEFORE assert: an error does not prove no reset occurred. */
 if(write(context,t->address,value|1)){r->error=QCA_RESET_IO;return -1;}
 return 0;
}
int qca_reset_poll(QcaReset*r,uint64_t now){
 if(!r)return -1;
 if(r->phase==QCA_RESET_DONE)return r->error?-1:1;
 if(!r->owned||r->phase==QCA_RESET_FAULT)return -1;
 if(now<r->last_time){r->error=QCA_RESET_CLOCK;return -1;}
 r->last_time=now;
 if(now-r->started>=r->target.deadline_us&&!r->error)r->error=QCA_RESET_TIMEOUT;
 if(now-r->operation_time<r->target.settle_us)return 0;
 if(r->phase==QCA_RESET_ASSERT_WAIT){
  r->operation_time=now;
  if(r->write(r->context,r->target.address,r->original&~1u)){
   r->error=QCA_RESET_IO;if(++r->attempts>=3)r->phase=QCA_RESET_FAULT;return -1;
  }
  r->deasserted=1;r->attempts=0;r->phase=QCA_RESET_CLEAR_WAIT;return 0;
 }
 if(r->phase==QCA_RESET_CLEAR_WAIT){
  r->operation_time=now;
  int io=r->read(r->context,r->target.address,&r->readback);
  if(!io&&r->readback!=0xffffffffu&&(r->readback&1))r->deasserted=0;
  if(io||r->readback==0xffffffffu||(r->readback&1)){
   r->error=QCA_RESET_IO;if(++r->attempts>=3)r->phase=QCA_RESET_FAULT;return -1;
  }
  r->owned=0;r->phase=QCA_RESET_DONE;return r->error?-1:1;
 }
 return -1;
}
int qca_reset_recover(QcaReset*r,uint64_t now){
 if(!r||!r->owned||r->phase!=QCA_RESET_FAULT||now<r->last_time)return -1;
 r->last_time=r->operation_time=now;r->attempts=0;
 r->phase=r->deasserted?QCA_RESET_CLEAR_WAIT:QCA_RESET_ASSERT_WAIT;return 0;
}
