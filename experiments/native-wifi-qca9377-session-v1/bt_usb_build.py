"""Isolated USB stream integration; never edits frozen native41 inputs."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LINK=ROOT.parent/'ble-connected-file-transfer-v1'
def one(s,a,b):
 if s.count(a)!=1:raise ValueError('USB source anchor changed')
 return s.replace(a,b)
def sources(out):
 out.mkdir(parents=True,exist_ok=True)
 h=(LINK/'usb_port.h').read_text()
 h=one(h,'#include "hci_link.h"','#include "hci_link.h"\n#include "bt_event_stream.h"')
 h=one(h,' RlEventObservation observation;',' RlEventObservation observation;\n RabbitBtEventStream event_stream;')
 h=one(h,'RL_USB_ACL_TRANSFER,RL_USB_PACKET_KIND,RL_USB_LINK_FAULT','RL_USB_ACL_TRANSFER,RL_USB_PACKET_KIND,RL_USB_LINK_FAULT,RL_USB_EVENT_STREAM')
 s=(LINK/'usb_port.c').read_text()
 s=one(s,'int rl_usb_poll(RlUsb*p,RlLink*l){','static void poll_event(void*context,const uint8_t*event,unsigned n){rl_event((RlLink*)context,event,n);}\nint rl_usb_poll(RlUsb*p,RlLink*l){')
 s=one(s,'if(!status&&!result){if(n>sizeof(buffer))return RL_USB_EVENT_SIZE;rl_event(l,buffer,n);}','if(!status&&!result){if(n>sizeof(buffer))return RL_USB_EVENT_SIZE;\n  if(rabbit_bt_events(&p->event_stream,buffer,(unsigned)n,poll_event,l))return RL_USB_EVENT_STREAM;}')
 a=s.index('static int completed(');b=s.index('int rl_usb_close(',a)
 s=s[:a]+CLOSE+s[b:]
 (out/'usb_port.c').write_text(s);(out/'usb_port.h').write_text(h)
 for name in ('bt_event_stream.c','bt_event_stream.h'):(out/name).write_bytes((ROOT/name).read_bytes())
CLOSE=r'''/* Poll and shutdown share ONE event stream: a partial event survives the
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
'''
