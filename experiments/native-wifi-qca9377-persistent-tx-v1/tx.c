#include "tx.h"
#include <stdatomic.h>
static QcaInitAdapter*adapter(QcaPersistentTx*s){return s->radio->startup->operating->boot->board->setup->read.full.adapter;}
static int empty(QcaCeRing*r){return r->read==r->write&&r->read==r->published;}
static int fault(QcaPersistentTx*s,unsigned n){s->error=n;s->phase=QCA_TX_FAULT;return -1;}
static int bound(QcaPersistentTx*s){
 return s&&s->radio&&s->life==&s->radio->life&&s->epoch==s->life->owners.epoch
 &&s->credit==&s->radio->startup->operating->control.credit;
}
static int guard(QcaPersistentTx*s,uint64_t now){
 if(!bound(s)||!qca_radio_accepts_work(s->life)||qca_persistent_poll(s->radio,now)!=1)return 0;
 QcaInitAdapter*a=adapter(s);QcaChannels*c=&a->channels;QcaCeRing*r=&c->rings[3];
 if(!r->owned||r->fault||r->entries!=8||r->receive||r->descriptors!=c->buffers[6].host
  ||r->context!=&c->routes[3]||c->routes[3].bus!=&a->bus||c->routes[3].pipe!=3||c->routes[3].receive
  ||r->publish!=c->rings[4].publish||r->stop!=c->rings[4].stop)return 0;
 if(s->phase!=QCA_TX_POSTED)return empty(r);
 return ((r->write-r->read)&7)==1&&r->published==r->write&&r->cookie[r->read]==s->cookie
  &&r->address[r->read]==c->buffers[7].address&&r->capacity[r->read]==s->bytes;
}
int qca_tx_begin(QcaPersistentTx*s,QcaPersistentNative*r,uint64_t now){
 if(!s||s->phase||!r||!r->startup||!r->startup->operating||!qca_radio_accepts_work(&r->life)||r->startup->tx_posted)return 0;
 s->radio=r;s->life=&r->life;s->epoch=r->life.owners.epoch;s->credit=&r->startup->operating->control.credit;
 s->phase=QCA_TX_IDLE;s->last=now;
 if(!guard(s,now)){(void)fault(s,1);return 0;}return 1;
}
int qca_tx_submit(QcaPersistentTx*s,const uint8_t*p,unsigned n,uint64_t now,uint64_t timeout,uint32_t*id){
 if(!s||s->phase!=QCA_TX_IDLE||!p||n<4||n>4088||!id||!timeout||timeout>10000000
  ||now>UINT64_MAX-timeout||now<s->last||s->serial==0xfffffff||!bound(s)||s->credit->reserved
  ||!((uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16))||p[3])return 0;
 uintptr_t a=(uintptr_t)s,b=(uintptr_t)p,c=(uintptr_t)id;
 if(a>UINTPTR_MAX-sizeof(*s)||b>UINTPTR_MAX-n||c>UINTPTR_MAX-sizeof(*id)
  ||(a<b?b-a<sizeof(*s):a-b<n)||(a<c?c-a<sizeof(*s):a-c<sizeof(*id)))return 0;
 if(!guard(s,now)){(void)fault(s,1);return 0;}
 if(n>s->credit->max_bytes||!s->credit->size||((n+8+s->credit->size-1)/s->credit->size)>s->credit->total)return 0;
 QcaHtcSession*h=&s->radio->startup->operating->control.session;
 if(!qca_htc_header(s->frame,sizeof(s->frame),s->credit->endpoint,n,h->sequence,1))return 0;
 for(unsigned j=0;j<n;j++)s->frame[j+8]=p[j];
 s->bytes=n+8;s->request=++s->serial;s->cookie=0x90000000u+s->serial;
 s->last=now;s->deadline=now+timeout;s->error=s->ticket=0;s->phase=QCA_TX_WAIT_CREDIT;*id=s->request;return 1;
}
int qca_tx_poll(QcaPersistentTx*s,uint64_t now){
 if(!s||!s->phase||s->phase==QCA_TX_FAULT||s->phase==QCA_TX_CLEARED)return -1;
 if(now<s->last)return fault(s,2);
 s->last=now;
 if(!guard(s,now))return fault(s,1);
 if(s->phase==QCA_TX_IDLE||s->phase==QCA_TX_CANCELLED)return 0;
 if(s->phase==QCA_TX_DMA_DONE)return 1;
 if(now>=s->deadline)return fault(s,3);
 if(s->phase==QCA_TX_WAIT_CREDIT){
  if(s->credit->reserved||s->credit->ticket)return fault(s,4);
  QcaHtcCredit next=*s->credit;uint32_t ticket=0;
  if(!qca_htc_credit_reserve(&next,s->bytes,&ticket))return 0;
  *s->credit=next;s->ticket=ticket;s->phase=QCA_TX_RESERVED;return 0;
 }
 QcaInitAdapter*a=adapter(s);
 if(s->phase==QCA_TX_RESERVED){
  QcaHtcCredit next=*s->credit;
  if(!qca_htc_credit_commit(&next,s->ticket))return fault(s,5);
  uint8_t*p=a->channels.buffers[7].host;for(unsigned j=0;j<s->bytes;j++)p[j]=s->frame[j];
  *s->credit=next;s->ticket=0;s->phase=QCA_TX_POSTED;s->attempted++;
  s->radio->startup->operating->control.session.sequence++;
  atomic_thread_fence(memory_order_release);
  if(qca_ce_post(&a->channels.rings[3],a->channels.buffers[7].address,s->bytes,s->cookie,s->credit->endpoint,0))return fault(s,6);
  return 0;
 }
 if(s->phase!=QCA_TX_POSTED)return fault(s,7);
 unsigned index=0;uint32_t cookie=0,n=0;
 if(qca_ce_hw_index(&a->bus.engines[3],0,&index))return fault(s,8);
 int rc=qca_ce_complete(&a->channels.rings[3],index,&cookie,&n);
 if(rc>0)return 0;
 if(rc<0)return fault(s,9);
 if(cookie!=s->cookie||n!=s->bytes)return fault(s,10);
 s->completed++;s->phase=QCA_TX_DMA_DONE;return 1;
}
int qca_tx_cancel(QcaPersistentTx*s,uint32_t id,uint64_t now){
 if(!s||!id||id!=s->request||!bound(s)||(s->phase!=QCA_TX_RESERVED&&s->phase!=QCA_TX_WAIT_CREDIT))return 0;
 if(now<s->last||!guard(s,now)){(void)fault(s,11);return 0;}
 s->last=now;
 if(s->phase==QCA_TX_RESERVED){
  QcaHtcCredit next=*s->credit;
  if(!qca_htc_credit_cancel(&next,s->ticket))return 0;
  *s->credit=next;s->ticket=0;
 }else if(s->phase!=QCA_TX_WAIT_CREDIT)return 0;
 s->phase=QCA_TX_CANCELLED;return 1;
}
int qca_tx_retire(QcaPersistentTx*s,uint32_t id){
 if(!s||!id||id!=s->request||(s->phase!=QCA_TX_DMA_DONE&&s->phase!=QCA_TX_CANCELLED))return 0;
 s->phase=QCA_TX_IDLE;return 1;
}
int qca_tx_clear(QcaPersistentTx*s){
 if(!s||!s->phase||!bound(s)||!qca_radio_can_unload(s->life))return 0;
 for(unsigned j=0;j<sizeof(s->frame);j++)s->frame[j]=0;
 s->phase=QCA_TX_CLEARED;return 1;
}
