#include "rx.h"
#include <stdatomic.h>
static QcaInitAdapter*adapter(QcaPersistentRx*s){return s->startup->operating->boot->board->setup->read.full.adapter;
 }
static int empty(QcaCeRing*r){return r->read==r->write&&r->read==r->published;
 }
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
 }
static int fail(QcaPersistentRx*s,unsigned n){s->phase=QCA_RX_FAULT;
 s->error=n;
 return -1;
 }
static int slot(QcaPersistentRx*s,unsigned k){
 QcaInitAdapter*a=adapter(s);
 QcaCeRing*r=&a->channels.rings[k+1];
 
 if(!r->owned||r->fault||r->entries!=8||!r->receive||r->write!=r->published)return 0;
 
 if(s->posted[k])return ((r->write-r->read)&7)==1&&r->cookie[r->read]==s->cookie[k]
  &&r->address[r->read]==a->channels.buffers[2*(k+1)+1].address&&r->capacity[r->read]==2048;
 
 return empty(r);
 
}
int qca_rx_begin(QcaPersistentRx*s,QcaWmiStartup*w,const QcaRadioLifecycle*life,uint64_t now){
 if(!s||s->phase||!w||w->phase!=2||w->error||w->transaction.phase!=QCA_INIT_RUNNING
  ||!w->transaction.ready_seen||!w->transaction.tx_complete||w->tx_posted
  ||w->rx1_posted>1||w->rx2_posted>1||!qca_radio_accepts_work(life))return 0;
 
 s->startup=w;
 s->life=life;
 s->epoch=life->owners.epoch;
 s->last=now;
 s->posted[0]=w->rx1_posted;
 s->posted[1]=w->rx2_posted;
 
 s->cookie[0]=s->posted[0]?0x601:0;
 s->cookie[1]=s->posted[1]?0x602:0;
 
 if(!slot(s,0)||!slot(s,1)){s->phase=QCA_RX_FAULT;
 s->error=1;
 return 0;
 }
 if(!qca_htt_version_bind(&w->operating->control.session,3,&s->htt)){s->phase=QCA_RX_FAULT;
 s->error=19;
 return 0;
 }
 s->phase=QCA_RX_ACTIVE;
 return 1;
 
}
static int post(QcaPersistentRx*s,unsigned k){
 if(s->posted[k])return 0;
 
 if(!slot(s,k)||s->next_cookie==0xfffffff||s->posted_count==UINT32_MAX)return fail(s,2);
 
 QcaInitAdapter*a=adapter(s);
 QcaDmaBuffer*d=&a->channels.buffers[2*(k+1)+1];
 
 for(unsigned j=0;j<2048;j++)((uint8_t*)d->host)[j]=0;
 
 s->cookie[k]=0x70000000u+(++s->next_cookie);
 s->posted[k]=1;
 s->posted_count++;
 
 if(k==0)s->startup->rx1_posted=1;
 else s->startup->rx2_posted=1;
 
 atomic_thread_fence(memory_order_release);
 
 if(qca_ce_post(&a->channels.rings[k+1],d->address,2048,s->cookie[k],0,0))return fail(s,3);
 
 return 0;
 
}
static int receive(QcaPersistentRx*s,unsigned k){
 if(!s->posted[k]||s->count==2)return 0;
 
 if(!slot(s,k))return fail(s,4);
 
 QcaInitAdapter*a=adapter(s);
 unsigned index=0;
 uint32_t cookie=0,n=0;
 
 if(qca_ce_hw_index(&a->bus.engines[k+1],1,&index))return fail(s,5);
 
 int rc=qca_ce_complete(&a->channels.rings[k+1],index,&cookie,&n);
 
 if(rc>0)return 0;
 
 if(rc<0)return fail(s,6);
 
 s->posted[k]=0;
 if(k==0)s->startup->rx1_posted=0;
 else s->startup->rx2_posted=0;
 
 if(cookie!=s->cookie[k]||n<8||n>2048||s->completed==UINT32_MAX)return fail(s,7);
 
 atomic_thread_fence(memory_order_acquire);
 
 const uint8_t*p=a->channels.buffers[2*(k+1)+1].host;
 QcaHtcFrame f;
 
 s->rejected.completion=s->completed+1;
 s->rejected.pipe=(uint8_t)(k+1);
 s->rejected.endpoint=p[0];
 s->rejected.raw_bytes=(uint16_t)n;
 
 for(unsigned j=0;j<2048;j++)s->rejected.raw[j]=j<n?p[j]:0;
 
 if(!qca_htc_decode(p,n,&f))return fail(s,8);
 
 QcaHtcCredit credit=s->startup->operating->control.credit;
 
 if((k==0&&f.endpoint&&f.endpoint!=s->htt.endpoint)||(k==1&&f.endpoint&&f.endpoint!=credit.endpoint))return fail(s,9);
 
 uint32_t event=0;
 
 if(f.payload_bytes){
  if((k==1&&f.endpoint!=credit.endpoint)||f.payload_bytes>2040)return fail(s,10);
 
  if(k==1){
   if(f.payload_bytes<4)return fail(s,11);
 
   event=word(f.payload);
 
   /* Startup events are not runtime confirmations; restart/duplicate faults. */
   if(event==1||event==2||event==3)return fail(s,12);
 
  }
 }
 if(!qca_htc_credit_receive(&credit,&f))return fail(s,13);
 
 uint32_t id=s->completed+1;
 
 { /* Own even credit-only raw frames; no trailer discard. */
  QcaRxEvent*e=&s->events[(s->head+s->count)&1];
 
  e->completion=id;
 e->event=event;
 e->bytes=(uint16_t)f.payload_bytes;
 e->endpoint=f.endpoint;
 e->pipe=(uint8_t)(k+1);
 
  /* One owned raw image. The normalized payload is a byte view at raw+8;
   * do not zero normalized padding and thereby erase an actual credit trailer. */
  if(f.payload!=p+8)return fail(s,14);
  e->raw_bytes=(uint16_t)n;
  for(unsigned j=0;j<2048;j++)e->raw[j]=j<n?p[j]:0;

  s->count++;
 
 }
 /* Commit only after entire frame, endpoint, payload and trailer validated. */
 s->startup->operating->control.credit=credit;
 s->completed=id;
 s->rejected.completion=0;
 s->rejected.raw_bytes=0;
 return 0;
 
}
int qca_rx_poll(QcaPersistentRx*s,const QcaRadioLifecycle*life,uint64_t now){
 if(!s||s->phase!=QCA_RX_ACTIVE)return -1;
 
 if(!life||life!=s->life||life->owners.epoch!=s->epoch)return fail(s,17);
 
 if(!qca_radio_accepts_work(life))return 0;
  /* No descriptor/register access. */
 if(s->head>1||s->count>2||s->posted[0]>1||s->posted[1]>1)return fail(s,18);
 
 if(now<s->last)return fail(s,14);
 
 s->last=now;
 
 QcaWmiStartup*w=s->startup;
 QcaHttBinding binding={0};
 
 if(!qca_htt_version_bind(&w->operating->control.session,3,&binding)||binding.endpoint!=s->htt.endpoint||binding.max_bytes!=s->htt.max_bytes)return fail(s,19);
 
 if(w->phase!=2||w->error||w->cancelled||w->transaction.phase!=QCA_INIT_RUNNING
  ||qca_operating_poll(w->operating,now)!=1||qca_channels_retained(&adapter(s)->channels))return fail(s,15);
 
 if(!slot(s,0)||!slot(s,1))return fail(s,16);
 
 if(receive(s,0)||receive(s,1))return -1;
 
 s->backpressure=s->count==2;
 
 if(!s->backpressure&&(post(s,0)||post(s,1)))return -1;
 
 return 1;
 
}
int qca_rx_take(QcaPersistentRx*s,uint32_t id,QcaRxEvent*out,unsigned bytes){
 if(!s||!s->count||s->count>2||s->head>1||!out||bytes<sizeof(*out)||!id||s->events[s->head].completion!=id)return 0;
 
 uintptr_t a=(uintptr_t)s,b=(uintptr_t)out;
 
 if(a>UINTPTR_MAX-sizeof(*s)||b>UINTPTR_MAX-sizeof(*out)||(a<b?b-a<sizeof(*s):a-b<sizeof(*out)))return 0;
 
 *out=s->events[s->head];
 s->head^=1;
 s->count--;
 s->backpressure=0;
 return 1;
 
}
int qca_rx_clear(QcaPersistentRx*s,const QcaRadioLifecycle*life){
 if(!s||!s->phase||life!=s->life||!life||life->owners.epoch!=s->epoch||!qca_radio_can_unload(life))return 0;
 
 for(unsigned j=0;j<sizeof(s->events);j++)((uint8_t*)s->events)[j]=0;
 
 s->posted[0]=s->posted[1]=s->head=s->count=s->backpressure=0;
 s->phase=QCA_RX_CLEARED;
 return 1;
 
}
