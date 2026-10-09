#include "htc_wire.h"
static unsigned le16(const uint8_t*p){return p[0]|((unsigned)p[1]<<8);}
static void put16(uint8_t*p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static void zero(uint8_t*p,unsigned n){for(unsigned i=0;i<n;i++)p[i]=0;}
int qca_htc_decode(const uint8_t*p,unsigned n,QcaHtcFrame*out){
 QcaHtcFrame v={0};unsigned bytes,trailer,pos,end;
 if(!p||!out||n<8||n>QCA_HTC_FRAME_LIMIT||p[0]>=QCA_HTC_ENDPOINTS)return 0;
 /* Bundled receive is never negotiated by this PCI profile. */
 if(p[1]&~3u)return 0;
 bytes=le16(p+2);if(bytes!=n-8)return 0;
 trailer=(p[1]&2)?p[4]:0;
 if(!(p[1]&2)&&p[4])return 0;
 if((p[1]&2)&&trailer<4)return 0;
 if(trailer>bytes)return 0;
 v.endpoint=p[0];v.payload=p+8;v.payload_bytes=bytes-trailer;
 pos=n-trailer;end=n;
 while(pos<end){
  unsigned id,len;
  if(end-pos<4)return 0;
  id=p[pos];len=p[pos+1];pos+=4;
  if(len>end-pos)return 0;
  if(id==1){
   if(!len||(len&3))return 0;
   for(unsigned i=0;i<len;i+=4){
    unsigned ep=p[pos+i],credit=p[pos+i+1];
    if(ep>=QCA_HTC_ENDPOINTS||v.credits[ep]+credit>65535)return 0;
    v.credits[ep]=(uint16_t)(v.credits[ep]+credit);
   }
  }else if(id==2){
   if(len!=12)return 0;
   /* Lookahead validity can be inconsistent in control responses. Ignore
    * this scheduling hint; never treat it as a payload or DMA address. */
  }else if(id==3){
   if(!len||(len&3)||len>128)return 0;
  }else if(id!=0)return 0;
  pos+=len;
 }
 *out=v;return 1;
}
int qca_htc_ready(const QcaHtcFrame*f,QcaHtcReady*out){
 QcaHtcReady v={0};const uint8_t*p;
 if(!f||!out||f->endpoint||!f->payload||(f->payload_bytes!=8&&f->payload_bytes!=12))return 0;
 p=f->payload;if(le16(p)!=1)return 0;
 v.credits=(uint16_t)le16(p+2);v.credit_size=(uint16_t)le16(p+4);v.endpoints=p[6];
 if(!v.credits||v.credits>255||!v.credit_size||v.credit_size>QCA_HTC_FRAME_LIMIT||v.endpoints<2||v.endpoints>QCA_HTC_ENDPOINTS)return 0;
 if(f->payload_bytes==12){v.version=p[8];v.max_bundle=p[9];v.alt_credit_size=(uint16_t)(le16(p+10)&0xfff);
  if(v.version>1||v.max_bundle>32)return 0;
 }
 *out=v;return 1;
}
int qca_htc_connection(const QcaHtcFrame*f,unsigned service,QcaHtcConnection*out){
 QcaHtcConnection v;const uint8_t*p;
 if(!f||!out||f->endpoint||!f->payload||(f->payload_bytes!=8&&f->payload_bytes!=12)||(service!=QCA_HTC_WMI&&service!=QCA_HTC_HTT))return 0;
 /* Pinned ath10k validates a minimum8-byte response core. This target
  * additionally emits four zero bytes. Admit only that observed extension;
  * unknown extension lengths/content remain unsupported. */
 p=f->payload;
 if(f->payload_bytes==12&&(p[8]||p[9]||p[10]||p[11]))return 0;
 if(le16(p)!=3||le16(p+2)!=service||p[4])return 0;
 v.service=(uint16_t)service;v.endpoint=p[5];v.max_bytes=(uint16_t)le16(p+6);
 if(!v.endpoint||v.endpoint>=QCA_HTC_ENDPOINTS||!v.max_bytes||v.max_bytes>QCA_HTC_FRAME_LIMIT-8)return 0;
 *out=v;return 1;
}
unsigned qca_htc_header(uint8_t*p,unsigned cap,unsigned ep,unsigned bytes,uint8_t seq,int credit){
 if(!p||ep>=QCA_HTC_ENDPOINTS||bytes>QCA_HTC_FRAME_LIMIT-8||cap<bytes+8||(credit!=0&&credit!=1)||(ep==0&&credit))return 0;
 zero(p,8);p[0]=(uint8_t)ep;p[1]=(uint8_t)credit;put16(p+2,bytes);p[5]=seq;return bytes+8;
}
unsigned qca_htc_connect(uint8_t*p,unsigned cap,unsigned service,unsigned credits,uint8_t seq){
 unsigned flags;
 if((service!=QCA_HTC_WMI&&service!=QCA_HTC_HTT)||credits>255||(service==QCA_HTC_WMI&&!credits)||(service==QCA_HTC_HTT&&credits))return 0;
 if(!qca_htc_header(p,cap,0,8,seq,0))return 0;
 zero(p+8,8);put16(p+8,2);put16(p+10,service);flags=(credits<<8)|(service==QCA_HTC_HTT?8:0);put16(p+12,flags);return 16;
}
unsigned qca_htc_setup(uint8_t*p,unsigned cap,uint8_t seq){
 /* PCI setup-complete-ex payload: 2-byte message id + 10-byte body;
  * RX bundling disabled, exactly as the pinned PCI reference path. */
 if(!qca_htc_header(p,cap,0,12,seq,0))return 0;
 zero(p+8,12);put16(p+8,5);return 20;
}
