#include "hci_link.h"
static uint16_t u16(const uint8_t*p){return (uint16_t)(p[0]|((unsigned)p[1]<<8));}
static void w16(uint8_t*p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static void copy(uint8_t*a,const uint8_t*b,size_t n){for(size_t i=0;i<n;i++)a[i]=b[i];}
static const uint16_t opcodes[]={0x0c03,0x0c01,0x2001,0x2002,0x2006,0x2008,0x200a};
static const uint8_t uuid[16]={1,0,0,0,0,0,0,0x80,0x49,0x46,0x54,0x49,0x42,0x42,0x41,0x52};
static void fault(RlLink*l){l->state=RL_FAULT;l->pending=0;l->count=0;l->rx_used=l->rx_goal=0;}
void rl_init(RlLink*l,RfApply apply){
 rg_init(&l->gatt,apply);l->rx_used=l->rx_goal=l->handle=l->acl_size=l->credits=l->buffers=l->inflight=l->pending=0;
 l->waited=0;l->step=0;l->state=RL_CONFIGURING;l->head=l->count=l->shared=l->connected=0;l->wire_used=0;l->command_credits=1;
}
void rl_stop(RlLink*l){l->state=RL_STOPPED;l->pending=0;l->count=0;l->rx_used=l->rx_goal=0;}
void rl_elapsed(RlLink*l,uint32_t ms){if(l->pending){if(ms>=10000||l->waited>=10000-ms)fault(l);else l->waited+=ms;}}
static size_t command(RlLink*l,uint8_t*p){
 uint16_t op=l->step==3&&l->shared?0x1005:opcodes[l->step];w16(p,op);p[2]=0;
 for(unsigned i=3;i<35;i++)p[i]=0;
 switch(l->step){
 case 1:p[2]=8;p[3]=0x10;p[4]=0xe0;p[5]=4;p[10]=0x20;break;
 case 2:p[2]=8;p[3]=0x1f;break;
 case 4:p[2]=15;w16(p+3,0x60);w16(p+5,0xa0);p[16]=7;break;
 case 5:p[2]=32;p[3]=21;p[4]=2;p[5]=1;p[6]=6;p[7]=17;p[8]=7;copy(p+9,uuid,16);break;
 case 6:p[2]=1;p[3]=1;break;
 default:break;
 }
 l->pending=op;l->command_credits--;l->waited=0;return p[2]+3u;
}
size_t rl_take(RlLink*l,uint8_t*out,size_t capacity,uint8_t*kind){
 if(!l||!out||!kind||capacity<RL_ACL_MAX+4||l->state==RL_FAULT||l->state==RL_STOPPED)return 0;
 if(l->state==RL_CONFIGURING&&!l->pending&&l->command_credits){*kind=1;return command(l,out);}
 if(l->state==RL_CONNECTED&&l->count&&l->credits){
  *kind=2;uint16_t n=l->qlen[l->head];copy(out,l->queue[l->head],n);
  l->head=(uint8_t)((l->head+1)%RL_TX_SLOTS);l->count--;l->credits--;l->inflight++;return n;
 }
 return 0;
}
void rl_event(RlLink*l,const uint8_t*p,size_t n){
 if(!l||!p||n<2||n!=p[1]+2u||l->state==RL_STOPPED||l->state==RL_FAULT)return;
 if(p[0]==0x10){fault(l);return;}
 if(p[0]==0x0e){
  if(n<6)return;
  l->command_credits=p[2];
  if(!l->pending||u16(p+3)!=l->pending)return;
  if(p[5]){fault(l);return;}
  if(l->pending==0x2002){
   if(n!=9){fault(l);return;}
   if(!p[8]&&!u16(p+6)){l->shared=1;l->pending=0;return;}
   if(u16(p+6)<4||u16(p+6)>RL_ACL_MAX||!p[8]){fault(l);return;}
   l->acl_size=u16(p+6);l->buffers=l->credits=p[8];
  }
  if(l->pending==0x1005){
   if(n!=13||u16(p+6)<4||!u16(p+9)){fault(l);return;}
   /* No BR/EDR links are created. Cap HCI fragments to our bounded buffer even
    * when the controller shares a larger classic/LE packet pool. */
   l->acl_size=u16(p+6)>RL_ACL_MAX?RL_ACL_MAX:u16(p+6);l->buffers=l->credits=u16(p+9);
  }
  l->pending=0;l->step++;
  if(l->step==7)l->state=RL_ADVERTISING;
  return;
 }
 if(p[0]==0x0f){if(n==6){l->command_credits=p[3];if(l->pending&&u16(p+4)==l->pending&&p[2])fault(l);}return;}
 if(p[0]==0x3e&&n==21&&p[2]==1){
  if(l->state!=RL_ADVERTISING)return;
  if(p[3]||p[6]!=1||u16(p+4)>0x0eff){fault(l);return;}
  l->handle=u16(p+4);l->connected=1;l->state=RL_CONNECTED;l->inflight=0;l->credits=l->buffers;l->head=l->count=0;
  l->rx_used=l->rx_goal=l->wire_used=0;rg_disconnected(&l->gatt);return;
 }
 if(p[0]==5&&n==6&&l->state==RL_CONNECTED&&u16(p+3)==l->handle){
  if(p[2]){fault(l);return;}
  l->state=RL_CONFIGURING;l->connected=0;l->step=6;l->pending=0;l->inflight=0;l->credits=l->buffers;
  l->head=l->count=0;l->rx_used=l->rx_goal=l->wire_used=0;rg_disconnected(&l->gatt);return;
 }
 if(p[0]==0x13&&l->state==RL_CONNECTED){
  if(n<3||n!=3u+4u*p[2]){fault(l);return;}
  for(unsigned i=0;i<p[2];i++)if(u16(p+3+4*i)==l->handle){
   uint16_t done=u16(p+5+4*i);
   if(done>l->inflight){fault(l);return;}
   l->inflight-=done;l->credits+=done;
  }
 }
}
static void reply(RlLink*l,uint16_t cid,const uint8_t*p,size_t n){
 if(!n||n>RG_MTU_MAX||l->acl_size<4){fault(l);return;}
 uint8_t data[RL_ACL_MAX];w16(data,(uint16_t)n);w16(data+2,cid);copy(data+4,p,n);n+=4;
 size_t needed=(n+l->acl_size-1)/l->acl_size;
 if(needed>RL_TX_SLOTS-l->count){fault(l);return;}
 for(size_t offset=0;offset<n;){
  size_t count=n-offset;if(count>l->acl_size)count=l->acl_size;
  uint8_t slot=(uint8_t)((l->head+l->count)%RL_TX_SLOTS);uint8_t*out=l->queue[slot];
  w16(out,(uint16_t)(l->handle|(offset?0x1000:0x2000)));w16(out+2,(uint16_t)count);copy(out+4,data+offset,count);
  l->qlen[slot]=(uint16_t)(count+4);l->count++;offset+=count;
 }
}
static void dispatch(RlLink*l){
 uint16_t cid=u16(l->rx+2);const uint8_t*p=l->rx+4;size_t n=l->rx_goal-4;uint8_t out[RG_MTU_MAX];
 if(cid==4){size_t length=rg_att(&l->gatt,p,n,out,sizeof(out));if(length)reply(l,cid,out,length);}
 else if(cid==6){out[0]=5;out[1]=5;reply(l,cid,out,2);} /* Pairing not supported. */
 else if(cid==5){
  if(n<4||!p[1]||u16(p+2)!=n-4){fault(l);return;}
  /* Reject connection-parameter update rather than claiming host coordination. */
  out[0]=p[0]==0x12?0x13:1;out[1]=p[1];w16(out+2,2);w16(out+4,p[0]==0x12?1:0);reply(l,cid,out,6);
 }
}
void rl_acl(RlLink*l,const uint8_t*p,size_t n){
 if(!l||!p||l->state!=RL_CONNECTED||n<4)return;
 uint16_t tag=u16(p),bytes=u16(p+2),pb=(tag>>12)&3;
 if((tag&0x0fff)!=l->handle)return;
 if(tag&0xc000||bytes>RL_ACL_MAX||n!=bytes+4u){fault(l);return;}
 if(pb==0||pb==2){
  if(l->rx_used||bytes<4){fault(l);return;}
  l->rx_goal=(uint16_t)(u16(p+4)+4u);
  if(u16(p+4)>RG_MTU_MAX||l->rx_goal<4||bytes>l->rx_goal){fault(l);return;}
 }else if(pb!=1||!l->rx_used){fault(l);return;}
 if(!bytes||bytes>l->rx_goal-l->rx_used){fault(l);return;}
 copy(l->rx+l->rx_used,p+4,bytes);l->rx_used+=bytes;
 if(l->rx_used==l->rx_goal){dispatch(l);l->rx_used=l->rx_goal=0;}
}
void rl_bulk(RlLink*l,const uint8_t*p,size_t n){
 if(!l||!p||l->state!=RL_CONNECTED)return;
 for(size_t i=0;i<n;i++){
  if(l->wire_used>=sizeof(l->wire)){fault(l);return;}
  l->wire[l->wire_used++]=p[i];
  if(l->wire_used>=4){
   uint16_t bytes=u16(l->wire+2);
   if(bytes>RL_ACL_MAX){fault(l);return;}
   if(l->wire_used==bytes+4u){rl_acl(l,l->wire,l->wire_used);l->wire_used=0;if(l->state!=RL_CONNECTED)return;}
  }
 }
}
