#include "version.h"
static int bounds(const void*p,unsigned n){return p&&(uintptr_t)p<=UINTPTR_MAX-n;}
static int overlap(const void*a,unsigned na,const void*b,unsigned nb){
 uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x<y?y-x<na:x-y<nb;
}
static int valid(const QcaHttBinding*b){return b&&b->endpoint&&b->endpoint<QCA_HTC_ENDPOINTS&&b->max_bytes>=4&&b->max_bytes<=QCA_HTC_FRAME_LIMIT&&b->op_version==3;}
int qca_htt_version_bind(const QcaHtcSession*s,unsigned op,QcaHttBinding*out){
 if(!bounds(s,sizeof(*s))||!bounds(out,sizeof(*out))||overlap(s,sizeof(*s),out,sizeof(*out)))return 0;
 if(op!=3||s->phase!=QCA_HTC_RUNNING||s->prepared||s->ready.endpoints<3||s->ready.endpoints>QCA_HTC_ENDPOINTS
 ||s->htt.service!=QCA_HTC_HTT||s->wmi.service!=QCA_HTC_WMI
 ||!s->htt.endpoint||s->htt.endpoint>=s->ready.endpoints||!s->wmi.endpoint||s->wmi.endpoint>=s->ready.endpoints
 ||s->htt.endpoint==s->wmi.endpoint||s->htt.max_bytes<4||s->htt.max_bytes>QCA_HTC_FRAME_LIMIT)return 0;
 QcaHttBinding value={s->htt.max_bytes,s->htt.endpoint,3};*out=value;return 1;
}
unsigned qca_htt_version_request(const QcaHttBinding*b,uint8_t*out,unsigned cap){
 if(!bounds(b,sizeof(*b))||!bounds(out,4)||cap<4||overlap(b,sizeof(*b),out,4)||!valid(b))return 0;
 for(unsigned i=0;i<4;i++)out[i]=0;return 4;
}
int qca_htt_version_conf(const QcaHttBinding*b,const uint8_t*p,unsigned n,QcaHttVersion*out){
 if(!bounds(b,sizeof(*b))||!bounds(p,4)||!bounds(out,sizeof(*out))||n!=4
 ||overlap(b,sizeof(*b),out,sizeof(*out))||overlap(p,4,out,sizeof(*out))||!valid(b))return 0;
 /* TLV target mapping: type0, minor, major, reserved; narrow unextended format. */
 if(p[0]||p[3]||(p[2]!=2&&p[2]!=3))return 0;
 QcaHttVersion v={p[2],p[1]};*out=v;return 1;
}
