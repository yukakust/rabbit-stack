/* One-shot reset/ROM/BMI query; no firmware upload or association. */
#include "bringup.h"
#include "pci_collect.h"
#include "pci_identity.h"
#include "power_core.h"
#include "uefi_port.h"
#include "reset_core.h"
#include "rom_ready.h"
#include "bmi_transport.h"
#include "pcie_link.h"
#include "diag_ce.h"
void*qca_image;
static QcaUefiPort port;static QcaWake wake;static QcaReset reset;
static uint32_t stage,failed,firmware,chip,revalidate_error,recoveries,cancelled,cleanup_attempts;
static uint16_t actual_command,pmcsr;
static uint64_t bar,last_now;
static QcaBootIrq boot_irq;static uint16_t post_reset_link;
static QcaPcieLink link;static uint16_t link_active;
static QcaRomReady rom;static QcaCeAccess access;static QcaCeBus bus;
static QcaDmaBuffer buffers[4];static QcaCeRing rings[2];static QcaBmiPipe pipes[2];static QcaBmiExchange exchange;
static uint8_t exchange_snapshot[76];static unsigned snapshot_latched;
static QcaDiagExchange diag;static QcaDiagPipe diag_pipes[2];
static uint8_t diag_snapshot[96];static unsigned diag_latched;
static uint8_t prehalt_snapshot[264];static unsigned prehalt_engine;
static unsigned bus_live,allocated,cleanup_slot,bus_retries,buffer_retries,succeeded;

static void record(unsigned off,uint64_t value,unsigned bytes){for(unsigned i=0;i<bytes;i++)qca_diagnostic[off+i]=(uint8_t)(value>>(8*i));}
static void telemetry(void){
 record(128,stage,4);record(132,chip,4);record(136,failed,4);record(140,port.claimed?2:1,4);
 record(144,port.bar_extent,8);record(152,port.original_attributes,8);
 record(160,reset.phase,4);record(164,reset.error,4);record(168,reset.owned,4);record(172,firmware,4);
 record(176,port.original_command,2);record(178,actual_command,2);record(180,pmcsr,2);
 record(184,reset.original,4);record(188,reset.readback,4);record(192,revalidate_error,4);
 record(196,rom.error,4);record(200,rom.indicator,4);record(204,exchange.error,4);
 record(208,exchange.version,4);record(212,exchange.type,4);record(216,exchange.info_length,4);
 record(220,port.dma_users,4);record(224,bus.phase,4);record(228,bus.error,4);record(232,bus.owned,4);
 uint32_t held=0;for(unsigned i=0;i<4;i++)if(buffers[i].allocated||buffers[i].mapped)held|=1u<<i;
 record(236,held,4);record(182,link_active,2);
 record(240,link.original,2);record(242,link.readback,2);record(244,link.owned,1);record(245,link.error,1);
 record(246,boot_irq.original_command,2);record(248,boot_irq.command_readback,2);
 record(250,boot_irq.owned,1);record(251,boot_irq.error,1);record(252,boot_irq.original_enable,4);
 record(256,boot_irq.last_enable,4);record(260,boot_irq.original_control,4);record(264,boot_irq.last_control,4);
 record(268,boot_irq.writes,4);record(272,post_reset_link,2);record(276,boot_irq.cause,4);
 for(unsigned i=0;i<sizeof(exchange_snapshot);i++)qca_diagnostic[280+i]=exchange_snapshot[i];
 for(unsigned i=0;i<sizeof(prehalt_snapshot);i++)qca_diagnostic[356+i]=prehalt_snapshot[i];
 for(unsigned i=0;i<sizeof(diag_snapshot);i++)qca_diagnostic[620+i]=diag_snapshot[i];
}
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
static void*method(unsigned offset){return *(void**)((uint8_t*)port.pci+offset);}
static int fresh(void){
 uint32_t c[64]={0};QcaPciIdentity id;uint8_t power[16];
 if(!port.claimed||!port.pci||((Config)method(48))(port.pci,2,0,64,c))return -1;
 qca_power_decode((const uint8_t*)c,power);pmcsr=(uint16_t)(power[2]|((uint16_t)power[3]<<8));actual_command=(uint16_t)c[1];
 if(qca_pci_identity(c,&id)||id.subsystem_vendor!=0x1028||id.subsystem_device!=0x1810||id.revision!=0x31
  ||(id.command&4)||power[8]!=1||(pmcsr&3))return -1;
 if(bar&&id.bar0!=bar)return -1;
 bar=id.bar0;return 0;
}
static int reset_read(void*context,uint32_t address,uint32_t*out){
 (void)context;if(!port.memory_ready||address!=0x80008||port.bar_extent<0x8000c)return -1;
 /* This callback after deassert executes only after the core's20ms window. */
 if(reset.phase==QCA_RESET_CLEAR_WAIT){
  if(fresh()){revalidate_error=1;return -1;}
  if(actual_command!=(uint16_t)(port.original_command|2)){
   if(actual_command!=(uint16_t)(port.original_command&~2u)){revalidate_error=2;return -1;}
   typedef Status(EFIAPI *Attributes)(void*,uint32_t,uint64_t,uint64_t*);
   if(((Attributes)method(120))(port.pci,2,0x200,0)||fresh()||actual_command!=(uint16_t)(port.original_command|2)){
    revalidate_error=3;return -1;
   }
  }
 }
 return ((Memory)method(16))(port.pci,2,0,address,1,out)?-1:0;
}
static int reset_write(void*context,uint32_t address,uint32_t value){
 (void)context;
 if(!port.memory_ready||address!=0x80008||port.bar_extent<0x8000c||!reset.owned
  ||(value!=reset.original&&value!=(reset.original|1)))return -1;
 return ((Memory)method(24))(port.pci,2,0,address,1,&value)?-1:0;
}
/* Snapshot only mapped, registered memory before any stop/unmap/free. No new
 * MMIO reads/writes: hardware indices come from the existing BMI polling path.
 * Keep this immutable during cleanup/retry and describe indices as last observed.
 */
static void snap_put(unsigned off,uint64_t value,unsigned bytes){
 for(unsigned i=0;i<bytes;i++)exchange_snapshot[off+i]=(uint8_t)(value>>(8*i));
}
static int snapshot_buffer(unsigned n,unsigned bytes){
 QcaDmaBuffer*d=&buffers[n];
 if(!d->host||!d->allocated||!d->mapped||!d->valid||d->closing||d->bytes<bytes)return 0;
 for(unsigned i=0;i<access.count;i++)if(access.buffers[i]==d)return 1;
 return 0;
}
static void snapshot_exchange(void){
 if(snapshot_latched||exchange.bus!=&bus)return;
 snapshot_latched=1;__atomic_thread_fence(__ATOMIC_ACQUIRE);unsigned flags=1|(exchange.tx_done?2u:0)|(exchange.rx_done?4u:0);
 snap_put(4,exchange.observed_mask,4);
 for(unsigned i=0;i<2;i++){
  snap_put(8+2*i,exchange.initial_index[i],2);snap_put(12+2*i,exchange.observed_index[i],2);
  snap_put(16+4*i,rings[i].read,2);snap_put(18+4*i,rings[i].write,2);
  /* Original posted slot, not a later advanced read index. */
  unsigned index=exchange.initial_index[i];
  if(rings[i].owned&&index<rings[i].entries&&snapshot_buffer(i,(index+1)*8)
    &&rings[i].descriptors==(volatile uint8_t*)buffers[i].host){
   flags|=1u<<(5+i);
   for(unsigned n=0;n<8;n++)exchange_snapshot[40+8*i+n]=rings[i].descriptors[index*8+n];
  }
 }
 if(snapshot_buffer(2,4)){
  flags|=8;snap_put(24,buffers[2].address,8);
  for(unsigned n=0;n<4;n++)exchange_snapshot[68+n]=((volatile uint8_t*)buffers[2].host)[n];
 }
 if(snapshot_buffer(3,12)){
  flags|=16;snap_put(32,buffers[3].address,8);
  for(unsigned n=0;n<12;n++)exchange_snapshot[56+n]=((volatile uint8_t*)buffers[3].host)[n];
 }
 snap_put(72,exchange.bytes,4);snap_put(0,flags,4);
}
/* Read only validated CE registers with bus mastering off, before any halt.
 * Raw addresses are diagnostic values, never dereferenced or adopted as DMA. */
static void snapshot_pre_halt(void){
 static const uint32_t offsets[8]={0,4,8,12,16,24,68,72};
 unsigned id=prehalt_engine;int valid=1;
 for(unsigned n=0;n<8;n++){
  uint32_t value=0;int rc=qca_ce_access_read(&access,0x34400+id*0x400+offsets[n],&value);
  if(rc||value==0xffffffffu)valid=0;
  for(unsigned k=0;k<4;k++)prehalt_snapshot[8+id*32+n*4+k]=(uint8_t)(value>>(8*k));
 }
 prehalt_snapshot[valid?0:4]|=(uint8_t)(1u<<id);prehalt_engine++;
}
static void diag_put(unsigned off,uint64_t value,unsigned bytes){
 for(unsigned i=0;i<bytes;i++)diag_snapshot[off+i]=(uint8_t)(value>>(8*i));
}
static void snapshot_diag(void){
 if(diag_latched||diag.bus!=&bus)return;
 diag_latched=1;__atomic_thread_fence(__ATOMIC_ACQUIRE);
 unsigned flags=1|(diag.tx_done?2u:0)|(diag.rx_done?4u:0);
 diag_put(0,diag.phase,4);diag_put(4,diag.error,4);
 diag_put(12,diag.target,4);diag_put(16,diag.ce_address,4);diag_put(20,diag.core,4);diag_put(24,diag.command,2);
 diag_put(26,diag.initial[0],2);diag_put(28,diag.initial[1],2);
 diag_put(30,diag.observed[0],2);diag_put(32,diag.observed[1],2);diag_put(34,diag.mask,2);
 for(unsigned i=0;i<2;i++){
  diag_put(36+4*i,rings[i].read,2);diag_put(38+4*i,rings[i].write,2);
  if(diag.initial[i]<8&&snapshot_buffer(i,(diag.initial[i]+1)*8))
   for(unsigned n=0;n<8;n++)diag_snapshot[52+8*i+n]=rings[i].descriptors[diag.initial[i]*8+n];
 }
 if(snapshot_buffer(3,4)){
  flags|=8;diag_put(44,buffers[3].address,8);
  for(unsigned n=0;n<4;n++)diag_snapshot[68+n]=((volatile uint8_t*)buffers[3].host)[n];
 }
 diag_put(72,diag.bytes,4);diag_put(8,flags,4);
 diag_put(80,diag.first_elapsed,4);diag_put(84,diag.last_elapsed,4);diag_put(88,diag.polls,4);diag_put(92,3000000,4);
}
static void shutdown(uint64_t now){
 if(bus_live){
  if(stage!=12){snapshot_diag();snapshot_exchange();stage=12;cleanup_slot=0;buffer_retries=0;qca_ce_bus_stop_begin(&bus,now);}
  return;
 }
 stage=succeeded?5:6;
 if(qca_boot_irq_close(&boot_irq)){succeeded=0;stage=6;if(!failed)failed=0xb00|boot_irq.error;return;}
 if(qca_pcie_restore(&link)){succeeded=0;stage=6;if(!failed)failed=0xa00|link.error;return;}
 if(qca_port_close(&port,&wake)&&!failed)failed=0x900;
}
int qca_stop(void){
 if(reset.owned){
  cancelled=1;
  if(reset.phase==QCA_RESET_FAULT)qca_reset_recover(&reset,reset.last_time);
  telemetry();return 1;
 }
 if(stage==7){telemetry();return 0;}
 if(stage==12){
  if(buffer_retries>=3)buffer_retries=0;
  if(bus.phase==QCA_BUS_FAULT&&bus_retries>=2){bus_retries=0;qca_ce_bus_stop_begin(&bus,last_now);}
 }
 if(stage!=5&&stage!=6&&stage!=12){cancelled=1;if(!failed)failed=0x103;}
 shutdown(last_now);telemetry();return port.claimed||port.dma_users||reset.owned;
}
void qca_start(SystemTable*st,uint64_t ms){
 if(stage){telemetry();return;}
 const QcaPciTarget t={0x1028,0x1810,0x31};const QcaWakeTarget w={0x80000,0x80004,0x8f0,3,1000000};
 if(!qca_controller||qca_diagnostic[4]!=15){stage=7;telemetry();return;}
 stage=1;last_now=ms*1000;
 if(qca_port_open(&port,st,qca_image,qca_controller,&t)||fresh()||port.bar_extent<0x8000c
  ||qca_pcie_pause(&link,&port)||qca_port_enable_memory(&port)||qca_wake_begin(&wake,&w,qca_port_read32,qca_port_write32,&port,ms*1000)){
  stage=6;failed=0x10000|port.error;qca_stop();
 }
 link_active=link.readback;telemetry();
}
void qca_poll(uint64_t ms){
 uint64_t now=ms*1000;last_now=now;
 if(stage==1){
  int rc=qca_wake_poll(&wake,now);
  if(rc){
   /* Zero chip-ID is inconclusive, but CHIP failure occurs after RTC ON. */
   if(rc<0&&(wake.error!=QCA_WAKE_CHIP||wake.chip_id)){failed=wake.error;stage=6;}
   else{
    const QcaResetTarget t={0x80008,20000,1000000};stage=2;
    if(qca_reset_begin(&reset,&t,reset_read,reset_write,0,now)){failed=0x200|reset.error;if(!reset.owned)stage=6;}
   }
  }
 }
 else if(stage==2){
  int rc=qca_reset_poll(&reset,now);
  if(reset.phase==QCA_RESET_FAULT&&recoveries<1){recoveries++;qca_reset_recover(&reset,now);}
  if(!reset.owned){
   if(cancelled||rc<0||fresh()){failed=0x300|reset.error;stage=6;}
   else if(qca_wake_close(&wake)){failed=0x301;stage=6;}
   else{
    const QcaWakeTarget w={0x80000,0x80004,0x8f0,3,1000000};stage=3;
    if(qca_wake_begin(&wake,&w,qca_port_read32,qca_port_write32,&port,now)){failed=0x302;stage=6;}
   }
  }
 }
 else if(stage==3){
  int rc=qca_wake_poll(&wake,now);chip=wake.chip_id;
  if(rc){
   if(rc<0||fresh()){failed=0x400|wake.error;stage=6;}
   else if(qca_pcie_recheck(&link)||qca_boot_irq_begin(&boot_irq,&port)||qca_rom_begin(&rom,&port,now)){failed=0x401;stage=6;}
   else{post_reset_link=link.readback;link_active=link.readback;rom.boot=&boot_irq;stage=4;}
  }
 }
 else if(stage==4){
  int rc=qca_rom_poll(&rom,now);firmware=rom.indicator;
  if(rc<0){failed=0x500|rom.error;stage=6;}
  else if(rc>0){
   if(qca_boot_irq_close(&boot_irq)||fresh()||qca_ce_access_init(&access,&port,255)||qca_ce_bus_init(&bus,&access)){failed=0x501;stage=6;}
   else{bus_live=1;stage=13;}
  }
 }
 else if(stage==13){
  snapshot_pre_halt();
  if(prehalt_engine==8){stage=8;if(qca_ce_bus_stop_begin(&bus,now)){failed=0x502;shutdown(now);}}
 }
 else if(stage==8){
  int rc=qca_ce_bus_stop_poll(&bus,now);
  if(rc<0){failed=0x600|bus.error;shutdown(now);}else if(rc>0)stage=9;
 }
 else if(stage==9){
  QcaDmaBuffer*d=&buffers[allocated];
  if(qca_dma_open(d,&port,1,qca_ce_bus_released,&bus)||qca_ce_access_buffer(&access,d)){
   failed=0x700|d->error;shutdown(now);
  }else if(++allocated==4)stage=10;
 }
 else if(stage==10){
  int rc=0;
  for(unsigned i=0;i<2;i++){
   diag_pipes[i]=(QcaDiagPipe){&bus,(uint8_t)i};
   if(qca_ce_init(&rings[i],buffers[i].host,buffers[i].address,8,i,qca_diag_publish,qca_diag_stop,&diag_pipes[i]))rc=1;
  }
  if(rc||qca_ce_hw_configure(&bus.engines[7],buffers[0].address,8,buffers[1].address,8,2048)
   ||qca_ce_seed(&rings[0],bus.engines[7].src_index)||qca_ce_seed(&rings[1],bus.engines[7].dst_index)
   ||qca_ce_bus_start(&bus)||qca_diag_begin(&diag,&bus,&rings[0],&rings[1],&buffers[3],chip,bar,now)){
   failed=0xd00|diag.error;shutdown(now);
  }else stage=14;
 }
 else if(stage==14){
  int rc=qca_diag_poll(&diag,now);
  if(rc<0){failed=0xd00|diag.error;shutdown(now);}
  else if(rc>0){snapshot_diag();stage=15;if(qca_ce_bus_stop_begin(&bus,now)){failed=0xd20;shutdown(now);}}
 }
 else if(stage==15){
  int rc=qca_ce_bus_stop_poll(&bus,now);
  if(rc<0){failed=0xd30|bus.error;shutdown(now);}
  else if(rc>0){
   if(qca_ce_close(&rings[0])||qca_ce_close(&rings[1])){failed=0xd40;shutdown(now);}
   else stage=16;
  }
 }
 else if(stage==16){
  pipes[0]=(QcaBmiPipe){&bus,0};pipes[1]=(QcaBmiPipe){&bus,1};
  int rc=0;
  for(unsigned i=0;i<2;i++)if(qca_ce_init(&rings[i],buffers[i].host,buffers[i].address,8,i,qca_bmi_publish,qca_bmi_ring_stop,&pipes[i]))rc=1;
  if(rc||qca_ce_hw_configure(&bus.engines[0],buffers[0].address,8,0,0,256)
   ||qca_ce_hw_configure(&bus.engines[1],0,0,buffers[1].address,8,0)
   ||qca_ce_seed(&rings[0],bus.engines[0].src_index)||qca_ce_seed(&rings[1],bus.engines[1].dst_index)
   ||qca_ce_bus_start(&bus)||qca_bmi_info_begin(&exchange,&bus,&rings[0],&rings[1],&buffers[2],&buffers[3],now)){
   failed=0x800|exchange.error;shutdown(now);
  }else stage=11;
 }
 else if(stage==11){
  int rc=qca_bmi_poll(&exchange,now);
  if(rc){succeeded=rc>0;if(rc<0)failed=0x800|exchange.error;shutdown(now);}
 }
 else if(stage==12){
  int rc=bus.phase==QCA_BUS_OFF?1:qca_ce_bus_stop_poll(&bus,now);
  if(rc<0){
   if(bus_retries<2){bus_retries++;qca_ce_bus_stop_begin(&bus,now);}
  }else if(rc>0){
   if(qca_ce_close(&rings[0])||qca_ce_close(&rings[1])){succeeded=0;if(!failed)failed=0x901;}
   else if(cleanup_slot<4&&buffer_retries<3){
    if(!qca_dma_close(&buffers[cleanup_slot])){cleanup_slot++;buffer_retries=0;}
    else{succeeded=0;if(!failed)failed=0x90000|buffers[cleanup_slot].error;buffer_retries++;} /* Retain. */
   }else if(cleanup_slot==4){bus_live=0;stage=succeeded?5:6;shutdown(now);}
  }
 }
 if(stage==6&&!reset.owned&&!bus_live&&port.claimed&&cleanup_attempts<3){cleanup_attempts++;shutdown(now);}
 telemetry();
}
