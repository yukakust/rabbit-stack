#include "init_transaction.h"
static int overlap(const void*a,unsigned na,const void*b,unsigned nb){
 if(!nb)return 0;
 uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 if(!a||!b||x>UINTPTR_MAX-na||y>UINTPTR_MAX-nb)return 1;
 return x<y?y-x<na:x-y<nb;
}
int qca_wmi_init_begin(QcaWmiInitTransaction*s,QcaHtcCredit*c,const QcaHtcSession*h,
 const QcaWmiServiceInfo*i,const QcaWmiResources*r,const uint32_t words[44],const QcaWmiHostChunk*chunks,unsigned count){
 if(!s||s->phase||!c||!h||!i||!r||!words||count>16||h->phase!=QCA_HTC_RUNNING||h->prepared
  ||h->ready.endpoints<2||h->ready.endpoints>QCA_HTC_ENDPOINTS||h->wmi.service!=QCA_HTC_WMI
  ||!h->wmi.endpoint||h->wmi.endpoint>=h->ready.endpoints||h->htt.service!=QCA_HTC_HTT
  ||!h->htt.endpoint||h->htt.endpoint>=h->ready.endpoints||h->htt.endpoint==h->wmi.endpoint
  ||!h->htt.max_bytes||h->htt.max_bytes>4088
  ||c->reserved||c->outstanding||c->ticket||c->available!=c->total||c->endpoint!=h->wmi.endpoint
  ||c->total!=h->ready.credits||c->size!=h->ready.credit_size||c->max_bytes!=h->wmi.max_bytes)return 0;
 const void*input[6]={c,h,i,r,words,chunks};unsigned sizes[6]={sizeof(*c),sizeof(*h),sizeof(*i),sizeof(*r),176,count*sizeof(*chunks)};
 for(unsigned j=0;j<6;j++)if(overlap(s,sizeof(*s),input[j],sizes[j]))return 0;
 for(unsigned j=1;j<6;j++)if(overlap(c,sizeof(*c),input[j],sizes[j]))return 0;
 uint8_t frame[548];unsigned n=qca_wmi_init_wire(frame+8,sizeof(frame)-8,words,i,r,chunks,count);
 if(!n||!qca_htc_header(frame,sizeof(frame),c->endpoint,n,h->sequence,1))return 0;
 QcaHtcCredit next=*c;uint32_t ticket=0;
 if(!qca_htc_credit_reserve(&next,n+8,&ticket))return 0;
 /* No externally published descriptor exists; commit both logical owners. */
 uint8_t*zero=(uint8_t*)s;for(unsigned j=0;j<sizeof(*s);j++)zero[j]=0;
 s->credit=c;s->ticket=ticket;s->phase=QCA_INIT_RESERVED;s->frame_bytes=n+8;
 for(unsigned j=0;j<n+8;j++)s->frame[j]=frame[j];
 *c=next;return 1;
}
int qca_wmi_init_post(QcaWmiInitTransaction*s){
 if(!s||s->phase!=QCA_INIT_RESERVED||!s->credit||!qca_htc_credit_commit(s->credit,s->ticket))return 0;
 s->ticket=0;s->phase=QCA_INIT_POSTED;return 1;
}
int qca_wmi_init_complete(QcaWmiInitTransaction*s,unsigned n){
 if(!s||s->phase!=QCA_INIT_POSTED||s->tx_complete||n!=s->frame_bytes)return 0;
 s->tx_complete=1;s->phase=s->ready_seen?QCA_INIT_RUNNING:QCA_INIT_WAIT_READY;return 1;
}
int qca_wmi_init_receive(QcaWmiInitTransaction*s,const uint8_t*p,unsigned n,uint32_t id){
 if(!s||!s->credit||(s->phase!=QCA_INIT_POSTED&&s->phase!=QCA_INIT_WAIT_READY)
  ||s->last_completion==UINT32_MAX||id!=s->last_completion+1||!p)return 0;
 QcaHtcFrame f;QcaHtcCredit credit=*s->credit;QcaWmiReadyInfo ready={0};
 if(!qca_htc_decode(p,n,&f)||(f.endpoint&&f.endpoint!=credit.endpoint))return 0;
 if(f.payload_bytes){
  if(f.endpoint!=credit.endpoint||s->ready_seen||!qca_wmi_ready_info(f.payload,f.payload_bytes,&ready)||ready.abi_minor!=53)return 0;
 }else{
  unsigned reports=0;for(unsigned j=0;j<QCA_HTC_ENDPOINTS;j++)reports+=f.credits[j];if(!reports)return 0;
 }
 if(!qca_htc_credit_receive(&credit,&f))return 0;
 *s->credit=credit;s->last_completion=id;
 if(f.payload_bytes){s->ready=ready;s->ready_seen=1;if(s->tx_complete)s->phase=QCA_INIT_RUNNING;}
 return 1;
}
int qca_wmi_init_cancel(QcaWmiInitTransaction*s){
 if(!s||s->phase!=QCA_INIT_RESERVED||!s->credit||!qca_htc_credit_cancel(s->credit,s->ticket))return 0;
 s->ticket=0;s->phase=QCA_INIT_CANCELLED;return 1;
}
void qca_wmi_init_fault(QcaWmiInitTransaction*s){
 /* Unposted reservations must use cancel. Never silently forget a ticket. */
 if(s&&(s->phase==QCA_INIT_POSTED||s->phase==QCA_INIT_WAIT_READY))s->phase=QCA_INIT_FAULT;
}
