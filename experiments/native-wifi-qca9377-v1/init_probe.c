/* One-shot native warm/full-channel trial. No target RAM writes or firmware. */
#include "bringup.h"
#include "pci_collect.h"
#include "pci_identity.h"
#include "power_core.h"
#include "uefi_port.h"
#include "reset_core.h"
#include "rom_ready.h"
#include "pcie_link.h"
#include "init_adapter.h"
void*qca_image;
static QcaUefiPort port;static QcaWake wake;static QcaReset reset;
static QcaPcieLink link;static QcaBootIrq irq;static QcaRomReady rom;
static QcaInitAdapter adapter;
static uint32_t stage,failed,chip,succeeded,cancelled,recoveries,close_attempts;
static uint16_t actual_command,pmcsr,post_reset_link;
static uint64_t bar,last_now;
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
static void*method(unsigned offset){return *(void**)((uint8_t*)port.pci+offset);}
static void record(unsigned off,uint64_t value,unsigned n){for(unsigned i=0;i<n;i++)qca_diagnostic[off+i]=(uint8_t)(value>>(8*i));}
static void telemetry(void){
 record(128,stage,4);record(132,chip,4);record(136,failed,4);record(140,port.claimed?2:1,4);
 record(144,port.bar_extent,8);record(152,port.original_attributes,8);
 record(160,reset.phase,4);record(164,reset.error,4);record(168,reset.owned,4);record(172,rom.indicator,4);
 record(176,port.original_command,2);record(178,actual_command,2);record(180,pmcsr,2);record(182,link.readback,2);
 record(184,reset.original,4);record(188,reset.readback,4);record(196,rom.error,4);record(200,rom.indicator,4);
 record(220,port.dma_users,4);record(224,adapter.bus.phase,4);record(228,adapter.bus.error,4);record(232,adapter.bus.owned,4);
 uint32_t held=0;for(unsigned i=0;i<14;i++)if(adapter.channels.buffers[i].allocated||adapter.channels.buffers[i].mapped)held|=1u<<i;
 record(236,held,4);record(240,link.original,2);record(242,link.readback,2);record(244,link.owned,1);record(245,link.error,1);
 record(246,irq.original_command,2);record(248,irq.command_readback,2);record(250,irq.owned,1);record(251,irq.error,1);
 record(252,irq.original_enable,4);record(256,irq.last_enable,4);record(260,irq.original_control,4);record(264,irq.last_control,4);
 record(268,irq.writes,4);record(272,post_reset_link,2);record(276,irq.cause,4);
 /* QPD14 preserves legacy prefix, adds64bytes of exact warm/resource proof. */
 record(800,adapter.phase,4);record(804,adapter.error,4);record(808,adapter.warm.phase,4);record(812,adapter.warm.error,4);
 record(816,adapter.warm.owned,4);record(820,adapter.warm.ce_owned,4);record(824,adapter.warm.cpu_resets,4);
 record(828,adapter.warm.pipe_inits,4);record(832,adapter.channels.phase,4);record(836,adapter.channels.allocated,4);
 record(840,adapter.channels.cleanup_slot,4);record(844,adapter.recovery_verified,4);record(848,adapter.recovery.phase,4);
 record(852,adapter.recovery.owned,4);record(856,adapter.recovery_indicator,4);record(860,adapter.mapped.error,4);
}
static int fresh(void){
 uint32_t config[64]={0};QcaPciIdentity id;uint8_t power[16];
 if(!port.claimed||!port.pci||((Config)method(48))(port.pci,2,0,64,config))return -1;
 qca_power_decode((const uint8_t*)config,power);pmcsr=(uint16_t)(power[2]|((uint16_t)power[3]<<8));actual_command=(uint16_t)config[1];
 if(qca_pci_identity(config,&id)||id.subsystem_vendor!=0x1028||id.subsystem_device!=0x1810||id.revision!=0x31
  ||(id.command&4)||power[8]!=1||(pmcsr&3)||(bar&&id.bar0!=bar))return -1;
 bar=id.bar0;return 0;
}
static int reset_read(void*c,uint32_t address,uint32_t*out){
 (void)c;if(!port.memory_ready||address!=0x80008||port.bar_extent<0x8000c)return -1;
 if(reset.phase==QCA_RESET_CLEAR_WAIT){
  if(fresh())return -1;
  if(actual_command!=(uint16_t)(port.original_command|2)){
   if(actual_command!=(uint16_t)(port.original_command&~2u))return -1;
   typedef Status(EFIAPI *Attributes)(void*,uint32_t,uint64_t,uint64_t*);
   if(((Attributes)method(120))(port.pci,2,0x200,0)||fresh()||actual_command!=(uint16_t)(port.original_command|2))return -1;
  }
 }
 return ((Memory)method(16))(port.pci,2,0,address,1,out)?-1:0;
}
static int reset_write(void*c,uint32_t address,uint32_t value){
 (void)c;if(!port.memory_ready||address!=0x80008||port.bar_extent<0x8000c||!reset.owned
  ||(value!=reset.original&&value!=(reset.original|1)))return -1;
 return ((Memory)method(24))(port.pci,2,0,address,1,&value)?-1:0;
}
static void close_port(void){
 if(reset.owned||(adapter.phase&&!qca_init_adapter_released(&adapter)))return;
 if(qca_boot_irq_close(&irq)||qca_pcie_restore(&link)||qca_port_close(&port,&wake)){
  if(!failed)failed=0x900;
  stage=6;succeeded=0;return;
 }
 stage=succeeded?5:6;
}
int qca_stop(void){
 cancelled=1;
 if(reset.owned){if(reset.phase==QCA_RESET_FAULT)qca_reset_recover(&reset,reset.last_time);telemetry();return 1;}
 if(adapter.phase&&!qca_init_adapter_released(&adapter)){qca_init_adapter_cancel(&adapter);telemetry();return 1;}
 if(stage!=7)close_port();
 telemetry();return port.claimed||reset.owned;
}
void qca_start(SystemTable*st,uint64_t ms){
 if(stage){telemetry();return;}
 if(!qca_controller||qca_diagnostic[4]!=15){stage=7;telemetry();return;}
 const QcaPciTarget t={0x1028,0x1810,0x31};const QcaWakeTarget w={0x80000,0x80004,0x8f0,3,1000000};
 stage=1;last_now=ms*1000;
 if(qca_port_open(&port,st,qca_image,qca_controller,&t)||fresh()||port.bar_extent<0x8000c||qca_pcie_pause(&link,&port)
  ||qca_port_enable_memory(&port)||qca_wake_begin(&wake,&w,qca_port_read32,qca_port_write32,&port,last_now)){
  failed=0x10000|port.error;stage=6;(void)qca_stop();
 }
 telemetry();
}
void qca_poll(uint64_t ms){
 uint64_t now=ms*1000;last_now=now;
 if(stage==1){
  int rc=qca_wake_poll(&wake,now);
  if(rc){
   if(rc<0&&(wake.error!=QCA_WAKE_CHIP||wake.chip_id)){failed=wake.error;stage=6;}
   else{const QcaResetTarget t={0x80008,20000,1000000};stage=2;
    if(qca_reset_begin(&reset,&t,reset_read,reset_write,0,now)){failed=0x200|reset.error;if(!reset.owned)stage=6;}}
  }
 }else if(stage==2){
  int rc=qca_reset_poll(&reset,now);
  if(reset.phase==QCA_RESET_FAULT&&recoveries<1){recoveries++;qca_reset_recover(&reset,now);}
  if(!reset.owned){
   if(cancelled||rc<0||fresh()){failed=0x300|reset.error;stage=6;}
   else if(qca_wake_close(&wake)){failed=0x301;stage=6;}
   else{const QcaWakeTarget w={0x80000,0x80004,0x8f0,3,1000000};stage=3;
    if(qca_wake_begin(&wake,&w,qca_port_read32,qca_port_write32,&port,now)){failed=0x302;stage=6;}}
  }
 }else if(stage==3){
  int rc=qca_wake_poll(&wake,now);chip=wake.chip_id;
  if(rc){
   if(rc<0||fresh()){failed=0x400|wake.error;stage=6;}
   else if(qca_pcie_recheck(&link)||qca_boot_irq_begin(&irq,&port)||qca_rom_begin(&rom,&port,now)){failed=0x401;stage=6;}
   else{post_reset_link=link.readback;rom.boot=&irq;stage=4;}
  }
 }else if(stage==4){
  int rc=qca_rom_poll(&rom,now);
  if(rc<0){failed=0x500|rom.error;stage=6;}
  else if(rc>0){
   if(qca_init_adapter_begin(&adapter,&irq,bar,link.offset,now)){
    failed=0x501;stage=adapter.phase?19:6;
   }else stage=18;
  }
 }else if(stage==18||stage==19){
  if(cancelled)qca_init_adapter_cancel(&adapter);
  int rc=qca_init_adapter_poll(&adapter,now);
  if(rc==1&&stage==18){succeeded=1;if(qca_init_adapter_close(&adapter)){succeeded=0;failed=0x601;}stage=19;}
  if(adapter.error&&!failed){failed=0x1000|adapter.error;succeeded=0;}
  if(adapter.phase==QCA_INIT_RETAINED){stage=20;succeeded=0;if(!failed)failed=0x602;}
  else if(qca_init_adapter_released(&adapter))close_port();
 }
 if(stage==6&&!reset.owned&&(!adapter.phase||qca_init_adapter_released(&adapter))&&port.claimed&&close_attempts<3){close_attempts++;close_port();}
 telemetry();
}
