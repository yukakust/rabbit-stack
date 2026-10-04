/* Actual link state machine with no USB/radio; stubs below only satisfy ATT API. */
#include <assert.h>
#include <string.h>
#include "hci_link.h"
void rg_init(RgServer*s,RfApply apply){(void)apply;memset(s,0,sizeof(*s));s->mtu=23;}
void rg_disconnected(RgServer*s){s->mtu=23;}
size_t rg_att(RgServer*s,const uint8_t*p,size_t n,uint8_t*r,size_t cap){(void)s;(void)p;(void)n;(void)r;(void)cap;return 0;}
static void idle(RlLink*l){rl_init(l,0);l->state=RL_ADVERTISING;l->step=7;l->buffers=l->credits=4;l->acl_size=251;}
int main(void){
 RlLink l;uint8_t out[260],kind;
 const uint8_t orphan[5]={0,0,0x48,0,1},disconnect[6]={5,4,0,3,0,0x13};
 idle(&l);rl_event(&l,orphan,sizeof(orphan));assert(l.state==RL_ADVERTISING);
 rl_event(&l,disconnect,sizeof(disconnect));
#ifdef BASELINE
 assert(l.state==RL_ADVERTISING);assert(!rl_take(&l,out,sizeof(out),&kind));
#else
 assert(l.state==RL_CONFIGURING&&!l.connected&&l.step==6);
 assert(rl_take(&l,out,sizeof(out),&kind)==4&&kind==1&&out[0]==0x0a&&out[1]==0x20&&out[3]==1);
 const uint8_t complete[6]={0x0e,4,1,0x0a,0x20,0};rl_event(&l,complete,sizeof(complete));assert(l.state==RL_ADVERTISING);
 uint8_t connected[21]={0x3e,19,1,0,4,0,1};rl_event(&l,connected,sizeof(connected));assert(l.state==RL_CONNECTED&&l.handle==4);
 rl_event(&l,disconnect,sizeof(disconnect));assert(l.state==RL_CONNECTED&&l.handle==4);
 connected[4]=3;idle(&l);rl_event(&l,connected,sizeof(connected));assert(l.state==RL_CONNECTED);
 rl_event(&l,disconnect,sizeof(disconnect));assert(l.state==RL_CONFIGURING&&!l.connected);
 uint8_t bad[6]={5,4,0,0xff,0xff,0x13};idle(&l);rl_event(&l,bad,sizeof(bad));assert(l.state==RL_ADVERTISING);
 bad[3]=3;bad[4]=0;bad[2]=1;rl_event(&l,bad,sizeof(bad));assert(l.state==RL_FAULT);
 idle(&l);l.pending=0x200a;rl_event(&l,disconnect,sizeof(disconnect));assert(l.state==RL_ADVERTISING&&l.pending==0x200a);
 idle(&l);l.state=RL_STOPPED;rl_event(&l,disconnect,sizeof(disconnect));assert(l.state==RL_STOPPED);
 idle(&l);l.state=RL_FAULT;rl_event(&l,disconnect,sizeof(disconnect));assert(l.state==RL_FAULT);
#endif
 return 0;
}
