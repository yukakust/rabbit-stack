#include "dispatch.h"
#include "scan_event_v2.h"
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
 
 }
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 
 return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);
 
 }
static int valid(const QcaStationDispatch*d){return d&&d->station&&d->station->credit&&d->endpoint&&d->endpoint<QCA_HTC_ENDPOINTS&&d->station->credit->endpoint==d->endpoint&&d->station->scan==d->scan&&d->station->request==d->request&&d->station->count&&d->station->count<=64&&!d->vdev&&d->head<2&&d->count<=2;
 
 }
int qca_station_dispatch_begin(QcaStationDispatch*d,QcaStationScan*s,unsigned vdev){
 if(!d||d->station||d->count||d->last_completion||!s||!s->credit||vdev||!s->phase||s->phase>=QCA_STA_CANCELLED||s->last_rx||!s->count||s->count>64||!s->scan||s->scan>4095||!s->request||s->request>4095||!s->credit->endpoint||s->credit->endpoint>=QCA_HTC_ENDPOINTS||overlap(d,sizeof(*d),s,sizeof(*s))||overlap(d,sizeof(*d),s->credit,sizeof(*s->credit)))return 0;
 
 
 uint8_t*z=(uint8_t*)d;
 
 for(unsigned j=0;j<sizeof(*d);j++)z[j]=0;
 
 d->station=s;
 
 d->endpoint=s->credit->endpoint;
 
 d->scan=s->scan;
 
 d->request=s->request;
 
 return 1;
 
 
}
int qca_station_dispatch_offer(QcaStationDispatch*d,const QcaRxEvent*e){
 if(!valid(d)||!e||overlap(d,sizeof(*d),e,sizeof(*e))||!e->completion||e->completion<=d->last_completion||!e->bytes||e->bytes>sizeof(e->payload)||(e->pipe!=1&&e->pipe!=2))return -1;
 
 
 if(e->pipe==1){if(e->endpoint||e->event)return -1;
 
 }
 else if(e->endpoint!=d->endpoint||e->bytes<4||e->event!=word(e->payload))return -1;
 
 
 if(d->count==2)return 0;
 
 
 d->owned[(d->head+d->count)&1]=*e;
 
 d->count++;
 
 d->last_completion=e->completion;
 
 return 1;
 
 
}
static int scan_event(const QcaRxEvent*e,QcaWmiScanEvent*out){return qca_scan_event_v2(e->payload,e->bytes,out);
 }
int qca_station_dispatch_head(QcaStationDispatch*d){
 if(!valid(d))return QCA_DISPATCH_MALFORMED;
 
 
 if(!d->count)return QCA_DISPATCH_EMPTY;
 
 
 QcaRxEvent*e=&d->owned[d->head];
 
 if(e->pipe!=2||e->event!=0x3001)return QCA_DISPATCH_UNMATCHED;
 
 
 QcaWmiScanEvent v;
 
 int parsed=scan_event(e,&v);
 
 if(!parsed)return QCA_DISPATCH_MALFORMED;
 
 if(parsed==2)return QCA_DISPATCH_UNMATCHED;
 
 
 QcaStationScan*s=d->station;
 
 
 if(v.scan_id!=(0xa000u|s->scan)||v.request_id!=(0xa000u|s->request)||v.vdev!=d->vdev)return QCA_DISPATCH_UNMATCHED;
 
 
 if((s->phase!=QCA_STA_SCAN_POSTED&&s->phase!=QCA_STA_SCAN_WAIT)||s->result==QCA_SCAN_DONE||s->result==QCA_SCAN_FAILED||e->completion<=s->last_rx)return QCA_DISPATCH_SEQUENCE;
 
 
 unsigned result=s->result,started=s->started;
 
 
 if(v.type==1){if(started)return QCA_DISPATCH_SEQUENCE;
 
 started=1;
 
 result=QCA_SCAN_ACTIVE;
 
 }
 else if(v.type==2){if(!started)return QCA_DISPATCH_SEQUENCE;
 
 result=v.reason?QCA_SCAN_FAILED:QCA_SCAN_DONE;
 
 }
 else if(v.type==16||v.type==64)result=QCA_SCAN_FAILED;
 
 
 else{if(!started)return QCA_DISPATCH_SEQUENCE;
 
 if(v.type==8||v.type==256){unsigned found=0;
 
 for(unsigned j=0;j<s->count&&j<64;j++)found|=s->frequencies[j]==v.frequency;
 
 if(!found)return QCA_DISPATCH_SEQUENCE;
 
 }}
 /* The pump already owns/validates HTC/trailers. Publish event state only. */
 s->last_event=v;
 
 s->last_rx=e->completion;
 
 s->result=result;
 
 s->started=(uint8_t)started;
 
 
 if(s->phase==QCA_STA_SCAN_WAIT&&(result==QCA_SCAN_DONE||result==QCA_SCAN_FAILED))s->phase=QCA_STA_SCAN_TERMINAL;
 
 
 d->head^=1;
 
 d->count--;
 
 return QCA_DISPATCH_SCAN;
 
 
}
int qca_station_dispatch_take(QcaStationDispatch*d,uint32_t id,QcaRxEvent*out,unsigned bytes){
 if(!valid(d)||!d->count||!out||bytes<sizeof(*out)||id!=d->owned[d->head].completion||overlap(d,sizeof(*d),out,sizeof(*out))||overlap(d->station,sizeof(*d->station),out,sizeof(*out))||overlap(d->station->credit,sizeof(*d->station->credit),out,sizeof(*out)))return 0;
 
 
 *out=d->owned[d->head];
 
 d->head^=1;
 
 d->count--;
 
 return 1;
 
 
}
