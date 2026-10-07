"""Offline57: authenticated boot-prefix only; no HTC/INIT/scan entrypoint calls."""
import importlib.util,sys,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent;E=ROOT.parent;BASE=E/'native-wifi-qca9377-v1';CHECKED=E/'native-wifi-qca9377-wmi-native-v5'
sys.path.insert(0,str(CHECKED));import startup_build as checked
one=checked.one
FILES=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c','full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','boot_gatt.c','operating.c','operating_gatt.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c','prefix.c','prefix_gatt.c')
def policy():
 p=json.loads((ROOT/'receiver-policy.json').read_bytes())
 if p!={**checked.policy(),'generation':57}:raise ValueError('exact reviewed public57 firmware policy required')
 return p
def sources(d):
 checked.sources(d)
 for n in ('prefix.h','prefix.c','prefix_gatt.c','overlay.h'):(d/n).write_bytes((ROOT/n).read_bytes())
 p=d/'init_probe.c';s=p.read_text();s=one(s,'.generation=52ull','.generation=57ull');s=one(s,'#include "startup.h"','#include "startup.h"\n#include "prefix.h"')
 s=one(s,'static QcaWmiStartup startup;','static QcaWmiStartup startup;\nstatic QcaPrefix prefix;\nQcaPrefix*qca_prefix_view(void){return &prefix;}\nstatic unsigned prefix_released(void);')
 start=s.index('     rc=qca_boot_native_poll(&boot,now);');end=s.index('\n    }\n   }\n   if(rc)',start)
 s=s[:start]+'''     if(!prefix.phase&&boot.phase==1&&boot.owns_pin&&ram.asset.pinned)qca_prefix_arm(&prefix,now);
     if(qca_prefix_tick(&prefix,now,boot.phase,boot.plan.phase,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.pending,boot.io.wire.phase,0))rc=-1;
     else {
      rc=qca_boot_native_poll(&boot,now);
      if(rc){qca_prefix_request(&prefix,rc<0?3:4,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.phase,boot.io.wire.phase);rc=-1;}
      else if(qca_prefix_tick(&prefix,now,boot.phase,boot.plan.phase,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.pending,boot.io.wire.phase,0))rc=-1;
     }
     /* No operating/startup/HTC/INIT branch is reachable in this profile. */''' +s[end:]
 s=one(s,' qca_hardware_poll(ms);',''' qca_hardware_poll(ms);
 if(prefix.phase==2){
  if(prefix.stop_calls!=UINT32_MAX)prefix.stop_calls++;
  (void)qca_stop();
  (void)qca_prefix_tick(&prefix,ms*1000,boot.phase,boot.plan.phase,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.pending,boot.io.wire.phase,prefix_released());
 }''')
 s+='''
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
 uint32_t f[58]={57,p->phase,p->reason,p->stop_calls,prefix_released(),p->stop_offset,p->stop_submitted,p->stop_completed,p->stop_plan,p->stop_io,
 boot.phase,boot.error,boot.plan.phase,boot.plan.error,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.io.wire.phase,
 stage,failed,adapter.phase,adapter.channels.cleanup_slot,held,port.dma_users,port.claimed,adapter.access.count,adapter.bus.owned,
 boot.owns_pin,ram.asset.pinned,irq.owned,link.owned,wake.owned,reset.owned,
 p->ble_state,p->pending,p->connected,p->credits,p->inflight,p->stream_used,p->stream_goal,p->usb_polls,p->usb_reads,p->usb_timeouts,p->usb_observation,
 (uint32_t)p->last_usb_status,(uint32_t)(p->last_usb_status>>32),p->last_usb_result,p->last_usb_bytes,
 p->raw_count,p->raw_overflow,p->usb_fault,p->frames,(uint32_t)p->max_poll_us,(uint32_t)p->max_qca_us,
 (uint32_t)p->started,(uint32_t)(p->started>>32),(uint32_t)p->last,(uint32_t)(p->last>>32)};
 for(unsigned j=0;j<58;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(f[j]>>(8*k));
}
'''
 p.write_text(s)
 p=d/'diagnostic_gatt.c';s=p.read_text();s=one(s,'#include "pci_collect.h"','#include "pci_collect.h"\nsize_t qca_prefix_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);')
 s=one(s,'if(s){size_t init=qca_wmi_att','if(s){size_t diag=qca_prefix_att(s->mtu,p,n,r,capacity);if(diag!=SIZE_MAX)return diag;}\n if(s){size_t init=qca_wmi_att');p.write_text(s)
def driver_sources(d):
 sources(d);checked.prior.bt_usb_build.sources(d)
 (d/'ble_recovery_link.c').write_text(checked.prior.prior.ble.link_source())
 p=d/'usb_port.c';s=p.read_text();s=one(s,'static void poll_event(void*context,const uint8_t*event,unsigned n){rl_event((RlLink*)context,event,n);}', 'void qca_prefix_hci(const uint8_t*,unsigned,const RlLink*);\nstatic void poll_event(void*context,const uint8_t*event,unsigned n){RlLink*l=context;qca_prefix_hci(event,n,l);rl_event(l,event,n);}')
 p.write_text(s)
 p=d/'driver.c';s=p.read_text();s=one(s,'static RlUsb radio_port;','''static RlUsb radio_port;
#ifdef RABBIT_PREFIX_DRIVER_MODEL
static uint32_t prefix_model_ms;
static uint32_t prefix_clock_ms(void){return prefix_model_ms;}
#else
static uint32_t prefix_clock_ms(void){return city_clock_ms();}
#endif
''');s=one(s,'static RlLink radio_link;', 'static RlLink radio_link;\n#include "prefix.h"\nQcaPrefix*qca_prefix_view(void);\nvoid qca_prefix_status(uint8_t[240]);\n#include "overlay.h"\nvoid qca_prefix_hci(const uint8_t*p,unsigned n,const RlLink*l){qca_prefix_event(qca_prefix_view(),p,n,((uint64_t)prefix_clock_ms())*1000,l->state,l->pending);}')
 s=one(s,' qca_poll(city_clock_ms());',''' QcaPrefix*diag=qca_prefix_view();uint64_t began=((uint64_t)prefix_clock_ms())*1000;
 qca_poll(began/1000);uint64_t after_qca=((uint64_t)prefix_clock_ms())*1000;
 diag->poll_before=began;
 if(after_qca>=began&&after_qca-began>diag->max_qca_us)diag->max_qca_us=after_qca-began;''')
 s=one(s,' int result=rl_usb_poll(&radio_port,&radio_link);',''' int result=rl_usb_poll(&radio_port,&radio_link);
 uint64_t ended=((uint64_t)prefix_clock_ms())*1000;
 diag->poll_after=ended;
 if(ended>=began&&ended-began>diag->max_poll_us)diag->max_poll_us=ended-began;
 diag->ble_state=radio_link.state;diag->pending=radio_link.pending;diag->connected=radio_link.connected;
 diag->credits=radio_link.credits;diag->inflight=radio_link.inflight;
 diag->stream_used=radio_port.event_stream.used;diag->stream_goal=radio_port.event_stream.goal;
 diag->usb_polls=radio_port.polls;diag->usb_reads=radio_port.event_reads;diag->usb_timeouts=radio_port.event_timeouts;
 diag->usb_observation=radio_port.observation_sequence;diag->last_usb_status=radio_port.observation.status;
 diag->last_usb_result=radio_port.observation.result;diag->last_usb_bytes=radio_port.observation.reported_length;
 if(result){diag->usb_fault=(unsigned)result;qca_prefix_request(diag,6,0,0,0,0,0);(void)qca_stop();}''')
 s=one(s,' r->init=driver_init;r->tick=scene_tick;r->frame=scene_frame;', ' r->init=driver_init;r->tick=prefix_tick_frame;r->frame=prefix_frame;');s+='''
#ifdef RABBIT_PREFIX_DRIVER_MODEL
void prefix_driver_model_bind(void*io){radio_port=(RlUsb){.io=io,.bound=1,.events=0x81,.in=0x82,.out=2};rl_init(&radio_link,0);radio_link.state=RL_CONNECTED;radio_link.connected=1;radio_link.handle=1;radio_link.buffers=radio_link.credits=8;radio_link.acl_size=64;}
int prefix_driver_model_poll(uint32_t ms){prefix_model_ms=ms;return poll_radio();}
void prefix_driver_model_display(uint32_t*physical,unsigned w,unsigned h,unsigned stride){city_physical=physical;city_width=w;city_height=h;city_stride=stride;city_format=1;}
int prefix_driver_model_world(const uint8_t*p,uint32_t n,Surface*s){uint32_t counter=0;return world(p,n,s,&counter);}
int prefix_driver_model_frame(Surface*s){return prefix_tick_frame(s);}
#endif
''';p.write_text(s)
def compile_driver(d,crypto):
 driver_sources(d);a=checked.prior.actors
 payload=a.compile_efi(d,'boot-prefix57',[d/'driver.c',d/'city_core.c',d/'pci_collect.c',d/'pci_identity.c',*[d/n for n in FILES],d/'usb_port.c',d/'bt_event_stream.c',d/'ble_recovery_link.c',d/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
 off=struct.unpack_from('<I',payload,60)[0]
 if len(payload)>262144 or struct.unpack_from('<I',payload,off+80)[0]>4*1024*1024:raise ValueError('wire/mapped bound')
 return payload
