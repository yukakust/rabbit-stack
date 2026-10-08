#include "bmi_loader.h"
#include <stdatomic.h>
static int fail(QcaBmiExchange*x,unsigned e){x->error=e;x->phase=QCA_BMI_FAULT;return -1;}
static int registered(QcaCeBus*b,QcaDmaBuffer*d){
 if(!d||d->port!=b->access->port||!d->valid||!d->allocated||!d->host||!d->mapped||d->closing)return 0;
 for(unsigned i=0;i<b->access->count;i++)if(b->access->buffers[i]==d)return 1;
 return 0;
}
static int ring_memory(QcaCeBus*b,QcaCeRing*r,unsigned engine,int receive){
 if(!r||!r->owned||r->fault||r->receive!=receive||r->read!=r->write||r->read!=r->published)return 0;
 QcaBmiPipe*p=r->context;
 if(r->publish!=qca_bmi_publish||r->stop!=qca_bmi_ring_stop||!p||p->bus!=b||p->receive!=receive)return 0;
 uint32_t base=0,n=0;
 if(qca_ce_access_read(b->access,b->engines[engine].base+(receive?8:0),&base)
  ||qca_ce_access_read(b->access,b->engines[engine].base+(receive?0xc:4),&n)||n!=r->entries)return 0;
 for(unsigned i=0;i<b->access->count;i++){
  QcaDmaBuffer*d=b->access->buffers[i];
  if(registered(b,d)&&base>=d->address&&(uint64_t)base-d->address<=d->bytes
    &&(uint64_t)r->entries*8<=d->bytes-((uint64_t)base-d->address)
    &&r->descriptors==(volatile uint8_t*)d->host+(base-d->address))return 1;
 }
 return 0;
}
static int overlap(QcaDmaBuffer*d,QcaCeRing*r){
 uintptr_t a=(uintptr_t)d->host,b=(uintptr_t)r->descriptors;
 return b>=a?(uint64_t)(b-a)<d->bytes:(uint64_t)(a-b)<(uint64_t)r->entries*8;
}

static uint32_t word(const uint8_t*p){uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
int qca_bmi_loader_begin(QcaBmiLoader*l,QcaCeBus*b,QcaCeRing*tx,QcaCeRing*rx,QcaDmaBuffer*req,QcaDmaBuffer*resp,const uint8_t*p,unsigned n,uint64_t now){
 if(!l||!p||n<8||n>256||n%4)return -1;
 unsigned response=0;uint32_t op=word(p),arg=word(p+4);
 if(op==13){if(n!=8||(arg!=0&&arg!=0x1234))return -1;}
 else if(op==14){if(!arg||arg>248||arg%4||n!=arg+8)return -1;}
 else if(op==4){if(n!=12||arg!=0x1234||word(p+8)!=0x10)return -1;response=4;}
 else return -1;
 QcaBmiExchange*x=&l->wire;
 if(x->phase==QCA_BMI_WAIT||!b||b->phase!=QCA_BUS_ACTIVE||!b->owned||now>UINT64_MAX-3000000
  ||!registered(b,req)||!registered(b,resp)||req==resp||req->bytes<n||resp->bytes<4
  ||!ring_memory(b,tx,0,0)||!ring_memory(b,rx,1,1)
  ||overlap(req,tx)||overlap(req,rx)||overlap(resp,tx)||overlap(resp,rx))return -1;
 *x=(QcaBmiExchange){.bus=b,.tx=tx,.rx=rx,.request=req,.response=resp,.started=now,.last=now,.phase=QCA_BMI_WAIT,.rx_done=(uint8_t)!response};
 l->request_bytes=n;l->response_bytes=response;
 x->initial_index[0]=x->observed_index[0]=tx->read;x->initial_index[1]=x->observed_index[1]=rx->read;
 if(qca_dma_expose(req)||(response&&qca_dma_expose(resp)))return fail(x,1);
 for(unsigned i=0;i<4;i++)((volatile uint8_t*)resp->host)[i]=0;
 for(unsigned i=0;i<n;i++)((uint8_t*)req->host)[i]=p[i];
 atomic_thread_fence(memory_order_release);
 if(response&&qca_ce_post(rx,resp->address,response,2,0,0))return fail(x,2);
 if(qca_ce_post(tx,req->address,n,1,0x3fff,0))return fail(x,3);
 return 0;
}
int qca_bmi_loader_poll(QcaBmiLoader*l,uint64_t now){
 if(!l)return -1;
 QcaBmiExchange*x=&l->wire;
 if(x->phase==QCA_BMI_DONE)return 1;
 if(x->phase!=QCA_BMI_WAIT)return -1;
 if(now<x->last)return fail(x,4);
 x->last=now;
 if(x->bus->phase!=QCA_BUS_ACTIVE||!registered(x->bus,x->request)||!registered(x->bus,x->response))return fail(x,6);
 for(unsigned receive=0;receive<2;receive++){
  uint8_t*done=receive?&x->rx_done:&x->tx_done;if(*done)continue;
  unsigned index=0;uint32_t cookie=0,nbytes=0;
  if(qca_ce_hw_index(&x->bus->engines[receive?1:0],receive,&index))return fail(x,7);
  x->observed_index[receive]=(uint16_t)index;x->observed_mask|=(uint8_t)(1u<<receive);
  int rc=qca_ce_complete(receive?x->rx:x->tx,index,&cookie,&nbytes);
  if(rc<0)return fail(x,8);
  if(!rc){if(cookie!=(receive?2u:1u)||nbytes!=(receive?l->response_bytes:l->request_bytes))return fail(x,9);*done=1;if(receive)x->bytes=nbytes;}
 }
 if(!x->tx_done||!x->rx_done)return now-x->started>=3000000?fail(x,5):0;
 atomic_thread_fence(memory_order_acquire);x->phase=QCA_BMI_DONE;return 1;
}
