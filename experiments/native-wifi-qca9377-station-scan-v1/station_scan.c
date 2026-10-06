#include "station_scan.h"
#include "vdev_wire.h"
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if(!a||!b||x>UINTPTR_MAX-n||y>UINTPTR_MAX-m)return 1;return x<y?y-x<n:x-y<m;}
static int terminal(unsigned result){return result==QCA_SCAN_DONE||result==QCA_SCAN_FAILED;}
int qca_station_scan_begin(QcaStationScan*s,QcaHtcCredit*c,const uint8_t*p,unsigned bytes,const uint16_t*f,unsigned count,unsigned scan,unsigned request,uint8_t seq){
 if(!s||s->phase||!c||!p||!f||!count||count>64||!scan||scan>4095||!request||request>4095||c->reserved||c->ticket||overlap(s,sizeof(*s),c,sizeof(*c))||overlap(s,sizeof(*s),p,bytes)||overlap(s,sizeof(*s),f,count*2)||overlap(c,sizeof(*c),p,bytes)||overlap(c,sizeof(*c),f,count*2))return 0;
 QcaWmiReadyInfo ready;uint8_t test[380];
 if(!qca_wmi_ready_info(p,bytes,&ready)||!qca_wmi_passive_scan(test,sizeof(test),scan,request,f,count))return 0;
 QcaHtcCredit check=*c;uint32_t ticket;if(!qca_htc_credit_reserve(&check,36,&ticket))return 0;
 uint8_t*z=(uint8_t*)s;for(unsigned j=0;j<sizeof(*s);j++)z[j]=0;
 s->credit=c;s->phase=QCA_STA_READY;s->sequence=seq;s->count=count;s->scan=scan;s->request=request;
 for(unsigned j=0;j<count;j++)s->frequencies[j]=f[j];for(unsigned j=0;j<6;j++)s->mac[j]=ready.mac[j];return 1;
}
static int prepare(QcaStationScan*s,unsigned scan){
 if(!s||!s->credit||s->phase!=(scan?QCA_STA_CREATE_ORDERED:QCA_STA_READY))return 0;
 uint8_t frame[388];unsigned n=scan?qca_wmi_passive_scan(frame+8,380,s->scan,s->request,s->frequencies,s->count):qca_station_create_wire(frame+8,380,0,s->mac);
 QcaHtcCredit c=*s->credit;uint32_t ticket;
 if(!n||!qca_htc_header(frame,sizeof(frame),c.endpoint,n,s->sequence,1)||!qca_htc_credit_reserve(&c,n+8,&ticket))return 0;
 *s->credit=c;s->ticket=ticket;s->frame_bytes=n+8;for(unsigned j=0;j<n+8;j++)s->frame[j]=frame[j];s->phase=scan?QCA_STA_SCAN_RESERVED:QCA_STA_CREATE_RESERVED;return 1;
}
int qca_station_scan_prepare_create(QcaStationScan*s){return prepare(s,0);}
int qca_station_scan_prepare_scan(QcaStationScan*s){return prepare(s,1);}
int qca_station_scan_post(QcaStationScan*s){
 if(!s||!s->credit||(s->phase!=QCA_STA_CREATE_RESERVED&&s->phase!=QCA_STA_SCAN_RESERVED)||!qca_htc_credit_commit(s->credit,s->ticket))return 0;
 s->ticket=0;s->sequence++;s->phase=s->phase==QCA_STA_CREATE_RESERVED?QCA_STA_CREATE_POSTED:QCA_STA_SCAN_POSTED;return 1;
}
int qca_station_scan_complete(QcaStationScan*s,unsigned n){
 if(!s||n!=s->frame_bytes)return 0;
 if(s->phase==QCA_STA_CREATE_POSTED){s->phase=QCA_STA_CREATE_ORDERED;return 1;}
 if(s->phase==QCA_STA_SCAN_POSTED){s->phase=terminal(s->result)?QCA_STA_SCAN_TERMINAL:QCA_STA_SCAN_WAIT;return 1;}return 0;
}
int qca_station_scan_receive(QcaStationScan*s,const uint8_t*p,unsigned n,uint32_t id){
 if(!s||!s->credit||s->phase<QCA_STA_CREATE_POSTED||s->phase>QCA_STA_SCAN_TERMINAL||s->last_rx==UINT32_MAX||id!=s->last_rx+1)return 0;
 QcaHtcFrame f;QcaHtcCredit c=*s->credit;QcaWmiScanEvent event={0};unsigned result=s->result,started=s->started;
 if(!qca_htc_decode(p,n,&f)||(f.endpoint&&f.endpoint!=c.endpoint))return 0;
 if(f.payload_bytes){
  if(f.endpoint!=c.endpoint||(s->phase!=QCA_STA_SCAN_POSTED&&s->phase!=QCA_STA_SCAN_WAIT)||terminal(result)||!qca_wmi_scan_event(f.payload,f.payload_bytes,s->scan,s->request,&event))return 0;
  if(event.type==1){if(started||event.reason)return 0;started=1;result=QCA_SCAN_ACTIVE;}
  else if(event.type==2){if(!started)return 0;result=event.reason?QCA_SCAN_FAILED:QCA_SCAN_DONE;}
  else if(event.type==16||event.type==64){result=QCA_SCAN_FAILED;}
  else {if(!started)return 0;if(event.type==8||event.type==256){unsigned found=0;for(unsigned j=0;j<s->count;j++)found|=s->frequencies[j]==event.frequency;if(!found)return 0;}}
 }else{unsigned reports=0;for(unsigned j=0;j<QCA_HTC_ENDPOINTS;j++)reports+=f.credits[j];if(!reports)return 0;}
 if(!qca_htc_credit_receive(&c,&f))return 0;
 *s->credit=c;s->last_rx=id;s->result=result;s->started=(uint8_t)started;
 if(f.payload_bytes){s->last_event=event;if(s->phase==QCA_STA_SCAN_WAIT&&terminal(result))s->phase=QCA_STA_SCAN_TERMINAL;}return 1;
}
int qca_station_scan_cancel(QcaStationScan*s){if(!s||!s->credit||(s->phase!=QCA_STA_CREATE_RESERVED&&s->phase!=QCA_STA_SCAN_RESERVED)||!qca_htc_credit_cancel(s->credit,s->ticket))return 0;s->ticket=0;s->phase=QCA_STA_CANCELLED;return 1;}
void qca_station_scan_fault(QcaStationScan*s){if(s&&s->phase>=QCA_STA_CREATE_POSTED&&s->phase<=QCA_STA_SCAN_TERMINAL&&s->phase!=QCA_STA_SCAN_RESERVED)s->phase=QCA_STA_FAULT;}
