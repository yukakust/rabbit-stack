#include "htc_session.h"
int qca_htc_session_begin(QcaHtcSession*s){
 if(!s||s->phase)return -1;
 *s=(QcaHtcSession){.phase=QCA_HTC_WAIT_READY};return 0;
}
unsigned qca_htc_session_prepare(QcaHtcSession*s,uint8_t*p,unsigned cap){
 unsigned bytes=0;
 if(!s)return 0;
 switch(s->phase){
 case QCA_HTC_SEND_WMI:bytes=qca_htc_connect(p,cap,QCA_HTC_WMI,s->ready.credits,s->sequence);break;
 case QCA_HTC_SEND_HTT:bytes=qca_htc_connect(p,cap,QCA_HTC_HTT,0,s->sequence);break;
 case QCA_HTC_SEND_SETUP:bytes=qca_htc_setup(p,cap,s->sequence);break;
 default:return 0;
 }
 if(bytes)s->prepared=bytes;
 return bytes;
}
int qca_htc_session_transmitted(QcaHtcSession*s,unsigned bytes){
 if(!s||!s->prepared||s->prepared!=bytes)return -1;
 if(s->phase==QCA_HTC_SEND_WMI)s->phase=QCA_HTC_WAIT_WMI;
 else if(s->phase==QCA_HTC_SEND_HTT)s->phase=QCA_HTC_WAIT_HTT;
 else if(s->phase==QCA_HTC_SEND_SETUP)s->phase=QCA_HTC_RUNNING;
 else return -1;
 s->prepared=0;s->sequence++;return 0;
}
int qca_htc_session_receive(QcaHtcSession*s,const uint8_t*p,unsigned n){
 QcaHtcFrame f;QcaHtcSession v;
 if(!s||!qca_htc_decode(p,n,&f))return -1;
 v=*s;
 if(s->phase==QCA_HTC_WAIT_READY){
  if(!qca_htc_ready(&f,&v.ready))return -1;
  v.phase=QCA_HTC_SEND_WMI;
 }else if(s->phase==QCA_HTC_WAIT_WMI){
  if(!qca_htc_connection(&f,QCA_HTC_WMI,&v.wmi)||v.wmi.endpoint>=v.ready.endpoints)return -1;
  v.phase=QCA_HTC_SEND_HTT;
 }else if(s->phase==QCA_HTC_WAIT_HTT){
  if(!qca_htc_connection(&f,QCA_HTC_HTT,&v.htt)||v.htt.endpoint>=v.ready.endpoints||v.htt.endpoint==v.wmi.endpoint)return -1;
  v.phase=QCA_HTC_SEND_SETUP;
 }else return -1;
 *s=v;return 0;
}
