#include "stop.h"
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
typedef Status(EFIAPI *Flush)(void*);
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
static int apart(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return a&&b&&x<=UINTPTR_MAX-n&&y<=UINTPTR_MAX-m&&(x+n<=y||y+m<=x);}
static void*method(QcaHttWarmStop*s,unsigned offset){return *(void**)((uint8_t*)s->data->runtime->port->pci+offset);}
static int fail(QcaHttWarmStop*s,unsigned error){if(!s->error)s->error=error;s->phase=QSTOP_RETAINED;qca_warm_cancel(&s->warm);return -1;}
static int bound(QcaHttWarmStop*s){
 if(!s||!s->data||!s->adapter||!s->epoch)return -1;
 QcaHttDataPath*d=s->data;QcaHttRuntime*r=d->runtime;QcaPersistentNative*p=d->radio;
 if(!r||!p||r->epoch!=s->epoch||p->epoch!=s->epoch||d->epoch!=s->epoch||d->phase!=QDP_QUARANTINED||p->htt_owner||qca_radio_accepts_work(&p->life)||p->life.phase==QCA_RADIO_ACTIVE||r->allocated!=33||r->cleanup||r->ce!=s->adapter->channels.buffers||r->port!=s->adapter->mapped.irq->port||s->adapter->channels.bus!=&s->adapter->bus||s->adapter->bus.access!=&s->adapter->access||s->adapter->access.count!=14||!qca_htt_runtime_inventory(r)||r->port->dma_users!=47)return -1;
 return 0;
}
static int warm_guard(void*c){QcaHttWarmStop*s=c;return bound(s)||qca_mapped_irq_guard(&s->adapter->mapped)?-1:0;}
static int read32(void*c,uint32_t address,uint32_t*out){
 QcaHttWarmStop*s=c;
 if(!out||!s->warm.owned||(address!=0x800&&address!=0x850&&address!=0x3a028)||warm_guard(s))return -1;
 if(address==0x3a028&&qca_mapped_irq_poll(&s->adapter->mapped))return -1;
 return ((Memory)method(s,16))(s->data->runtime->port->pci,2,0,address,1,out)?-1:0;
}
static int write32(void*c,uint32_t address,uint32_t value){
 QcaHttWarmStop*s=c;
 if(!s->warm.owned||(address!=0x800&&address!=0x850&&address!=0x3a028)||warm_guard(s))return -1;
 if(address==0x3a028&&value)return -1;
 int cpu_request=address==0x800&&(s->warm.phase==QCA_WARM_CPU_FIRST||s->warm.phase==QCA_WARM_CPU_SECOND);
 if(cpu_request){
  /* A fresh actual FW_IND clear precedes each CPU-reset request. */
  uint32_t indicator=UINT32_MAX;
  if(!(value&0x40)||(value&1)||s->clear_readbacks!=s->cpu_writes+1||((Memory)method(s,16))(s->data->runtime->port->pci,2,0,0x3a028,1,&indicator)||indicator)return -1;
 }
 if(((Memory)method(s,24))(s->data->runtime->port->pci,2,0,address,1,&value))return -1;
 if(address==0x3a028){uint32_t observed=UINT32_MAX;if(((Memory)method(s,16))(s->data->runtime->port->pci,2,0,address,1,&observed)||observed)return -1;s->clear_readbacks++;}
 else if(cpu_request)s->cpu_writes++;
 return 0;
}
static int pipes(void*c){
 QcaHttWarmStop*s=c;QcaInitAdapter*a=s->adapter;
 if(!s->pipe_phase){if(qca_ce_bus_stop_begin(&a->bus,s->last))return -1;s->pipe_phase=1;return 0;}
 int rc=qca_ce_bus_stop_poll(&a->bus,s->last);if(rc<=0)return rc;
 if(qca_channels_reconfigure(&a->channels))return -1;
 s->pipe_phase=0;return 1;
}
int qstop_begin(QcaHttWarmStop*s,QcaHttDataPath*d,uint64_t now){
 if(!s||!d||!d->runtime||!d->radio||!now||now>UINT64_MAX-9000000||(d->phase!=QDP_RX_ACTIVE&&d->phase!=QDP_QUARANTINED)||d->radio->htt_owner!=d||d->epoch!=d->runtime->epoch||d->epoch!=d->radio->epoch||!qca_htt_runtime_inventory(d->runtime)||d->runtime->port->dma_users!=47||!d->runtime->ring.cfg_posted||d->runtime->callback_owners!=1||!d->radio->startup||!d->radio->startup->operating||!d->radio->startup->operating->boot||!d->radio->startup->operating->boot->board||!d->radio->startup->operating->boot->board->setup)return -1;
 if(!apart(s,sizeof(*s),d,sizeof(*d))||!apart(s,sizeof(*s),d->runtime,sizeof(*d->runtime))||!apart(s,sizeof(*s),d->radio,sizeof(*d->radio)))return -1;
 for(unsigned j=0;j<sizeof(*s);j++)if(((const uint8_t*)s)[j])return -1;
 QcaInitAdapter*a=d->radio->startup->operating->boot->board->setup->read.full.adapter;
 if(!a||d->runtime->ce!=a->channels.buffers||d->runtime->port!=a->mapped.irq->port)return -1;
 if(!apart(s,sizeof(*s),a,sizeof(*a)))return -1;
 for(unsigned j=0;j<47;j++){QcaDmaBuffer*m=j<14?&d->runtime->ce[j]:&d->runtime->extra[j-14];if(m->bytes>UINT32_MAX||!apart(s,sizeof(*s),m->host,(unsigned)m->bytes))return -1;}
 QcaHttWarmStop v={0};v.data=d;v.adapter=a;v.epoch=d->epoch;v.started=v.last=now;v.deadline=now+9000000;*s=v;
 qdp_quarantine(d,200);d->radio->htt_owner=0;
 uint16_t command=0;if(((Config)method(s,48))(d->runtime->port->pci,1,4,1,&command)||((command&4)?qca_mapped_irq_active_guard(&a->mapped):qca_mapped_irq_guard(&a->mapped)))return fail(s,15);
 if(bound(s)||qca_ce_bus_stop_begin(&a->bus,now))return fail(s,1);
 s->phase=QSTOP_CE_WAIT;return 0;
}
int qstop_poll(QcaHttWarmStop*s,uint64_t now){
 if(!s||!s->phase)return -1;if(s->phase==QSTOP_PROVEN)return 1;if(s->phase==QSTOP_RETAINED)return -1;
 if(now<s->last||now>=s->deadline)return fail(s,2);s->last=now;
 if(bound(s))return fail(s,3);
 switch(s->phase){
 case QSTOP_CE_WAIT:{int rc=qca_ce_bus_stop_poll(&s->adapter->bus,now);if(rc<0)return fail(s,4);if(!rc)return 0;
  if(qca_mapped_irq_quiesce(&s->adapter->mapped)||qca_warm_begin(&s->warm,read32,write32,warm_guard,pipes,s,now))return fail(s,5);s->phase=QSTOP_WARM;return 0;}
 case QSTOP_WARM:{int rc=qca_warm_poll(&s->warm,now);if(rc<0)return fail(s,6);if(!rc)return 0;
  if(s->warm.cpu_resets!=2||s->warm.pipe_inits!=2||s->warm.ce_owned||s->warm.owned||s->clear_readbacks!=2||s->cpu_writes!=2||(s->warm.indicator&3)!=2)return fail(s,7);
  if(qca_ce_bus_stop_begin(&s->adapter->bus,now))return fail(s,8);s->phase=QSTOP_FINAL_CE;return 0;}
 case QSTOP_FINAL_CE:{int rc=qca_ce_bus_stop_poll(&s->adapter->bus,now);if(rc<0)return fail(s,9);if(!rc)return 0;s->phase=QSTOP_FENCE;return 0;}
 case QSTOP_FENCE:{
  if(qca_ce_bus_released(&s->adapter->bus)||qca_mapped_irq_quiesce(&s->adapter->mapped)||((Flush)method(s,104))(s->data->runtime->port->pci)||qca_ce_bus_released(&s->adapter->bus)||qca_mapped_irq_guard(&s->adapter->mapped))return fail(s,10);
  __atomic_thread_fence(__ATOMIC_SEQ_CST);
  uint32_t rom=UINT32_MAX;if(((Memory)method(s,16))(s->data->runtime->port->pci,2,0,0x3a028,1,&rom)||(rom&3)!=2)return fail(s,11);
  QcaHttRuntime*r=s->data->runtime;s->completion=now;
  /* Actual selector/admission revoked before reset, actual target reset/CE/IRQ/
   * BME/Flush complete before callbacks and pending ownership are detached. */
  if(s->data->radio->htt_owner||qca_radio_accepts_work(&s->data->radio->life))return fail(s,12);
  QRingQuiesceProof proof={s->epoch,s->completion,1,1,1,1};if(qca_ring_quiesce(&r->ring,&proof))return fail(s,13);
  r->callback_owners=r->rx_copy_owners=r->tx_owners=0;s->data->rx.owners=0;s->data->phase=QDP_QUIESCED;
  /* Published ACTIVE runtime can leave that phase only after this actual
   * target-stop/CE/IRQ/BME/Flush proof, never from a caller Boolean. */
  if(r->phase!=HTT_RUNTIME_MAPPED&&r->phase!=HTT_RUNTIME_ACTIVE)return fail(s,16);
  r->phase=HTT_RUNTIME_CLOSING;
  s->phase=QSTOP_PROVEN;return 1;}
 default:return fail(s,14);
 }
}
int qstop_recover_ce(QcaHttWarmStop*s,uint64_t now){
 if(!s||s->phase!=QSTOP_RETAINED||!s->warm.ce_owned||s->recovery_calls>=3||now<s->last)return -1;
 s->last=now;if(now-s->warm.operation<10000)return 0;s->recovery_calls++;
 return qca_warm_recover_ce(&s->warm,now);
}
int qstop_release_guard(QcaHttWarmStop*s){
 if(!s||s->phase!=QSTOP_PROVEN||!s->completion||s->warm.owned||s->warm.ce_owned||s->data->phase!=QDP_QUIESCED||s->data->radio->htt_owner||s->data->rx.owners||(s->data->runtime->ring.phase!=Q_RING_QUIESCED&&s->data->runtime->ring.phase!=Q_RING_CLOSED)||s->data->runtime->callback_owners||s->data->runtime->rx_copy_owners||s->data->runtime->tx_owners)return -1;
 /* Constructor integration must supply the separately checked remaining-map
  * inventory during 47→14 cleanup; this guard grants no unmap/free itself. */
 return !qstop_remaining_inventory(s)||qca_ce_bus_released(&s->adapter->bus)||qca_mapped_irq_guard(&s->adapter->mapped)?-1:0;
}
int qstop_remaining_inventory(QcaHttWarmStop*s){
 if(!s||s->phase!=QSTOP_PROVEN||!s->data||!s->data->runtime||!s->adapter)return 0;
 QcaHttRuntime*r=s->data->runtime;QcaUefiPort*p=r->port;
 if(r->epoch!=s->epoch||r->allocated!=33||r->cleanup>33||r->ring.released_maps!=r->cleanup||(r->ring.phase!=Q_RING_QUIESCED&&!(r->ring.phase==Q_RING_CLOSED&&r->cleanup==33))||!p||!p->claimed||!p->validated||r->ce!=s->adapter->channels.buffers||r->callback_owners||r->rx_copy_owners||r->tx_owners)return 0;
 unsigned actual=0;
 for(unsigned j=0;j<47;j++){
  QcaDmaBuffer*d=j<14?&r->ce[j]:&r->extra[j-14];unsigned pages=j<14?1:j<46?16:3;
  if(d->port!=p||d->allocation_uncertain||d->pages!=pages||d->bytes!=(uint64_t)pages*4096)return 0;
  if(j>=14&&j-14<r->cleanup){if(d->allocated||d->mapped||d->host||d->mapping||d->valid||d->exposed||r->ring.map_released[j-14]!=1)return 0;continue;}
  if(d->allocated!=1||!d->host||d->address>UINT32_MAX-(d->bytes-1)||(d->address&4095))return 0;
  if(j<14||j-14>r->cleanup){if(d->mapped!=1||d->valid!=1||d->closing)return 0;}
  else if(d->mapped>1||(!d->mapped&&(d->mapping||d->valid))||(d->mapped&&d->valid!=1))return 0;
  if(j>=14){QRingMap*m=&r->maps[j-14];if(m->identity!=(uintptr_t)d||m->epoch!=s->epoch||m->paddr!=d->address||m->bytes!=d->bytes||m->actual_map_valid!=1||m->coherent_common!=1||m->allocated_masteroff!=1||r->ring.map_released[j-14])return 0;}
  actual++;
 }
 return actual==p->dma_users&&actual==14+33-r->cleanup;
}
int qstop_close_extra_one(QcaHttWarmStop*s){
 if(!s||qstop_release_guard(s))return -1;
 QcaHttRuntime*r=s->data->runtime;unsigned before=r->cleanup;
 if(!qca_htt_runtime_close_one(r))return -1;
 if(r->cleanup==before+1){if(qca_ring_map_released(&r->ring,r->maps[before].identity,s->epoch,1))return -1;}
 else if(r->cleanup!=before||before!=33)return -1;
 return qstop_remaining_inventory(s)?(r->phase==HTT_RUNTIME_CLOSED?1:0):-1;
}
