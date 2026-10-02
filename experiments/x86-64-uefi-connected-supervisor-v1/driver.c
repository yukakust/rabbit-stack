/* Scene + HCI/ACL/ATT/USB are one owner-updateable UEFI driver. */
#include "connected_abi.h"
#include "usb_port.h"
#define module_entry legacy_scene_entry
#include "scene_module.c"
#undef module_entry
static RlUsb radio_port;
static RlLink radio_link;
static SystemTable*diagnostic_system;
static void diagnostic(const char*text){
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
 if(radio_port.bound||!file||rl_usb_bind(&radio_port,st))return 1;
 rl_init(&radio_link,0);rg_init_shared(&radio_link.gatt,file);return 0;
}
static int EFIAPI poll_radio(void){
 unsigned previous=radio_link.state;int result=rl_usb_poll(&radio_port,&radio_link);
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
 if(!radio_port.bound)return 0;
 return rl_usb_close(&radio_port,&radio_link);
}
static uint32_t EFIAPI pending_command(void){return radio_link.pending;}
static int EFIAPI world(const uint8_t*p,uint32_t n,Surface*s,uint32_t*counter){
 if(surface(s)||!counter||activate(p,n)!=1)return 1;
 *counter=last_counter;return 0;
}
static Status EFIAPI connected_unload(void*h){(void)h;return radio_port.bound?EFI_ERROR(6):0;}
Status EFIAPI module_entry(void*h,SystemTable*st){
 LoadedImage*image=0;
 if(((HandleProtocol)service(st,152))(h,&loaded_image_guid,(void**)&image)||!image||
 !image->options||image->options_size!=sizeof(ConnectedRegistration))return EFI_ERROR(2);
 ConnectedRegistration*r=image->options;
 if(r->magic!=CONNECTED_MAGIC||r->abi!=3||r->state_abi!=2||r->size!=sizeof(*r))return EFI_ERROR(2);
 r->init=driver_init;r->tick=scene_tick;r->frame=scene_frame;r->snapshot=scene_export;
 r->receipt=scene_receipt;r->counter=scene_counter;r->attach=attach;r->poll=poll_radio;
 r->close=close_radio;r->command=pending_command;r->world=world;
 image->unload=connected_unload;return 0;
}
