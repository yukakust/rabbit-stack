#include "bt_event_stream.h"
#include "hci_link.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
/* ATT is not exercised; these stubs only satisfy the actual link ABI. */
void rg_init(RgServer*s,RfApply apply){(void)apply;memset(s,0,sizeof(*s));s->mtu=23;}
void rg_disconnected(RgServer*s){s->mtu=23;}
size_t rg_att(RgServer*s,const uint8_t*p,size_t n,uint8_t*r,size_t cap){(void)s;(void)p;(void)n;(void)r;(void)cap;return 0;}
typedef struct {unsigned count,bytes;uint8_t observed[8192];RlLink*link;} Capture;
static void collect(void*ctx,const uint8_t*p,unsigned n){Capture*c=ctx;assert(c->bytes+n<=sizeof(c->observed));memcpy(c->observed+c->bytes,p,n);c->bytes+=n;c->count++;if(c->link)rl_event(c->link,p,n);}
static unsigned checks;
static void connected(RlLink*l){rl_init(l,0);l->state=RL_ADVERTISING;l->buffers=l->credits=2;l->acl_size=27;}
int main(void){
 /* Exact ordinary event shapes, explicit mock controller/USB, no real radio. */
 uint8_t connection[21]={0x3e,19,1,0,2,0,1,0,0x7c,0x15,0xce,0xcd,0xa6,0x74,24,0,0,0,72,0,1};
 RlLink old,new;connected(&old);connected(&new);rl_event(&old,connection,16);rl_event(&old,connection+16,5);assert(old.state==RL_ADVERTISING);
 RabbitBtEventStream s={0};Capture c={0};c.link=&new;
 assert(!rabbit_bt_events(&s,connection,16,collect,&c)&&c.count==0&&new.state==RL_ADVERTISING);
 assert(!rabbit_bt_events(&s,connection+16,5,collect,&c)&&c.count==1&&new.state==RL_CONNECTED&&new.handle==2&&s.used==0);checks++;
 uint8_t completions[14]={0x13,5,1,2,0,1,0,0x13,5,1,2,0,1,0};old=new;old.inflight=new.inflight=2;old.credits=new.credits=0;
 rl_event(&old,completions,14);assert(old.credits==0&&old.inflight==2);
 assert(!rabbit_bt_events(&s,completions,14,collect,&c)&&new.credits==2&&new.inflight==0&&c.count==3);checks++;
 for(unsigned payload=0;payload<=255;payload++){
  uint8_t event[257];event[0]=0xff;event[1]=(uint8_t)payload;for(unsigned j=0;j<payload;j++)event[j+2]=(uint8_t)j;
  unsigned n=payload+2;
  for(unsigned split=0;split<=n;split++){
   RabbitBtEventStream t={0};Capture d={0};assert(!rabbit_bt_events(&t,event,split,collect,&d));assert(!rabbit_bt_events(&t,event+split,n-split,collect,&d));assert(d.count==1&&d.bytes==n&&!memcmp(d.observed,event,n)&&!t.used&&!t.goal);checks++;
  }
  RabbitBtEventStream t={0};Capture d={0};for(unsigned i=0;i<n;i++)assert(!rabbit_bt_events(&t,event+i,1,collect,&d));assert(d.count==1&&!memcmp(d.observed,event,n));checks++;
 }
 uint8_t stream[8192];unsigned bytes=0,count=0;
 for(unsigned i=0;i<64;i++){unsigned n=i%64;stream[bytes++]=(uint8_t)(0xa0+i%16);stream[bytes++]=(uint8_t)n;for(unsigned j=0;j<n;j++)stream[bytes++]=(uint8_t)(i+j);count++;}
 for(unsigned block=1;block<=260;block++){
  RabbitBtEventStream t={0};Capture d={0};for(unsigned at=0;at<bytes;){unsigned n=bytes-at;if(n>block)n=block;assert(!rabbit_bt_events(&t,stream+at,n,collect,&d));at+=n;}assert(d.count==count&&d.bytes==bytes&&!memcmp(d.observed,stream,bytes)&&!t.used&&!t.goal);checks++;
 }
 RabbitBtEventStream t={0};Capture d={0};assert(!rabbit_bt_events(&t,connection,16,collect,&d));RabbitBtEventStream before=t;
 assert(rabbit_bt_events(&t,connection,261,collect,&d)==-1&&!memcmp(&before,&t,sizeof(t))&&!d.count);
 assert(rabbit_bt_events(&t,0,1,collect,&d)==-1&&!memcmp(&before,&t,sizeof(t)));
 assert(rabbit_bt_events(&t,connection,1,0,&d)==-1&&!memcmp(&before,&t,sizeof(t)));
 t.used=257;before=t;assert(rabbit_bt_events(&t,connection,1,collect,&d)==-1&&!memcmp(&before,&t,sizeof(t)));
 t=(RabbitBtEventStream){0};t.used=1;t.goal=5;before=t;assert(rabbit_bt_events(&t,connection,1,collect,&d)==-1&&!memcmp(&before,&t,sizeof(t)));
 printf("BT EVENT STREAM %u split/coalesced/credit mock cases PASS; BASELINE LOSES16+5 AND7+7; NOT NATIVE-INTEGRATED\n",checks);return 0;
}
