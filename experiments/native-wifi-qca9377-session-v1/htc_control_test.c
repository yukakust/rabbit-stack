#include "htc_control.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do{checks++;assert(x);}while(0)
static void same(const QcaHtcControl*a,const QcaHtcControl*b){CHECK(!memcmp(a,b,sizeof *a));}
static void conn(uint8_t*p,unsigned service,unsigned ep){
 memset(p,0,16);p[2]=8;p[8]=3;p[10]=(uint8_t)service;p[11]=(uint8_t)(service>>8);p[13]=(uint8_t)ep;p[14]=0xf8;p[15]=0x0f;
}
int main(void){
 for(unsigned wmi=1;wmi<4;wmi++)for(unsigned htt=1;htt<4;htt++)if(wmi!=htt)
 for(unsigned order=0;order<4;order++){
  QcaHtcControl s={0},before;uint8_t packet[32],reply[20]={0};
  CHECK(!qca_htc_control_begin(&s));reply[2]=12;reply[8]=1;reply[10]=2;reply[12]=0;reply[13]=7;reply[14]=4;
  CHECK(!qca_htc_control_receive(&s,reply,20));CHECK(s.session.phase==QCA_HTC_SEND_WMI);
  for(unsigned step=0;step<2;step++){
   unsigned service=step?QCA_HTC_HTT:QCA_HTC_WMI;
   unsigned ep=step?htt:wmi;before=s;
   CHECK(!qca_htc_control_prepare(&s,packet,15));same(&s,&before);
   CHECK(qca_htc_control_prepare(&s,packet,sizeof packet)==16);
   uint8_t repeated[32];CHECK(qca_htc_control_prepare(&s,repeated,sizeof repeated)==16);CHECK(!memcmp(packet,repeated,16));
   CHECK(!qca_htc_control_post(&s,16));before=s;
   CHECK(qca_htc_control_post(&s,16)<0);same(&s,&before);
   CHECK(!qca_htc_control_prepare(&s,packet,sizeof packet));same(&s,&before);
   CHECK(qca_htc_control_complete(&s,15)<0);same(&s,&before);
   conn(reply,service,ep);reply[12]=1;CHECK(qca_htc_control_receive(&s,reply,16)<0);same(&s,&before);reply[12]=0;
   if(order&(1u<<step)){
    CHECK(!qca_htc_control_receive(&s,reply,16));CHECK(s.deferred_bytes==16);before=s;
    CHECK(qca_htc_control_receive(&s,reply,16)<0);same(&s,&before);
    memset(reply,0,16);CHECK(!qca_htc_control_complete(&s,16));
   }else{
    CHECK(!qca_htc_control_complete(&s,16));CHECK(!qca_htc_control_receive(&s,reply,16));
   }
   CHECK(!s.posted&&!s.deferred_bytes);CHECK(s.session.sequence==step+1);
   before=s;CHECK(qca_htc_control_complete(&s,16)<0);same(&s,&before);
  }
  CHECK(qca_htc_control_prepare(&s,packet,sizeof packet)==20);CHECK(!qca_htc_control_post(&s,20));
  before=s;CHECK(qca_htc_control_receive(&s,reply,16)<0);same(&s,&before);
  CHECK(!qca_htc_control_complete(&s,20));CHECK(s.session.phase==QCA_HTC_RUNNING);
  CHECK(s.credit.endpoint==wmi&&s.credit.total==2&&s.credit.size==1792&&s.credit.available==2);
  uint32_t t=0;CHECK(qca_htc_credit_reserve(&s.credit,1793,&t));CHECK(s.credit.reserved==2);
  CHECK(qca_htc_credit_commit(&s.credit,t));CHECK(!s.credit.available);
  before=s;CHECK(!qca_htc_control_prepare(&s,packet,sizeof packet));same(&s,&before);
 }
 CHECK(qca_htc_control_begin(0)<0);CHECK(qca_htc_control_receive(0,0,0)<0);
 printf("CONTROL %u endpoint/early-RX/owner-order checks PASS\n",checks);return 0;
}
