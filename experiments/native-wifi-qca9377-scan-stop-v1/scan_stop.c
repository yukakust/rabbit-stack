#include "scan_stop.h"
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(j*8));}
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);}
unsigned qca_scan_stop_wire(uint8_t*p,unsigned cap,unsigned scan,unsigned request){
 if(!p||cap<24||!scan||scan>4095||!request||request>4095||(uintptr_t)p>UINTPTR_MAX-24)return 0;
 put(p,0x3002);put(p+4,16|(78u<<16));put(p+8,0xa000|request);put(p+12,0xa000|scan);put(p+16,0);put(p+20,scan);return 24;
}
int qca_scan_stop_begin(QcaScanStop*s,QcaStationScan*scan,uint64_t now,unsigned duration){
 if(!s||s->phase||!scan||!scan->credit||(scan->phase!=QCA_STA_SCAN_POSTED&&scan->phase!=QCA_STA_SCAN_WAIT)||!duration||duration>60000||now>UINT64_MAX-duration||overlap(s,sizeof(*s),scan,sizeof(*scan))||overlap(s,sizeof(*s),scan->credit,sizeof(*scan->credit)))return 0;
 uint8_t*z=(uint8_t*)s;for(unsigned j=0;j<sizeof(*s);j++)z[j]=0;s->scan=scan;s->last_tick=now;s->deadline=now+duration;s->phase=QCA_STOP_MONITOR;return 1;
}
int qca_scan_stop_tick(QcaScanStop*s,uint64_t now){
 if(!s||!s->scan||s->phase==QCA_STOP_FAULT||s->phase==QCA_STOP_ENDED||now<s->last_tick)return 0;
 s->last_tick=now;
 if((s->phase==QCA_STOP_POSTED||s->phase==QCA_STOP_WAIT)&&now>=s->stop_deadline){s->phase=QCA_STOP_FAULT;return 1;}
 if(s->phase==QCA_STOP_MONITOR&&now>=s->deadline)s->phase=QCA_STOP_REQUESTED;return 1;
}
int qca_scan_stop_request(QcaScanStop*s){if(!s||s->phase!=QCA_STOP_MONITOR)return 0;s->phase=QCA_STOP_REQUESTED;return 1;}
int qca_scan_stop_prepare(QcaScanStop*s){
 if(!s||s->phase!=QCA_STOP_REQUESTED||!s->scan||s->scan->phase!=QCA_STA_SCAN_WAIT||!s->scan->credit)return 0;
 uint8_t frame[32];QcaHtcCredit c=*s->scan->credit;uint32_t ticket;
 unsigned n=qca_scan_stop_wire(frame+8,24,s->scan->scan,s->scan->request);
 if(!n||!qca_htc_header(frame,sizeof(frame),c.endpoint,n,s->scan->sequence,1)||!qca_htc_credit_reserve(&c,32,&ticket))return 0;
 *s->scan->credit=c;s->ticket=ticket;s->frame_bytes=32;for(unsigned j=0;j<32;j++)s->frame[j]=frame[j];s->phase=QCA_STOP_RESERVED;return 1;
}
int qca_scan_stop_post(QcaScanStop*s,unsigned timeout){
 if(!s||s->phase!=QCA_STOP_RESERVED||!s->scan||!s->scan->credit||!timeout||timeout>60000||s->last_tick>UINT64_MAX-timeout||!qca_htc_credit_commit(s->scan->credit,s->ticket))return 0;
 s->ticket=0;s->scan->sequence++;s->stop_deadline=s->last_tick+timeout;s->phase=QCA_STOP_POSTED;return 1;
}
int qca_scan_stop_complete(QcaScanStop*s,unsigned n){if(!s||s->phase!=QCA_STOP_POSTED||n!=s->frame_bytes||s->tx_complete)return 0;s->tx_complete=1;s->phase=s->terminal_seen?QCA_STOP_ENDED:QCA_STOP_WAIT;return 1;}
int qca_scan_stop_receive(QcaScanStop*s,const uint8_t*p,unsigned n,uint32_t id){
 if(!s||!s->scan||s->phase==QCA_STOP_FAULT||s->phase<QCA_STOP_MONITOR||s->phase>QCA_STOP_ENDED)return 0;
 QcaHtcFrame f;QcaWmiScanEvent event={0};unsigned terminal=0;
 if(!qca_htc_decode(p,n,&f))return 0;
 if(f.payload_bytes){if(!qca_wmi_scan_event(f.payload,f.payload_bytes,s->scan->scan,s->scan->request,&event))return 0;terminal=event.type==2||event.type==16||event.type==64;}
 if(!qca_station_scan_receive(s->scan,p,n,id))return 0;
 if(terminal){
  s->terminal_seen=1;
  if(s->phase==QCA_STOP_RESERVED){/* Genuine natural termination before STOP publication. */
   if(!qca_htc_credit_cancel(s->scan->credit,s->ticket)){s->phase=QCA_STOP_FAULT;return 1;}s->ticket=0;
  }
  if(s->phase==QCA_STOP_POSTED||s->phase==QCA_STOP_WAIT){if(s->tx_complete)s->phase=QCA_STOP_ENDED;}
  else s->phase=QCA_STOP_ENDED;
 }return 1;
}
int qca_scan_stop_cancel_unposted(QcaScanStop*s){if(!s||s->phase!=QCA_STOP_RESERVED||!s->scan||!qca_htc_credit_cancel(s->scan->credit,s->ticket))return 0;s->ticket=0;s->phase=QCA_STOP_REQUESTED;return 1;}
void qca_scan_stop_fault(QcaScanStop*s){if(s&&(s->phase==QCA_STOP_POSTED||s->phase==QCA_STOP_WAIT||s->phase==QCA_STOP_REQUESTED))s->phase=QCA_STOP_FAULT;}
