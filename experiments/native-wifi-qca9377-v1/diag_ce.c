/* SPDX-License-Identifier: GPL-2.0-only
 * Narrow read-only CE7 diagnostic adapted from pinned ath10k pci.c. */
#include "diag_ce.h"
#include <stdatomic.h>
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
typedef Status(EFIAPI *Flush)(void*);
static void*method(QcaUefiPort*p,unsigned off){return *(void**)((uint8_t*)p->pci+off);}
static int fail(QcaDiagExchange*x,unsigned error){x->error=error;x->phase=QCA_DIAG_FAULT;return -1;}
static int registered(QcaCeBus*b,QcaDmaBuffer*d){
 if(!d||d->port!=b->access->port||!d->valid||!d->allocated||!d->mapped||!d->host||d->closing)return 0;
 for(unsigned i=0;i<b->access->count;i++)if(b->access->buffers[i]==d)return 1;
 return 0;
}
static int ring(QcaCeBus*b,QcaCeRing*r,int receive){
 if(!r||!r->owned||r->fault||r->receive!=receive||r->read!=r->write||r->read!=r->published
  ||r->publish!=qca_diag_publish||r->stop!=qca_diag_stop)return 0;
 QcaDiagPipe*p=r->context;if(!p||p->bus!=b||p->receive!=receive)return 0;
 uint32_t base=0,n=0;
 if(qca_ce_access_read(b->access,0x36000+(receive?8:0),&base)
  ||qca_ce_access_read(b->access,0x36000+(receive?12:4),&n)||n!=r->entries)return 0;
 for(unsigned i=0;i<b->access->count;i++){
  QcaDmaBuffer*d=b->access->buffers[i];
  if(registered(b,d)&&base>=d->address&&(uint64_t)base-d->address<=d->bytes
   &&(uint64_t)r->entries*8<=d->bytes-((uint64_t)base-d->address)
   &&r->descriptors==(volatile uint8_t*)d->host+(base-d->address))return 1;
 }
 return 0;
}
int qca_diag_publish(void*context,uint32_t index){
 QcaDiagPipe*p=context;
 if(!p||!p->bus||p->bus->phase!=QCA_BUS_ACTIVE||p->receive>1)return -1;
 return qca_ce_hw_publish(&p->bus->engines[7],p->receive,index);
}
int qca_diag_stop(void*context){
 QcaDiagPipe*p=context;if(!p||qca_ce_bus_released(p->bus))return -1;
 QcaUefiPort*port=p->bus->access->port;return ((Flush)method(port,104))(port->pci)?-1:0;
}
int qca_diag_begin(QcaDiagExchange*x,QcaCeBus*b,QcaCeRing*tx,QcaCeRing*rx,QcaDmaBuffer*resp,uint32_t chip,uint64_t bar,uint64_t now){
 if(!x||x->phase!=QCA_DIAG_IDLE||!b||!b->access||!b->access->port||b->phase!=QCA_BUS_ACTIVE||!b->owned)return -1;
 x->bus=b;x->tx=tx;x->rx=rx;x->response=resp;x->started=x->last=now;
 QcaUefiPort*p=b->access->port;
 if(chip!=0x003821ff||now>UINT64_MAX-3000000||bar>UINT32_MAX||p->bar_extent<0x1008fc
  ||!registered(b,resp)||resp->bytes<4||!ring(b,tx,0)||!ring(b,rx,1)
  ||tx->descriptors==rx->descriptors)return fail(x,1);
 uintptr_t h=(uintptr_t)resp->host;
 for(unsigned i=0;i<2;i++){
  QcaCeRing*r=i?rx:tx;uintptr_t d=(uintptr_t)r->descriptors;
  if(d>=h?(uint64_t)(d-h)<resp->bytes:(uint64_t)(h-d)<(uint64_t)r->entries*8)return fail(x,1);
 }
 if(((Config)method(p,48))(p->pci,1,4,1,&x->command)||x->command!=(uint16_t)(b->command|4)
  ||((Memory)method(p,16))(p->pci,2,0,0x3a000,1,&x->core)||x->core==0xffffffffu
  ||((uint64_t)(x->core&0x7ff)<<21)!=bar)return fail(x,2);
 x->target=0x004008f8;x->ce_address=(uint32_t)bar|0x1008f8;
 x->initial[0]=x->observed[0]=tx->read;x->initial[1]=x->observed[1]=rx->read;
 if(qca_dma_expose(resp))return fail(x,3);
 for(unsigned i=0;i<4;i++)((volatile uint8_t*)resp->host)[i]=0;
 x->phase=QCA_DIAG_WAIT;atomic_thread_fence(memory_order_release);
 if(qca_ce_post(rx,resp->address,4,2,0,0))return fail(x,4);
 if(qca_ce_post(tx,x->ce_address,4,1,0,0))return fail(x,5);
 return 0;
}
int qca_diag_poll(QcaDiagExchange*x,uint64_t now){
 if(!x)return -1;
 if(x->phase==QCA_DIAG_DONE)return 1;
 if(x->phase!=QCA_DIAG_WAIT)return -1;
 if(now<x->last)return fail(x,6);
 x->last=now;uint64_t elapsed=now-x->started;
 x->last_elapsed=elapsed>UINT32_MAX?UINT32_MAX:(uint32_t)elapsed;
 if(!x->polls)x->first_elapsed=x->last_elapsed;
 if(x->polls<UINT32_MAX)x->polls++;
 /* Rendering may delay the first poll. Observe completion before declaring a
  * wait timeout; this proves observed completion, not device completion time. */
 if(x->bus->phase!=QCA_BUS_ACTIVE||!registered(x->bus,x->response))return fail(x,8);
 for(unsigned receive=0;receive<2;receive++){
  uint8_t*done=receive?&x->rx_done:&x->tx_done;if(*done)continue;
  unsigned index=0;uint32_t cookie=0,bytes=0;
  if(qca_ce_hw_index(&x->bus->engines[7],receive,&index))return fail(x,9);
  x->observed[receive]=(uint16_t)index;x->mask|=(uint8_t)(1u<<receive);
  int rc=qca_ce_complete(receive?x->rx:x->tx,index,&cookie,&bytes);
  if(rc<0)return fail(x,10);
  if(!rc){if(cookie!=(receive?2u:1u)||bytes!=4)return fail(x,11);*done=1;if(receive)x->bytes=bytes;}
 }
 if(!x->tx_done||!x->rx_done)return elapsed>=3000000?fail(x,7):0;
 atomic_thread_fence(memory_order_acquire);const volatile uint8_t*p=x->response->host;
 for(unsigned i=0;i<4;i++)x->value|=(uint32_t)p[i]<<(8*i);
 x->phase=QCA_DIAG_DONE;return 1;
}
