#include "station_scan.h"
#include "oracle.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do{assert(x);checks++;}while(0)
static void put(uint8_t*p,uint32_t v){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(v>>(8*j));}
static void ready(uint8_t*p){memset(p,0,44);put(p,2);put(p+4,36|(35u<<16));put(p+8,0x1000000);put(p+12,574);put(p+16,0x5f414351);put(p+20,0x4c4d);p[32]=2;p[33]=3;p[34]=4;p[35]=5;p[36]=6;p[37]=7;}
static void begin(QcaStationScan*s,QcaHtcCredit*c){uint8_t p[44];ready(p);uint16_t f[]={2412,2437,2462};memset(s,0,sizeof(*s));memset(c,0,sizeof(*c));QcaHtcReady r={.credits=1,.credit_size=1792,.endpoints=4};QcaHtcConnection w={.service=256,.max_bytes=1784,.endpoint=1};CHECK(qca_htc_credit_begin(c,&r,&w));CHECK(qca_station_scan_begin(s,c,p,44,f,3,7,8,0));}
static unsigned credit(uint8_t*p){memset(p,0,16);p[0]=1;p[1]=2;p[2]=8;p[4]=8;p[8]=1;p[9]=4;p[12]=1;p[13]=1;return 16;}
static unsigned event(uint8_t*p,unsigned type,unsigned reason,unsigned frequency){memset(p,0,40);p[0]=1;p[2]=32;put(p+8,WMI_TLV_SCAN_EVENTID);put(p+12,24|(WMI_TLV_TAG_STRUCT_SCAN_EVENT<<16));struct wmi_scan_event e={.event_type=type,.reason=reason,.channel_freq=frequency,.scan_req_id=0xa008,.scan_id=0xa007,.vdev_id=0};memcpy(p+16,&e,sizeof(e));return 40;}
static void scan(QcaStationScan*s,QcaHtcCredit*c){uint8_t p[40];begin(s,c);CHECK(qca_station_scan_prepare_create(s));CHECK(s->frame_bytes==36);struct wmi_vdev_create_cmd expected={.vdev_id=0,.vdev_type=WMI_VDEV_TYPE_STA,.vdev_subtype=WMI_VDEV_SUBTYPE_NONE};memcpy(expected.vdev_macaddr.addr,s->mac,6);CHECK(!memcmp(s->frame+16,&expected,sizeof(expected)));CHECK(qca_station_scan_post(s));CHECK(!qca_station_scan_cancel(s));CHECK(qca_station_scan_complete(s,36));CHECK(c->available==0&&c->outstanding==1);CHECK(!qca_station_scan_prepare_scan(s));CHECK(qca_station_scan_receive(s,p,credit(p),1));CHECK(qca_station_scan_prepare_scan(s));
 struct wmi_tlv_start_scan_cmd cmd={0};cmd.common.scan_id=0xa007;cmd.common.scan_req_id=0xa008;cmd.common.scan_priority=1;cmd.common.notify_scan_events=0x4b;cmd.common.dwell_time_active=50;cmd.common.dwell_time_passive=100;cmd.common.min_rest_time=50;cmd.common.max_rest_time=500;cmd.common.idle_time=50;cmd.common.max_scan_time=5300;cmd.common.probe_delay=5;cmd.common.scan_ctrl_flags=0x21;cmd.num_channels=3;cmd.num_probes=3;
 CHECK(s->frame_bytes==144&&!memcmp(s->frame+16,&cmd,sizeof(cmd)));CHECK(s->frame[0]==1&&s->frame[5]==1);CHECK(qca_station_scan_post(s));}
int main(void){QcaStationScan s;QcaHtcCredit c;uint8_t p[64];
 _Static_assert(WMI_SCAN_EVENT_STARTED==1&&WMI_SCAN_EVENT_COMPLETED==2&&WMI_SCAN_EVENT_START_FAILED==64,"pinned events");
 scan(&s,&c);CHECK(qca_station_scan_receive(&s,p,event(p,1,0,0),2));CHECK(s.result==QCA_SCAN_ACTIVE&&s.phase==QCA_STA_SCAN_POSTED);CHECK(qca_station_scan_receive(&s,p,event(p,2,0,0),3));CHECK(s.result==QCA_SCAN_DONE&&s.phase==QCA_STA_SCAN_POSTED);CHECK(qca_station_scan_complete(&s,s.frame_bytes));CHECK(s.phase==QCA_STA_SCAN_TERMINAL&&c.outstanding==1);CHECK(qca_station_scan_receive(&s,p,credit(p),4));CHECK(c.available==1&&c.outstanding==0);
 for(unsigned type=1;type<=256;type<<=1)for(unsigned reason=0;reason<5;reason++){
  scan(&s,&c);unsigned n=event(p,type,reason,2437);QcaStationScan old=s;QcaHtcCredit prior=c;int accepted=qca_station_scan_receive(&s,p,n,2);
  if(type==1&&!reason)CHECK(accepted&&s.started);else if(type==16||type==64)CHECK(accepted&&s.result==QCA_SCAN_FAILED);else CHECK(!accepted&&!memcmp(&s,&old,sizeof(s))&&!memcmp(&c,&prior,sizeof(c)));
 }
 scan(&s,&c);CHECK(qca_station_scan_complete(&s,s.frame_bytes));CHECK(qca_station_scan_receive(&s,p,event(p,1,0,0),2));
 for(unsigned type=1;type<=256;type<<=1){QcaStationScan old=s;QcaHtcCredit prior=c;unsigned n=event(p,type,0,2437);int accepted=qca_station_scan_receive(&s,p,n,3);if(type==1)CHECK(!accepted);else CHECK(accepted);s=old;c=prior;}
 scan(&s,&c);unsigned n=event(p,1,0,0);for(unsigned cut=0;cut<n;cut++){QcaStationScan old=s;QcaHtcCredit prior=c;CHECK(!qca_station_scan_receive(&s,p,cut,2));CHECK(!memcmp(&s,&old,sizeof(s))&&!memcmp(&c,&prior,sizeof(c)));}
 for(unsigned at=0;at<n;at++)for(unsigned v=0;v<256;v++){uint8_t mut[64];memcpy(mut,p,n);mut[at]=(uint8_t)v;QcaStationScan old=s;QcaHtcCredit prior=c;int ok=qca_station_scan_receive(&s,mut,n,2);if(!ok)CHECK(!memcmp(&s,&old,sizeof(s))&&!memcmp(&c,&prior,sizeof(c)));else checks++;s=old;c=prior;}
 CHECK(!qca_station_scan_receive(&s,p,n,1));CHECK(!qca_station_scan_receive(&s,p,n,3));CHECK(qca_station_scan_receive(&s,p,n,2));CHECK(!qca_station_scan_receive(&s,p,n,2));CHECK(!qca_station_scan_receive(&s,p,event(p,8,0,5180),3));CHECK(qca_station_scan_receive(&s,p,event(p,8,0,2437),3));
 qca_station_scan_fault(&s);CHECK(s.phase==QCA_STA_FAULT&&c.outstanding==1);CHECK(!qca_station_scan_receive(&s,p,credit(p),4));
 begin(&s,&c);CHECK(qca_station_scan_prepare_create(&s));CHECK(qca_station_scan_cancel(&s));CHECK(c.available==1&&!c.outstanding&&!c.reserved);
 for(unsigned len=0;len<44;len++){uint8_t r[44];ready(r);uint16_t f=2412;memset(&s,0,sizeof(s));CHECK(!qca_station_scan_begin(&s,&c,r,len,&f,1,7,8,0));}
 begin(&s,&c);s.last_rx=UINT32_MAX;CHECK(qca_station_scan_prepare_create(&s));CHECK(qca_station_scan_post(&s));CHECK(!qca_station_scan_receive(&s,p,credit(p),0));
 printf("checks=%u station-scan ordering/credit/early-event/rejection PASS\n",checks);return 0;}
