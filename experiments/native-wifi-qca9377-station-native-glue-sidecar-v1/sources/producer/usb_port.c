/* UEFI USB adapter candidate. No standalone entry point or media writer.
 * Called only after exact QCA transient RAM setup by a new exclusive supervisor.
 * Timeouts are finite and no asynchronous callback survives an unload. */
#include "usb_port.h"
typedef Status(EFIAPI *Control)(void*,void*,uint32_t,uint32_t,void*,size_t,uint32_t*);
typedef Status(EFIAPI *Transfer)(void*,uint8_t,void*,size_t*,size_t,uint32_t*);
typedef Status(EFIAPI *Descriptor)(void*,void*);
typedef Status(EFIAPI *Endpoint)(void*,uint8_t,void*);
typedef Status(EFIAPI *Locate)(uint32_t,const Guid*,void*,size_t*,void***);
typedef Status(EFIAPI *Free)(void*);
static const Guid usb_guid={0x2b2f68d6,0x0cd2,0x44cf,{0x8e,0x8b,0xbb,0xa2,0x0b,0x1b,0x5b,0x75}};
static uint16_t read16(const uint8_t*p){return (uint16_t)(p[0]|((unsigned)p[1]<<8));}
static void *fn(void*io,size_t offset){return *(void**)((uint8_t*)io+offset);}
int rl_usb_bind(RlUsb*p,SystemTable*st){
 if(!p||!st||!st->boot)return 1;
 *p=(RlUsb){0};size_t count=0;void**handles=0;
 if(((Locate)service(st,312))(2,&usb_guid,0,&count,&handles)||!handles)return 1;
 int bad=count>64;unsigned matches=0;
 for(size_t i=0;!bad&&i<count;i++){
  void*io=0;uint8_t device[18],interface[9];
  if(((HandleProtocol)service(st,152))(handles[i],&usb_guid,&io)||!io)continue;
  if(((Descriptor)fn(io,48))(io,device)||((Descriptor)fn(io,64))(io,interface))continue;
  if(device[0]!=18||device[1]!=1||interface[0]!=9||interface[1]!=4)continue;
  if(read16(device+8)!=0x0cf3||read16(device+10)!=0xe009||interface[2]!=0||interface[3]!=0||interface[5]!=0xe0||interface[6]!=1||interface[7]!=1)continue;
  if(++matches!=1||interface[4]>16){bad=1;break;}
  RlUsb candidate={0};candidate.io=io;candidate.bound=1;
  for(uint8_t j=0;j<interface[4];j++){
   uint8_t endpoint[7];if(((Endpoint)fn(io,72))(io,j,endpoint)||endpoint[0]!=7||endpoint[1]!=5){bad=1;break;}
   uint8_t address=endpoint[2],type=endpoint[3]&3;uint16_t packet=read16(endpoint+4)&0x7ff;
   if(!(address&15)||!packet||packet>1024){bad=1;break;}
   if(type==3&&(address&0x80)){if(candidate.events){bad=1;break;}candidate.events=address;candidate.event_packet=packet;candidate.event_interval=endpoint[6];}
   if(type==2&&(address&0x80)){if(candidate.in){bad=1;break;}candidate.in=address;}
   if(type==2&&!(address&0x80)){if(candidate.out){bad=1;break;}candidate.out=address;}
  }
  if(!candidate.events||!candidate.in||!candidate.out)bad=1;
  if(!bad)*p=candidate;
 }
 Status freed=((Free)service(st,72))(handles);
 if(bad||matches!=1||freed){*p=(RlUsb){0};return 1;}
 return 0;
}
static int command(RlUsb*p,const uint8_t*data,size_t n){
 if(n<3||n>258||data[2]+3u!=n)return 1;
 uint8_t request[8]={0x20,0,0,0,0,0,(uint8_t)n,(uint8_t)(n>>8)};uint32_t result=0;
 if(((Control)fn(p->io,0))(p->io,request,1,200,(void*)data,n,&result)||result)return 1;
 /* Record exact bytes accepted by the existing control-transfer call. A USB
  * success is not a claim that a controller event or connection occurred. */
 if(n==11&&(read16(data)==0x0c01||read16(data)==0x2001)){
  uint8_t*mask=read16(data)==0x0c01?p->event_mask:p->le_mask;
  for(unsigned i=0;i<8;i++)mask[i]=data[3+i];
  p->mask_seen|=read16(data)==0x0c01?1:2;
 }
 return 0;
}
static void increment(uint32_t*p){if(*p!=0xffffffffu)(*p)++;}
static void observe_event(RlUsb*p,Status status,uint32_t result,size_t n,const uint8_t*buffer,size_t capacity){
 increment(&p->polls);
 if(status==EFI_ERROR(18)||status==EFI_ERROR(6)){
  increment(&p->event_timeouts);
  /* Firmware may leave DataLength at the requested length on timeout. That
   * is NOT received data. Only a changed positive length is worth recording;
   * no bytes from unsuccessful reads are labelled as valid HCI input. */
  if(!n||n==capacity)return;
 }
 if(!status&&!result)increment(&p->event_reads);
 increment(&p->observation_sequence);p->observation=(RlEventObservation){0};
 p->observation.status=status;p->observation.result=result;
 p->observation.reported_length=n>0xffffffffu?0xffffffffu:(uint32_t)n;
 if(!status&&!result&&n<=capacity){
  size_t count=n<RL_EVENT_PREFIX?n:RL_EVENT_PREFIX;
  for(size_t i=0;i<count;i++)p->observation.prefix[i]=buffer[i];
  p->observation.copied=(uint8_t)count;
 }
}
void qca_prefix_hci(const uint8_t*,unsigned,const RlLink*);
static void poll_event(void*context,const uint8_t*event,unsigned n){RlLink*l=context;qca_prefix_hci(event,n,l);rl_event(l,event,n);}
int rl_usb_poll(RlUsb*p,RlLink*l){
 if(!p||!p->bound||!l)return RL_USB_ARGUMENT;
 uint8_t buffer[260],kind=0;size_t n=sizeof(buffer);uint32_t result=0;
 Status status=((Transfer)fn(p->io,24))(p->io,p->events,buffer,&n,RL_EVENT_TIMEOUT_MS,&result);
 observe_event(p,status,result,n,buffer,sizeof(buffer));
 if(!status&&!result){if(n>sizeof(buffer))return RL_USB_EVENT_SIZE;
  if(rabbit_bt_events(&p->event_stream,buffer,(unsigned)n,poll_event,l))return RL_USB_EVENT_STREAM;}
 else if(status!=EFI_ERROR(18)&&status!=EFI_ERROR(6))return RL_USB_EVENT_TRANSFER; /* timeout/not ready */
 if(l->state==RL_CONNECTED){
  n=sizeof(buffer);result=0;status=((Transfer)fn(p->io,8))(p->io,p->in,buffer,&n,1,&result);
  if(!status&&!result){if(n>sizeof(buffer))return RL_USB_BULK_SIZE;rl_bulk(l,buffer,n);}
  else if(status!=EFI_ERROR(18)&&status!=EFI_ERROR(6))return RL_USB_BULK_TRANSFER;
 }
 /* Bounded batch, never an unbounded drain that starves animation/Esc. */
 for(unsigned i=0;i<16;i++){
  n=rl_take(l,buffer,sizeof(buffer),&kind);if(!n)break;
  if(kind==1){if(command(p,buffer,n))return RL_USB_COMMAND_TRANSFER;}
  else if(kind==2){size_t sent=n;result=0;status=((Transfer)fn(p->io,8))(p->io,p->out,buffer,&sent,200,&result);if(status||result||sent!=n)return RL_USB_ACL_TRANSFER;}
  else return RL_USB_PACKET_KIND;
 }
 return l->state==RL_FAULT?RL_USB_LINK_FAULT:0;
}
/* Poll and shutdown share ONE event stream: a partial event survives the
 * handover. Every complete event in a USB read is checked, even after the
 * awaited completion, so a coalesced connection race cannot be lost. */
typedef struct {RlLink*link;uint16_t opcode,handle;int disconnect,done,bad;} CloseWait;
static void close_event(void*context,const uint8_t*event,unsigned n){
 CloseWait*w=context;RlLink*l=w->link;
 if(event[0]==0x3e&&n==21&&event[2]==1&&!event[3]){
  uint16_t incoming=read16(event+4);
  if(incoming>0x0eff||event[6]!=1||(l->connected&&incoming!=l->handle)){w->bad=1;return;}
  l->connected=1;l->handle=incoming;
 }
 if(event[0]==5&&n==6&&read16(event+3)==l->handle){
  if(event[2]){w->bad=1;return;}
  l->connected=0;
  if(w->disconnect&&read16(event+3)==w->handle)w->done=1;
 }
 /* Command acceptance still does not prove disconnection. */
 if(event[0]==0x0e&&n>=6&&read16(event+3)==w->opcode){
  if(event[5]){w->bad=1;return;}
  if(!w->disconnect)w->done=1;
 }
 if(event[0]==0x0f&&n==6&&read16(event+4)==w->opcode&&event[2])w->bad=1;
 if(event[0]==0x10)w->bad=1;
}
static int completed(RlUsb*p,RlLink*l,uint16_t opcode,uint16_t handle,int disconnect){
 CloseWait w={l,opcode,handle,disconnect,0,0};
 for(unsigned tries=0;tries<128;tries++){
  uint8_t event[260];size_t n=sizeof(event);uint32_t result=0;
  Status status=((Transfer)fn(p->io,24))(p->io,p->events,event,&n,RL_EVENT_TIMEOUT_MS,&result);
  if(status==EFI_ERROR(18)||status==EFI_ERROR(6))continue;
  if(status||result||n>sizeof(event))return 1;
  if(rabbit_bt_events(&p->event_stream,event,(unsigned)n,close_event,&w)||w.bad)return 1;
  /* A trailing partial event may hide a connection or controller error.
   * Finish it before declaring this command complete. */
  if(w.done&&!p->event_stream.used)return 0;
 }
 return 1; /* Unknown outcome, NEVER claim radio OFF. */
}
int rl_usb_close(RlUsb*p,RlLink*l){
 if(!p||!p->bound||!l)return 1;
 if(l->pending&&completed(p,l,l->pending,0,0))return 1;
 uint8_t off[4]={0x0a,0x20,1,0};
 if(command(p,off,4)||completed(p,l,0x200a,0,0))return 1;
 if(l->connected){
  uint8_t disconnect[6]={6,4,3,(uint8_t)l->handle,(uint8_t)(l->handle>>8),0x13};
  if(command(p,disconnect,6)||completed(p,l,0x0406,l->handle,1))return 1;
 }
 /* A confirmed final Reset provides a controller-wide quiescence barrier,
  * including any delayed connection/ACL event not yet observed by the host.
  * The QCA setup already uses standard post-RAM Reset; no flash write. */
 uint8_t reset[3]={3,12,0};
 if(command(p,reset,3)||completed(p,l,0x0c03,0,0))return 1;
 rl_stop(l);p->bound=0;return 0;
}
