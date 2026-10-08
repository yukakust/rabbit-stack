#include "filter_barrier.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static void begin(QcaFilterBarrier*s,QcaHtcCredit*c,uint64_t at){memset(s,0,sizeof(*s));memset(c,0,sizeof(*c));QcaHtcReady h={.credits=8,.credit_size=256,.endpoints=3};QcaHtcConnection w={.service=QCA_HTC_WMI,.max_bytes=4088,.endpoint=1};assert(qca_htc_credit_begin(c,&h,&w));uint8_t ready[44]={0};put(ready,2);put(ready+4,36|(35u<<16));put(ready+8,0x01000000);put(ready+12,574);put(ready+16,0x5f414351);put(ready+20,0x4c4d);ready[32]=2;ready[37]=1;assert(qca_filter_begin(s,c,ready,44,7,0,0x64000001,at));}
static void post(QcaFilterBarrier*s,QcaHtcCredit*c,unsigned id,uint64_t at){assert(qca_filter_prepare(s,7,at));assert(qca_filter_submitted(s,7,id,at));uint8_t raw[36]={0};assert(qca_htc_header(raw,36,1,s->frame_bytes,(uint8_t)id,1));memcpy(raw+8,s->frame,s->frame_bytes);uint32_t ticket;assert(qca_htc_credit_reserve(c,s->frame_bytes+8,&ticket));assert(qca_htc_credit_commit(c,ticket));assert(qca_filter_post(s,7,id,id==3?6:0,raw,s->frame_bytes+8,at));}
static void slow(QcaFilterBarrier*s,QcaHtcCredit*c){begin(s,c,0);post(s,c,1,800000);assert(qca_filter_tx_complete(s,7,1,36,1600000));post(s,c,2,2000000);assert(qca_filter_tx_complete(s,7,2,20,2800000));post(s,c,3,3600000);assert(s->overall_deadline==12000000&&s->echo_deadline==6600000&&s->stage_deadline==5800000&&qca_filter_effective_deadline(s)==6600000);}
static unsigned echo(QcaFilterBarrier*s,uint64_t at,unsigned completion,uint32_t arg){uint8_t raw[20]={1,0,12};put(raw+8,0x1d001);put(raw+12,4|(54u<<16));put(raw+16,arg);return qca_filter_receive(s,7,completion,2,raw,20,at);}
int main(void){QcaFilterBarrier s;QcaHtcCredit c,before;unsigned checks=0;
 for(unsigned order=0;order<2;order++){slow(&s,&c);before=c;assert(qca_filter_poll(&s,7,3900000)==0);if(order){assert(echo(&s,4000000,8,s.echo_arg)==1&&!qca_filter_passed(&s));assert(qca_filter_tx_complete(&s,7,3,20,4100000));}else{assert(qca_filter_tx_complete(&s,7,3,20,4000000));assert(echo(&s,6000000,8,s.echo_arg)==1);}assert(qca_filter_passed(&s)&&!memcmp(&before,&c,sizeof(c)));uint64_t last=s.last_poll,gap=s.maximum_poll_gap;assert(qca_filter_poll(&s,7,10000000)==1&&s.last_poll==last&&s.maximum_poll_gap==gap);checks++;}
 for(unsigned late=0;late<2;late++){slow(&s,&c);assert((int)echo(&s,6600000+late,8,s.echo_arg)<0&&s.error==4&&!qca_filter_passed(&s)&&s.timeout_observed==6600000+late);checks++;}
 slow(&s,&c);assert(echo(&s,4000000,8,s.echo_arg)==1&&!qca_filter_passed(&s));assert(qca_filter_poll(&s,7,6600000)<0&&!qca_filter_passed(&s));checks++;
 for(unsigned fault=0;fault<4;fault++){slow(&s,&c);int rc=fault==0?(int)echo(&s,4000000,6,s.echo_arg):fault==1?(int)echo(&s,4000000,8,s.echo_arg+1):fault==2?qca_filter_poll(&s,8,4000000):qca_filter_poll(&s,7,3599999);assert(rc<0&&!qca_filter_passed(&s));checks++;}
 begin(&s,&c,0);post(&s,&c,1,2900000);assert(qca_filter_tx_complete(&s,7,1,36,2999999));post(&s,&c,2,5900000);assert(qca_filter_tx_complete(&s,7,2,20,5999998));post(&s,&c,3,8900000);assert(s.echo_deadline==11900000);assert(qca_filter_poll(&s,7,12000000)<0&&s.error==4);checks++;
 memset(&s,0,sizeof(s));QcaFilterBarrier prior=s;assert(!qca_filter_begin(&s,&c,(uint8_t[44]){0},44,7,0,1,UINT64_MAX-11999999)&&!memcmp(&prior,&s,sizeof(s)));checks++;
 printf("FILTER64 TIMING %u bounded slow/order/deadline/missingDMA/epoch/arg/floor/overflow checks PASS; synthetic only\n",checks);
}
