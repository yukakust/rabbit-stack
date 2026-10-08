#include "htt_native.h"
#include <stdatomic.h>
extern int qca_stop(void);
 
static QcaInitAdapter*adapter(QcaHttNative*s){return s->radio->startup->operating->boot->board->setup->read.full.adapter;
 }
static int overlap(const void*a,unsigned na,const void*b,unsigned nb){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 return x<y?y-x<na:x-y<nb;
 }
static int stop(QcaHttNative*s,unsigned error){
 if(error&&!s->error)s->error=error;
 
 s->phase=s->error?QCA_HTTN_FAULT:QCA_HTTN_STOPPING;
 
 if(!s->stop_requested){s->stop_requested=1;
 (void)qca_persistent_quiesce(s->radio,s->last);
 (void)qca_stop();
 }
 if(s->error)s->phase=QCA_HTTN_FAULT;
 return s->error?-1:0;
 
}
static int bound(QcaHttNative*s){return s&&s->radio&&s->radio->htt_owner==s&&s->radio->epoch==s->epoch&&s->radio->life.owners.epoch==s->epoch;
 }
static int guard(QcaHttNative*s,uint64_t now){
 if(!bound(s)||qca_persistent_poll(s->radio,now)!=1)return 0;
 
 QcaHttBinding b={0};
 QcaHtcSession*h=&s->radio->startup->operating->control.session;
 
 if(!qca_htt_version_bind(h,3,&b)||b.endpoint!=s->binding.endpoint||b.max_bytes!=s->binding.max_bytes)return 0;
 
 QcaInitAdapter*a=adapter(s);
 QcaCeRing*r=&a->channels.rings[4];
 
 if(!r->owned||r->fault||r->entries!=8||r->receive||r->descriptors!=a->channels.buffers[8].host
 ||r->context!=&a->channels.routes[4]||a->channels.routes[4].pipe!=4||a->channels.routes[4].receive
 ||a->channels.routes[4].bus!=&a->bus||r->write!=r->published)return 0;
 
 if(!s->attempted||s->dma_completed)return r->read==r->write;
 
 return ((r->write-r->read)&7)==1&&r->cookie[r->read]==s->cookie&&r->address[r->read]==a->channels.buffers[9].address&&r->capacity[r->read]==12;
 
}
int qca_htt_native_begin(QcaHttNative*s,QcaPersistentNative*r,unsigned op,uint64_t now){
 if(!s||!r||(uintptr_t)s>UINTPTR_MAX-sizeof(*s)||(uintptr_t)r>UINTPTR_MAX-sizeof(*r)||overlap(s,sizeof(*s),r,sizeof(*r))||s->phase||r->htt_owner||!r->startup||now>UINT64_MAX-3000000||!qca_radio_accepts_work(&r->life))return 0;
 
 if(!qca_htt_version_bind(&r->startup->operating->control.session,op,&s->binding))return 0;
 
 s->radio=r;
 r->htt_owner=s;
 s->epoch=r->epoch;
 s->last=now;
 s->deadline=now+3000000;
 s->cookie=0xa0000001;
 
 if(!guard(s,now)){(void)stop(s,1);
 return 0;
 }
 QcaInitAdapter*a=adapter(s);
 uint8_t*p=a->channels.buffers[9].host;
 
 QcaHtcSession*h=&r->startup->operating->control.session;
 
 if(!qca_htc_header(p,256,s->binding.endpoint,4,h->sequence,0)||qca_htt_version_request(&s->binding,p+8,4)!=4){(void)stop(s,2);
 return 0;
 }
 s->watermark=r->rx.completed;
 s->attempted=1;
 s->phase=QCA_HTTN_POSTED;
 h->sequence++;
 
 atomic_thread_fence(memory_order_release);
 
 if(qca_ce_post(&a->channels.rings[4],a->channels.buffers[9].address,12,s->cookie,s->binding.endpoint,0)){(void)stop(s,3);
 return 0;
 }
 return 1;
 
}
static int observe(QcaHttNative*s){
 QcaPersistentRx*x=&s->radio->rx;
 
 if(!x->count)return 0;
 
 const QcaRxEvent*e=&x->events[x->head];
 
 if(e->endpoint==s->binding.endpoint&&e->pipe==1&&e->bytes&&e->payload[0]==0){
  if(s->version_seen||s->response.completion)return stop(s,8);
 
  if(!qca_rx_take(x,e->completion,&s->response,sizeof(s->response)))return stop(s,9);
 
  s->consumed++;
 
  if(s->response.completion<=s->watermark||!qca_htt_version_conf(&s->binding,s->response.payload,s->response.bytes,&s->version))return stop(s,10);
 
  s->version_seen=1;
 
 }else{
  if(s->archive_count==2)return stop(s,11);
  /* queue stays owned */
  if(!qca_rx_take(x,e->completion,&s->archive[s->archive_count],sizeof(QcaRxEvent)))return stop(s,9);
 
  s->archive_count++;
 s->consumed++;
 
 }
 return 0;
 
}
int qca_htt_native_poll(QcaHttNative*s,uint64_t now){
 if(!s||!s->phase)return -1;
 
 if(!bound(s))return stop(s,4);
 
 if(s->phase==QCA_HTTN_RELEASED)return 1;
 
 if(s->stop_requested){
  (void)qca_persistent_poll(s->radio,now);
 
  if(!s->error&&qca_persistent_unload_safe(s->radio)){s->phase=QCA_HTTN_RELEASED;
 return 1;
 }
  return s->error?-1:0;
 
 }
 if(now<s->last)return stop(s,5);
 s->last=now;
 
 if(!guard(s,now))return stop(s,6);
 
 if(observe(s)<0)return -1;
 
 if(!s->dma_completed){
  QcaInitAdapter*a=adapter(s);
 unsigned index=0;
 uint32_t cookie=0,n=0;
 
  if(qca_ce_hw_index(&a->bus.engines[4],0,&index))return stop(s,12);
 
  int rc=qca_ce_complete(&a->channels.rings[4],index,&cookie,&n);
 
  if(rc<0)return stop(s,13);
 
  if(!rc){if(cookie!=s->cookie||n!=12)return stop(s,14);
 s->dma_completed=1;
 }
 }
 if(s->dma_completed&&s->version_seen)return stop(s,0);
 
 if(now>=s->deadline)return stop(s,7);
 
 if(s->radio->rx.backpressure)return stop(s,11);
 
 return 0;
 
}
int qca_htt_native_export(const QcaHttNative*s,unsigned slot,QcaRxEvent*out,unsigned bytes){
 if(!s||!out||bytes<sizeof(*out)||slot>5||(uintptr_t)s>UINTPTR_MAX-sizeof(*s)||(uintptr_t)out>UINTPTR_MAX-sizeof(*out)||overlap(s,sizeof(*s),out,sizeof(*out)))return 0;
 
 const QcaRxEvent*e=0;
 
 if(!s->stop_requested||!s->radio||s->radio->htt_owner!=s||(uintptr_t)s->radio>UINTPTR_MAX-sizeof(*s->radio)||overlap(s->radio,sizeof(*s->radio),out,sizeof(*out)))return 0;
 
 if(slot==5)e=&s->radio->rx.rejected;
 
 else if(slot<3)e=slot?&s->archive[slot-1]:&s->response;
 
 else {const QcaPersistentRx*x=&s->radio->rx;
 unsigned at=slot-3;
 
  if(x->count>2||x->head>1||at>=x->count)return 0;
 e=&x->events[(x->head+at)&1];
 }
 if(!e->completion)return 0;
 *out=*e;
 return 1;
 
}
