#include "htc_credit.h"
static int valid(const QcaHtcCredit*s){
 return s&&s->total&&s->total<=255&&s->size&&s->size<=4096
  &&s->endpoint&&s->endpoint<QCA_HTC_ENDPOINTS&&s->max_bytes&&s->max_bytes<=4088
  &&(unsigned)s->available+s->reserved+s->outstanding==s->total
  &&((s->reserved!=0)==(s->ticket!=0))&&s->ticket<=s->serial;
}
int qca_htc_credit_begin(QcaHtcCredit*s,const QcaHtcReady*r,const QcaHtcConnection*c){
 if(!s||!r||!c)return 0;
 const QcaHtcCredit zero={0};
 if(s->total||s->size||s->available||s->reserved||s->outstanding||s->max_bytes||s->endpoint||s->serial||s->ticket)return 0;
 if(!r->credits||r->credits>255||!r->credit_size||r->credit_size>4096
  ||r->endpoints<2||r->endpoints>QCA_HTC_ENDPOINTS||c->service!=QCA_HTC_WMI
  ||!c->endpoint||c->endpoint>=r->endpoints||!c->max_bytes||c->max_bytes>4088)return 0;
 QcaHtcCredit v=zero;v.total=v.available=r->credits;v.size=r->credit_size;
 v.endpoint=c->endpoint;v.max_bytes=c->max_bytes;*s=v;return 1;
}
int qca_htc_credit_reserve(QcaHtcCredit*s,unsigned bytes,uint32_t*ticket){
 if(!valid(s)||!ticket||s->reserved||bytes<8||bytes>(unsigned)s->max_bytes+8||s->serial==UINT32_MAX)return 0;
 unsigned cost=(bytes+s->size-1)/s->size;
 if(cost>s->available)return 0;
 s->available=(uint16_t)(s->available-cost);s->reserved=(uint16_t)cost;
 s->ticket=++s->serial;*ticket=s->ticket;return 1;
}
int qca_htc_credit_cancel(QcaHtcCredit*s,uint32_t ticket){
 if(!valid(s)||!ticket||ticket!=s->ticket)return 0;
 s->available=(uint16_t)(s->available+s->reserved);s->reserved=0;s->ticket=0;return 1;
}
int qca_htc_credit_commit(QcaHtcCredit*s,uint32_t ticket){
 if(!valid(s)||!ticket||ticket!=s->ticket)return 0;
 s->outstanding=(uint16_t)(s->outstanding+s->reserved);s->reserved=0;s->ticket=0;return 1;
}
int qca_htc_credit_receive(QcaHtcCredit*s,const QcaHtcFrame*f){
 if(!valid(s)||!f||f->endpoint>=QCA_HTC_ENDPOINTS)return 0;
 for(unsigned i=0;i<QCA_HTC_ENDPOINTS;i++)if(i!=s->endpoint&&f->credits[i])return 0;
 unsigned n=f->credits[s->endpoint];if(n>s->outstanding)return 0;
 s->outstanding=(uint16_t)(s->outstanding-n);s->available=(uint16_t)(s->available+n);return 1;
}
