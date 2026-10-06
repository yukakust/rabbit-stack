#include "scan_stop.h"
#include "oracle.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do{assert(x);checks++;}while(0)
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
static void fixture(QcaScanStop*t,QcaStationScan*s,QcaHtcCredit*c,unsigned total){memset(t,0,sizeof(*t));memset(s,0,sizeof(*s));memset(c,0,sizeof(*c));QcaHtcReady r={.credits=total,.credit_size=1792,.endpoints=4};QcaHtcConnection w={.service=256,.max_bytes=1784,.endpoint=1};CHECK(qca_htc_credit_begin(c,&r,&w));uint32_t ticket;CHECK(qca_htc_credit_reserve(c,144,&ticket));CHECK(qca_htc_credit_commit(c,ticket));s->credit=c;s->phase=QCA_STA_SCAN_WAIT;s->scan=7;s->request=8;s->count=1;s->frequencies[0]=2412;s->result=QCA_SCAN_ACTIVE;s->started=1;s->sequence=2;CHECK(qca_scan_stop_begin(t,s,1000,100));}
static unsigned event(uint8_t*p,unsigned type,unsigned reason){memset(p,0,40);p[0]=1;p[2]=32;put(p+8,WMI_TLV_SCAN_EVENTID);put(p+12,24|(WMI_TLV_TAG_STRUCT_SCAN_EVENT<<16));struct wmi_scan_event e={.event_type=type,.reason=reason,.scan_req_id=0xa008,.scan_id=0xa007};memcpy(p+16,&e,sizeof(e));return 40;}
static unsigned credit(uint8_t*p,unsigned amount){memset(p,0,16);p[0]=1;p[1]=2;p[2]=8;p[4]=8;p[8]=1;p[9]=4;p[12]=1;p[13]=amount;return 16;}
int main(void){uint8_t p[64],wire[24],expected[24];QcaScanStop t;QcaStationScan s;QcaHtcCredit c;
 for(unsigned scan=1;scan<=4095;scan++){for(unsigned request=1;request<=4095;request+=127){CHECK(qca_scan_stop_wire(wire,24,scan,request)==24);reference_stop(expected,scan,request);CHECK(!memcmp(wire,expected,24));}}
 for(unsigned n=0;n<24;n++){memset(wire,0xa5,24);memcpy(expected,wire,24);CHECK(!qca_scan_stop_wire(wire,n,7,8)&&!memcmp(wire,expected,24));}
 CHECK(!qca_scan_stop_wire(wire,24,0,8));CHECK(!qca_scan_stop_wire(wire,24,7,4096));
 fixture(&t,&s,&c,2);CHECK(qca_scan_stop_tick(&t,1099)&&t.phase==QCA_STOP_MONITOR);CHECK(!qca_scan_stop_tick(&t,1098));CHECK(qca_scan_stop_tick(&t,1100)&&t.phase==QCA_STOP_REQUESTED);CHECK(qca_scan_stop_prepare(&t));CHECK(c.reserved==1&&c.outstanding==1);CHECK(qca_scan_stop_post(&t,500));CHECK(c.outstanding==2&&!c.available);CHECK(!qca_scan_stop_cancel_unposted(&t));CHECK(qca_scan_stop_complete(&t,32));CHECK(t.phase==QCA_STOP_WAIT&&c.outstanding==2);CHECK(qca_scan_stop_receive(&t,p,event(p,2,WMI_SCAN_REASON_CANCELLED),1));CHECK(t.phase==QCA_STOP_ENDED);CHECK(qca_scan_stop_receive(&t,p,credit(p,2),2));CHECK(c.available==2&&!c.outstanding);
 fixture(&t,&s,&c,2);CHECK(qca_scan_stop_request(&t));CHECK(qca_scan_stop_prepare(&t));CHECK(qca_scan_stop_post(&t,500));CHECK(qca_scan_stop_receive(&t,p,event(p,2,0),1));CHECK(t.phase==QCA_STOP_POSTED&&t.terminal_seen);CHECK(qca_scan_stop_complete(&t,32)&&t.phase==QCA_STOP_ENDED);
 fixture(&t,&s,&c,2);CHECK(qca_scan_stop_request(&t));CHECK(qca_scan_stop_prepare(&t));CHECK(qca_scan_stop_receive(&t,p,event(p,2,0),1));CHECK(t.phase==QCA_STOP_ENDED&&c.available==1&&!c.reserved&&c.outstanding==1);CHECK(!qca_scan_stop_post(&t,500));
 fixture(&t,&s,&c,1);CHECK(qca_scan_stop_request(&t));CHECK(!qca_scan_stop_prepare(&t));CHECK(qca_scan_stop_receive(&t,p,credit(p,1),1));CHECK(qca_scan_stop_prepare(&t));CHECK(qca_scan_stop_cancel_unposted(&t)&&c.available==1&&!c.outstanding);CHECK(qca_scan_stop_prepare(&t));CHECK(qca_scan_stop_post(&t,10));CHECK(qca_scan_stop_tick(&t,1010)&&t.phase==QCA_STOP_FAULT&&c.outstanding==1&&!t.terminal_seen);CHECK(!qca_scan_stop_receive(&t,p,event(p,2,1),2));
 fixture(&t,&s,&c,2);CHECK(qca_scan_stop_request(&t));CHECK(qca_scan_stop_prepare(&t));CHECK(qca_scan_stop_post(&t,500));unsigned n=event(p,2,1);
 for(unsigned cut=0;cut<n;cut++){QcaScanStop old=t;QcaStationScan prior=s;QcaHtcCredit ledger=c;CHECK(!qca_scan_stop_receive(&t,p,cut,1));CHECK(!memcmp(&t,&old,sizeof(t))&&!memcmp(&s,&prior,sizeof(s))&&!memcmp(&c,&ledger,sizeof(c)));}
 for(unsigned at=0;at<n;at++)for(unsigned v=0;v<256;v++){uint8_t mut[64];memcpy(mut,p,n);mut[at]=v;QcaScanStop old=t;QcaStationScan prior=s;QcaHtcCredit ledger=c;int ok=qca_scan_stop_receive(&t,mut,n,1);if(!ok)CHECK(!memcmp(&t,&old,sizeof(t))&&!memcmp(&s,&prior,sizeof(s))&&!memcmp(&c,&ledger,sizeof(c)));else checks++;t=old;s=prior;c=ledger;}
 CHECK(!qca_scan_stop_receive(&t,p,n,2));CHECK(qca_scan_stop_receive(&t,p,n,1));CHECK(!qca_scan_stop_receive(&t,p,n,1));CHECK(!qca_scan_stop_complete(&t,31));CHECK(qca_scan_stop_complete(&t,32));
 memset(&t,0,sizeof(t));CHECK(!qca_scan_stop_begin(&t,&s,UINT64_MAX,1));fixture(&t,&s,&c,2);CHECK(qca_scan_stop_request(&t));qca_scan_stop_fault(&t);CHECK(t.phase==QCA_STOP_FAULT&&c.outstanding==1);
 printf("checks=%u stop-wire/deadline/credit/terminal/early-event PASS\n",checks);return 0;}
