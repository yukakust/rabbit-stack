#include "owned_stop.h"
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);}
static int binding(const QcaOwnedScanStop*s){
 return s&&s->dispatch&&s->stop.scan&&s->dispatch->station==s->stop.scan&&s->stop.scan->credit
  &&s->dispatch->scan==s->stop.scan->scan&&s->dispatch->request==s->stop.scan->request
  &&!s->dispatch->vdev&&s->dispatch->endpoint==s->stop.scan->credit->endpoint;
}
void qca_owned_scan_stop_fault(QcaOwnedScanStop*s){if(s){s->fault=1;s->stop.phase=QCA_STOP_FAULT;}}
int qca_owned_scan_stop_begin(QcaOwnedScanStop*s,QcaStationDispatch*d,uint64_t now,unsigned duration,unsigned credit_wait,unsigned stop_wait){
 if(!s||s->dispatch||s->stop.phase||!d||!d->station||!d->station->credit||d->head>1||d->count>2||d->vdev||d->scan!=d->station->scan||d->request!=d->station->request||d->endpoint!=d->station->credit->endpoint||!credit_wait||credit_wait>60000||!stop_wait||stop_wait>60000||overlap(s,sizeof(*s),d,sizeof(*d))||overlap(s,sizeof(*s),d->station,sizeof(*d->station))||overlap(s,sizeof(*s),d->station->credit,sizeof(*d->station->credit)))return 0;
 QcaScanStop stop={0};if(!qca_scan_stop_begin(&stop,d->station,now,duration))return 0;
 uint8_t*z=(uint8_t*)s;for(unsigned j=0;j<sizeof(*s);j++)z[j]=0;s->stop=stop;s->dispatch=d;s->credit_wait=credit_wait;s->stop_wait=stop_wait;s->last_processed=d->station->last_rx;return 1;
}
static int request(QcaOwnedScanStop*s){
 if(s->stop.last_tick>UINT64_MAX-s->credit_wait){qca_owned_scan_stop_fault(s);return 0;}
 if(!qca_scan_stop_request(&s->stop))return 0;s->credit_deadline=s->stop.last_tick+s->credit_wait;return 1;
}
int qca_owned_scan_stop_tick(QcaOwnedScanStop*s,uint64_t now){
 if(!s||s->fault||!s->stop.phase)return 0;if(!binding(s)){qca_owned_scan_stop_fault(s);return 0;}
 if(now<s->stop.last_tick||s->stop.scan->phase==QCA_STA_FAULT||s->stop.scan->phase==QCA_STA_CANCELLED){qca_owned_scan_stop_fault(s);return 0;}
 s->stop.last_tick=now;
 if((s->stop.phase==QCA_STOP_REQUESTED||s->stop.phase==QCA_STOP_RESERVED)&&now>=s->credit_deadline){qca_owned_scan_stop_fault(s);return 0;}
 if((s->stop.phase==QCA_STOP_POSTED||s->stop.phase==QCA_STOP_WAIT)&&now>=s->stop.stop_deadline){qca_owned_scan_stop_fault(s);return 0;}
 if(s->stop.phase==QCA_STOP_MONITOR&&now>=s->stop.deadline)return request(s);
 return 1;
}
int qca_owned_scan_stop_request(QcaOwnedScanStop*s,uint64_t now){
 if(!qca_owned_scan_stop_tick(s,now))return 0;if(s->stop.phase==QCA_STOP_REQUESTED)return 1;return request(s);
}
int qca_owned_scan_stop_prepare(QcaOwnedScanStop*s,uint64_t now){if(!qca_owned_scan_stop_tick(s,now))return 0;return qca_scan_stop_prepare(&s->stop);}
int qca_owned_scan_stop_post(QcaOwnedScanStop*s,uint64_t now){if(!qca_owned_scan_stop_tick(s,now))return 0;return qca_scan_stop_post(&s->stop,s->stop_wait);}
int qca_owned_scan_stop_complete(QcaOwnedScanStop*s,unsigned bytes,uint64_t now){if(!qca_owned_scan_stop_tick(s,now))return 0;return qca_scan_stop_complete(&s->stop,bytes);}
int qca_owned_scan_stop_head(QcaOwnedScanStop*s,uint64_t now){
 if(!qca_owned_scan_stop_tick(s,now))return QCA_DISPATCH_SEQUENCE;
 QcaStationDispatch*d=s->dispatch;
 if(d->head>1||d->count>2){qca_owned_scan_stop_fault(s);return QCA_DISPATCH_MALFORMED;}
 uint32_t completion=d->count?d->owned[d->head].completion:0;
 int rc=qca_station_dispatch_head(d);
 if(rc<0){qca_owned_scan_stop_fault(s);return rc;}
 if(rc!=QCA_DISPATCH_SCAN)return rc;
 QcaStationScan*scan=s->stop.scan;QcaWmiScanEvent*event=&scan->last_event;
 if(!completion||completion<=s->last_processed||scan->last_rx!=completion||event->scan_id!=(0xa000u|d->scan)||event->request_id!=(0xa000u|d->request)||event->vdev!=d->vdev){qca_owned_scan_stop_fault(s);return QCA_DISPATCH_SEQUENCE;}
 s->last_processed=completion;
 unsigned terminal=event->type==2||event->type==16||event->type==64;
 if(!terminal)return rc;
 if(s->stop.terminal_seen){qca_owned_scan_stop_fault(s);return QCA_DISPATCH_SEQUENCE;}
 s->terminal_completion=completion;s->stop.terminal_seen=1;
 if(s->stop.phase==QCA_STOP_RESERVED){if(!qca_scan_stop_cancel_unposted(&s->stop)){qca_owned_scan_stop_fault(s);return QCA_DISPATCH_SEQUENCE;}}
 if(s->stop.phase==QCA_STOP_POSTED||s->stop.phase==QCA_STOP_WAIT){if(s->stop.tx_complete)s->stop.phase=QCA_STOP_ENDED;}
 else s->stop.phase=QCA_STOP_ENDED;
 return rc;
}
