#include "channels_core.h"
#include "owner47.h"
extern int runtime_extra_retained(QcaChannels*);
/* Full QCA9377 host resource preparation, no firmware/target RAM writes. */
#include "channels_core.h"
static const uint8_t pipe_id[7]={0,1,2,3,4,7,7};
static const uint8_t receive[7]={0,1,1,0,0,0,1};
static const uint16_t capacity[7]={256,2048,2048,2048,256,2048,2048};
static int publish(void*c,uint32_t index){
 QcaChannelRoute*r=c;
 if(!r||!r->bus||r->bus->phase!=QCA_BUS_ACTIVE||!r->bus->owned)return -1;
 return qca_ce_hw_publish(&r->bus->engines[r->pipe],r->receive,index);
}
static int stop(void*c){QcaChannelRoute*r=c;return r?qca_ce_bus_released(r->bus):-1;}
static int fail(QcaChannels*c,unsigned error){c->error=error;c->phase=QCA_CHANNEL_FAULT;return -1;}
int qca_channels_begin(QcaChannels*c,QcaCeBus*b){
 if(!c||c->phase||!b||!b->access||b->access->count||qca_ce_bus_released(b))return -1;
 c->bus=b;c->phase=QCA_CHANNEL_ALLOCATING;return 0;
}
int qca_channels_prepare_step(QcaChannels*c){
 if(!c||c->phase!=QCA_CHANNEL_ALLOCATING||c->allocated>=14||qca_ce_bus_released(c->bus))return -1;
 QcaDmaBuffer*d=&c->buffers[c->allocated];
 if(qca_dma_open(d,c->bus->access->port,1,qca_ce_bus_released,c->bus))return fail(c,1);
 for(unsigned i=0;i<c->allocated;i++){
  QcaDmaBuffer*old=&c->buffers[i];
  if(d->host==old->host){d->allocation_uncertain=old->allocation_uncertain=1;return fail(c,6);}
  if(d->address==old->address)return fail(c,6); /* Page-aligned full-page mappings. */
 }
 if(qca_ce_access_buffer(c->bus->access,d))return fail(c,1);
 if(++c->allocated<14)return 0;
 c->phase=QCA_CHANNEL_READY;return 1;
}
static int mappings_ready(QcaChannels*c){
 if(!c||!c->bus||!c->bus->access||c->allocated!=14||c->bus->access->count!=14
  )return -1;
 QcaUefiPort*p=c->bus->access->port;
 if(!p||!p->pci||!p->claimed||!p->validated||!p->memory_ready||!p->wake_owned)return -1;
 if(!runtime_extra_retained(c))return -1;
 for(unsigned i=0;i<14;i++){
  QcaDmaBuffer*d=&c->buffers[i];
  if(c->bus->access->buffers[i]!=d||d->port!=p||!d->allocated||!d->mapped||!d->valid||d->closing
   ||d->bytes!=4096||d->pages!=1||d->stop!=qca_ce_bus_released||d->context!=c->bus
   ||d->allocation_uncertain||!d->host||((uintptr_t)d->host&4095)||d->address>UINT32_MAX-4095u||(d->address&4095))return -1;
  for(unsigned j=0;j<i;j++)if(d->address==c->buffers[j].address||d->host==c->buffers[j].host)return -1;
 }
 return 0;
}
int qca_channels_retained(QcaChannels*c){return mappings_ready(c);}
int qca_channels_prepared(QcaChannels*c){
 if(mappings_ready(c)||(c->phase!=QCA_CHANNEL_CONFIGURED&&c->phase!=QCA_CHANNEL_POSTED))return -1;
 QcaUefiPort*p=c->bus->access->port;
 if((c->bus->phase!=QCA_BUS_OFF&&c->bus->phase!=QCA_BUS_ACTIVE)
  ||(c->bus->phase==QCA_BUS_ACTIVE)!=(c->bus->owned!=0))return -1;
 typedef Status(EFIAPI *ReadConfig)(void*,uint32_t,uint32_t,uint64_t,void*);
 uint16_t command=0;void*method=*(void**)((uint8_t*)p->pci+48);
 if(!method||((ReadConfig)method)(p->pci,1,4,1,&command)||!(command&2)
  ||((command&4)!=0)!=(c->bus->phase==QCA_BUS_ACTIVE))return -1;
 if(c->bus->phase==QCA_BUS_ACTIVE)for(unsigned i=0;i<14;i++)if(!c->buffers[i].exposed)return -1;
 for(unsigned i=0;i<7;i++){
  QcaCeRing*r=&c->rings[i];QcaCeHw*h=&c->bus->engines[pipe_id[i]];
  if(!r->owned||r->fault||r->entries!=8||r->receive!=receive[i]||r->descriptors!=c->buffers[2*i].host
   ||r->context!=&c->routes[i]||c->routes[i].bus!=c->bus||c->routes[i].pipe!=pipe_id[i]
   ||c->routes[i].receive!=receive[i]||(h->phase!=QCA_CE_HW_CONFIGURED&&h->phase!=QCA_CE_HW_RUNNING)
   ||(receive[i]?h->dst_entries:h->src_entries)!=8)return -1;
  uint32_t base=0,entries=0;
  if(qca_ce_access_read(c->bus->access,h->base+(receive[i]?8:0),&base)
   ||qca_ce_access_read(c->bus->access,h->base+(receive[i]?12:4),&entries)
   ||base!=c->buffers[2*i].address||entries!=8)return -1;
 }
 for(unsigned i=5;i<=6;i++)if(c->bus->engines[i].phase!=QCA_CE_HW_STOPPED)return -1;
 return 0;
}
int qca_channels_configure(QcaChannels*c){
 if(!c||c->phase!=QCA_CHANNEL_READY||qca_ce_bus_released(c->bus)||mappings_ready(c))return -1;
 for(unsigned i=0;i<7;i++){
  c->routes[i]=(QcaChannelRoute){c->bus,pipe_id[i],receive[i]};
  if(qca_ce_init(&c->rings[i],c->buffers[2*i].host,c->buffers[2*i].address,8,receive[i],publish,stop,&c->routes[i]))return fail(c,2);
 }
 for(unsigned i=0;i<6;i++){
  unsigned ring=i,pipe=pipe_id[ring];uint64_t src=0,dst=0;unsigned ns=0,nd=0;
  if(receive[ring]){dst=c->buffers[2*ring].address;nd=8;}
  else{src=c->buffers[2*ring].address;ns=8;}
  if(pipe==7){dst=c->buffers[12].address;nd=8;}
  QcaCeHw*h=&c->bus->engines[pipe];
  if(qca_ce_hw_configure(h,src,ns,dst,nd,capacity[ring])
   ||qca_ce_seed(&c->rings[ring],receive[ring]?h->dst_index:h->src_index))return fail(c,3);
  if(pipe==7&&qca_ce_seed(&c->rings[6],h->dst_index))return fail(c,3);
 }
 c->phase=QCA_CHANNEL_CONFIGURED;
 if(qca_channels_prepared(c))return fail(c,4);
 return 0;
}
int qca_channels_reconfigure(QcaChannels*c){
 if(!c||(c->phase!=QCA_CHANNEL_CONFIGURED&&c->phase!=QCA_CHANNEL_POSTED)
  ||mappings_ready(c)||qca_ce_bus_released(c->bus))return -1;
 for(unsigned i=0;i<7;i++)if(qca_ce_close(&c->rings[i]))return fail(c,7);
 c->phase=QCA_CHANNEL_READY;return qca_channels_configure(c);
}
int qca_channels_post_receive(QcaChannels*c){
 if(!c||c->phase!=QCA_CHANNEL_CONFIGURED||qca_channels_prepared(c)||c->bus->phase!=QCA_BUS_ACTIVE||!c->bus->owned)return -1;
 for(unsigned i=1;i<=2;i++)
  if(qca_ce_post(&c->rings[i],c->buffers[2*i+1].address,capacity[i],i,0,0))return fail(c,5);
 c->phase=QCA_CHANNEL_POSTED;return 0;
}
int qca_channels_close_step(QcaChannels*c){
 if(!c||!c->bus||qca_ce_bus_released(c->bus))return -1;
 if(c->phase==QCA_CHANNEL_CLOSED)return 1;
 c->phase=QCA_CHANNEL_CLOSING;
 for(unsigned i=0;i<7;i++)if(qca_ce_close(&c->rings[i]))return -1;
 if(c->cleanup_slot<14){
  if(qca_dma_close(&c->buffers[c->cleanup_slot]))return -1;
  c->cleanup_slot++;return 0;
 }
 /* Access slots are safe to clear only after every registered buffer closed. */
 for(unsigned i=0;i<c->bus->access->count;i++)c->bus->access->buffers[i]=0;
 c->bus->access->count=0;c->phase=QCA_CHANNEL_CLOSED;return 1;
}
