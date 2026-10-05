#include "operating.h"
#include <stdatomic.h>
static QcaInitAdapter*adapter(QcaBootNative*b){return b->board->setup->read.full.adapter;}
static int fail(QcaOperating*s,unsigned e){s->error=e;s->phase=3;return -1;}
static int active(QcaBootNative*b){
 if(!b||b->phase!=5||b->error||!b->owns_pin||!b->asset||!b->asset->ready||!b->asset->pinned||b->asset->poisoned||!b->board||!b->board->setup)return -1;
 QcaInitAdapter*a=adapter(b);
 if(!a||a->phase!=QCA_INIT_READY||a->error||a->cancelled||a->bus.phase!=QCA_BUS_ACTIVE||!a->bus.owned
  ||a->access.count!=14||a->channels.allocated!=14||qca_mapped_irq_active_guard(&a->mapped))return -1;
 for(unsigned i=0;i<3;i++){
  QcaCeRing*r=&a->channels.rings[i];QcaDmaBuffer*d=&a->channels.buffers[2*i],*p=&a->channels.buffers[2*i+1];
  if(a->access.buffers[2*i]!=d||a->access.buffers[2*i+1]!=p||!r->owned||r->fault||r->entries!=8||r->receive!=(i!=0)
   ||r->descriptors!=d->host||!r->publish||!r->stop)return -1;
  if(i<2){
   QcaBmiPipe*route=&b->board->setup->bmi_routes[i];
   if(r->context!=route||route->bus!=&a->bus||route->receive!=(i!=0)
    ||r->publish!=qca_bmi_publish||r->stop!=qca_bmi_ring_stop)return -1;
  }else if(r->context!=&a->channels.routes[i]||a->channels.routes[i].bus!=&a->bus
   ||a->channels.routes[i].pipe!=2||!a->channels.routes[i].receive
   ||r->publish!=a->channels.rings[3].publish||r->stop!=a->channels.rings[3].stop)return -1;
  for(unsigned j=0;j<2;j++){
   QcaDmaBuffer*x=j?p:d;
   if(x->port!=a->access.port||!x->host||!x->allocated||!x->mapped||!x->valid||!x->exposed||x->closing||x->allocation_uncertain
    ||x->bytes!=4096||x->pages!=1||((uintptr_t)x->host&4095)||x->address>UINT32_MAX-4095u||(x->address&4095))return -1;
  }
  uint32_t base=0,count=0;
  if(qca_ce_access_read(&a->access,a->bus.engines[i].base+(i?8:0),&base)
   ||qca_ce_access_read(&a->access,a->bus.engines[i].base+(i?12:4),&count)||base!=d->address||count!=8)return -1;
 }
 return 0;
}
static int empty(QcaCeRing*r){return r->read==r->write&&r->read==r->published;}
int qca_operating_begin(QcaOperating*s,QcaBootNative*b,uint64_t now){
 if(!s||s->phase||now>UINT64_MAX-20000000||active(b))return -1;
 QcaInitAdapter*a=adapter(b);
 for(unsigned i=0;i<3;i++)if(!empty(&a->channels.rings[i]))return -1;
 QcaHtcSession session={0};
 if(qca_htc_session_begin(&session)||qca_htc_session_receive(&session,b->ready,b->ready_bytes))return -1;
 /* No large temporary or platform stack-probe dependency in native UEFI. */
 uint8_t*zero=(uint8_t*)s;for(unsigned i=0;i<sizeof(*s);i++)zero[i]=0;
 s->boot=b;s->control.session=session;s->started=s->last=now;s->phase=1;return 0;
}
static int post_receive(QcaOperating*s,unsigned i){
 QcaInitAdapter*a=adapter(s->boot);QcaCeRing*r=&a->channels.rings[i];QcaDmaBuffer*d=&a->channels.buffers[2*i+1];
 uint8_t*posted=i==1?&s->rx1_posted:&s->rx2_posted;
 if(*posted||!empty(r))return -1;
 for(unsigned j=0;j<2048;j++)((uint8_t*)d->host)[j]=0;
 atomic_thread_fence(memory_order_release);*posted=1;
 return qca_ce_post(r,d->address,2048,0x500+i,0,0);
}
static int receive(QcaOperating*s,unsigned i){
 uint8_t*posted=i==1?&s->rx1_posted:&s->rx2_posted;if(!*posted)return 0;
 QcaInitAdapter*a=adapter(s->boot);QcaCeRing*r=&a->channels.rings[i];
 unsigned index=0;uint32_t cookie=0,n=0;
 if(qca_ce_hw_index(&a->bus.engines[i],1,&index))return -1;
 int rc=qca_ce_complete(r,index,&cookie,&n);if(rc>0)return 0;
 if(rc<0||cookie!=0x500+i||n<8||n>2048)return -1;
 atomic_thread_fence(memory_order_acquire);const uint8_t*p=a->channels.buffers[2*i+1].host;
 *posted=0;s->rx_count++;
 if(i==1)return qca_htc_control_receive(&s->control,p,n);
 if(s->service_bytes)return -1;
 QcaHtcFrame f;if(!qca_htc_decode(p,n,&f))return -1;
 for(unsigned j=0;j<n;j++)s->service_frame[j]=p[j];
 s->service_bytes=n;return 0;
}
int qca_operating_poll(QcaOperating*s,uint64_t now){
 if(!s||!s->phase||s->phase==3)return -1;
 if(now<s->last)return fail(s,1);
 s->last=now;
 if(active(s->boot))return fail(s,2);
 if(s->cancelled)return fail(s,3);
 if(s->phase==2)return 1;
 if(receive(s,1))return fail(s,4);
 if(receive(s,2))return fail(s,5);
 QcaInitAdapter*a=adapter(s->boot);
 if(s->control.posted){
  unsigned index=0;uint32_t cookie=0,n=0;
  if(qca_ce_hw_index(&a->bus.engines[0],0,&index))return fail(s,6);
  int rc=qca_ce_complete(&a->channels.rings[0],index,&cookie,&n);
  if(rc<0)return fail(s,7);
  if(!rc){if(cookie!=0x400||n!=s->control.posted||qca_htc_control_complete(&s->control,n))return fail(s,8);}
 }
 if(s->service_bytes&&s->control.session.wmi.endpoint&&!s->service_valid){
  QcaHtcFrame f;QcaWmiServiceInfo info;
  if(!qca_htc_decode(s->service_frame,s->service_bytes,&f)||f.endpoint!=s->control.session.wmi.endpoint
   ||!qca_wmi_service_info(f.payload,f.payload_bytes,&info))return fail(s,9);
  for(unsigned i=0;i<QCA_HTC_ENDPOINTS;i++)if(f.credits[i])return fail(s,10);
  s->service=info;s->service_valid=1;
 }
 if(s->control.session.phase==QCA_HTC_RUNNING&&s->service_valid){s->phase=2;return 1;}
 if(now-s->started>=20000000)return fail(s,11);
 unsigned p=s->control.session.phase;
 if(!s->control.posted&&(p==QCA_HTC_SEND_WMI||p==QCA_HTC_SEND_HTT||p==QCA_HTC_SEND_SETUP)){
  if(!s->rx2_posted&&!s->service_bytes&&post_receive(s,2))return fail(s,12);
  if(p!=QCA_HTC_SEND_SETUP&&!s->rx1_posted&&post_receive(s,1))return fail(s,13);
  QcaCeRing*r=&a->channels.rings[0];if(!empty(r))return fail(s,14);
  uint8_t*data=a->channels.buffers[1].host;
  unsigned n=qca_htc_control_prepare(&s->control,data,256);
  if(!n||qca_htc_control_post(&s->control,n))return fail(s,15);
  atomic_thread_fence(memory_order_release);s->tx_count++;
  /* Pinned Linux HTC uses endpoint id as CE transfer metadata: endpoint0,
   * unlike the special0x3fff BMI diagnostic transfer id. */
  if(qca_ce_post(r,a->channels.buffers[1].address,n,0x400,0,0))return fail(s,16);
 }
 return 0;
}
void qca_operating_cancel(QcaOperating*s){if(s)s->cancelled=1;}
