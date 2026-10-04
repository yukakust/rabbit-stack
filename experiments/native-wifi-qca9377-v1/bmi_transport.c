#include "bmi_transport.h"
#include <stdatomic.h>
typedef Status(EFIAPI *Flush)(void*);
static int fail(QcaBmiExchange*x,unsigned error){x->error=error;x->phase=QCA_BMI_FAULT;return -1;}
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
int qca_bmi_publish(void*context,uint32_t index){
 QcaBmiPipe*p=context;
 if(!p||!p->bus||p->bus->phase!=QCA_BUS_ACTIVE||p->receive>1)return -1;
 return qca_ce_hw_publish(&p->bus->engines[p->receive?1:0],p->receive,index);
}
int qca_bmi_ring_stop(void*context){
 QcaBmiPipe*p=context;
 if(!p||qca_ce_bus_released(p->bus))return -1;
 QcaUefiPort*port=p->bus->access->port;void*fn=*(void**)((uint8_t*)port->pci+104);
 return ((Flush)fn)(port->pci)?-1:0;
}
static int overlap(QcaDmaBuffer*d,QcaCeRing*r){
 uintptr_t a=(uintptr_t)d->host,b=(uintptr_t)r->descriptors;
 return b>=a?(uint64_t)(b-a)<d->bytes:(uint64_t)(a-b)<(uint64_t)r->entries*8;
}
int qca_bmi_info_begin(QcaBmiExchange*x,QcaCeBus*b,QcaCeRing*tx,QcaCeRing*rx,QcaDmaBuffer*req,QcaDmaBuffer*resp,uint64_t now){
 if(!x||x->phase==QCA_BMI_WAIT||!b||b->phase!=QCA_BUS_ACTIVE||!b->owned||now>UINT64_MAX-3000000
  ||!registered(b,req)||!registered(b,resp)||req==resp||req->bytes<4||resp->bytes<12
  ||!ring_memory(b,tx,0,0)||!ring_memory(b,rx,1,1)
  ||overlap(req,tx)||overlap(req,rx)||overlap(resp,tx)||overlap(resp,rx))return -1;
 x->bus=b;x->tx=tx;x->rx=rx;x->request=req;x->response=resp;x->started=x->last=now;
 x->bytes=x->error=x->version=x->type=x->info_length=0;x->tx_done=x->rx_done=x->observed_mask=0;
 x->initial_index[0]=x->observed_index[0]=tx->read;
 x->initial_index[1]=x->observed_index[1]=rx->read;x->phase=QCA_BMI_WAIT;
 if(qca_dma_expose(req)||qca_dma_expose(resp))return fail(x,1);
 for(unsigned i=0;i<12;i++)((volatile uint8_t*)resp->host)[i]=0;
 for(unsigned i=0;i<4;i++)((uint8_t*)req->host)[i]=i?0:8; /* BMI_GET_TARGET_INFO LE32 */
 atomic_thread_fence(memory_order_release);
 if(qca_ce_post(rx,resp->address,12,2,0,0))return fail(x,2);
 if(qca_ce_post(tx,req->address,4,1,0x3fff,0))return fail(x,3);
 return 0;
}
static uint32_t le32(const volatile uint8_t*p){uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
int qca_bmi_poll(QcaBmiExchange*x,uint64_t now){
 if(!x)return -1;
 if(x->phase==QCA_BMI_DONE)return 1;
 if(x->phase!=QCA_BMI_WAIT)return -1;
 if(now<x->last)return fail(x,4);
 x->last=now;
 if(now-x->started>=3000000)return fail(x,5);
 if(x->bus->phase!=QCA_BUS_ACTIVE||!registered(x->bus,x->request)||!registered(x->bus,x->response))return fail(x,6);
 for(unsigned receive=0;receive<2;receive++){
  uint8_t*done=receive?&x->rx_done:&x->tx_done;if(*done)continue;
  unsigned index=0;uint32_t cookie=0,nbytes=0;
  if(qca_ce_hw_index(&x->bus->engines[receive?1:0],receive,&index))return fail(x,7);
  x->observed_index[receive]=(uint16_t)index;x->observed_mask|=(uint8_t)(1u<<receive);
  int rc=qca_ce_complete(receive?x->rx:x->tx,index,&cookie,&nbytes);
  if(rc<0)return fail(x,8);
  if(!rc){if(cookie!=(receive?2u:1u)||(!receive&&nbytes!=4))return fail(x,9);*done=1;if(receive)x->bytes=nbytes;}
 }
 if(!x->tx_done||!x->rx_done)return 0;
 if(x->bytes!=12)return fail(x,10);
 atomic_thread_fence(memory_order_acquire);const volatile uint8_t*p=x->response->host;
 x->info_length=le32(p);x->version=le32(p+4);x->type=le32(p+8);
 if(!x->version||x->version==UINT32_MAX||!x->type||x->type==UINT32_MAX)return fail(x,11);
 /* Preserve length/version/type raw. Compatibility is a separate preflight. */
 x->phase=QCA_BMI_DONE;return 1;
}
