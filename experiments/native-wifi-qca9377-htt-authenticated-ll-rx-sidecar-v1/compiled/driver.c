#include "data_path.h"
static void*volatile data_linked_methods[]={qdp_submit_raw,qdp_submit_mgmt,qdp_take_frame,qdp_quarantine};
/* Scene + HCI/ACL/ATT/USB are one owner-updateable UEFI driver. */
#include "connected_abi.h"
#include "usb_port.h"
#define module_entry legacy_scene_entry
#include "scene_module.c"
#undef module_entry
#include "city_display.c"
#include "actor_clock.c"
void qca_collect(SystemTable*);
#include "bringup.h"
static RlUsb radio_port;
#ifdef RABBIT_PREFIX_DRIVER_MODEL
static uint32_t prefix_model_ms;
static uint32_t prefix_clock_ms(void){return prefix_model_ms;}
#else
static uint32_t prefix_clock_ms(void){return city_clock_ms();}
#endif

static RlLink radio_link;
#include "prefix.h"
QcaPrefix*qca_prefix_view(void);
void qca_prefix_status(uint8_t[240]);
#include "overlay.h"
void qca_prefix_hci(const uint8_t*p,unsigned n,const RlLink*l){qca_prefix_event(qca_prefix_view(),p,n,((uint64_t)prefix_clock_ms())*1000,l->state,l->pending);}
static SystemTable*diagnostic_system;
static unsigned traces_printed,masks_printed;
static void diagnostic(const char*text){
 if(active_length&&(active_package[4]==4||active_package[4]==5))return;
 typedef Status(EFIAPI *Output)(void*,const uint16_t*);
 uint16_t line[160];unsigned i=0;
 while(text[i]&&i<159){line[i]=(uint8_t)text[i];i++;}line[i]=0;
 if(diagnostic_system&&diagnostic_system->output)
  ((Output)*(void**)((uint8_t*)diagnostic_system->output+8))(diagnostic_system->output,line);
}
static void diagnostic_value(const char*label,uint32_t value){
 char line[100];unsigned i=0;
 while(label[i]&&i<80){line[i]=label[i];i++;}
 for(unsigned j=0;j<8;j++)line[i++]="0123456789ABCDEF"[(value>>(28-4*j))&15];
 line[i++]='\r';line[i++]='\n';line[i]=0;diagnostic(line);
}
static unsigned hex(char*out,unsigned at,uint64_t value,unsigned digits){
 for(unsigned j=0;j<digits;j++)out[at++]="0123456789ABCDEF"[(value>>(4*(digits-1-j)))&15];
 return at;
}
static void mask_diagnostic(const char*label,const uint8_t*mask){
 char text[100];unsigned at=0;
 while(*label&&at<60)text[at++]=*label++;
 for(unsigned j=0;j<8;j++){text[at++]=' ';at=hex(text,at,mask[j],2);}
 text[at++]='\r';text[at++]='\n';text[at]=0;diagnostic(text);
}
static void event_diagnostic(void){
 const RlEventObservation*e=&radio_port.observation;char text[128];unsigned at=0;
 const char*label="USB EVENT LEN=";for(unsigned j=0;label[j];j++)text[at++]=label[j];
 at=hex(text,at,e->reported_length,8);
 label=" STATUS=";for(unsigned j=0;label[j];j++)text[at++]=label[j];at=hex(text,at,e->status,16);
 label=" RESULT=";for(unsigned j=0;label[j];j++)text[at++]=label[j];at=hex(text,at,e->result,8);
 text[at++]='\r';text[at++]='\n';text[at]=0;diagnostic(text);
 if(e->copied){
  at=0;label="HCI RAW:";for(unsigned j=0;label[j];j++)text[at++]=label[j];
  for(unsigned j=0;j<e->copied;j++){text[at++]=' ';at=hex(text,at,e->prefix[j],2);}
  text[at++]='\r';text[at++]='\n';text[at]=0;diagnostic(text);
  if(e->copied>=2&&e->reported_length!=e->prefix[1]+2u)
   diagnostic("HCI INPUT IGNORED: EVENT LENGTH MISMATCH\r\n");
  else if(e->copied>=3&&e->prefix[0]==0x3e&&e->prefix[2]!=1)
   diagnostic("HCI LE META: SUBEVENT NOT HANDLED BY THIS DRIVER\r\n");
 }
}
static int EFIAPI driver_init(const uint8_t*p,uint32_t n,Surface*s){
 int r=scene_init(p,n,s);
#if SCENE_REVISION == 4
 const char*marker="CONNECTED HUNG INIT ENTERED\n";
 for(unsigned i=0;marker[i];i++)__asm__ volatile("outb %0,%1"::"a"((uint8_t)marker[i]),"Nd"((uint16_t)0xe9));
 for(;;)__asm__ volatile("pause"); /* Test-only, interrupts enabled. */
#endif
 return r;
}
static int EFIAPI attach(SystemTable*st,RfFile*file){
 diagnostic_system=st;
 if(city_display_bind(st)||city_clock_bind(st))return 1;
 qca_collect(st);qca_start(st,city_clock_ms());
 if(radio_port.bound||!file||rl_usb_bind(&radio_port,st))return 1;
 traces_printed=masks_printed=0;
 diagnostic_value("USB EVENT ENDPOINT=",radio_port.events);
 diagnostic_value("USB EVENT MAX_PACKET=",radio_port.event_packet);
 /* Raw bInterval: units depend on USB speed, NOT a millisecond claim. */
 diagnostic_value("USB EVENT BINTERVAL RAW=",radio_port.event_interval);
 diagnostic_value("USB EVENT TIMEOUT MS=",RL_EVENT_TIMEOUT_MS);
 rl_init(&radio_link,0);rg_init_shared(&radio_link.gatt,file);return 0;
}
static int EFIAPI poll_radio(void){
 QcaPrefix*diag=qca_prefix_view();uint64_t began=((uint64_t)prefix_clock_ms())*1000;
 qca_poll(began/1000);uint64_t after_qca=((uint64_t)prefix_clock_ms())*1000;
 diag->poll_before=began;
 if(after_qca>=began&&after_qca-began>diag->max_qca_us)diag->max_qca_us=after_qca-began;
 unsigned previous=radio_link.state;uint32_t serial=radio_port.observation_sequence;
 int result=rl_usb_poll(&radio_port,&radio_link);
 uint64_t ended=((uint64_t)prefix_clock_ms())*1000;
 diag->poll_after=ended;
 if(ended>=began&&ended-began>diag->max_poll_us)diag->max_poll_us=ended-began;
 diag->ble_state=radio_link.state;diag->pending=radio_link.pending;diag->connected=radio_link.connected;
 diag->credits=radio_link.credits;diag->inflight=radio_link.inflight;
 diag->stream_used=radio_port.event_stream.used;diag->stream_goal=radio_port.event_stream.goal;
 diag->usb_polls=radio_port.polls;diag->usb_reads=radio_port.event_reads;diag->usb_timeouts=radio_port.event_timeouts;
 diag->usb_observation=radio_port.observation_sequence;diag->last_usb_status=radio_port.observation.status;
 diag->last_usb_result=radio_port.observation.result;diag->last_usb_bytes=radio_port.observation.reported_length;
 if(result){diag->usb_fault=(unsigned)result;qca_prefix_request(diag,6,0,0,0,0,0);(void)qca_stop();}
 if((radio_port.mask_seen&1)&&!(masks_printed&1)){
  mask_diagnostic("HCI GENERAL MASK SUBMITTED:",radio_port.event_mask);masks_printed|=1;}
 if((radio_port.mask_seen&2)&&!(masks_printed&2)){
  mask_diagnostic("HCI LE MASK SUBMITTED:",radio_port.le_mask);masks_printed|=2;}
 if(serial!=radio_port.observation_sequence&&traces_printed<48){event_diagnostic();traces_printed++;
  if(traces_printed==48)diagnostic("HCI RAW TRACE LIMIT REACHED (48 READS)\r\n");}
 /* Four bounded heartbeat samples, in poll counts, NOT elapsed-time claims. */
 if(radio_port.polls==1024||radio_port.polls==4096||radio_port.polls==16384||radio_port.polls==65536){
  diagnostic_value("USB EVENT READS=",radio_port.event_reads);
  diagnostic_value("USB EVENT TIMEOUTS=",radio_port.event_timeouts);
 }
 if(radio_link.state!=previous){
  if(radio_link.state==RL_ADVERTISING)diagnostic("BLE FILE SERVICE ADVERTISING; READY TO CONNECT\r\n");
  if(radio_link.state==RL_CONNECTED)diagnostic("BLE CONNECTED; GATT DISCOVERY READY\r\n");
  if(previous==RL_CONNECTED&&radio_link.state==RL_CONFIGURING)diagnostic("BLE DISCONNECTED; RESTARTING ADVERTISING\r\n");
 }
 if(result){
  diagnostic_value("BLE POLL ERROR CODE=",(uint32_t)result);
  diagnostic_value("BLE LINK STATE=",radio_link.state);
  diagnostic_value("BLE PENDING HCI OPCODE=",radio_link.pending);
 }
 return result;
}
static int EFIAPI close_radio(void){
 if(qca_stop())return 1;
 if(!radio_port.bound)return 0;
 return rl_usb_close(&radio_port,&radio_link);
}
static uint32_t EFIAPI pending_command(void){return radio_link.pending;}
static int EFIAPI world(const uint8_t*p,uint32_t n,Surface*s,uint32_t*counter){
 if(surface(s)||!counter||activate(p,n)!=1)return 1;
 *counter=last_counter;return 0;
}
extern int runtime_phase_retire(void);
static Status EFIAPI connected_unload(void*h){(void)h;if(radio_port.bound||qca_stop()||!runtime_phase_retire())return EFI_ERROR(6);return 0;}
Status EFIAPI module_entry(void*h,SystemTable*st){
 (void)data_linked_methods[0];
 qca_image=h;
 LoadedImage*image=0;
 if(((HandleProtocol)service(st,152))(h,&loaded_image_guid,(void**)&image)||!image||
 !image->options||image->options_size!=sizeof(ConnectedRegistration))return EFI_ERROR(2);
 ConnectedRegistration*r=image->options;
 if(r->magic!=CONNECTED_MAGIC||r->abi!=3||r->state_abi!=2||r->size!=sizeof(*r))return EFI_ERROR(2);
 r->init=driver_init;r->tick=prefix_tick_frame;r->frame=prefix_frame;r->snapshot=scene_export;
 r->receipt=scene_receipt;r->counter=scene_counter;r->attach=attach;r->poll=poll_radio;
 r->close=close_radio;r->command=pending_command;r->world=world;
 image->unload=connected_unload;return 0;
}

#ifdef RABBIT_PREFIX_DRIVER_MODEL
void prefix_driver_model_bind(void*io){radio_port=(RlUsb){.io=io,.bound=1,.events=0x81,.in=0x82,.out=2};rl_init(&radio_link,0);radio_link.state=RL_CONNECTED;radio_link.connected=1;radio_link.handle=1;radio_link.buffers=radio_link.credits=8;radio_link.acl_size=64;}
int prefix_driver_model_poll(uint32_t ms){prefix_model_ms=ms;return poll_radio();}
void prefix_driver_model_display(uint32_t*physical,unsigned w,unsigned h,unsigned stride){city_physical=physical;city_width=w;city_height=h;city_stride=stride;city_format=1;}
int prefix_driver_model_world(const uint8_t*p,uint32_t n,Surface*s){uint32_t counter=0;return world(p,n,s,&counter);}
int prefix_driver_model_frame(Surface*s){return prefix_tick_frame(s);}
#endif
