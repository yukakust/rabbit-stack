#include "persistent.h"
#include <stdatomic.h>
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
static QcaInitAdapter*adapter(QcaPersistentNative*s){return s->startup->operating->boot->board->setup->read.full.adapter;}
static int ready(QcaWmiStartup*w){return w&&w->phase==2&&!w->error&&w->transaction.phase==QCA_INIT_RUNNING
 &&w->transaction.ready_seen&&w->transaction.tx_complete&&!w->tx_posted;}
static int active(QcaPersistentNative*s,uint64_t now){
 QcaWmiStartup*w=s->startup;QcaInitAdapter*a=adapter(s);
 if(!ready(w))return -1;
 if(qca_operating_poll(w->operating,now)!=1)return -2;
 if(qca_channels_retained(&a->channels))return -3;
 /* Existing operating guard proves BMI0/1 and CE2. Explicitly include WMI3,
  * HTT4 and both CE7 directions, which use native channel routes. */
 static const uint8_t pipes[7]={0,1,2,3,4,7,7};
 for(unsigned i=3;i<7;i++){
  QcaCeRing*r=&a->channels.rings[i];QcaCeHw*h=&a->bus.engines[pipes[i]];
  QcaChannelRoute*t=&a->channels.routes[i];unsigned rx=i==6;uint32_t base=0,count=0;
  if(i<5){
   if(r->context!=t||t->bus!=&a->bus||t->pipe!=pipes[i]||t->receive!=rx
    ||r->publish!=a->channels.rings[4].publish||r->stop!=a->channels.rings[4].stop)return -(int)(10+i);
  }else{
   QcaDiagPipe*d=&w->operating->boot->board->setup->read.full.routes[i-5];
   if(r->context!=d||d->bus!=&a->bus||d->receive!=rx
    ||r->publish!=qca_diag_publish||r->stop!=qca_diag_stop)return -(int)(10+i);
  }
  if(!r->owned||r->fault||r->entries!=8||r->receive!=rx||r->descriptors!=a->channels.buffers[2*i].host
   ||!r->publish||!r->stop
   ||h->phase!=QCA_CE_HW_RUNNING||qca_ce_access_read(&a->access,h->base+(rx?8:0),&base)
   ||qca_ce_access_read(&a->access,h->base+(rx?12:4),&count)||base!=a->channels.buffers[2*i].address||count!=8)return -(int)(10+i);
 }
 return 0;
}
static int snapshot(QcaPersistentNative*s,QcaRadioOwners*o){
 QcaInitAdapter*a=adapter(s);QcaBootNative*b=s->startup->operating->boot;
 QcaUefiPort*p=a->mapped.irq->port;
 *o=(QcaRadioOwners){0};o->epoch=s->epoch;o->dma_users=p->dma_users;
 o->pci=p->claimed;o->wake=p->wake_owned;o->link=p->link_owned;o->irq=p->boot_irq_owned;
 o->pin=b->owns_pin;o->init_ready=ready(s->startup);
 /* bus here is retained adapter lifetime, not the hardware BME flag. */
 o->bus=!qca_init_adapter_released(a);
 for(unsigned i=0;i<14;i++){
  QcaDmaBuffer*d=&a->channels.buffers[i];
  if(d->allocated||d->mapped||d->allocation_uncertain)o->mappings++;
 }
 if(p->claimed){
  if(!p->pci)return -1;
  Config read=*(Config*)((uint8_t*)p->pci+48);uint16_t command=0;
  if(!read||read(p->pci,1,4,1,&command))return -1;
  o->bus_master=!!(command&4);
  if(a->bus.phase==QCA_BUS_OFF&&!a->bus.owned){
   Memory mem=*(Memory*)((uint8_t*)p->pci+16);uint32_t enable=0,cause=0;
   if(qca_ce_bus_released(&a->bus)||!mem||mem(p->pci,2,0,0x3a008,1,&enable)||enable
    ||mem(p->pci,2,0,0x3a00c,1,&cause)||(cause&0x7fc00))return -1;
   atomic_thread_fence(memory_order_acquire);s->stop_latched=1;
  }
 }
 if(!p->claimed&&(o->mappings||o->dma_users||o->wake||o->link||o->irq||o->pin||o->bus))return -1;
 o->stop_verified=s->stop_latched;
 return 0;
}
int qca_persistent_begin(QcaPersistentNative*s,QcaWmiStartup*w,uint64_t epoch,uint64_t now){
 if(!s||s->life.phase||!epoch||!ready(w)||!w->operating||!w->operating->boot)return -1;
 s->startup=w;s->epoch=epoch;s->polls=0;s->error=0;s->stop_latched=0;
 QcaRadioOwners o;
 int rc=active(s,now);if(rc){s->error=(uint32_t)-rc;return -1;}
 if(snapshot(s,&o)){s->error=30;return -1;}
 if(!qca_radio_begin(&s->life,&o,now)){s->error=31;return -1;}
 return 1;
}
int qca_persistent_poll(QcaPersistentNative*s,uint64_t now){
 if(!s||!s->life.phase)return 0;
 if(s->life.phase==QCA_RADIO_CLOSED)return 0;
 if(s->life.phase==QCA_RADIO_RETAINED)return -1;
 QcaRadioOwners o;
 if((s->life.phase==QCA_RADIO_ACTIVE&&active(s,now))||snapshot(s,&o)){
  (void)qca_radio_observe(&s->life,0,now);return -1;
 }
 if(!qca_radio_observe(&s->life,&o,now))return -1;
 if(s->polls!=UINT32_MAX)s->polls++;
 return qca_radio_accepts_work(&s->life)?1:0;
}
int qca_persistent_quiesce(QcaPersistentNative*s,uint64_t now){
 if(!s||!s->life.phase)return 0;
 if(s->life.phase==QCA_RADIO_ACTIVE)return qca_radio_quiesce(&s->life,now,10000000)?0:-1;
 return s->life.phase==QCA_RADIO_RETAINED?-1:0;
}
int qca_persistent_unload_safe(const QcaPersistentNative*s){return s&&qca_radio_can_unload(&s->life);}
