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
#include "config_setup.h"
#include "firmware_port.h"
#include "boot_native.h"
#include "operating.h"
#include "startup.h"
#include "persistent.h"
#include "htt_native.h"
#include "firmware_op.h"
#include "boot_assets.h"
void*qca_image;
 
static QcaUefiPort port;
 static QcaWake wake;
 static QcaReset reset;
 
static QcaPcieLink link;
 static QcaBootIrq irq;
 static QcaRomReady rom;
 
static QcaInitAdapter adapter;
 
static QcaConfigSetup setup;
 
static QcaBoardQuery board;
 static QcaBoardSmbios smbios;
 static QcaBootNative boot;
 
static unsigned boot_round,board_once,boot_once;
 
static QcaOperating operating;
 
static QcaWmiStartup startup;
 
static QcaPersistentNative persistent;
 
static QcaHttNative htt_query;
 static QcaHttFirmwareProof htt_proof;
 static unsigned htt_attempted;
 static QcaRxEvent htt_export_scratch;
 
static QcaFirmwarePort ram;
 static SystemTable*ram_system;
 static unsigned ram_attempted,ram_closing;
 
static const QcaFirmwarePolicy ram_policy={.owner={175,6,163,227,41,23,20,228,243,86,193,156,155,21,205,25,81,236,110,102,98,170,119,190,7,84,127,40,147,131,52,29},.target={54,61,117,18,136,223,123,71,41,95,156,122,82,80,195,180,29,178,78,253,26,67,164,189,52,143,0,116,76,107,199,233},.digest={143,139,0,47,204,254,129,212,34,56,242,125,209,245,109,24,150,4,241,128,189,71,114,199,200,231,90,225,254,241,111,1},.total=751436ull,.type=8ull,.version=84017153ull,.kind=1ull,.generation=56ull};
 

#define config_read setup.read
#define full_read config_read.full
static uint32_t stage,failed,chip,succeeded,cancelled,recoveries,close_attempts;
 
static uint16_t actual_command,pmcsr,post_reset_link;
 
static uint64_t bar,last_now;
 
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
 
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
 
static void*method(unsigned offset){return *(void**)((uint8_t*)port.pci+offset);
 }
static void record(unsigned off,uint64_t value,unsigned n){for(unsigned i=0;i<n;i++)qca_diagnostic[off+i]=(uint8_t)(value>>(8*i));
 }
static void telemetry(void){
 record(128,stage,4);
 record(132,chip,4);
 record(136,failed,4);
 record(140,port.claimed?2:1,4);
 
 record(144,port.bar_extent,8);
 record(152,port.original_attributes,8);
 
 record(160,reset.phase,4);
 record(164,reset.error,4);
 record(168,reset.owned,4);
 record(172,rom.indicator,4);
 
 record(176,port.original_command,2);
 record(178,actual_command,2);
 record(180,pmcsr,2);
 record(182,link.readback,2);
 
 record(184,reset.original,4);
 record(188,reset.readback,4);
 record(196,rom.error,4);
 record(200,rom.indicator,4);
 
 record(220,port.dma_users,4);
 record(224,adapter.bus.phase,4);
 record(228,adapter.bus.error,4);
 record(232,adapter.bus.owned,4);
 
 uint32_t held=0;
 for(unsigned i=0;i<14;i++)if(adapter.channels.buffers[i].allocated||adapter.channels.buffers[i].mapped)held|=1u<<i;
 
 record(236,held,4);
 record(240,link.original,2);
 record(242,link.readback,2);
 record(244,link.owned,1);
 record(245,link.error,1);
 
 record(246,irq.original_command,2);
 record(248,irq.command_readback,2);
 record(250,irq.owned,1);
 record(251,irq.error,1);
 
 record(252,irq.original_enable,4);
 record(256,irq.last_enable,4);
 record(260,irq.original_control,4);
 record(264,irq.last_control,4);
 
 record(268,irq.writes,4);
 record(272,post_reset_link,2);
 record(276,irq.cause,4);
 
 /* QPD14 preserves legacy prefix, adds64bytes of exact warm/resource proof. */
 record(800,adapter.phase,4);
 record(804,adapter.error,4);
 record(808,adapter.warm.phase,4);
 record(812,adapter.warm.error,4);
 
 record(816,adapter.warm.owned,4);
 record(820,adapter.warm.ce_owned,4);
 record(824,adapter.warm.cpu_resets,4);
 
 record(828,adapter.warm.pipe_inits,4);
 record(832,adapter.channels.phase,4);
 record(836,adapter.channels.allocated,4);
 
 record(840,adapter.channels.cleanup_slot,4);
 record(844,adapter.recovery_verified,4);
 record(848,adapter.recovery.phase,4);
 
 record(852,adapter.recovery.owned,4);
 record(856,adapter.recovery_indicator,4);
 record(860,adapter.mapped.error,4);
 
 /* QPD15: cached warm failure only; no additional hardware reads/writes. */
 record(864,adapter.warm.failure_phase,4);
 record(868,adapter.warm.indicator,4);
 
 record(872,adapter.warm.failure_elapsed_us,4);
 record(876,adapter.warm.first_rom_polls,4);
 
 record(880,adapter.warm.second_rom_polls,4);
 record(884,adapter.warm.last_reset_read,4);
 
 record(280,setup.phase,4);
 record(284,setup.error,4);
 record(288,setup.op,4);
 
 record(292,setup.write_mask,4);
 record(296,setup.readback_mask,4);
 record(300,setup.write_attempts,4);
 
 record(304,setup.cpu_attempted,4);
 record(308,setup.cpu_before,4);
 record(312,setup.cpu_readback,4);
 
 record(316,setup.bmi.phase,4);
 record(320,setup.bmi.error,4);
 record(324,setup.bmi.version,4);
 
 record(328,setup.bmi.type,4);
 record(332,setup.bmi.info_length,4);
 record(336,setup.bmi.bytes,4);
 
 record(340,setup.bmi.tx_done,4);
 record(344,setup.bmi.rx_done,4);
 record(348,setup.bmi_polls,4);
 
 record(352,setup.bmi.last>=setup.bmi.started?setup.bmi.last-setup.bmi.started:0,4);
 
 record(716,config_read.phase,4);
 record(720,config_read.error,4);
 record(724,config_read.mask,4);
 
 if(config_read.phase)record(728,full_read.exchange.value,4);
 
 unsigned ci=config_read.slot<3?config_read.slot:2;
 QcaDiagExchange*cr=&config_read.reads[ci];
 
 record(732,cr->target,4);
 record(736,cr->bytes,4);
 
 for(unsigned j=0;j<11;j++)record(740+j*4,config_read.words[j],4);
 
 record(784,cr->first_elapsed,4);
 record(788,cr->last_elapsed,4);
 record(792,cr->polls,4);
 
 record(888,full_read.exchange.phase,4);
 record(892,full_read.error,4);
 record(896,full_read.exchange.value,4);
 
 record(900,full_read.exchange.bytes,4);
 record(904,full_read.exchange.tx_done,4);
 record(908,full_read.exchange.rx_done,4);
 
 record(912,full_read.exchange.mask,4);
 record(916,full_read.exchange.polls,4);
 record(920,full_read.exchange.last_elapsed,4);
 
}
static int fresh(void){
 uint32_t config[64]={0};
 QcaPciIdentity id;
 uint8_t power[16];
 
 if(!port.claimed||!port.pci||((Config)method(48))(port.pci,2,0,64,config))return -1;
 
 qca_power_decode((const uint8_t*)config,power);
 pmcsr=(uint16_t)(power[2]|((uint16_t)power[3]<<8));
 actual_command=(uint16_t)config[1];
 
 if(qca_pci_identity(config,&id)||id.subsystem_vendor!=0x1028||id.subsystem_device!=0x1810||id.revision!=0x31
  ||(id.command&4)||power[8]!=1||(pmcsr&3)||(bar&&id.bar0!=bar))return -1;
 
 bar=id.bar0;
 return 0;
 
}
static int reset_read(void*c,uint32_t address,uint32_t*out){
 (void)c;
 if(!port.memory_ready||address!=0x80008||port.bar_extent<0x8000c)return -1;
 
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
 (void)c;
 if(!port.memory_ready||address!=0x80008||port.bar_extent<0x8000c||!reset.owned
  ||(value!=reset.original&&value!=(reset.original|1)))return -1;
 
 return ((Memory)method(24))(port.pci,2,0,address,1,&value)?-1:0;
 
}
static void close_port(void){
 if(reset.owned||(adapter.phase&&!qca_init_adapter_released(&adapter)))return;
 
 if(qca_boot_irq_close(&irq)||qca_pcie_restore(&link)||qca_port_close(&port,&wake)){
  if(!failed)failed=0x900;
 
  stage=6;
 succeeded=0;
 return;
 
 }
 stage=succeeded?5:6;
 
}
static int qca_hardware_stop(void){
 cancelled=1;
 
 if(reset.owned){if(reset.phase==QCA_RESET_FAULT)qca_reset_recover(&reset,reset.last_time);
 telemetry();
 return 1;
 }
 if(adapter.phase&&!qca_init_adapter_released(&adapter)){qca_init_adapter_cancel(&adapter);
 telemetry();
 return 1;
 }
 if(stage!=7)close_port();
 
 telemetry();
 return port.claimed||reset.owned;
 
}
void qca_start(SystemTable*st,uint64_t ms){
 ram_system=st;
 
 if(!stage)(void)qca_board_smbios_collect(&smbios,st);
 
 if(stage){telemetry();
 return;
 }
 if(!qca_controller||qca_diagnostic[4]!=15){stage=7;
 telemetry();
 return;
 }
 const QcaPciTarget t={0x1028,0x1810,0x31};
 const QcaWakeTarget w={0x80000,0x80004,0x8f0,3,1000000};
 
 stage=1;
 last_now=ms*1000;
 
 if(qca_port_open(&port,st,qca_image,qca_controller,&t)||fresh()||port.bar_extent<0x8000c||qca_pcie_pause(&link,&port)
  ||qca_port_enable_memory(&port)||qca_wake_begin(&wake,&w,qca_port_read32,qca_port_write32,&port,last_now)){
  failed=0x10000|port.error;
 stage=6;
 (void)qca_stop();
 
 }
 telemetry();
 
}
static void qca_hardware_poll(uint64_t ms){
 uint64_t now=ms*1000;
 last_now=now;
 
 if(stage==1){
  int rc=qca_wake_poll(&wake,now);
 
  if(rc){
   if(rc<0&&(wake.error!=QCA_WAKE_CHIP||wake.chip_id)){failed=wake.error;
 stage=6;
 }
   else{const QcaResetTarget t={0x80008,20000,1000000};
 stage=2;
 
    if(qca_reset_begin(&reset,&t,reset_read,reset_write,0,now)){failed=0x200|reset.error;
 if(!reset.owned)stage=6;
 }}
  }
 }else if(stage==2){
  int rc=qca_reset_poll(&reset,now);
 
  if(reset.phase==QCA_RESET_FAULT&&recoveries<1){recoveries++;
 qca_reset_recover(&reset,now);
 }
  if(!reset.owned){
   if(cancelled||rc<0||fresh()){failed=0x300|reset.error;
 stage=6;
 }
   else if(qca_wake_close(&wake)){failed=0x301;
 stage=6;
 }
   else{const QcaWakeTarget w={0x80000,0x80004,0x8f0,3,1000000};
 stage=3;
 
    if(qca_wake_begin(&wake,&w,qca_port_read32,qca_port_write32,&port,now)){failed=0x302;
 stage=6;
 }}
  }
 }else if(stage==3){
  int rc=qca_wake_poll(&wake,now);
 chip=wake.chip_id;
 
  if(rc){
   if(rc<0||fresh()){failed=0x400|wake.error;
 stage=6;
 }
   else if(qca_pcie_recheck(&link)||qca_boot_irq_begin(&irq,&port)||qca_rom_begin(&rom,&port,now)){failed=0x401;
 stage=6;
 }
   else{post_reset_link=link.readback;
 rom.boot=&irq;
 stage=4;
 }
  }
 }else if(stage==4){
  int rc=qca_rom_poll(&rom,now);
 
  if(rc<0){failed=0x500|rom.error;
 stage=6;
 }
  else if(rc>0){
   if(qca_init_adapter_begin(&adapter,&irq,bar,link.offset,now)){
    failed=0x501;
 stage=adapter.phase?19:6;
 
   }else stage=18;
 
  }
 }else if(stage==18||stage==19){
  if(cancelled)qca_init_adapter_cancel(&adapter);
 
  int rc=0;
 
  if(stage==18&&full_read.started){
   rc=cancelled?-1:qca_config_setup_poll(&setup,now);
 
   if(rc==1&&boot_round){
    if(!board_once){board_once=1;
 if(smbios.state!=2||qca_board_begin(&board,&setup,boot_helper,sizeof(boot_helper),boot_helper_digest))rc=-1;
 else rc=0;
 }
    else if(board.phase!=5){rc=qca_board_poll(&board,now);
 if(rc>0)rc=0;
 }
    else if(!boot_once){boot_once=1;
 if(qca_boot_native_begin(&boot,&board,&smbios,&ram.asset,boot_board,sizeof(boot_board),now))rc=-1;
 else rc=0;
 }
    else {
     rc=qca_boot_native_poll(&boot,now);
 
     if(rc==1){
      if(!operating.phase)rc=qca_operating_begin(&operating,&boot,now);
 
      else {
       rc=qca_operating_poll(&operating,now);
 
       if(rc==1){
        if(!startup.phase)rc=qca_wmi_startup_begin(&startup,&operating,now);
 
        else rc=qca_wmi_startup_poll(&startup,now);
 
        if(rc==1){
         if(!persistent.life.phase)rc=qca_persistent_begin(&persistent,&startup,1,now);
 
         else rc=qca_persistent_poll(&persistent,now);
 
         if(rc==1)rc=0;
  /* Retain exact hardware lifetime; no diagnostic teardown. */
        }
       }
       else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);
 
       if(rc<0&&persistent.life.phase)(void)qca_persistent_poll(&persistent,now);
 
      }
     }
    }
   }
   if(rc){
    succeeded=rc>0;
 
    if(!succeeded&&!failed)failed=0x2000|(full_read.error?full_read.error:0x100);
 
    if(qca_init_adapter_close(&adapter)){succeeded=0;
 if(!failed)failed=0x601;
 }
    stage=19;
 
   }
  }else{
   rc=qca_init_adapter_poll(&adapter,now);
 
   if(rc==1&&stage==18){
    if(qca_full_read_begin(&full_read,&adapter,chip,bar,now)){
     failed=0x2000|(full_read.error?full_read.error:0x101);
 succeeded=0;
 
     (void)qca_init_adapter_close(&adapter);
 stage=19;
 
    }
   }
  }
  if(adapter.error&&!failed){failed=0x1000|adapter.error;
 succeeded=0;
 }
  if(adapter.phase==QCA_INIT_RETAINED){stage=20;
 succeeded=0;
 if(!failed)failed=0x602;
 }
  else if(qca_init_adapter_released(&adapter))close_port();
 
 }
 if(stage==6&&!reset.owned&&(!adapter.phase||qca_init_adapter_released(&adapter))&&port.claimed&&close_attempts<3){close_attempts++;
 close_port();
 }
 telemetry();
 
}

static void clear(void*p,size_t n){volatile uint8_t*b=p;
 while(n--)*b++=0;
 }
/* The hardware owner closes FIRST. RAM assets never borrow DMA mappings. */
static void qca_htt_profile_step(uint64_t);
 
void qca_poll(uint64_t ms){
 qca_hardware_poll(ms);
 
 qca_htt_profile_step(ms*1000);
 
 if(ram_closing){
  if(boot_round&&qca_boot_native_close(&boot)){
   (void)qca_persistent_poll(&persistent,ms*1000);
 return;
 
  }
  (void)qca_persistent_poll(&persistent,ms*1000);
 
  (void)qca_fwp_close(&ram);
 return;
 
 }
 if(boot_round){
  if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);
 
  if(persistent.life.phase&&persistent.life.phase!=QCA_RADIO_ACTIVE)
   (void)qca_persistent_poll(&persistent,ms*1000);
 
  return;
 
 }
 if(stage!=5||failed||cancelled)return;
 
 if(!ram_attempted){ram_attempted=1;
 if(qca_fwp_start_setup(&ram,ram_system,&ram_policy,&setup)){ram.phase=6;
 ram.error=0x100;
 return;
 }}
 if(ram.phase>0&&ram.phase<4)(void)qca_fwp_step(&ram);
 
 if(ram.phase==4&&ram.asset.ready&&!ram.asset.poisoned&&!ram.asset.pinned){
  /* First hardware lifetime must be completely released before reuse. */
  if(!qca_init_adapter_released(&adapter)||port.claimed||port.dma_users||adapter.access.count||reset.owned||irq.owned||link.owned||wake.owned){failed=0x8001;
 return;
 }
  boot_round=1;
 
  clear(&port,sizeof(port));
 clear(&wake,sizeof(wake));
 clear(&reset,sizeof(reset));
 clear(&link,sizeof(link));
 clear(&irq,sizeof(irq));
 clear(&rom,sizeof(rom));
 clear(&adapter,sizeof(adapter));
 clear(&setup,sizeof(setup));
 clear(&smbios,sizeof(smbios));
 
  stage=failed=chip=succeeded=cancelled=recoveries=close_attempts=0;
 actual_command=pmcsr=post_reset_link=0;
 bar=last_now=0;
 
  qca_start(ram_system,ms);
 
 }
}
int qca_stop(void){
 (void)qca_persistent_quiesce(&persistent,last_now);
 
 qca_wmi_startup_cancel(&startup);
 
 ram_closing=1;
 int hardware=qca_hardware_stop();
 
 if(boot_round&&qca_boot_native_close(&boot))return 1;
 
 int result=qca_fwp_close(&ram);
 
 /* Resident close is a single-call ABI. Two bounded pool releases complete
  * unpinned RAM teardown; faults/pins retain ownership and still refuse close. */
 if(result==1)result=qca_fwp_close(&ram);
 
 return hardware||qca_fwp_owned(&ram)||result<0;
 
}
const QcaFirmwarePort*qca_ram_view(void){return &ram;
 }
size_t qca_ram_att(uint16_t mtu,const uint8_t*p,size_t n,uint8_t*r,size_t capacity){
 if(boot_round&&p&&n>=3&&(p[0]==0x12||p[0]==0x52)){
  unsigned handle=(unsigned)p[1]|((unsigned)p[2]<<8);
 
  /* Asset writes remain sealed. Legacy replacement is delegated only after
     every hardware owner and the firmware pin have actually been released. */
  if((handle>=13&&handle<=19)||!qca_init_adapter_released(&adapter)||port.claimed||port.dma_users||ram.asset.pinned){
   if(!r||capacity<5)return 0;
 
   r[0]=1;
 r[1]=p[0];
 r[2]=p[1];
 r[3]=p[2];
 r[4]=3;
 return p[0]==0x52?0:5;
 
  }
 }
 return qca_fwp_att(&ram,mtu,p,n,r,capacity);
 
}

const QcaBootNative*qca_boot_view(void){return &boot;
 }
unsigned qca_boot_round(void){return boot_round;
 }
void qca_boot_status(uint8_t out[160]){
 for(unsigned i=0;i<160;i++)out[i]=0;
 
 const uint8_t magic[8]={'Q','W','B','T','0','0','0','1'};
 for(unsigned i=0;i<8;i++)out[i]=magic[i];
 
 uint32_t fields[30]={boot.phase,boot.error,boot.plan.phase,boot.plan.error,boot.plan.submitted,boot.plan.completed,boot.plan.board_address,boot.plan.calibration_result,boot.plan.offset,boot.ready_bytes,boot.credit_count,boot.credit_size,boot.max_endpoints,boot_round,ram.phase,ram.error,ram.asset.ready,ram.asset.pinned,stage,failed,adapter.phase,adapter.channels.cleanup_slot,port.dma_users,setup.bmi.version,setup.bmi.type,board.phase,board.error,board.result,ram.asset.received,boot_once};
 
 for(unsigned j=0;j<30;j++)for(unsigned i=0;i<4;i++)out[8+j*4+i]=(uint8_t)(fields[j]>>(8*i));
 
 for(unsigned i=0;i<32;i++)out[128+i]=ram_policy.digest[i];
 
}

const QcaOperating*qca_operating_view(void){return &operating;
 }

void qca_operating_status(uint8_t out[488]){
 for(unsigned i=0;i<488;i++)out[i]=0;
 
 const uint8_t magic[8]={'Q','W','O','P','0','0','0','3'};
 for(unsigned i=0;i<8;i++)out[i]=magic[i];
 
 const QcaOperating*s=&operating;
 const QcaHtcSession*h=&s->control.session;
 const QcaWmiServiceInfo*w=&s->service;
 
 uint32_t fields[22]={s->phase,s->error,h->phase,s->control.posted,s->control.deferred_bytes,s->tx_count,s->rx_count,s->service_bytes,s->service_valid,h->wmi.endpoint,h->htt.endpoint,w->build,w->abi_minor,w->chains,w->memory_count,w->regdomain,w->low2,w->high2,w->low5,w->high5,s->control.credit.available,s->control.credit.outstanding};
 
 for(unsigned j=0;j<22;j++)for(unsigned i=0;i<4;i++)out[8+j*4+i]=(uint8_t)(fields[j]>>(8*i));
 
 for(unsigned j=0;j<10;j++)for(unsigned i=0;i<4;i++)out[96+j*4+i]=(uint8_t)(s->rx_diagnostic[j]>>(8*i));
 
 for(unsigned i=0;i<8;i++)out[136+i]=s->rx_descriptor[i];
 
 for(unsigned i=0;i<64;i++)out[144+i]=s->rx_prefix[i];
 
 uint32_t av[6]={s->available_seen,s->available.advertised_length,s->available.words[0],s->available.words[1],s->available.words[2],s->available.words[3]};
 
 for(unsigned j=0;j<6;j++)for(unsigned i=0;i<4;i++)out[208+4*j+i]=(uint8_t)(av[j]>>(8*i));
 
 if(s->service_valid){
  for(unsigned j=0;j<16;j++){
   const QcaWmiMemoryRequest*m=&s->service.memory[j];
 uint32_t fields[4]={m->id,m->unit_size,m->unit_flags,m->units};
 
   for(unsigned k=0;k<4;k++)for(unsigned i=0;i<4;i++)out[232+16*j+4*k+i]=(uint8_t)(fields[k]>>(8*i));
 
  }
 }else{
  unsigned n=s->service_bytes;
 if(n>256)n=256;
 
  for(unsigned i=0;i<n;i++)out[232+i]=s->service_frame[i];
 
 }
}

const QcaWmiStartup*qca_wmi_startup_view(void){return &startup;
 }

void qca_wmi_status(uint8_t out[244]){
 for(unsigned j=0;j<244;j++)out[j]=0;
 
 const uint8_t magic[8]={'Q','W','I','N','0','0','0','2'};
 for(unsigned j=0;j<8;j++)out[j]=magic[j];
 
 const QcaWmiStartup*s=&startup;
 const QcaWmiInitTransaction*t=&s->transaction;
 
 uint32_t fields[12]={s->phase,s->error,t->phase,s->tx_posted,s->tx_count,s->rx_count,t->ready_seen,t->tx_complete,t->ready.abi_minor,operating.control.credit.available,operating.control.credit.outstanding,operating.service.memory_count};
 
 for(unsigned j=0;j<12;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(fields[j]>>(8*k));
 
 for(unsigned j=0;j<6;j++)out[56+j]=t->ready.mac[j];
 
 for(unsigned j=0;j<8;j++)for(unsigned k=0;k<4;k++)out[64+4*j+k]=(uint8_t)(s->diagnostic[j]>>(8*k));
 
 const uint32_t diag[5]={s->reject_reason,s->frame_bytes,s->prefix_bytes,s->frame_endpoint,s->payload_bytes};
 
 for(unsigned j=0;j<5;j++)for(unsigned k=0;k<4;k++)out[96+4*j+k]=(uint8_t)(diag[j]>>(8*k));
 
 for(unsigned j=0;j<128;j++)out[116+j]=s->prefix[j];
 
}

const QcaPersistentNative*qca_persistent_view(void){return &persistent;
 }

static unsigned htt_actual_released(void){
 return persistent.life.phase&&qca_init_adapter_released(&adapter)&&!port.claimed&&!port.dma_users
 &&!adapter.access.count&&!boot.owns_pin&&!ram.asset.pinned&&!irq.owned&&!link.owned&&!wake.owned;
 
}
static void qca_htt_profile_step(uint64_t now){
 if(!htt_attempted&&qca_radio_accepts_work(&persistent.life)){
  htt_attempted=1;
 
  if(!qca_htt_firmware_proof(&htt_proof,&boot)||!qca_htt_native_begin(&htt_query,&persistent,htt_proof.htt_op,now)){
   if(!htt_query.error)htt_query.error=30;
 
   htt_query.phase=QCA_HTTN_FAULT;
 htt_query.stop_requested=1;
 
   (void)qca_persistent_quiesce(&persistent,now);
 (void)qca_stop();
 
  }
 }
 if(htt_query.phase&&(!htt_query.stop_requested||htt_actual_released()))(void)qca_htt_native_poll(&htt_query,now);
 
}
const QcaHttNative*qca_htt_native_view(void){return &htt_query;
 }
const QcaHttFirmwareProof*qca_htt_firmware_view(void){return &htt_proof;
 }
void qca_htt_status(uint8_t out[320]){
 for(unsigned j=0;j<320;j++)out[j]=0;
 
 const uint8_t magic[8]={'Q','H','T','T','0','0','0','1'};
 for(unsigned j=0;j<8;j++)out[j]=magic[j];
 
 uint32_t held=0;
 for(unsigned j=0;j<14;j++)if(adapter.channels.buffers[j].allocated||adapter.channels.buffers[j].mapped||adapter.channels.buffers[j].allocation_uncertain)held++;
 
 const QcaHttNative*s=&htt_query;
 const QcaPersistentRx*r=&persistent.rx;
 
 uint32_t f[56]={s->phase,s->error,s->stop_requested,htt_attempted,htt_actual_released(),
 s->attempted,s->dma_completed,s->version_seen,s->version.major,s->version.minor,s->binding.endpoint,s->binding.max_bytes,s->binding.op_version,
 s->watermark,s->consumed,s->archive_count,htt_proof.valid,htt_proof.error,htt_proof.htt_op,htt_proof.wmi_op,htt_proof.htt_offset,htt_proof.main_offset,htt_proof.main_bytes,
 (uint32_t)htt_proof.generation,(uint32_t)(htt_proof.generation>>32),r->phase,r->error,r->completed,r->posted_count,r->count,r->backpressure,
 operating.control.credit.available,operating.control.credit.outstanding,operating.control.credit.reserved,operating.control.credit.total,
 held,port.dma_users,port.claimed,wake.owned,link.owned,irq.owned,boot.owns_pin,adapter.bus.owned,adapter.access.count,
 adapter.phase,adapter.channels.cleanup_slot,persistent.life.phase,persistent.life.error,persistent.error,persistent.polls,
 startup.transaction.ready_seen,startup.transaction.tx_complete,(uint32_t)s->epoch,(uint32_t)(s->epoch>>32),56,persistent.stop_latched};
 
 for(unsigned j=0;j<56;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(f[j]>>(8*k));
 
 for(unsigned j=0;j<32;j++){out[232+j]=htt_proof.digest[j];
 out[264+j]=htt_proof.main_digest[j];
 }
}
unsigned qca_htt_profile_export(unsigned page,uint8_t*out,unsigned cap){
 if(!out||cap<512||page>=30)return 0;
 
 unsigned slot=page/5,offset=(page%5)*512,length=2104-offset;
 if(length>512)length=512;
 
 unsigned present=qca_htt_native_export(&htt_query,slot,&htt_export_scratch,sizeof(htt_export_scratch));
 
 const QcaRxEvent*e=&htt_export_scratch;
 
 uint32_t f[12]={slot,present,present&&slot!=5,present?e->completion:0,(uint32_t)htt_query.epoch,(uint32_t)(htt_query.epoch>>32),
 present?e->endpoint:0,present?e->pipe:0,present?e->bytes:0,present?e->raw_bytes:0,present?e->event:0,slot==5?persistent.rx.error:0};
 
 const uint8_t magic[8]={'Q','H','T','X','0','0','0','1'};
 
 for(unsigned j=0;j<length;j++){
  unsigned at=offset+j;
 uint8_t v=0;
 
  if(at<8)v=magic[at];
 else if(at<56)v=(uint8_t)(f[(at-8)/4]>>(8*((at-8)&3)));
 
  else if(present&&at-56<e->raw_bytes)v=e->raw[at-56];
 out[j]=v;
 
 }
 return length;
 
}
