/* One-shot physical reset/identity probe. No DMA, firmware or association. */
#include "bringup.h"
#include "pci_collect.h"
#include "pci_identity.h"
#include "power_core.h"
#include "uefi_port.h"
#include "reset_core.h"
void*qca_image;
static QcaUefiPort port;static QcaWake wake;static QcaReset reset;
static uint32_t stage,failed,firmware,chip,revalidate_error,recoveries,cancelled,cleanup_attempts;
static uint16_t actual_command,pmcsr;
static uint64_t bar;
static void record(unsigned off,uint64_t value,unsigned bytes){for(unsigned i=0;i<bytes;i++)qca_diagnostic[off+i]=(uint8_t)(value>>(8*i));}
static void telemetry(void){
 record(128,stage,4);record(132,chip,4);record(136,failed,4);record(140,port.claimed?2:1,4);
 record(144,port.bar_extent,8);record(152,port.original_attributes,8);
 record(160,reset.phase,4);record(164,reset.error,4);record(168,reset.owned,4);record(172,firmware,4);
 record(176,port.original_command,2);record(178,actual_command,2);record(180,pmcsr,2);
 record(184,reset.original,4);record(188,reset.readback,4);record(192,revalidate_error,4);
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
int qca_stop(void){
 if(reset.owned){
  cancelled=1;
  if(reset.phase==QCA_RESET_FAULT)qca_reset_recover(&reset,reset.last_time);
  telemetry();return 1;
 }
 int rc=qca_port_close(&port,&wake);
 if(!rc&&stage!=5&&stage!=7){stage=6;if(!failed)failed=0x103;}
 telemetry();return rc;
}
void qca_start(SystemTable*st,uint64_t ms){
 if(stage){telemetry();return;}
 const QcaPciTarget t={0x1028,0x1810,0x31};const QcaWakeTarget w={0x80000,0x80004,0x8f0,3,1000000};
 if(!qca_controller||qca_diagnostic[4]!=15){stage=7;telemetry();return;}
 stage=1;
 if(qca_port_open(&port,st,qca_image,qca_controller,&t)||fresh()||port.bar_extent<0x8000c
  ||qca_port_enable_memory(&port)||qca_wake_begin(&wake,&w,qca_port_read32,qca_port_write32,&port,ms*1000)){
  stage=6;failed=0x10000|port.error;qca_stop();
 }
 telemetry();
}
void qca_poll(uint64_t ms){
 uint64_t now=ms*1000;
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
   stage=rc>0?5:6;failed=rc>0?0:0x400|wake.error;
   if((rc>0||wake.error==QCA_WAKE_CHIP)&&((Memory)method(16))(port.pci,2,0,0x3a028,1,&firmware)){failed=0x401;stage=6;}
  }
 }
 if((stage==5||stage==6)&&port.claimed&&!reset.owned&&cleanup_attempts<3){cleanup_attempts++;qca_stop();}
 telemetry();
}
