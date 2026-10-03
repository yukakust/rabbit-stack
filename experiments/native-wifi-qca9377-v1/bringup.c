/* One-shot reversible wake/chip-ID probe. Never resets, enables DMA or uploads firmware. */
#include "bringup.h"
#include "pci_collect.h"
#include "uefi_port.h"
void*qca_image;
static QcaUefiPort port;
static QcaWake wake;
static uint32_t stage,failed,cleanup_attempts;
static void record(unsigned off,uint64_t value,unsigned bytes){
 for(unsigned i=0;i<bytes;i++)qca_diagnostic[off+i]=(uint8_t)(value>>(8*i));
}
static void telemetry(void){
 record(128,stage,4);record(132,wake.chip_id,4);record(136,failed,4);
 record(140,port.claimed?2:1,4);record(144,port.bar_extent,8);record(152,port.original_attributes,8);
}
int qca_stop(void){
 if(stage==1){stage=3;failed=0x103;}
 int result=qca_port_close(&port,&wake);telemetry();return result;
}
void qca_start(SystemTable*st,uint64_t milliseconds){
 /* Re-attach after another candidate failed must not repeat hardware work. */
 if(stage){telemetry();return;}
 const QcaPciTarget target={0x1028,0x1810,0x31};
 const QcaWakeTarget registers={0x80000,0x80004,0x8f0,3,1000000};
 if(!qca_controller||qca_diagnostic[4]!=15){stage=4;telemetry();return;}
 stage=1;
 if(qca_port_open(&port,st,qca_image,qca_controller,&target)){failed=0x10000|port.error;stage=3;}
 else if(qca_port_enable_memory(&port)){failed=0x10000|port.error;stage=3;}
 else if(qca_wake_begin(&wake,&registers,qca_port_read32,qca_port_write32,&port,milliseconds*1000)){failed=0x102;stage=3;}
 if(stage==3){cleanup_attempts++;qca_stop();}
 telemetry();
}
void qca_poll(uint64_t milliseconds){
 if(stage==1){
  int result=qca_wake_poll(&wake,milliseconds*1000);
  if(result){stage=result>0?2:3;failed=result>0?0:wake.error;cleanup_attempts++;qca_stop();}
 }
 else if(port.claimed&&cleanup_attempts<3){cleanup_attempts++;qca_stop();}
 telemetry();
}
