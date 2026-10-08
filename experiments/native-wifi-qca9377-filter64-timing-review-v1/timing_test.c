#include "filter_barrier.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
static const uint8_t echo_raw[20]={0x01,0x00,0x0c,0x00,0x00,0x0d,0x00,0x00,0x01,0xd0,0x01,0x00,0x04,0x00,0x36,0x00,0x01,0x00,0x00,0x63};
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static void begin(QcaFilterBarrier*s,QcaHtcCredit*c){
 memset(s,0,sizeof(*s));memset(c,0,sizeof(*c));QcaHtcReady h={.credits=8,.credit_size=256,.endpoints=3};QcaHtcConnection w={.service=QCA_HTC_WMI,.max_bytes=4088,.endpoint=1};assert(qca_htc_credit_begin(c,&h,&w));
 uint8_t ready[44]={0};put(ready,2);put(ready+4,36|(35u<<16));put(ready+8,0x01000000);put(ready+12,574);put(ready+16,0x5f414351);put(ready+20,0x4c4d);ready[32]=2;ready[37]=1;
 assert(qca_filter_begin(s,c,ready,44,7,0,0x63000001,0));
}
static void publish(QcaFilterBarrier*s,QcaHtcCredit*c,unsigned id,unsigned floor,uint64_t now){
 assert(qca_filter_prepare(s,7,now));assert(qca_filter_submitted(s,7,id,now));uint8_t raw[36]={0};assert(qca_htc_header(raw,36,1,s->frame_bytes,(uint8_t)id,1));memcpy(raw+8,s->frame,s->frame_bytes);uint32_t ticket;assert(qca_htc_credit_reserve(c,s->frame_bytes+8,&ticket));assert(qca_htc_credit_commit(c,ticket));assert(qca_filter_post(s,7,id,floor,raw,s->frame_bytes+8,now));
}
static void first_two(QcaFilterBarrier*s,QcaHtcCredit*c){begin(s,c);publish(s,c,1,0,800000);assert(qca_filter_tx_complete(s,7,1,36,1000000));publish(s,c,2,3,1400000);assert(qca_filter_tx_complete(s,7,2,20,1700000));publish(s,c,3,6,2400000);}
int main(void){QcaFilterBarrier s;QcaHtcCredit c,saved;QcaHtcFrame parsed={0};uint32_t arg=0;
 assert(qca_htc_decode(echo_raw,20,&parsed)&&qca_filter_echo_payload(parsed.payload,parsed.payload_bytes,&arg)&&arg==0x63000001);
 first_two(&s,&c);saved=c;assert(s.step==2&&s.tx_count==3&&!s.tx_completed&&s.echo_floor==6);
 assert(qca_filter_poll(&s,7,3100000)<0&&s.error==4&&!s.echo_seen);assert(qca_filter_receive(&s,7,8,2,echo_raw,20,3100000)<0);assert(!memcmp(&c,&saved,sizeof(c))&&!qca_filter_passed(&s));
 puts("SYNTHETIC frozen63: exact physical Echo bytes queued; global poll rejects before consume, DMA3 not invented");
 first_two(&s,&c);saved=c;assert(qca_filter_receive(&s,7,8,2,echo_raw,20,2900000)==1&&!qca_filter_passed(&s));assert(qca_filter_tx_complete(&s,7,3,20,2950000)&&qca_filter_passed(&s));assert(!memcmp(&c,&saved,sizeof(c)));
 puts("SYNTHETIC frozen63: exact Echo observed within global budget plus actual modeled DMA3 passes");
 first_two(&s,&c);assert(qca_filter_receive(&s,7,8,2,echo_raw,20,2900000)==1&&!qca_filter_passed(&s));assert(!qca_filter_tx_complete(&s,7,3,20,3100000)&&s.error==4&&!qca_filter_passed(&s));
 puts("SYNTHETIC frozen63: Echo alone does not bypass unobserved DMA or expired deadline");return 0;}
