#include "owner47.h"
static int valid(const QcaRadioOwners*o){
 return o&&o->epoch&&o->mappings<=47&&o->dma_users<=47&&o->pci<=1&&o->wake<=1
 &&o->link<=1&&o->irq<=1&&o->pin<=1&&o->bus<=1&&o->bus_master<=1
 &&o->init_ready<=1&&o->stop_verified<=1;
}
static int full(const QcaRadioOwners*o){
 return o->mappings==47&&o->dma_users==47&&o->pci&&o->wake&&o->link&&o->irq
 &&o->pin&&o->bus&&o->bus_master&&o->init_ready&&!o->stop_verified;
}
static int empty(const QcaRadioOwners*o){
 return !o->mappings&&!o->dma_users&&!o->pci&&!o->wake&&!o->link&&!o->irq
 &&!o->pin&&!o->bus&&!o->bus_master;
}
static int stopped(const QcaRadioOwners*o){return o->stop_verified&&!o->bus_master;}
static int decrease(const QcaRadioOwners*a,const QcaRadioOwners*b){
 return b->mappings<=a->mappings&&b->dma_users<=a->dma_users&&b->pci<=a->pci
 &&b->wake<=a->wake&&b->link<=a->link&&b->irq<=a->irq&&b->pin<=a->pin
 &&b->bus<=a->bus&&!b->bus_master;
}
static int fail(QcaRadioLifecycle*s,uint32_t error){s->phase=QCA_RADIO_RETAINED;s->error=error;return 0;}
int qca_radio47_begin(QcaRadioLifecycle*s,const QcaRadioOwners*o,uint64_t now){
 if(!s||s->phase||!valid(o)||!full(o))return 0;
 /* Snapshot may be embedded in caller storage: copy before assigning. */
 QcaRadioOwners copy=*o;
 s->owners=copy;s->last=now;s->deadline=0;s->error=0;s->phase=QCA_RADIO_ACTIVE;return 1;
}
int qca_radio47_observe(QcaRadioLifecycle*s,const QcaRadioOwners*o,uint64_t now){
 if(!s||!s->phase)return 0;
 if(s->phase==QCA_RADIO_CLOSED||s->phase==QCA_RADIO_RETAINED)return 0;
 if(!valid(o)||o->epoch!=s->owners.epoch)return fail(s,QCA_RADIO_OWNERS);
 if(now<s->last)return fail(s,QCA_RADIO_CLOCK);
 s->last=now;
 if(s->phase==QCA_RADIO_ACTIVE){
  if(!full(o))return fail(s,QCA_RADIO_OWNERS);
  s->owners=*o;return 1;
 }
 if(now>=s->deadline)return fail(s,QCA_RADIO_TIMEOUT);
 if(s->phase==QCA_RADIO_QUIESCING){
  /* No releases before actual stop; bus/PCI/pin/mappings stay retained. */
  if(o->mappings!=47||o->dma_users!=47||!o->pci||!o->wake||!o->link||!o->irq||!o->pin||!o->bus)
   return fail(s,QCA_RADIO_OWNERS);
  s->owners=*o;
  if(stopped(o))s->phase=QCA_RADIO_RELEASING;
  return 1;
 }
 if(s->phase!=QCA_RADIO_RELEASING||!stopped(o)||!decrease(&s->owners,o))return fail(s,QCA_RADIO_OWNERS);
 /* Nested DMA/map/bus owners must close before pin or PCI/link/wake/IRQ.
  * A single snapshot may show several successful releases. */
 if((o->mappings||o->dma_users||o->bus)&&(!o->pci||!o->wake||!o->link||!o->irq||!o->pin))
  return fail(s,QCA_RADIO_OWNERS);
 if(o->dma_users&&!o->mappings)return fail(s,QCA_RADIO_OWNERS);
 if(!o->pci&&(o->wake||o->link||o->irq||o->pin))return fail(s,QCA_RADIO_OWNERS);
 s->owners=*o;
 if(empty(o))s->phase=QCA_RADIO_CLOSED;
 return 1;
}
int qca_radio47_accepts_work(const QcaRadioLifecycle*s){return s&&s->phase==QCA_RADIO_ACTIVE&&full(&s->owners);}
int qca_radio47_quiesce(QcaRadioLifecycle*s,uint64_t now,uint64_t timeout){
 if(!s||s->phase!=QCA_RADIO_ACTIVE||!timeout||now>UINT64_MAX-timeout)return 0;
 if(now<s->last)return fail(s,QCA_RADIO_CLOCK);
 s->last=now;s->deadline=now+timeout;s->phase=QCA_RADIO_QUIESCING;return 1;
}
int qca_radio47_can_release(const QcaRadioLifecycle*s){return s&&s->phase==QCA_RADIO_RELEASING&&stopped(&s->owners);}
int qca_radio47_can_unload(const QcaRadioLifecycle*s){return s&&s->phase==QCA_RADIO_CLOSED&&empty(&s->owners)&&stopped(&s->owners);}
