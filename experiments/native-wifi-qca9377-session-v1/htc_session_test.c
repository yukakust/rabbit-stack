#include "htc_session.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void u16(uint8_t*p,unsigned n){p[0]=n;p[1]=n>>8;}
static void response(uint8_t*p,unsigned id,unsigned service,unsigned ep){memset(p,0,16);u16(p+2,8);u16(p+8,id);u16(p+10,service);p[13]=ep;u16(p+14,1536);}
int main(void){
 QcaHtcSession s={0},old;uint8_t rx[32],tx[64],again[64];unsigned checks=0;
 assert(!qca_htc_session_begin(&s));assert(qca_htc_session_begin(&s)==-1);checks++;
 memset(rx,0,sizeof(rx));u16(rx+2,8);u16(rx+8,1);u16(rx+10,12);u16(rx+12,256);rx[14]=9;
 assert(!qca_htc_session_receive(&s,rx,16)&&s.phase==QCA_HTC_SEND_WMI);checks++;
 old=s;assert(qca_htc_session_transmitted(&s,16)==-1&&!memcmp(&s,&old,sizeof(s)));checks++;
 assert(qca_htc_session_prepare(&s,tx,sizeof(tx))==16);assert(qca_htc_session_prepare(&s,again,sizeof(again))==16&&!memcmp(tx,again,16));checks++;
 old=s;response(rx,3,QCA_HTC_WMI,2);assert(qca_htc_session_receive(&s,rx,16)==-1&&!memcmp(&s,&old,sizeof(s)));checks++;
 assert(qca_htc_session_transmitted(&s,15)==-1&&!memcmp(&s,&old,sizeof(s)));checks++;
 assert(!qca_htc_session_transmitted(&s,16)&&s.sequence==1);checks++;
 old=s;response(rx,3,QCA_HTC_HTT,2);assert(qca_htc_session_receive(&s,rx,16)==-1&&!memcmp(&s,&old,sizeof(s)));checks++;
 response(rx,3,QCA_HTC_WMI,9);assert(qca_htc_session_receive(&s,rx,16)==-1&&!memcmp(&s,&old,sizeof(s)));checks++;
 response(rx,3,QCA_HTC_WMI,2);assert(!qca_htc_session_receive(&s,rx,16)&&s.phase==QCA_HTC_SEND_HTT);checks++;
 assert(qca_htc_session_prepare(&s,tx,sizeof(tx))==16&&tx[5]==1);assert(!qca_htc_session_transmitted(&s,16));checks++;
 old=s;response(rx,3,QCA_HTC_HTT,2);assert(qca_htc_session_receive(&s,rx,16)==-1&&!memcmp(&s,&old,sizeof(s)));checks++;
 response(rx,3,QCA_HTC_HTT,1);assert(!qca_htc_session_receive(&s,rx,16)&&s.phase==QCA_HTC_SEND_SETUP);checks++;
 assert(qca_htc_session_prepare(&s,tx,sizeof(tx))==20&&tx[5]==2);assert(!qca_htc_session_transmitted(&s,20)&&s.phase==QCA_HTC_RUNNING);checks++;
 old=s;assert(qca_htc_session_receive(&s,rx,16)==-1&&!memcmp(&s,&old,sizeof(s)));checks++;
 assert(!qca_htc_session_prepare(&s,tx,sizeof(tx)));assert(qca_htc_session_transmitted(&s,20)==-1&&!memcmp(&s,&old,sizeof(s)));checks++;
 puts("HTC HANDSHAKE ORDER, TX RECEIPTS, ENDPOINT CORRELATION AND REJECTIONS PASS");printf("assertion_groups=%u\n",checks);return 0;
}
