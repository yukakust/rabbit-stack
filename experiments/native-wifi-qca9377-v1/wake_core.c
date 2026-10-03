/* SPDX-License-Identifier: GPL-2.0-only
 * QCA9377 bring-up component, adapted from pinned ath10k wake behaviour.
 * No firmware upload, reset, interrupts, DMA or association is implemented here.
 */
#include "wake_core.h"
static int fail(QcaWake*w,uint8_t error){w->error=error;w->phase=QCA_WAKE_FAULT;return -1;}
int qca_wake_begin(QcaWake*w,const QcaWakeTarget*t,QcaRead32 read,QcaWrite32 write,void*context,uint64_t now){
 if(!w||!t||!read||!write||w->owned||!t->timeout_us||t->timeout_us>1000000u
  ||(t->state|t->wake|t->chip_id)&3||t->state==t->wake||t->chip_id==t->wake||t->chip_id==t->state
  ||t->on>7)return -1;
 w->target=*t;w->read=read;w->write=write;w->context=context;w->started=w->last_time=now;
 w->chip_id=0;w->phase=QCA_WAKE_WAIT;w->error=0;w->owned=1;
 if(write(context,t->wake,1))return fail(w,QCA_WAKE_IO);
 return 0;
}
int qca_wake_poll(QcaWake*w,uint64_t now){
 if(!w||!w->owned)return -1;
 if(w->phase==QCA_WAKE_READY)return 1;
 if(w->phase!=QCA_WAKE_WAIT)return -1;
 if(now<w->last_time)return fail(w,QCA_WAKE_CLOCK);
 w->last_time=now;
 if(now-w->started>=w->target.timeout_us)return fail(w,QCA_WAKE_TIMEOUT);
 uint32_t value=0;
 if(w->read(w->context,w->target.state,&value)||value==0xffffffffu)return fail(w,QCA_WAKE_IO);
 if((value&7)!=w->target.on)return 0;
 if(w->read(w->context,w->target.chip_id,&value))return fail(w,QCA_WAKE_IO);
 /* PCI ID0042 supports chip revisions0 and1. Zero/all-ones fail closed. */
 if(!value||value==0xffffffffu||((value>>8)&15)>1)return fail(w,QCA_WAKE_CHIP);
 w->chip_id=value;w->phase=QCA_WAKE_READY;return 1;
}
int qca_wake_close(QcaWake*w){
 if(!w)return -1;
 if(!w->owned){w->phase=QCA_SLEEPING;return 0;}
 if(w->write(w->context,w->target.wake,0))return fail(w,QCA_WAKE_IO);
 w->owned=0;w->phase=QCA_SLEEPING;return 0;
}
