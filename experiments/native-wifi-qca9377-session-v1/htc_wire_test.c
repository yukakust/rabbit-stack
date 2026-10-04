#include "htc_wire.h"
#include "upstream-wire.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void u16(uint8_t*p,unsigned n){p[0]=n;p[1]=n>>8;}
static unsigned frame(uint8_t*p,unsigned bytes){memset(p,0,512);u16(p+2,bytes);return bytes+8;}
int main(void){
 uint8_t p[512],expected[512],mut[512];unsigned n,checks=0;QcaHtcFrame f,old;QcaHtcReady r;QcaHtcConnection c;
 assert(sizeof(struct ath10k_htc_hdr)==8);
 assert(sizeof(struct ath10k_ath10k_htc_msg_hdr)==2);
 assert(sizeof(struct ath10k_htc_ready)==6);
 assert(sizeof(struct ath10k_htc_ready_extended)==10);
 assert(sizeof(struct ath10k_htc_conn_svc)==6);
 assert(sizeof(struct ath10k_htc_conn_svc_response)==6);
 assert(sizeof(struct ath10k_htc_setup_complete_extended)==10);
 n=frame(expected,8);struct ath10k_htc_hdr h={0};struct ath10k_ath10k_htc_msg_hdr mh={2};
 struct ath10k_htc_conn_svc req={.service_id=QCA_HTC_WMI,.flags=12<<8};
 h.len=8;h.seq_no=7;memcpy(expected,&h,8);memcpy(expected+8,&mh,2);memcpy(expected+10,&req,6);
 assert(qca_htc_connect(p,sizeof(p),QCA_HTC_WMI,12,7)==n&&!memcmp(p,expected,n));checks++;
 req.service_id=QCA_HTC_HTT;req.flags=8;memcpy(expected+10,&req,6);
 assert(qca_htc_connect(p,sizeof(p),QCA_HTC_HTT,0,7)==n&&!memcmp(p,expected,n));checks++;
 memset(expected,0,sizeof(expected));h.len=12;mh.message_id=5;memcpy(expected,&h,8);memcpy(expected+8,&mh,2);
 struct ath10k_htc_setup_complete_extended setup={0};memcpy(expected+10,&setup,sizeof(setup));
 assert(qca_htc_setup(p,sizeof(p),7)==20&&!memcmp(p,expected,20));checks++;
 n=frame(p,8);u16(p+8,1);u16(p+10,12);u16(p+12,256);p[14]=9;
 assert(qca_htc_decode(p,n,&f)&&qca_htc_ready(&f,&r)&&r.credits==12&&r.credit_size==256&&r.endpoints==9);checks++;
 /* Real layout with credits + lookahead trailers; invalid lookahead hints
  * cannot affect the decoded payload or introduce addresses. */
 n=frame(p,36);p[1]=2;p[4]=28;u16(p+8,1);u16(p+10,12);u16(p+12,256);p[14]=9;
 p[16]=1;p[17]=8;p[20]=1;p[21]=3;p[24]=1;p[25]=7;
 p[28]=2;p[29]=12;p[32]=0x12;p[40]=0x98;
 assert(qca_htc_decode(p,n,&f)&&qca_htc_ready(&f,&r)&&f.payload_bytes==8&&f.credits[1]==10);checks++;
 old=f;
 for(unsigned i=0;i<n;i++){
  for(unsigned b=0;b<256;b++){
   memcpy(mut,p,n);mut[i]=b;QcaHtcFrame tmp=old;
   int ok=qca_htc_decode(mut,n,&tmp);
   if(!ok)assert(!memcmp(&old,&tmp,sizeof(tmp)));
   else{assert(tmp.payload==mut+8&&tmp.payload_bytes<=n-8&&tmp.endpoint<9);}
   checks++;
  }
 }
 for(unsigned i=0;i<n;i++){QcaHtcFrame tmp=old;assert(!qca_htc_decode(p,i,&tmp)&&!memcmp(&tmp,&old,sizeof(tmp)));checks++;}
 const unsigned idx[]={0,1,4,17,20,29};const uint8_t val[]={9,0x10,29,255,9,11};
 for(unsigned i=0;i<sizeof(idx)/sizeof(idx[0]);i++){memcpy(mut,p,n);mut[idx[i]]=val[i];QcaHtcFrame tmp=old;assert(!qca_htc_decode(mut,n,&tmp)&&!memcmp(&old,&tmp,sizeof(tmp)));checks++;}
 n=frame(p,12);u16(p+8,1);u16(p+10,12);u16(p+12,256);p[14]=9;p[16]=1;p[17]=16;u16(p+18,512);
 assert(qca_htc_decode(p,n,&f)&&qca_htc_ready(&f,&r)&&r.version==1&&r.max_bundle==16&&r.alt_credit_size==512);checks++;
 p[16]=2;assert(qca_htc_decode(p,n,&f)&&!qca_htc_ready(&f,&r));checks++;
 n=frame(p,8);u16(p+8,3);u16(p+10,QCA_HTC_WMI);p[13]=2;u16(p+14,1536);
 assert(qca_htc_decode(p,n,&f)&&qca_htc_connection(&f,QCA_HTC_WMI,&c)&&c.endpoint==2&&c.max_bytes==1536);checks++;
 assert(!qca_htc_connection(&f,QCA_HTC_HTT,&c));checks++;
 p[12]=1;assert(qca_htc_decode(p,n,&f)&&!qca_htc_connection(&f,QCA_HTC_WMI,&c));checks++;
 assert(!qca_htc_connect(p,15,QCA_HTC_WMI,12,0));checks++;
 assert(!qca_htc_connect(p,sizeof(p),QCA_HTC_WMI,0,0));checks++;
 assert(!qca_htc_connect(p,sizeof(p),QCA_HTC_HTT,1,0));checks++;
 assert(!qca_htc_connect(p,sizeof(p),0x999,1,0));checks++;
 assert(!qca_htc_setup(p,19,0));checks++;
 assert(!qca_htc_header(p,sizeof(p),9,8,0,0));checks++;
 assert(!qca_htc_header(p,sizeof(p),0,8,0,1));checks++;
 puts("HTC PINNED-STRUCT DIFFERENTIAL AND MALFORMED-FRAME CHECKS PASS");printf("assertion_groups=%u\n",checks);return 0;
}
