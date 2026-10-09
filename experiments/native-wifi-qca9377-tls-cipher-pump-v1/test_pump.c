#include "pump.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static TlsCipherPump p;
static struct {uint64_t us;unsigned feeds,polls,drains,revokes,bad,reenter,disconnect;uint32_t sequence;uint8_t received[240];size_t count;} m;
static int clockfn(void*c,uint64_t*out){assert(c==&m);*out=m.us;return m.bad==4?-1:0;}
static int feed(void*c,uint64_t e,uint32_t seq,const uint8_t*b,size_t n){assert(c==&m&&e==66&&p.busy);m.feeds++;m.sequence=seq;m.count=n;memcpy(m.received,b,n);if(m.reenter)assert(tp_close(&p,66)<0);if(m.disconnect)tp_disconnected(&p);return m.bad==1?-1:1;}
static int poll(void*c,uint64_t e,uint64_t us){assert(c==&m&&e==66&&p.busy&&us==p.last);m.polls++;return m.bad==2?-1:0;}
static int drain(void*c,uint64_t e,uint8_t*b,size_t n){assert(c==&m&&e==66&&p.busy&&n==240);m.drains++;memset(b,0x55,n);return m.bad==3?241:240;}
static int revoke(void*c,uint64_t e){assert(c==&m&&e==66&&p.busy);m.revokes++;if(m.reenter)assert(tp_close(&p,66)<0);return m.bad==5?-1:0;}
static void bind(void){memset(&p,0,sizeof p);memset(&m,0,sizeof m);m.us=1;TpOps ops={&m,sizeof m,clockfn,feed,poll,drain,revoke};assert(!tp_bind(&p,&ops,66,1,100));}
static void empty(void){for(unsigned i=0;i<240;i++)assert(!p.incoming[i]&&!p.previous[i]&&!p.outgoing[i]);assert(!p.incoming_bytes&&!p.previous_bytes&&!p.outgoing_bytes);}
int main(void){uint8_t in[240],out[240];uint32_t seq;memset(in,0xa1,sizeof in);unsigned cases=0;
 bind();assert(!tp_offer(&p,66,0,in,240,1));assert(!m.feeds&&!m.polls);assert(!tp_offer(&p,66,0,in,240,1));assert(!tp_poll(&p,66,1));assert(m.feeds==1&&m.polls==1&&m.drains==1&&m.sequence==0&&m.count==240&&!memcmp(in,m.received,240));assert(!tp_offer(&p,66,0,in,240,1));assert(tp_view(&p,66,out,240,&seq,1)==240&&seq==0);assert(tp_view(&p,66,out,239,&seq,1)==-2);assert(tp_view(&p,66,out,240,&seq,1)==240&&seq==0);assert(!tp_poll(&p,66,1)&&m.drains==1);assert(!tp_ack(&p,66,0,1)&&!tp_ack(&p,66,0,1));assert(!tp_poll(&p,66,1)&&m.drains==2);assert(tp_view(&p,66,out,240,&seq,1)==240&&seq==1);assert(!tp_ack(&p,66,0,1)&&p.outgoing_bytes==240);assert(!tp_close(&p,66)&&m.revokes==1);empty();assert(!tp_close(&p,66)&&m.revokes==1);cases++;
 for(unsigned mode=0;mode<12;mode++){
  bind();assert(!tp_offer(&p,66,0,in,240,1));
  switch(mode){
   case 0:assert(tp_poll(&p,65,1)<0);break;
   case 1:assert(tp_poll(&p,66,101)<0);break;
   case 2:m.us=101;assert(tp_poll(&p,66,1)<0);break;
   case 3:m.us=0;assert(tp_poll(&p,66,1)<0);break;
   case 4:m.bad=1;assert(tp_poll(&p,66,1)<0);break;
   case 5:m.bad=2;assert(tp_poll(&p,66,1)<0);break;
   case 6:m.bad=3;assert(tp_poll(&p,66,1)<0);break;
   case 7:m.bad=4;assert(tp_poll(&p,66,1)<0);break;
   case 8:m.disconnect=1;assert(tp_poll(&p,66,1)<0);break;
   case 9:tp_disconnected(&p);assert(!m.revokes);break;
   case 10:in[0]^=1;assert(tp_offer(&p,66,0,in,240,1)<0);in[0]^=1;break;
   case 11:assert(tp_offer(&p,66,1,in,240,1)<0);break;
  }
  assert(p.fault);empty();m.bad=0;assert(tp_poll(&p,66,1)<0&&m.revokes==1);assert(tp_poll(&p,66,1)<0&&m.revokes==1);assert(!tp_close(&p,66));cases++;
 }
 bind();m.reenter=1;assert(!tp_offer(&p,66,0,in,240,1));assert(!tp_poll(&p,66,1));assert(!tp_close(&p,66));empty();cases++;
 bind();m.bad=5;assert(tp_close(&p,66)<0&&!p.closed&&m.revokes==1);m.bad=0;assert(!tp_close(&p,66)&&m.revokes==2);cases++;
 bind();p.rx_next=UINT32_MAX;assert(tp_offer(&p,66,UINT32_MAX,in,240,1)<0);empty();cases++;
 bind();p.tx_next=UINT32_MAX;assert(tp_poll(&p,66,1)<0);empty();cases++;
 bind();assert(tp_offer(&p,66,0,p.incoming,1,1)<0&&!p.fault);assert(tp_view(&p,66,out,240,(uint32_t*)out,1)<0);assert(!tp_close(&p,66));cases++;
 printf("CIPHERTEXT-PUMP %u adversarial cases; providers injected, TLS/physical pairing authority=0\n",cases);return 0;}
