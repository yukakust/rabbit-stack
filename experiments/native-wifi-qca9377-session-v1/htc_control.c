#include "htc_control.h"
int qca_htc_control_begin(QcaHtcControl*s){
 if(!s||s->session.phase||s->posted||s->deferred_bytes||s->credit.total)return -1;
 *s=(QcaHtcControl){0};return qca_htc_session_begin(&s->session);
}
unsigned qca_htc_control_prepare(QcaHtcControl*s,uint8_t*p,unsigned n){
 if(!s||s->posted||s->deferred_bytes)return 0;
 return qca_htc_session_prepare(&s->session,p,n);
}
int qca_htc_control_post(QcaHtcControl*s,unsigned n){
 if(!s||s->posted||s->deferred_bytes||!n||s->session.prepared!=n)return -1;
 QcaHtcSession next=s->session;
 if(qca_htc_session_transmitted(&next,n))return -1;
 s->posted=n;return 0;
}
int qca_htc_control_complete(QcaHtcControl*s,unsigned n){
 if(!s||!s->posted||n!=s->posted)return -1;
 QcaHtcSession next=s->session;QcaHtcCredit credit=s->credit;
 if(qca_htc_session_transmitted(&next,n))return -1;
 if(s->deferred_bytes&&qca_htc_session_receive(&next,s->deferred,s->deferred_bytes))return -1;
 if(next.phase==QCA_HTC_RUNNING&&!qca_htc_credit_begin(&credit,&next.ready,&next.wmi))return -1;
 s->session=next;s->credit=credit;s->posted=0;s->deferred_bytes=0;return 0;
}
int qca_htc_control_receive(QcaHtcControl*s,const uint8_t*p,unsigned n){
 if(!s||!p||!n||n>QCA_HTC_FRAME_LIMIT||s->deferred_bytes)return -1;
 QcaHtcSession next=s->session;
 if(s->posted&&qca_htc_session_transmitted(&next,s->posted))return -1;
 if(qca_htc_session_receive(&next,p,n))return -1;
 if(s->posted){for(unsigned i=0;i<n;i++)s->deferred[i]=p[i];s->deferred_bytes=n;}
 else s->session=next;
 return 0;
}
