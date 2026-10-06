#include "startup.h"
#include <stdatomic.h>
static QcaInitAdapter*adapter(QcaWmiStartup*s){return s->operating->boot->board->setup->read.full.adapter;}
static int empty(QcaCeRing*r){return r->read==r->write&&r->read==r->published;}
static int tx_guard(QcaWmiStartup*s){
 QcaInitAdapter*a=adapter(s);QcaChannels*c=&a->channels;QcaCeRing*r=&c->rings[3];
 if(qca_channels_retained(c)||!r->owned||r->fault||r->entries!=8||r->receive
  ||r->descriptors!=c->buffers[6].host||r->context!=&c->routes[3]
  ||c->routes[3].bus!=&a->bus||c->routes[3].pipe!=3||c->routes[3].receive
  ||r->publish!=c->rings[4].publish||r->stop!=c->rings[4].stop)return -1;
 for(unsigned j=0;j<14;j++)if(!c->buffers[j].exposed)return -1;
 uint32_t base=0,entries=0;
 if(qca_ce_access_read(&a->access,a->bus.engines[3].base,&base)
  ||qca_ce_access_read(&a->access,a->bus.engines[3].base+4,&entries)
  ||base!=c->buffers[6].address||entries!=8)return -1;
 return 0;
}
static int fail(QcaWmiStartup*s,unsigned error){
 if(s->transaction.phase==QCA_INIT_RESERVED)(void)qca_wmi_init_cancel(&s->transaction);
 else qca_wmi_init_fault(&s->transaction);
 s->phase=3;s->error=error;return -1;
}
int qca_wmi_startup_begin(QcaWmiStartup*s,QcaOperating*o,uint64_t now){
 if(!s||s->phase||!o||o->phase!=2||!o->service_valid||now>UINT64_MAX-20000000)return -1;
 uintptr_t a=(uintptr_t)s,b=(uintptr_t)o;
 if(a>UINTPTR_MAX-sizeof(*s)||b>UINTPTR_MAX-sizeof(*o)||(a<b?b-a<sizeof(*s):a-b<sizeof(*o)))return -1;
 if(qca_operating_poll(o,now)!=1)return -1; /* Actual retained14-map/pin guard. */
 uint8_t*zero=(uint8_t*)s;for(unsigned j=0;j<sizeof(*s);j++)zero[j]=0;
 s->operating=o;s->started=s->last=now;s->phase=1;
 if(o->service.memory_count)return fail(s,1); /* New host DMA ownership not implemented. */
 QcaInitAdapter*d=adapter(s);
 if(o->rx1_posted||o->rx2_posted||o->control.posted||o->control.deferred_bytes)return fail(s,2);
 for(unsigned j=0;j<4;j++)if(!empty(&d->channels.rings[j]))return fail(s,2);
 if(tx_guard(s))return fail(s,19);
 if(!qca_tlv_resources(&o->service,&s->resources))return fail(s,3);
 if(!qca_wmi_init_begin(&s->transaction,&o->control.credit,&o->control.session,&o->service,
  &s->resources.memory,s->resources.words,0,0))return fail(s,4);
 return 0;
}
static int post_rx(QcaWmiStartup*s,unsigned pipe){
 QcaInitAdapter*a=adapter(s);QcaCeRing*r=&a->channels.rings[pipe];
 uint8_t*posted=pipe==1?&s->rx1_posted:&s->rx2_posted;
 if(*posted||!empty(r))return -1;
 for(unsigned j=0;j<2048;j++)((uint8_t*)a->channels.buffers[2*pipe+1].host)[j]=0;
 *posted=1;atomic_thread_fence(memory_order_release);
 return qca_ce_post(r,a->channels.buffers[2*pipe+1].address,2048,0x600+pipe,0,0);
}
static int receive(QcaWmiStartup*s,unsigned pipe){
 uint8_t*posted=pipe==1?&s->rx1_posted:&s->rx2_posted;if(!*posted)return 0;
 QcaInitAdapter*a=adapter(s);QcaCeRing*r=&a->channels.rings[pipe];unsigned index=0;uint32_t cookie=0,n=0;
 if(qca_ce_hw_index(&a->bus.engines[pipe],1,&index)){s->diagnostic[0]=pipe;s->diagnostic[1]=1;return -1;}
 unsigned read=r->read;int rc=qca_ce_complete(r,index,&cookie,&n);if(rc>0)return 0;
 s->diagnostic[0]=pipe;s->diagnostic[1]=0;s->diagnostic[2]=index;s->diagnostic[3]=read;
 s->diagnostic[4]=r->write;s->diagnostic[5]=r->published;s->diagnostic[6]=cookie;s->diagnostic[7]=n;
 s->diagnostic[8]=r->fault;s->diagnostic[9]=a->bus.engines[pipe].error;
 if(rc<0){s->diagnostic[1]=2;return -1;}
 if(cookie!=0x600+pipe||n<8||n>2048){s->diagnostic[1]=3;return -1;}
 atomic_thread_fence(memory_order_acquire);const uint8_t*p=a->channels.buffers[2*pipe+1].host;
 for(unsigned j=0;j<64;j++)s->prefix[j]=j<n?p[j]:0;
 *posted=0;
 if(s->rx_count==UINT32_MAX||!qca_wmi_init_receive(&s->transaction,p,n,s->rx_count+1)){s->diagnostic[1]=4;return -1;}
 s->rx_count++;return 0;
}
int qca_wmi_startup_poll(QcaWmiStartup*s,uint64_t now){
 if(!s||!s->phase||s->phase==3)return -1;
 if(now<s->last)return fail(s,5);
 s->last=now;
 if(qca_operating_poll(s->operating,now)!=1)return fail(s,6);
 if(tx_guard(s))return fail(s,19);
 if(s->cancelled)return fail(s,7);
 if(s->phase==2)return 1;
 if(receive(s,1)||receive(s,2))return fail(s,8);
 QcaInitAdapter*a=adapter(s);
 if(s->tx_posted){
  unsigned index=0;uint32_t cookie=0,n=0;
  if(qca_ce_hw_index(&a->bus.engines[3],0,&index))return fail(s,9);
  int rc=qca_ce_complete(&a->channels.rings[3],index,&cookie,&n);
  if(rc<0)return fail(s,10);
  if(!rc){
   if(cookie!=0x601||n!=s->tx_posted||!qca_wmi_init_complete(&s->transaction,n))return fail(s,11);
   s->tx_posted=0;
  }
 }
 if(s->transaction.phase==QCA_INIT_RUNNING){s->phase=2;return 1;}
 if(now-s->started>=20000000)return fail(s,12);
 if(!s->rx1_posted&&post_rx(s,1))return fail(s,13);
 if(!s->rx2_posted&&post_rx(s,2))return fail(s,14);
 if(s->transaction.phase==QCA_INIT_RESERVED){
  if(!empty(&a->channels.rings[3]))return fail(s,15);
  uint8_t*p=a->channels.buffers[7].host;unsigned n=s->transaction.frame_bytes;
  if(n!=228||n>4096)return fail(s,16);
  for(unsigned j=0;j<n;j++)p[j]=s->transaction.frame[j];
  if(!qca_wmi_init_post(&s->transaction))return fail(s,17);
  s->tx_posted=n;s->tx_count++;atomic_thread_fence(memory_order_release);
  if(qca_ce_post(&a->channels.rings[3],a->channels.buffers[7].address,n,0x601,s->operating->control.session.wmi.endpoint,0))return fail(s,18);
 }
 return 0;
}
void qca_wmi_startup_cancel(QcaWmiStartup*s){if(s){s->cancelled=1;if(s->phase==1)(void)fail(s,7);}}
