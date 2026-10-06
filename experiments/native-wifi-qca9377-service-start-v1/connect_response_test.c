#include "htc_control.h"
#include "upstream-wire.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static const uint8_t captured[20]={0,0,12,0,0,1,0,0,3,0,0,1,0,1,0xf8,6,0,0,0,0};
static unsigned checks;
static int oracle(const uint8_t*p,unsigned n){
 if(n!=16&&n!=20)return 0;
 struct ath10k_htc_hdr h;struct ath10k_ath10k_htc_msg_hdr m;struct ath10k_htc_conn_svc_response v;
 memcpy(&h,p,sizeof(h));memcpy(&m,p+sizeof(h),sizeof(m));memcpy(&v,p+sizeof(h)+sizeof(m),sizeof(v));
 if(p[0]||p[1]>1||p[4]||h.len!=n-sizeof(h)||m.message_id!=3||v.service_id!=0x100||v.status||!v.eid||v.eid>=9||!v.max_msg_size||v.max_msg_size>4088)return 0;
 for(unsigned j=16;j<n;j++)if(p[j])return 0;
 return 1;
}
static void test(const uint8_t*p,unsigned n){
 QcaHtcFrame f;QcaHtcConnection c={.service=0xaabb,.max_bytes=0xccdd,.endpoint=7},before=c;
 int valid=qca_htc_decode(p,n,&f)&&qca_htc_connection(&f,0x100,&c);
 assert(valid==oracle(p,n));if(!valid)assert(!memcmp(&c,&before,sizeof(c)));checks++;
}
int main(void){
 assert(sizeof(struct ath10k_htc_hdr)==8&&sizeof(struct ath10k_ath10k_htc_msg_hdr)==2&&sizeof(struct ath10k_htc_conn_svc_response)==6);
 test(captured,20);uint8_t p[64];
 for(unsigned i=0;i<20;i++)for(unsigned v=0;v<256;v++){memcpy(p,captured,20);p[i]=(uint8_t)v;test(p,20);}
 for(unsigned n=0;n<=64;n++){memset(p,0,sizeof(p));memcpy(p,captured,20);if(n>=8){p[2]=(uint8_t)(n-8);p[3]=0;}test(p,n);}
 QcaHtcControl control={0};assert(!qca_htc_control_begin(&control));
 uint8_t ready[16]={0,0,8,0,0,0,0,0,1,0,2,0,0,7,4,0};
 assert(!qca_htc_control_receive(&control,ready,sizeof(ready)));
 assert(qca_htc_control_prepare(&control,p,sizeof(p))==16&&!qca_htc_control_post(&control,16));
 assert(!qca_htc_control_receive(&control,captured,20)&&control.deferred_bytes==20);
 assert(!qca_htc_control_complete(&control,16)&&control.session.wmi.endpoint==1&&control.session.wmi.max_bytes==1784);
 assert(qca_htc_control_prepare(&control,p,sizeof(p))==16&&!qca_htc_control_post(&control,16));
 memcpy(p,captured,20);p[11]=3;p[13]=2;
 assert(!qca_htc_control_receive(&control,p,20)&&!qca_htc_control_complete(&control,16));
 assert(qca_htc_control_prepare(&control,p,sizeof(p))==20&&!qca_htc_control_post(&control,20)&&!qca_htc_control_complete(&control,20));
 assert(control.session.phase==QCA_HTC_RUNNING&&control.credit.available==2);
 printf("PINNED8 CORE + ACTUAL20 FRAME + STRICT EXTENSION + EARLY RX checks=%u PASS\n",checks);return 0;
}
