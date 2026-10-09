#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#include "filter_barrier.h"
static int span(const void*p,unsigned n){return p&&(uintptr_t)p<=UINTPTR_MAX-n;}
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if(!span(a,n)||!span(b,m))return 1;return x<y?y-x<n:x-y<m;}
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static int mac_ok(const uint8_t*p){unsigned any=0;if(!span(p,6)||(p[0]&1))return 0;for(unsigned i=0;i<6;i++)any|=p[i];return any!=0;}
unsigned qca_filter_wire(unsigned step,uint8_t*out,unsigned cap,const uint8_t mac[6],uint32_t arg){
 unsigned n=step==QCA_FILTER_CREATE?28:12;
 if(step>QCA_FILTER_ECHO||cap<n||!span(out,n)||(step==QCA_FILTER_CREATE&&(!mac_ok(mac)||overlap(out,n,mac,6)))||(step==QCA_FILTER_ECHO&&!arg))return 0;
 uint8_t p[28]={0};put(p,step==0?0x5001:step==1?0x5002:0x1d001);put(p+4,(step==0?20u:4u)|((step==0?86u:step==1?87u:149u)<<16));
 if(step==0){put(p+12,2);for(unsigned i=0;i<6;i++)p[20+i]=mac[i];}
 else if(step==2)put(p+8,arg);
 for(unsigned i=0;i<n;i++)out[i]=p[i];return n;
}
int qca_filter_echo_payload(const uint8_t*p,unsigned n,uint32_t*out){
 if(n!=12||!span(p,n)||!span(out,sizeof(*out))||overlap(p,n,out,sizeof(*out))||word(p)!=0x1d001||word(p+4)!=(4u|(54u<<16)))return 0;
 *out=word(p+8);return 1;
}
static int credit_ok(const QcaHtcCredit*c){return c&&c->total&&c->total<=255&&c->size&&c->size<=4096&&c->endpoint&&c->endpoint<QCA_HTC_ENDPOINTS&&c->max_bytes>=28&&c->max_bytes<=4088&&(unsigned)c->available+c->reserved+c->outstanding==c->total&&((c->reserved!=0)==(c->ticket!=0))&&c->ticket<=c->serial;}
static int fail(QcaFilterBarrier*s,unsigned n){if(s){if(!s->error)s->error=n;s->phase=QCA_FILTER_FAULT;}return -1;}
uint64_t qca_filter_effective_deadline(const QcaFilterBarrier*s){
 if(!s||!s->phase)return 0;
 uint64_t d=s->step==2&&s->echo_deadline?s->echo_deadline:s->stage_deadline;
 return d<s->overall_deadline?d:s->overall_deadline;
}
static uint64_t stage_end(uint64_t now,uint64_t cap){return now>UINT64_MAX-3000000||now+3000000>cap?cap:now+3000000;}
static int tick(QcaFilterBarrier*s,uint64_t epoch,uint64_t now){
 if(!s||!s->phase)return 0;
 if(s->phase==QCA_FILTER_FAULT||s->phase==QCA_FILTER_CANCELLED)return 0;
 if(epoch!=s->epoch)return fail(s,1);
 if(now<s->last)return fail(s,2);
 if(!credit_ok(s->credit))return fail(s,3);
 s->last=now;s->deadline=qca_filter_effective_deadline(s);
 if(s->phase!=QCA_FILTER_PASSED&&now>=s->deadline){s->timeout_observed=now;return fail(s,4);}
 return 1;
}
int qca_filter_begin(QcaFilterBarrier*s,QcaHtcCredit*c,const uint8_t*p,unsigned n,uint64_t epoch,uint32_t floor,uint32_t arg,uint64_t now){
 if(!span(s,sizeof(*s))||s->phase||!span(c,sizeof(*c))||!credit_ok(c)||c->reserved||c->ticket||!epoch||!arg||floor==UINT32_MAX||now>UINT64_MAX-12000000||n<4||n>4096||!span(p,n)||overlap(s,sizeof(*s),c,sizeof(*c))||overlap(s,sizeof(*s),p,n)||overlap(c,sizeof(*c),p,n))return 0;
 QcaWmiReadyInfo ready={0};if(!qca_wmi_ready_info(p,n,&ready)||!mac_ok(ready.mac))return 0;
 QcaFilterBarrier value={0};value.credit=c;value.epoch=epoch;value.last=now;value.started=value.stage_started=value.last_poll=now;value.overall_deadline=now+12000000;value.stage_deadline=value.deadline=now+3000000;value.phase=QCA_FILTER_READY;value.echo_arg=arg;value.initial_floor=value.last_rx=floor;for(unsigned i=0;i<6;i++)value.mac[i]=ready.mac[i];*s=value;return 1;
}
int qca_filter_prepare(QcaFilterBarrier*s,uint64_t epoch,uint64_t now){
 if(tick(s,epoch,now)!=1||(s->phase!=QCA_FILTER_READY&&s->phase!=QCA_FILTER_ORDERED)||s->step>2||s->credit->reserved||s->credit->ticket)return 0;
 uint8_t body[28]={0};unsigned n=qca_filter_wire(s->step,body,sizeof(body),s->mac,s->echo_arg);
 if(!n||n>s->credit->max_bytes||(n+8+s->credit->size-1)/s->credit->size>s->credit->total)return 0;
 s->credit_serial=s->credit->serial;s->frame_bytes=n;for(unsigned i=0;i<n;i++)s->frame[i]=body[i];s->phase=QCA_FILTER_PREPARED;return 1;
}
int qca_filter_submitted(QcaFilterBarrier*s,uint64_t epoch,uint32_t id,uint64_t now){
 if(tick(s,epoch,now)!=1||s->phase!=QCA_FILTER_PREPARED||!id||id<=s->last_request)return 0;
 s->tx_request=id;s->last_request=id;s->tx_completed=0;s->phase=QCA_FILTER_SUBMITTED;return 1;
}
int qca_filter_post(QcaFilterBarrier*s,uint64_t epoch,uint32_t request,uint32_t completed,const uint8_t*p,unsigned n,uint64_t now){
 if(tick(s,epoch,now)!=1||s->phase!=QCA_FILTER_SUBMITTED||request!=s->tx_request||completed<s->last_rx||completed==UINT32_MAX||n!=s->frame_bytes+8||!span(p,n)||overlap(s,sizeof(*s),p,n)||overlap(s->credit,sizeof(*s->credit),p,n))return 0;
 QcaHtcFrame f={0};if(!qca_htc_decode(p,n,&f)||p[1]!=1||p[4]||f.endpoint!=s->credit->endpoint||f.payload_bytes!=s->frame_bytes)return fail(s,11);
 for(unsigned i=0;i<s->frame_bytes;i++)if(f.payload[i]!=s->frame[i])return fail(s,11);
 unsigned cost=(n+s->credit->size-1)/s->credit->size;
 if(s->credit->reserved||s->credit->ticket||s->credit->serial<=s->credit_serial||s->credit->outstanding<cost)return fail(s,12);
 s->last_rx=completed;s->tx_count++;if(s->step==2){s->echo_floor=completed;s->echo_posted=now;s->echo_deadline=stage_end(now,s->overall_deadline);s->deadline=qca_filter_effective_deadline(s);}s->phase=QCA_FILTER_POSTED;return 1;
}
int qca_filter_tx_complete(QcaFilterBarrier*s,uint64_t epoch,uint32_t request,unsigned n,uint64_t now){
 if(tick(s,epoch,now)!=1||s->phase!=QCA_FILTER_POSTED||s->tx_completed||request!=s->tx_request)return 0;
 if(n!=s->frame_bytes+8)return fail(s,5);s->tx_completed=1;s->tx_complete_observed=now;
 if(s->step<2){s->step++;s->stage_started=now;s->stage_deadline=stage_end(now,s->overall_deadline);s->deadline=qca_filter_effective_deadline(s);s->phase=QCA_FILTER_ORDERED;return 1;}
 s->phase=s->echo_seen?QCA_FILTER_PASSED:QCA_FILTER_WAIT_ECHO;return 1;
}
static void raw_save(QcaFilterBarrier*s,uint32_t id,unsigned pipe,unsigned endpoint,const uint8_t*p,unsigned n){if(s->raw_bytes)return;s->raw_bytes=n;s->raw_completion=id;s->raw_pipe=(uint8_t)pipe;s->raw_endpoint=(uint8_t)endpoint;for(unsigned i=0;i<n;i++)s->raw[i]=p[i];}
int qca_filter_receive(QcaFilterBarrier*s,uint64_t epoch,uint32_t id,unsigned pipe,const uint8_t*p,unsigned n,uint64_t now){
 if(tick(s,epoch,now)!=1)return -1;
 if(n<8||n>2048||!span(p,n)||overlap(s,sizeof(*s),p,n)||overlap(s->credit,sizeof(*s->credit),p,n))return fail(s,6);
 QcaHtcFrame frame={0};if(!qca_htc_decode(p,n,&frame))return fail(s,7);
 if(frame.payload_bytes<4||word(frame.payload)!=0x1d001)return 0;
 /* Echo from another service, too early or malformed belongs to diagnostic failure. */
 raw_save(s,id,pipe,frame.endpoint,p,n);
 if(pipe!=2||frame.endpoint!=s->credit->endpoint||s->step!=2||(s->phase!=QCA_FILTER_POSTED&&s->phase!=QCA_FILTER_WAIT_ECHO&&s->phase!=QCA_FILTER_PASSED))return fail(s,8);
 uint32_t arg=0;if(!qca_filter_echo_payload(frame.payload,frame.payload_bytes,&arg)||arg!=s->echo_arg)return fail(s,9);
 if(s->echo_seen||id<=s->echo_floor||id<=s->last_rx||!id)return fail(s,10);
 s->last_rx=id;s->echo_seen=1;s->echo_observed=now;if(s->tx_completed)s->phase=QCA_FILTER_PASSED;return 1;
}
int qca_filter_poll(QcaFilterBarrier*s,uint64_t epoch,uint64_t now){if(s&&s->phase!=QCA_FILTER_PASSED&&s->phase!=QCA_FILTER_FAULT&&s->phase!=QCA_FILTER_CANCELLED&&s->phase&&now>=s->last_poll){uint64_t gap=now-s->last_poll;if(gap>s->maximum_poll_gap)s->maximum_poll_gap=gap;s->last_poll=now;}int rc=tick(s,epoch,now);if(rc!=1)return -1;return qca_filter_passed(s)?1:0;}
int qca_filter_cancel_unposted(QcaFilterBarrier*s){if(!s||s->phase!=QCA_FILTER_PREPARED)return 0;s->phase=QCA_FILTER_CANCELLED;return 1;}
void qca_filter_fault(QcaFilterBarrier*s,unsigned error){(void)fail(s,error?error:11);}
int qca_filter_passed(const QcaFilterBarrier*s){return s&&s->phase==QCA_FILTER_PASSED&&!s->error&&s->step==2&&s->tx_count==3&&s->tx_completed&&s->echo_seen&&s->raw_bytes&&s->raw_completion>s->echo_floor;}

#pragma GCC diagnostic pop
