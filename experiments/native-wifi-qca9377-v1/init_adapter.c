/* Native adapter for retained full-channel QCA9377 warm reset and recovery. */
#include "init_adapter.h"
#include "pci_identity.h"
#include "power_core.h"
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
static void*method(QcaInitAdapter*a,unsigned off){return *(void**)((uint8_t*)a->mapped.irq->port->pci+off);}
static int warm_guard(void*c){return qca_mapped_irq_guard(&((QcaInitAdapter*)c)->mapped);}
static int warm_read(void*c,uint32_t address,uint32_t*out){
 QcaInitAdapter*a=c;
 if(!out||!a->warm.owned||(address!=0x800&&address!=0x850&&address!=0x3a028)||warm_guard(a))return -1;
 if(address==0x3a028&&qca_mapped_irq_poll(&a->mapped))return -1;
 return ((Memory)method(a,16))(a->mapped.irq->port->pci,2,0,address,1,out)?-1:0;
}
static int warm_write(void*c,uint32_t address,uint32_t value){
 QcaInitAdapter*a=c;
 if(!a->warm.owned||(address!=0x800&&address!=0x850&&address!=0x3a028)||warm_guard(a))return -1;
 if(address==0x3a028&&value)return -1;
 return ((Memory)method(a,24))(a->mapped.irq->port->pci,2,0,address,1,&value)?-1:0;
}
static int warm_pipes(void*c){
 QcaInitAdapter*a=c;
 if(!a->pipes_phase){
  if(qca_ce_bus_stop_begin(&a->bus,a->last))return -1;
  a->pipes_phase=1;return 0;
 }
 int rc=qca_ce_bus_stop_poll(&a->bus,a->last);
 if(rc<=0)return rc;
 rc=a->channels.phase==QCA_CHANNEL_READY?qca_channels_configure(&a->channels):qca_channels_reconfigure(&a->channels);
 if(rc)return -1;
 a->pipes_phase=0;return 1;
}
static int cold_read(void*c,uint32_t address,uint32_t*out){
 QcaInitAdapter*a=c;
 if(address!=0x80008||!out||qca_mapped_irq_pci_guard(&a->mapped))return -1;
 return ((Memory)method(a,16))(a->mapped.irq->port->pci,2,0,address,1,out)?-1:0;
}
static int cold_write(void*c,uint32_t address,uint32_t value){
 QcaInitAdapter*a=c;
 if(address!=0x80008||!a->recovery.owned||(value!=a->recovery.original&&value!=(a->recovery.original|1))
  ||qca_mapped_irq_pci_guard(&a->mapped))return -1;
 return ((Memory)method(a,24))(a->mapped.irq->port->pci,2,0,address,1,&value)?-1:0;
}
static void error(QcaInitAdapter*a,unsigned e){if(!a->error)a->error=e;a->cancelled=1;}
static int retain(QcaInitAdapter*a,unsigned e){error(a,e);a->phase=QCA_INIT_RETAINED;return -1;}
static void cleanup(QcaInitAdapter*a){a->phase=QCA_INIT_CLEANUP_STOP;a->stop_started=0;a->retries=0;}
static int initial_snapshot(QcaInitAdapter*a){
 QcaBootIrq*q=a->mapped.irq;QcaUefiPort*p=q->port;
 if(!p->pci||!p->claimed||!p->validated||!p->memory_ready||!p->wake_owned||!p->link_owned||!p->boot_irq_owned)return -1;
 uint32_t config[64]={0};uint8_t power[16];QcaPciIdentity id;
 if(((Config)method(a,48))(p->pci,2,0,64,config))return -1;
 qca_power_decode((const uint8_t*)config,power);
 if(qca_pci_identity(config,&id)||id.bar0!=a->mapped.bar||id.subsystem_vendor!=0x1028||id.subsystem_device!=0x1810||id.revision!=0x31
  ||id.command!=(uint16_t)(q->original_command|0x400)||!(id.command&2)||(id.command&4)||power[8]!=1||(power[2]&3)
  ||!power[4]||((power[4]|((unsigned)power[5]<<8))+0x10)!=a->mapped.link_offset||(power[6]&3))return -1;
 uint32_t state=0,chip=0,indicator=0;
 if(((Memory)method(a,16))(p->pci,2,0,0x80000,1,&state)||(state&7)!=3
  ||((Memory)method(a,16))(p->pci,2,0,0x8f0,1,&chip)||chip!=0x003821ff
  ||((Memory)method(a,16))(p->pci,2,0,0x3a028,1,&indicator)||indicator==UINT32_MAX||(indicator&3)!=2)return -1;
 return 0;
}
int qca_init_adapter_begin(QcaInitAdapter*a,QcaBootIrq*q,uint64_t bar,unsigned offset,uint64_t now){
 if(!a||a->phase||!q||!q->port||!q->owned||q->port->dma_users||q->port->bar_extent<0x8000c||!bar||offset<0x50||offset>0xfc
  ||(offset&3)||now>UINT64_MAX-20000000)return -1;
 a->mapped=(QcaMappedIrq){.irq=q,.channels=&a->channels,.bar=bar,.link_offset=(uint16_t)offset};
 a->last=now;
 if(initial_snapshot(a)||qca_boot_irq_poll(q)||qca_ce_access_init(&a->access,q->port,255)||qca_ce_bus_init(&a->bus,&a->access))return -1;
 a->phase=QCA_INIT_STOP;
 if(qca_ce_bus_stop_begin(&a->bus,now)){error(a,0x101);cleanup(a);return -1;}
 return 0;
}
void qca_init_adapter_cancel(QcaInitAdapter*a){if(a&&a->phase&&a->phase!=QCA_INIT_CLOSED){error(a,0x100);qca_warm_cancel(&a->warm);}}
int qca_init_adapter_close(QcaInitAdapter*a){
 if(!a||a->phase!=QCA_INIT_READY||a->warm.owned||a->recovery.owned)return -1;
 a->cancelled=1;return 0;
}
int qca_init_adapter_released(const QcaInitAdapter*a){
 if(!a||a->phase!=QCA_INIT_CLOSED||a->warm.owned||a->recovery.owned||a->bus.owned)return 0;
 for(unsigned i=0;i<14;i++)if(a->channels.buffers[i].mapped||a->channels.buffers[i].allocated)return 0;
 return 1;
}
int qca_init_adapter_poll(QcaInitAdapter*a,uint64_t now){
 if(!a||!a->phase)return -1;
 if(a->phase==QCA_INIT_CLOSED)return a->error?-1:0;
 if(a->phase==QCA_INIT_RETAINED)return -1;
 if(now<a->last)return retain(a,0x102);
 a->last=now;
 if(a->phase==QCA_INIT_READY){
  if(qca_channels_prepared(&a->channels)||qca_mapped_irq_guard(&a->mapped))error(a,0x401);
  if(a->cancelled)cleanup(a);else return 1;
 }
 if(a->cancelled&&(a->phase==QCA_INIT_STOP||a->phase==QCA_INIT_ALLOCATE))cleanup(a);
 switch(a->phase){
 case QCA_INIT_STOP:{
  int rc=qca_ce_bus_stop_poll(&a->bus,now);
  if(rc<0){error(a,0x200|a->bus.error);cleanup(a);}
  else if(rc>0){
   if(qca_channels_begin(&a->channels,&a->bus)){error(a,0x201);cleanup(a);}
   else a->phase=QCA_INIT_ALLOCATE;
  }
  break;
 }
 case QCA_INIT_ALLOCATE:{
  if(initial_snapshot(a)){error(a,0x302);cleanup(a);break;}
  int rc=qca_channels_prepare_step(&a->channels);
  if(rc<0){error(a,0x300|a->channels.error);cleanup(a);}
  else if(rc>0){
   if(qca_warm_begin(&a->warm,warm_read,warm_write,warm_guard,warm_pipes,a,now)){
    error(a,0x301);if(a->warm.owned)a->phase=QCA_INIT_RELEASE_CE;else cleanup(a);
   }else a->phase=QCA_INIT_WARM;
  }
  break;
 }
 case QCA_INIT_WARM:{
  if(a->cancelled)qca_warm_cancel(&a->warm);
  int rc=qca_warm_poll(&a->warm,now);
  if(rc<0){error(a,0x400|a->warm.error);a->phase=QCA_INIT_RELEASE_CE;a->retries=0;}
  else if(rc>0){
   if(qca_channels_prepared(&a->channels)){error(a,0x401);cleanup(a);}
   else a->phase=QCA_INIT_READY;
  }
  break;
 }
 case QCA_INIT_RELEASE_CE:
  if(a->warm.ce_owned){
   if(now-a->warm.operation<10000)break;
   (void)qca_warm_recover_ce(&a->warm,now);
   if(a->warm.ce_owned){if(++a->retries>=3)return retain(a,0x501);break;}
  }
  a->phase=QCA_INIT_QUIESCE;a->retries=0;break;
 case QCA_INIT_QUIESCE:
  if(qca_mapped_irq_quiesce(&a->mapped)){if(++a->retries>=3)return retain(a,0x502);break;}
  a->phase=QCA_INIT_RECOVERY_STOP;a->stop_started=0;a->retries=0;break;
 case QCA_INIT_RECOVERY_STOP:case QCA_INIT_CLEANUP_STOP:{
  if(!a->stop_started){if(qca_ce_bus_stop_begin(&a->bus,now)){if(++a->retries>=3)return retain(a,0x503);break;}a->stop_started=1;break;}
  int rc=qca_ce_bus_stop_poll(&a->bus,now);
  if(rc<0){a->stop_started=0;if(++a->retries>=3)return retain(a,0x504);break;}
  if(!rc)break;
  if(a->phase==QCA_INIT_CLEANUP_STOP){a->phase=QCA_INIT_CLEANUP;a->retries=0;break;}
  const QcaResetTarget target={0x80008,20000,1000000};
  if(qca_reset_begin(&a->recovery,&target,cold_read,cold_write,a,now)){
   if(!a->recovery.owned)return retain(a,0x505);
  }
  a->phase=QCA_INIT_COLD;a->retries=0;break;
 }
 case QCA_INIT_COLD:{
  int rc=qca_reset_poll(&a->recovery,now);
  if(a->recovery.phase==QCA_RESET_FAULT){
   if(a->retries++>=1||qca_reset_recover(&a->recovery,now))return retain(a,0x506);
  }
  if(!a->recovery.owned){
   /* Deassertion with an earlier error is not a successful recovery proof. */
   if(rc<0||a->recovery.error||qca_mapped_irq_guard(&a->mapped))return retain(a,0x507);
   a->phase=QCA_INIT_ROM_RECOVERY;a->rom_started=a->next_rom=now;
  }
  break;
 }
 case QCA_INIT_ROM_RECOVERY:{
  if(now-a->rom_started>=3000000)return retain(a,0x508);
  if(now<a->next_rom)break;
  a->next_rom=now+10000;
  if(qca_mapped_irq_poll(&a->mapped)||((Memory)method(a,16))(a->mapped.irq->port->pci,2,0,0x3a028,1,&a->recovery_indicator)
   ||a->recovery_indicator==UINT32_MAX||(a->recovery_indicator&1))return retain(a,0x509);
  if(a->recovery_indicator&2){
   if(qca_mapped_irq_quiesce(&a->mapped)||qca_ce_bus_released(&a->bus))return retain(a,0x50a);
   /* Clear warm ownership ONLY under verified cold deassert/ROM/PCI/BM-off/
    * all-eight-stop proof. No exposed mappings have been released yet. */
   a->recovery_verified=1;a->warm.owned=0;cleanup(a);
  }
  break;
 }
 case QCA_INIT_CLEANUP:
  if(a->warm.owned||a->recovery.owned)return retain(a,0x50b);
  if(!a->channels.bus){
   if(a->mapped.irq->port->dma_users||qca_ce_bus_released(&a->bus))return retain(a,0x50c);
   a->phase=QCA_INIT_CLOSED;break;
  }
  {
  int rc=qca_channels_close_step(&a->channels);
  if(rc<0){if(++a->retries>=3)return retain(a,0x600);}
  else{a->retries=0;if(rc>0)a->phase=QCA_INIT_CLOSED;}
  }
  break;
 default:return retain(a,0x700);
 }
 return a->phase==QCA_INIT_READY?1:a->phase==QCA_INIT_RETAINED?-1:0;
}
