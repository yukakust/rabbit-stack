#include "htc_credit.h"
#include "upstream-credit.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned long checks;
#define CHECK(x) do{checks++;assert(x);}while(0)
static void same(QcaHtcCredit a,QcaHtcCredit b){CHECK(!memcmp(&a,&b,sizeof a));}
int main(void){
 QcaHtcReady r={.credits=2,.credit_size=1792,.endpoints=4};
 QcaHtcConnection w={.service=QCA_HTC_WMI,.max_bytes=4088,.endpoint=1};
 QcaHtcCredit s={0};uint32_t ticket=0;
 CHECK(qca_htc_credit_begin(&s,&r,&w));
 CHECK(qca_htc_credit_reserve(&s,1792,&ticket));CHECK(s.available==1);
 CHECK(qca_htc_credit_commit(&s,ticket));QcaHtcCredit before=s;
 CHECK(!qca_htc_credit_commit(&s,ticket));same(s,before);
 CHECK(!qca_htc_credit_cancel(&s,ticket));same(s,before);
 QcaHtcFrame f={.endpoint=2};f.credits[1]=1;
 CHECK(qca_htc_credit_receive(&s,&f));CHECK(s.available==2);
 before=s;CHECK(!qca_htc_credit_receive(&s,&f));same(s,before);
 /* Cost oracle taken verbatim from pinned Linux. All admitted sizes/lengths. */
 for(unsigned size=1;size<=4096;size++)for(unsigned bytes=8;bytes<=4096;bytes++){
  r.credit_size=(uint16_t)size;r.credits=255;s=(QcaHtcCredit){0};
  CHECK(qca_htc_credit_begin(&s,&r,&w));before=s;ticket=0xabcdef;
  unsigned cost=oracle_credit_cost(bytes,size);
  int ok=qca_htc_credit_reserve(&s,bytes,&ticket);CHECK(ok==(cost<=255));
  if(ok){CHECK(s.available==255-cost&&s.reserved==cost);CHECK(qca_htc_credit_commit(&s,ticket));
   f=(QcaHtcFrame){.endpoint=1};f.credits[1]=(uint16_t)cost;
   CHECK(qca_htc_credit_receive(&s,&f));CHECK(s.available==255&&s.outstanding==0);
  }else{same(s,before);CHECK(ticket==0xabcdef);}
 }
 /* Every small reachable ledger state: credits received during a reservation
  * cannot make that reservation cancellable after commit. Reject atomically. */
 for(unsigned total=1;total<=16;total++)for(unsigned reserved=0;reserved<=total;reserved++)
 for(unsigned outstanding=0;outstanding<=total-reserved;outstanding++){
  s=(QcaHtcCredit){.total=total,.size=1792,.max_bytes=4088,.endpoint=1,
   .reserved=reserved,.outstanding=outstanding,.available=total-reserved-outstanding,
   .serial=1,.ticket=reserved?1:0};
  for(unsigned returned=0;returned<=total+1;returned++){
   QcaHtcCredit a=s;f=(QcaHtcFrame){.endpoint=2};f.credits[1]=(uint16_t)returned;
   CHECK(qca_htc_credit_receive(&a,&f)==(returned<=outstanding));
   if(returned<=outstanding)CHECK(a.available==s.available+returned&&a.reserved==reserved&&a.outstanding==outstanding-returned);
   else same(a,s);
   f.credits[3]=1;a=s;CHECK(!qca_htc_credit_receive(&a,&f));same(a,s);
  }
  QcaHtcCredit a=s;CHECK(qca_htc_credit_cancel(&a,1)==(reserved!=0));
  if(reserved)CHECK(a.available==s.available+reserved&&a.outstanding==outstanding&&!a.ticket);
  else same(a,s);
  a=s;CHECK(qca_htc_credit_commit(&a,1)==(reserved!=0));
  if(reserved)CHECK(a.outstanding==outstanding+reserved&&a.available==s.available&&!a.ticket);
  else same(a,s);
 }
 r=(QcaHtcReady){.credits=2,.credit_size=1792,.endpoints=4};s=(QcaHtcCredit){0};
 CHECK(qca_htc_credit_begin(&s,&r,&w));before=s;
 for(unsigned n=0;n<8;n++){CHECK(!qca_htc_credit_reserve(&s,n,&ticket));same(s,before);}
 CHECK(!qca_htc_credit_reserve(&s,UINT32_MAX,&ticket));same(s,before);
 s.serial=UINT32_MAX;before=s;CHECK(!qca_htc_credit_reserve(&s,8,&ticket));same(s,before);
 s=(QcaHtcCredit){0};w.service=QCA_HTC_HTT;before=s;CHECK(!qca_htc_credit_begin(&s,&r,&w));same(s,before);
 w.service=QCA_HTC_WMI;w.endpoint=4;CHECK(!qca_htc_credit_begin(&s,&r,&w));same(s,before);
 w.endpoint=1;r.credit_size=0;CHECK(!qca_htc_credit_begin(&s,&r,&w));same(s,before);
 CHECK(!qca_htc_credit_reserve(0,8,&ticket));CHECK(!qca_htc_credit_receive(0,&f));
 printf("CREDIT %lu pinned-cost and ownership checks PASS\n",checks);return 0;
}
