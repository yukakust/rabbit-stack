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
#include "prefix.h"
#include "persistent.h"
#include "htt_native.h"
#include "firmware_op.h"
#include "scan_native.h"
#include "phase_arena.h"
#include "data_path.h"
#include "owner47.h"
#include "scan_policy.h"
#include "filter_barrier.h"
#include "query_handover.h"
#include "boot_assets.h"
void*qca_image;
static QcaUefiPort port;static QcaWake wake;static QcaReset reset;
static QcaPcieLink link;static QcaBootIrq irq;static QcaRomReady rom;
static QcaInitAdapter adapter;
static QcaConfigSetup setup;
static QcaBoardQuery board;static QcaBoardSmbios smbios;static QcaBootNative boot;
static unsigned boot_round,board_once,boot_once;
static QcaOperating operating;
static QcaWmiStartup startup;
static QcaPrefix prefix;
static QcaPersistentNative persistent;
static QcaHttNative htt_query;static QcaHttFirmwareProof htt_proof;static unsigned htt_attempted;
static QcaHttPhaseOwner runtime_phase;
#define native_scan (runtime_phase.arena->scan)
QcaPrefix*qca_prefix_view(void){return &prefix;}
static unsigned prefix_released(void);
static QcaFirmwarePort ram;static SystemTable*ram_system;static unsigned ram_attempted,ram_closing;
static const QcaFirmwarePolicy ram_policy={.owner={175,6,163,227,41,23,20,228,243,86,193,156,155,21,205,25,81,236,110,102,98,170,119,190,7,84,127,40,147,131,52,29},.target={54,61,117,18,136,223,123,71,41,95,156,122,82,80,195,180,29,178,78,253,26,67,164,189,52,143,0,116,76,107,199,233},.digest={143,139,0,47,204,254,129,212,34,56,242,125,209,245,109,24,150,4,241,128,189,71,114,199,200,231,90,225,254,241,111,1},.total=751436ull,.type=8ull,.version=84017153ull,.kind=1ull,.generation=64ull};

#define config_read setup.read
#define full_read config_read.full
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
 /* QPD15: cached warm failure only; no additional hardware reads/writes. */
 record(864,adapter.warm.failure_phase,4);record(868,adapter.warm.indicator,4);
 record(872,adapter.warm.failure_elapsed_us,4);record(876,adapter.warm.first_rom_polls,4);
 record(880,adapter.warm.second_rom_polls,4);record(884,adapter.warm.last_reset_read,4);
 record(280,setup.phase,4);record(284,setup.error,4);record(288,setup.op,4);
 record(292,setup.write_mask,4);record(296,setup.readback_mask,4);record(300,setup.write_attempts,4);
 record(304,setup.cpu_attempted,4);record(308,setup.cpu_before,4);record(312,setup.cpu_readback,4);
 record(316,setup.bmi.phase,4);record(320,setup.bmi.error,4);record(324,setup.bmi.version,4);
 record(328,setup.bmi.type,4);record(332,setup.bmi.info_length,4);record(336,setup.bmi.bytes,4);
 record(340,setup.bmi.tx_done,4);record(344,setup.bmi.rx_done,4);record(348,setup.bmi_polls,4);
 record(352,setup.bmi.last>=setup.bmi.started?setup.bmi.last-setup.bmi.started:0,4);
 record(716,config_read.phase,4);record(720,config_read.error,4);record(724,config_read.mask,4);
 if(config_read.phase)record(728,full_read.exchange.value,4);
 unsigned ci=config_read.slot<3?config_read.slot:2;QcaDiagExchange*cr=&config_read.reads[ci];
 record(732,cr->target,4);record(736,cr->bytes,4);
 for(unsigned j=0;j<11;j++)record(740+j*4,config_read.words[j],4);
 record(784,cr->first_elapsed,4);record(788,cr->last_elapsed,4);record(792,cr->polls,4);
 record(888,full_read.exchange.phase,4);record(892,full_read.error,4);record(896,full_read.exchange.value,4);
 record(900,full_read.exchange.bytes,4);record(904,full_read.exchange.tx_done,4);record(908,full_read.exchange.rx_done,4);
 record(912,full_read.exchange.mask,4);record(916,full_read.exchange.polls,4);record(920,full_read.exchange.last_elapsed,4);
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
static int qca_hardware_stop(void){
 cancelled=1;
 if(reset.owned){if(reset.phase==QCA_RESET_FAULT)qca_reset_recover(&reset,reset.last_time);telemetry();return 1;}
 if(adapter.phase&&!qca_init_adapter_released(&adapter)){qca_init_adapter_cancel(&adapter);telemetry();return 1;}
 if(stage!=7)close_port();
 telemetry();return port.claimed||reset.owned;
}
void qca_start(SystemTable*st,uint64_t ms){
 if(!stage&&!runtime_phase.arena){QcaHttPoolBoot boot_api;
  if(!qca_htt_pool_boot(st,&boot_api)||!qca_htt_phase_acquire(&runtime_phase,&boot_api,1)){failed=0x7e01;stage=7;telemetry();return;}}
 if(runtime_phase.arena&&!runtime_phase.arena->rng.attempted){
  /* No self-code hash is invented. Zero means unresolved code-artifact provenance. */
  static const uint8_t inventory_code[32]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  (void)qca_htt_public_rng_inventory(&runtime_phase.arena->rng,st,runtime_phase.epoch,inventory_code);
 }


 ram_system=st;
 if(!stage)(void)qca_board_smbios_collect(&smbios,st);
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
static void qca_hardware_poll(uint64_t ms){
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
  int rc=0;
  if(stage==18&&full_read.started){
   rc=cancelled?-1:qca_config_setup_poll(&setup,now);
   if(rc==1&&boot_round){
    if(!board_once){board_once=1;if(smbios.state!=2||qca_board_begin(&board,&setup,boot_helper,sizeof(boot_helper),boot_helper_digest))rc=-1;else rc=0;}
    else if(board.phase!=5){rc=qca_board_poll(&board,now);if(rc>0)rc=0;}
    else if(!boot_once){boot_once=1;if(qca_boot_native_begin(&boot,&board,&smbios,&ram.asset,boot_board,sizeof(boot_board),now))rc=-1;else rc=0;}
    else {
     if(!prefix.phase&&boot.phase==1&&boot.owns_pin&&ram.asset.pinned)qca_prefix_arm(&prefix,now);
     if(qca_prefix_tick(&prefix,now,boot.phase,boot.plan.phase,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.pending,boot.io.wire.phase,0))rc=-1;
     else {
      rc=qca_boot_native_poll(&boot,now);
      if(rc==1){
       if(!operating.phase)rc=qca_operating_begin(&operating,&boot,now);
       else {
        rc=qca_operating_poll(&operating,now);
        if(rc==1){
         if(!startup.phase)rc=qca_wmi_startup_begin(&startup,&operating,now);
         else rc=qca_wmi_startup_poll(&startup,now);
         if(rc==1){if(!persistent.life.phase)rc=qca_persistent_begin(&persistent,&startup,1,now);else rc=qca_persistent_poll(&persistent,now);if(rc==1)rc=0;}
        }
        else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);
        if(rc<0&&persistent.life.phase)(void)qca_persistent_poll(&persistent,now);
       }
      }
      if(rc)qca_prefix_request(&prefix,rc<0?3:0,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.phase,boot.io.wire.phase);
      else if(qca_prefix_tick(&prefix,now,boot.phase,boot.plan.phase,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.pending,boot.io.wire.phase,0))rc=-1;
     }
     /* Success requires actual WMI INIT TX completion and parsed WMI READY. */
    }
   }
   if(rc){
    succeeded=rc>0;
    if(!succeeded&&!failed)failed=0x2000|(full_read.error?full_read.error:0x100);
    if(qca_init_adapter_close(&adapter)){succeeded=0;if(!failed)failed=0x601;}
    stage=19;
   }
  }else{
   rc=qca_init_adapter_poll(&adapter,now);
   if(rc==1&&stage==18){
    if(qca_full_read_begin(&full_read,&adapter,chip,bar,now)){
     failed=0x2000|(full_read.error?full_read.error:0x101);succeeded=0;
     (void)qca_init_adapter_close(&adapter);stage=19;
    }
   }
  }
  if(adapter.error&&!failed){failed=0x1000|adapter.error;succeeded=0;}
  if(adapter.phase==QCA_INIT_RETAINED){stage=20;succeeded=0;if(!failed)failed=0x602;}
  else if(qca_init_adapter_released(&adapter))close_port();
 }
 if(stage==6&&!reset.owned&&(!adapter.phase||qca_init_adapter_released(&adapter))&&port.claimed&&close_attempts<3){close_attempts++;close_port();}
 telemetry();
}

static void clear(void*p,size_t n){volatile uint8_t*b=p;while(n--)*b++=0;}
/* The hardware owner closes FIRST. RAM assets never borrow DMA mappings. */
static void qca_filter64_step(uint64_t);
void qca_poll(uint64_t ms){
 qca_hardware_poll(ms);
 qca_filter64_step(ms*1000);
 if(prefix.phase==2){
  /* Successful WMI completion already started checked hardware teardown.
   * Do not cancel that successful cleanup; release RAM only after hardware. */
  if(prefix.reason||(qca_init_adapter_released(&adapter)&&!port.claimed)){
   if(prefix.stop_calls!=UINT32_MAX)prefix.stop_calls++;
   (void)qca_stop();
  }
  (void)qca_prefix_tick(&prefix,ms*1000,boot.phase,boot.plan.phase,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.pending,boot.io.wire.phase,prefix_released());
 }
 if(ram_closing){if(boot_round&&qca_boot_native_close(&boot)){(void)qca_persistent_poll(&persistent,ms*1000);return;}(void)qca_persistent_poll(&persistent,ms*1000);(void)qca_fwp_close(&ram);return;}
 if(boot_round){
  if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);
  if(persistent.life.phase&&persistent.life.phase!=QCA_RADIO_ACTIVE)(void)qca_persistent_poll(&persistent,ms*1000);
  return;
 }
 if(stage!=5||failed||cancelled)return;
 if(!ram_attempted){ram_attempted=1;if(qca_fwp_start_setup(&ram,ram_system,&ram_policy,&setup)){ram.phase=6;ram.error=0x100;return;}}
 if(ram.phase>0&&ram.phase<4)(void)qca_fwp_step(&ram);
 if(ram.phase==4&&ram.asset.ready&&!ram.asset.poisoned&&!ram.asset.pinned){
  /* First hardware lifetime must be completely released before reuse. */
  if(!qca_init_adapter_released(&adapter)||port.claimed||port.dma_users||adapter.access.count||reset.owned||irq.owned||link.owned||wake.owned){failed=0x8001;return;}
  boot_round=1;
  clear(&port,sizeof(port));clear(&wake,sizeof(wake));clear(&reset,sizeof(reset));clear(&link,sizeof(link));clear(&irq,sizeof(irq));clear(&rom,sizeof(rom));clear(&adapter,sizeof(adapter));clear(&setup,sizeof(setup));clear(&smbios,sizeof(smbios));
  stage=failed=chip=succeeded=cancelled=recoveries=close_attempts=0;actual_command=pmcsr=post_reset_link=0;bar=last_now=0;
  qca_start(ram_system,ms);
 }
}
int qca_stop(void){
 (void)qca_persistent_quiesce(&persistent,last_now);
 qca_prefix_request(&prefix,7,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.phase,boot.io.wire.phase);
 qca_wmi_startup_cancel(&startup);
 ram_closing=1;int hardware=qca_hardware_stop();
 if(boot_round&&qca_boot_native_close(&boot))return 1;
 int result=qca_fwp_close(&ram);
 /* Resident close is a single-call ABI. Two bounded pool releases complete
  * unpinned RAM teardown; faults/pins retain ownership and still refuse close. */
 if(result==1)result=qca_fwp_close(&ram);
 return hardware||qca_fwp_owned(&ram)||result<0;
}
const QcaFirmwarePort*qca_ram_view(void){return &ram;}
size_t qca_ram_att(uint16_t mtu,const uint8_t*p,size_t n,uint8_t*r,size_t capacity){
 if(boot_round&&p&&n>=3&&(p[0]==0x12||p[0]==0x52)){
  unsigned handle=(unsigned)p[1]|((unsigned)p[2]<<8);
  /* Asset writes remain sealed. Legacy replacement is delegated only after
     every hardware owner and the firmware pin have actually been released. */
  if((handle>=13&&handle<=19)||!qca_init_adapter_released(&adapter)||port.claimed||port.dma_users||ram.asset.pinned){
   if(!r||capacity<5)return 0;
   r[0]=1;r[1]=p[0];r[2]=p[1];r[3]=p[2];r[4]=3;return p[0]==0x52?0:5;
  }
 }
 return qca_fwp_att(&ram,mtu,p,n,r,capacity);
}

const QcaBootNative*qca_boot_view(void){return &boot;}
unsigned qca_boot_round(void){return boot_round;}
void qca_boot_status(uint8_t out[160]){
 for(unsigned i=0;i<160;i++)out[i]=0;
 const uint8_t magic[8]={'Q','W','B','T','0','0','0','1'};for(unsigned i=0;i<8;i++)out[i]=magic[i];
 uint32_t fields[30]={boot.phase,boot.error,boot.plan.phase,boot.plan.error,boot.plan.submitted,boot.plan.completed,boot.plan.board_address,boot.plan.calibration_result,boot.plan.offset,boot.ready_bytes,boot.credit_count,boot.credit_size,boot.max_endpoints,boot_round,ram.phase,ram.error,ram.asset.ready,ram.asset.pinned,stage,failed,adapter.phase,adapter.channels.cleanup_slot,port.dma_users,setup.bmi.version,setup.bmi.type,board.phase,board.error,board.result,ram.asset.received,boot_once};
 for(unsigned j=0;j<30;j++)for(unsigned i=0;i<4;i++)out[8+j*4+i]=(uint8_t)(fields[j]>>(8*i));
 for(unsigned i=0;i<32;i++)out[128+i]=ram_policy.digest[i];
}

const QcaOperating*qca_operating_view(void){return &operating;}

void qca_operating_status(uint8_t out[488]){
 for(unsigned i=0;i<488;i++)out[i]=0;
 const uint8_t magic[8]={'Q','W','O','P','0','0','0','3'};for(unsigned i=0;i<8;i++)out[i]=magic[i];
 const QcaOperating*s=&operating;const QcaHtcSession*h=&s->control.session;const QcaWmiServiceInfo*w=&s->service;
 uint32_t fields[22]={s->phase,s->error,h->phase,s->control.posted,s->control.deferred_bytes,s->tx_count,s->rx_count,s->service_bytes,s->service_valid,h->wmi.endpoint,h->htt.endpoint,w->build,w->abi_minor,w->chains,w->memory_count,w->regdomain,w->low2,w->high2,w->low5,w->high5,s->control.credit.available,s->control.credit.outstanding};
 for(unsigned j=0;j<22;j++)for(unsigned i=0;i<4;i++)out[8+j*4+i]=(uint8_t)(fields[j]>>(8*i));
 for(unsigned j=0;j<10;j++)for(unsigned i=0;i<4;i++)out[96+j*4+i]=(uint8_t)(s->rx_diagnostic[j]>>(8*i));
 for(unsigned i=0;i<8;i++)out[136+i]=s->rx_descriptor[i];
 for(unsigned i=0;i<64;i++)out[144+i]=s->rx_prefix[i];
 uint32_t av[6]={s->available_seen,s->available.advertised_length,s->available.words[0],s->available.words[1],s->available.words[2],s->available.words[3]};
 for(unsigned j=0;j<6;j++)for(unsigned i=0;i<4;i++)out[208+4*j+i]=(uint8_t)(av[j]>>(8*i));
 if(s->service_valid){
  for(unsigned j=0;j<16;j++){
   const QcaWmiMemoryRequest*m=&s->service.memory[j];uint32_t fields[4]={m->id,m->unit_size,m->unit_flags,m->units};
   for(unsigned k=0;k<4;k++)for(unsigned i=0;i<4;i++)out[232+16*j+4*k+i]=(uint8_t)(fields[k]>>(8*i));
  }
 }else{
  unsigned n=s->service_bytes;if(n>256)n=256;
  for(unsigned i=0;i<n;i++)out[232+i]=s->service_frame[i];
 }
}

const QcaWmiStartup*qca_wmi_startup_view(void){return &startup;}

void qca_wmi_status(uint8_t out[244]){
 for(unsigned j=0;j<244;j++)out[j]=0;
 const uint8_t magic[8]={'Q','W','I','N','0','0','0','2'};for(unsigned j=0;j<8;j++)out[j]=magic[j];
 const QcaWmiStartup*s=&startup;const QcaWmiInitTransaction*t=&s->transaction;
 uint32_t fields[12]={s->phase,s->error,t->phase,s->tx_posted,s->tx_count,s->rx_count,t->ready_seen,t->tx_complete,t->ready.abi_minor,operating.control.credit.available,operating.control.credit.outstanding,operating.service.memory_count};
 for(unsigned j=0;j<12;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(fields[j]>>(8*k));
 for(unsigned j=0;j<6;j++)out[56+j]=t->ready.mac[j];
 for(unsigned j=0;j<8;j++)for(unsigned k=0;k<4;k++)out[64+4*j+k]=(uint8_t)(s->diagnostic[j]>>(8*k));
 const uint32_t diag[5]={s->reject_reason,s->frame_bytes,s->prefix_bytes,s->frame_endpoint,s->payload_bytes};
 for(unsigned j=0;j<5;j++)for(unsigned k=0;k<4;k++)out[96+4*j+k]=(uint8_t)(diag[j]>>(8*k));
 for(unsigned j=0;j<128;j++)out[116+j]=s->prefix[j];
}

static unsigned prefix_released(void){
 if(!boot_round||!prefix.phase||!qca_init_adapter_released(&adapter)||adapter.phase!=QCA_INIT_CLOSED
  ||adapter.channels.cleanup_slot!=14||port.claimed||port.dma_users||adapter.access.count||adapter.bus.owned
  ||boot.owns_pin||ram.asset.pinned||qca_fwp_owned(&ram)||irq.owned||link.owned||wake.owned||reset.owned)return 0;
 for(unsigned i=0;i<14;i++)if(adapter.channels.buffers[i].allocated||adapter.channels.buffers[i].mapped||adapter.channels.buffers[i].allocation_uncertain)return 0;
 return 1;
}
void qca_prefix_status(uint8_t out[240]){
 for(unsigned i=0;i<240;i++)out[i]=0;
 const uint8_t magic[8]={'Q','P','F','X','0','0','0','1'};for(unsigned i=0;i<8;i++)out[i]=magic[i];
 unsigned held=0;for(unsigned i=0;i<14;i++)if(adapter.channels.buffers[i].allocated||adapter.channels.buffers[i].mapped||adapter.channels.buffers[i].allocation_uncertain)held++;
 const QcaPrefix*p=&prefix;
 uint32_t f[58]={64,p->phase,p->reason,p->stop_calls,prefix_released(),p->stop_offset,p->stop_submitted,p->stop_completed,p->stop_plan,p->stop_io,
 boot.phase,boot.error,boot.plan.phase,boot.plan.error,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.io.wire.phase,
 stage,failed,adapter.phase,adapter.channels.cleanup_slot,held,port.dma_users,port.claimed,adapter.access.count,adapter.bus.owned,
 boot.owns_pin,ram.asset.pinned,irq.owned,link.owned,wake.owned,reset.owned,
 p->ble_state,p->pending,p->connected,p->credits,p->inflight,p->stream_used,p->stream_goal,p->usb_polls,p->usb_reads,p->usb_timeouts,p->usb_observation,
 (uint32_t)p->last_usb_status,(uint32_t)(p->last_usb_status>>32),p->last_usb_result,p->last_usb_bytes,
 p->raw_count,p->raw_overflow,p->usb_fault,p->frames,(uint32_t)p->max_poll_us,(uint32_t)p->max_qca_us,
 (uint32_t)p->started,(uint32_t)(p->started>>32),(uint32_t)p->last,(uint32_t)(p->last>>32)};
 for(unsigned j=0;j<58;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(f[j]>>(8*k));
}

const QcaPersistentNative*qca_persistent_view(void){return &persistent;}
static unsigned actual_released(void){return persistent.life.phase==QCA_RADIO_CLOSED&&prefix_released();}
static uint32_t pipeline_phase,pipeline_error,filter_attempted;

static QcaHttDataPath*data_path;static void*data_pool_raw;static size_t data_pool_bytes;static unsigned data_pool_uncertain;
static int data_overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x<y?y-x<n:x-y<m;}
static int data_pool_prepare(SystemTable*st){
 if(data_path)return 1;
 if(data_pool_raw||data_pool_uncertain)return 0;
 QcaHttPoolBoot boot_api;if(!qca_htt_pool_boot(st,&boot_api))return 0;
 data_pool_bytes=sizeof(QcaHttDataPath)+_Alignof(QcaHttDataPath)-1;
 if(data_pool_bytes>131072)return 0;
 void*raw=0;Status rc=boot_api.allocate(2,data_pool_bytes,&raw);data_pool_raw=raw;
 uintptr_t v=(uintptr_t)raw;
 if(rc||!raw||v>UINTPTR_MAX-data_pool_bytes){data_pool_uncertain=raw!=0;return 0;}
 uintptr_t old=(uintptr_t)runtime_phase.raw;size_t n=runtime_phase.bytes;
 if(old&&((v<old&&old-v<data_pool_bytes)||(v>=old&&v-old<n))){data_pool_uncertain=1;return 0;}
 if(data_overlap(raw,data_pool_bytes,&runtime_phase,sizeof(runtime_phase))||data_overlap(raw,data_pool_bytes,&port,sizeof(port))||data_overlap(raw,data_pool_bytes,st,sizeof(*st))||data_overlap(raw,data_pool_bytes,&boot_api,sizeof(boot_api))||data_overlap(raw,data_pool_bytes,&data_path,sizeof(data_path))||data_overlap(raw,data_pool_bytes,&data_pool_raw,sizeof(data_pool_raw))||data_overlap(raw,data_pool_bytes,&data_pool_bytes,sizeof(data_pool_bytes))||data_overlap(raw,data_pool_bytes,&data_pool_uncertain,sizeof(data_pool_uncertain))){data_pool_uncertain=1;return 0;}
 QcaHttRuntime*r=&runtime_phase.arena->runtime;
 for(unsigned j=0;j<14+33;j++){QcaDmaBuffer*d=j<14?&r->ce[j]:&r->extra[j-14];if(d->host&&data_overlap(raw,data_pool_bytes,d->host,(size_t)d->bytes)){data_pool_uncertain=1;return 0;}}
 uintptr_t aligned=(v+_Alignof(QcaHttDataPath)-1)&~(uintptr_t)(_Alignof(QcaHttDataPath)-1);
 data_path=(QcaHttDataPath*)aligned;for(size_t i=0;i<data_pool_bytes;i++)((volatile uint8_t*)raw)[i]=0;return 1;
}
#ifdef RABBIT_PREFIX_DRIVER_MODEL
QcaHttDataPath*data_model_view(void){return data_path;}
unsigned data_model_uncertain(void){return data_pool_uncertain;}
#endif
static int data_pool_retire(void){
 if(data_pool_uncertain)return 0;
 if(!data_pool_raw)return !data_path;
 if(!data_path||data_pool_bytes!=sizeof(QcaHttDataPath)+_Alignof(QcaHttDataPath)-1||port.claimed||port.dma_users)return 0;
 for(size_t i=0;i<sizeof(*data_path);i++)if(((const uint8_t*)data_path)[i])return 0;
 QcaHttPoolBoot api;if(!qca_htt_pool_boot(ram_system,&api))return 0;
 /* Revoke the only native callback getter before wipe/free. */
 data_path=0;for(size_t i=0;i<data_pool_bytes;i++)((volatile uint8_t*)data_pool_raw)[i]=0;
 if(api.release(data_pool_raw)){data_pool_uncertain=1;return 0;}data_pool_raw=0;data_pool_bytes=0;return 1;
}
static void data_native_step(uint64_t now){
 if(!data_path)return;
 if(pipeline_phase==6){
  if(data_path->phase==QDP_FILLING){
   for(unsigned i=0;i<16&&data_path->runtime->ring.fill<1023;i++)if(!qdp_refill_initial(data_path,now)){qdp_quarantine(data_path,100);return;}
   if(data_path->runtime->ring.fill==1023&&qdp_publish_cfg(data_path,now)<0)return;
  }
  if(data_path->phase==QDP_CFG_POSTED||data_path->phase==QDP_AGGR_POSTED||data_path->tx_posted)(void)qdp_poll_dma(data_path,now);
  if(data_path->phase==QDP_RX_ACTIVE&&!data_path->aggr_done){(void)qdp_publish_aggr(data_path,now);return;}
  if(data_path->phase==QDP_RX_ACTIVE){
   if(!native_scan.phase&&!qca_native_scan_begin(&native_scan,&persistent,now)){qdp_quarantine(data_path,103);return;}

   if(persistent.rx.count){const QcaRxEvent*e=&persistent.rx.events[persistent.rx.head];
    if(e->pipe==1&&e->endpoint==data_path->binding.endpoint&&e->bytes&&(e->payload[0]==7||e->payload[0]==0x12)){
     int rc=qdp_receive(data_path,e,now);if(!rc)return; /* targeted HTT head remains owned under output backpressure */
     if(rc){QcaRxEvent copy;if(!qca_rx_take(&persistent.rx,e->completion,&copy,sizeof(copy))){qdp_quarantine(data_path,101);return;}}
    }
   }
   (void)qdp_copy_one(data_path,now);
   if(native_scan.phase!=QCA_NATIVE_SCAN_LIVE_DONE){int rc=qca_native_scan_poll(&native_scan,now);if(rc<0||native_scan.error){qdp_quarantine(data_path,104);return;}}

  }
 }
}

#define filter (runtime_phase.arena->filter)
int qca_filter64_archive_take(QcaPersistentRx*r,uint32_t completion){
 if(r!=&persistent.rx||native_scan.epoch!=persistent.epoch||native_scan.archive_count>=16)return 0;
 if(!qca_rx_take(r,completion,&native_scan.archive[native_scan.archive_count],sizeof(QcaRxEvent)))return 0;
 native_scan.archive_count++;return 1;
}
static int archive_owned(const QcaRxEvent*e){
 if(!e||!e->completion||native_scan.archive_count>=16||native_scan.epoch!=persistent.epoch)return 0;
 for(unsigned i=0;i<native_scan.archive_count;i++)if(native_scan.archive[i].completion==e->completion)return 0;
 native_scan.archive[native_scan.archive_count++]=*e;return 1;
}
static void pipeline_fault(unsigned error,uint64_t now){
 if(!pipeline_error)pipeline_error=error;
 pipeline_phase=5;native_scan.error=error;native_scan.phase=QCA_NATIVE_SCAN_FAULT;native_scan.quiesce_requested=1;
 qca_prefix_request(&prefix,3,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.phase,boot.io.wire.phase);
 (void)qca_persistent_quiesce(&persistent,now);(void)qca_stop();
}
static void qca_filter64_step(uint64_t now){
 if(!runtime_phase.arena)return;
 if(qca_radio_accepts_work(&persistent.life)&&!data_pool_prepare(port.system)){pipeline_fault(190,now);return;}
 if(pipeline_phase==6){data_native_step(now);return;}
 if(!pipeline_phase&&qca_radio_accepts_work(&persistent.life)){
  filter_attempted=1;native_scan.radio=&persistent;native_scan.epoch=persistent.epoch;
  QcaHtcFrame ready={0};
  if(!startup.transaction.ready_seen||!startup.transaction.tx_complete||!startup.ready_frame_bytes||startup.ready_frame_bytes>128||!qca_htc_decode(startup.prefix,startup.ready_frame_bytes,&ready)
    ||!qca_tx_begin(&native_scan.tx,&persistent,now)
    ||!qca_filter_begin(&filter,&operating.control.credit,ready.payload,ready.payload_bytes,persistent.epoch,persistent.rx.completed,0x64000001u,now)){pipeline_fault(101,now);return;}
  pipeline_phase=1;
 }
 if(pipeline_phase==1){
  if(qca_filter_poll(&filter,persistent.epoch,now)<0){pipeline_fault(102,now);return;}
  QcaPersistentTx*t=&native_scan.tx;
  if((filter.phase==QCA_FILTER_READY||filter.phase==QCA_FILTER_ORDERED)&&t->phase==QCA_TX_IDLE){
   uint32_t id=0;if(!qca_filter_prepare(&filter,persistent.epoch,now)||!qca_tx_submit(t,filter.frame,filter.frame_bytes,now,2000000,&id)||!qca_filter_submitted(&filter,persistent.epoch,id,now)){pipeline_fault(103,now);return;}
  }
  if(t->phase!=QCA_TX_IDLE){
   int rc=qca_tx_poll(t,now);if(rc<0){pipeline_fault(104,now);return;}
   /* Immediately after actual POSTED transition, before another RX pump. */
   if(t->phase==QCA_TX_POSTED&&filter.phase==QCA_FILTER_SUBMITTED&&!qca_filter_post(&filter,persistent.epoch,t->request,persistent.rx.completed,t->frame,t->bytes,now)){pipeline_fault(105,now);return;}
   if(rc==1){if(!qca_filter_tx_complete(&filter,persistent.epoch,t->request,t->bytes,now)||!qca_tx_retire(t,t->request)){pipeline_fault(106,now);return;}}
  }
  for(unsigned i=0;i<2&&persistent.rx.count;i++){
   QcaRxEvent e;
   uint32_t id=persistent.rx.events[persistent.rx.head].completion;
   if(native_scan.archive_count>=16||!qca_rx_take(&persistent.rx,id,&e,sizeof(e))){pipeline_fault(107,now);return;}
   int rc=qca_filter_receive(&filter,persistent.epoch,e.completion,e.pipe,e.raw,e.raw_bytes,now);
   if(!archive_owned(&e)){pipeline_fault(108,now);return;}
   if(rc<0){pipeline_fault(109,now);return;}
  }
  if(qca_filter_passed(&filter)){
   if(native_scan.tx.phase!=QCA_TX_IDLE||native_scan.tx.request!=filter.last_request||native_scan.tx.completed!=3||native_scan.tx.attempted!=3){pipeline_fault(110,now);return;}
   htt_attempted=1;
   if(native_scan.archive_count>13||!qca_htt_firmware_proof(&htt_proof,&boot)||!qca_htt_native_begin(&htt_query,&persistent,htt_proof.htt_op,now,&native_scan.archive[13],3)){pipeline_fault(111,now);return;}
   pipeline_phase=2;
  }
 }
 if(pipeline_phase==2){
  int rc=qca_htt_native_poll(&htt_query,now);
  /* Preserve taken HTT bytes on both success and failure, before fault export. */
  if(rc<0){
   if(!qca63_query_handover(&native_scan,&htt_query)){pipeline_fault(114,now);return;}
  }
  if(rc<0){pipeline_fault(112,now);return;}
  if(rc==1){
   if(htt_query.phase!=QCA_HTTN_READY||!htt_query.version_seen||!htt_query.dma_completed||htt_query.stop_requested||htt_query.version.major!=3||htt_query.version.minor!=56||htt_query.epoch!=persistent.epoch){pipeline_fault(113,now);return;}
   if(!qdp_begin(data_path,&runtime_phase.arena->runtime,&persistent,&htt_query,&native_scan,now)){if(htt_query.response&&!qca63_query_handover(&native_scan,&htt_query)){pipeline_fault(192,now);return;}pipeline_fault(191,now);return;}
   pipeline_phase=6;
  }
 }
 if(pipeline_phase==3&&!native_scan.quiesce_requested&&qca_native_scan_poll(&native_scan,now)){
  qca_prefix_request(&prefix,native_scan.error?3:0,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.phase,boot.io.wire.phase);(void)qca_stop();
 }
 if(native_scan.quiesce_requested&&actual_released()){
  if(!pipeline_error&&!native_scan.error&&qca_filter_passed(&filter)&&htt_query.phase==QCA_HTTN_READY){native_scan.phase=QCA_NATIVE_SCAN_RELEASED;pipeline_phase=4;}
  else pipeline_phase=5;
 }
}

const QcaNativeScan*qca_scan_native_view(void){return runtime_phase.arena?&native_scan:0;}
unsigned qca_scan_export(unsigned page,uint8_t*out,unsigned cap){return runtime_phase.arena?qca_native_scan_export(&native_scan,page,out,cap):qca_htt_phase_empty_raw(page,out,cap);}
void qca_scan_status(uint8_t out[416]){
 if(!runtime_phase.arena){for(unsigned i=0;i<416;i++)out[i]=0;const uint8_t magic[8]={'Q','S','C','N','0','0','0','1'};for(unsigned i=0;i<8;i++)out[i]=magic[i];out[248]=64;out[252]=13;for(unsigned j=0;j<32;j++){out[264+j]=scan_policy.reviewed_digest[j];out[296+j]=scan_policy.ruleset_digest[j];out[328+j]=scan_policy.location_digest[j];}return;}

 for(unsigned j=0;j<416;j++)out[j]=0;
 const uint8_t magic[8]={'Q','S','C','N','0','0','0','1'};for(unsigned j=0;j<8;j++)out[j]=magic[j];
 const QcaNativeScan*s=&native_scan;const QcaScanCoordinator*c=&s->scan;const QcaPersistentTx*t=&s->tx;const QcaPersistentRx*r=&persistent.rx;
 uint32_t held=0;for(unsigned j=0;j<14;j++)if(adapter.channels.buffers[j].allocated||adapter.channels.buffers[j].mapped||adapter.channels.buffers[j].allocation_uncertain)held++;
 uint32_t f[64]={s->phase,s->error,s->stop_requested,s->quiesce_requested,actual_released(),
 c->phase,c->error,c->stage,c->request,t->phase,t->error,t->request,t->attempted,t->completed,
 c->pending.phase,c->pending.result,c->pending.started,c->pending.last_event.type,c->pending.last_event.reason,
 c->pending.last_event.frequency,c->pending.last_event.request_id,c->pending.last_event.scan_id,c->pending.last_rx,
 c->start_floor,c->live_frequency,c->stop.stop.phase,c->stop.stop.terminal_seen,c->stop.stop.tx_complete,
 c->stop.terminal_completion,c->ssid_seen,c->has_observation,(c->has_orphan||r->rejected.raw_bytes),c->dispatch.count,s->archive_count,
 r->phase,r->error,r->completed,r->posted_count,r->count,r->backpressure,
 operating.control.credit.available,operating.control.credit.outstanding,operating.control.credit.reserved,operating.control.credit.total,
 held,port.dma_users,port.claimed,wake.owned,link.owned,irq.owned,boot.owns_pin,adapter.bus.owned,adapter.access.count,
 adapter.phase,adapter.channels.cleanup_slot,persistent.life.phase,persistent.life.error,persistent.error,
 startup.transaction.ready_seen,startup.transaction.tx_complete,64,13,0,0};
 for(unsigned j=0;j<64;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(f[j]>>(8*k));
 for(unsigned j=0;j<32;j++){out[264+j]=scan_policy.reviewed_digest[j];out[296+j]=scan_policy.ruleset_digest[j];out[328+j]=scan_policy.location_digest[j];}
 if(c->has_observation){const QcaBeaconInfo*b=&c->observation.parsed.bss;out[360]=(uint8_t)b->ssid_bytes;
  for(unsigned j=0;j<32;j++)out[364+j]=j<b->ssid_bytes?b->ssid[j]:0;
  for(unsigned j=0;j<6;j++)out[396+j]=b->bssid[j];
 }
}

void qca_filter64_status(uint8_t out[544]){
 if(!runtime_phase.arena){qca_htt_phase_empty_pipeline(out,64);out[398]=10;const uint8_t plan[10]={'i','P','h','o','n','e',' ','(','9',')'};for(unsigned i=0;i<10;i++)out[400+i]=plan[i];return;}

 for(unsigned i=0;i<544;i++)out[i]=0;
 const uint8_t magic[8]={'Q','F','6','4','0','0','0','1'};for(unsigned i=0;i<8;i++)out[i]=magic[i];
 const QcaPersistentTx*t=&native_scan.tx;uint32_t held=0;
 for(unsigned i=0;i<14;i++)if(adapter.channels.buffers[i].allocated||adapter.channels.buffers[i].mapped||adapter.channels.buffers[i].allocation_uncertain)held++;
 uint32_t f[64]={pipeline_phase,pipeline_error,filter_attempted,filter.phase,filter.error,filter.step,
 filter.tx_count,filter.tx_completed,filter.echo_seen,filter.initial_floor,filter.echo_floor,filter.last_rx,filter.raw_completion,filter.raw_bytes,filter.raw_pipe,filter.raw_endpoint,
 filter.tx_request,filter.last_request,filter.credit_serial,filter.echo_arg,t->phase,t->error,t->serial,t->request,t->attempted,t->completed,
 htt_query.phase,htt_query.error,htt_query.attempted,htt_query.dma_completed,htt_query.version_seen,htt_query.version.major,htt_query.version.minor,htt_query.watermark,htt_query.response_completion,htt_query.binding.endpoint,htt_query.binding.max_bytes,htt_query.binding.op_version,
 htt_proof.valid,htt_proof.error,(uint32_t)htt_proof.generation,(uint32_t)(htt_proof.generation>>32),(uint32_t)persistent.epoch,(uint32_t)(persistent.epoch>>32),actual_released(),held,port.dma_users,adapter.access.count,port.claimed,adapter.bus.owned,
 wake.owned,link.owned,irq.owned,boot.owns_pin,ram.asset.pinned,adapter.phase,adapter.channels.cleanup_slot,persistent.life.phase,persistent.life.error,64,operating.service.service_count,persistent.rx.error,persistent.rx.completed,persistent.error};
 for(unsigned i=0;i<64;i++)for(unsigned k=0;k<4;k++)out[8+4*i+k]=(uint8_t)(f[i]>>(8*k));
 for(unsigned i=0;i<32&&i<operating.service.service_count;i++)for(unsigned k=0;k<4;k++)out[264+4*i+k]=(uint8_t)(operating.service.service_words[i]>>(8*k));
 for(unsigned i=0;i<6;i++)out[392+i]=filter.mac[i];
 out[398]=10;
 const uint8_t requested[10]={'i','P','h','o','n','e',' ','(','9',')'};for(unsigned i=0;i<10;i++)out[400+i]=requested[i];
 uint32_t echo_slot=UINT32_MAX,version_slot=UINT32_MAX;
 for(unsigned i=0;i<native_scan.archive_count;i++){if(native_scan.archive[i].completion==filter.raw_completion)echo_slot=i;if(native_scan.archive[i].completion==htt_query.response_completion)version_slot=i;}
 for(unsigned k=0;k<4;k++){out[432+k]=(uint8_t)(echo_slot>>(8*k));out[436+k]=(uint8_t)(version_slot>>(8*k));}
 uint64_t clocks[12]={filter.started,filter.overall_deadline,filter.stage_started,filter.stage_deadline,filter.echo_posted,filter.echo_deadline,filter.last_poll,filter.maximum_poll_gap,filter.tx_complete_observed,filter.echo_observed,filter.timeout_observed,qca_filter_effective_deadline(&filter)};
 for(unsigned i=0;i<12;i++)for(unsigned k=0;k<8;k++)out[448+i*8+k]=(uint8_t)(clocks[i]>>(k*8));
 out[440]=1; /* Explicit PARTIAL startup: no RX_RING_CFG or aggregation. */
}

#ifdef RABBIT_PREFIX_DRIVER_MODEL
const QcaHttPhaseOwner*runtime_phase_model(void){return &runtime_phase;}
#endif
int runtime_rng_public(RngPublicDiagnostic*out){
 if(!out||!runtime_phase.arena||!runtime_phase.arena->rng.attempted)return 0;
 *out=runtime_phase.arena->rng.diagnostic;return 1;
}
static int runtime_extra_stop(void*context){
 QcaHttRuntime*r=context;
 /* Target configuration needs a real target halt backend, not CE-only proof. */
 if(data_pool_uncertain||r->ring.cfg_posted||r->callback_owners||r->rx_copy_owners||r->tx_owners)return -1;
 return qca_ce_bus_released(&adapter.bus);
}
int runtime_extra_prepare(QcaInitAdapter*a){
 if(a!=&adapter||!runtime_phase.arena)return -1;
 QcaHttRuntime*r=&runtime_phase.arena->runtime;
 /* Initial read-only probe may close all extra maps before firmware acquisition.
  * Reuse only before filter/query/scan has begun, with every extra owner closed. */
 if(r->phase==HTT_RUNTIME_CLOSED){
  if(!qca_htt_runtime_detachable(r)||filter.phase||pipeline_phase||native_scan.phase||htt_query.phase)return -1;
  for(size_t j=0;j<sizeof(*r);j++)((uint8_t*)r)[j]=0;
 }
 if(!r->phase&&!qca_htt_runtime_begin(r,&port,a->channels.buffers,persistent.epoch?persistent.epoch:1,runtime_extra_stop,r))return -1;
 if(r->phase==HTT_RUNTIME_ALLOCATING){int rc=qca_htt_runtime_allocate_one(r);if(rc<0)return -1;return r->phase==HTT_RUNTIME_MAPPED?1:0;}
 return r->phase==HTT_RUNTIME_MAPPED&&qca_htt_runtime_inventory(r)?1:-1;
}
int runtime_extra_retained(QcaChannels*c){
 if(c!=&adapter.channels)return 0;
 if(!runtime_phase.arena)return port.dma_users==14;
 QcaHttRuntime*r=&runtime_phase.arena->runtime;
 if(!r->phase||r->phase==HTT_RUNTIME_CLOSED)return port.dma_users==14;
 return r->phase==HTT_RUNTIME_MAPPED&&qca_htt_runtime_inventory(r);
}
int runtime_extra_cleanup(QcaInitAdapter*a){
 if(a!=&adapter)return -1;
 if(!runtime_phase.arena)return 1;
 QcaHttRuntime*r=&runtime_phase.arena->runtime;
 if(!r->phase||r->phase==HTT_RUNTIME_CLOSED)return 1;
 if(r->ring.cfg_posted)return -1; /* No target-halt fabrication. */
 if(!qca_htt_runtime_close_one(r))return -1;
 return r->phase==HTT_RUNTIME_CLOSED?1:0;
}
int runtime_extra_snapshot(QcaPersistentNative*p,QcaRadioOwners*out){
 if(p!=&persistent||!out||!runtime_phase.arena)return 0;
 QcaHttRuntime*r=&runtime_phase.arena->runtime;
 if(!r->phase)return 0;
 QcaRadioOwners next;if(!qca_htt_owner47_snapshot(r,out,&next))return 0;*out=next;return 1;
}
static int data_runtime_retirable(const QcaHttRuntime*r){
 if(r->phase)return qca_htt_runtime_detachable(r);
 for(size_t i=0;i<sizeof(*r);i++)if(((const uint8_t*)r)[i])return 0;
 return 1;
}
int runtime_phase_retire(void){
 if(!data_pool_retire())return 0;
 if(!runtime_phase.arena)return !runtime_phase.uncertain;
 if(runtime_phase.capture_readers||!data_runtime_retirable(&runtime_phase.arena->runtime)||!qca_htt_public_rng_cleanup(&runtime_phase.arena->rng))return 0;
 /* Captured queue remains readable until this explicit retirement. This
  * original clear primitive admits only CLOSED actual all-owner lifecycle. */
 if(persistent.rx.phase&&!qca_rx_clear(&persistent.rx,&persistent.life))return 0;
 if(!qca_htt_phase_detach(&runtime_phase,&htt_query))return 0;
 return qca_htt_phase_release(&runtime_phase);
}
