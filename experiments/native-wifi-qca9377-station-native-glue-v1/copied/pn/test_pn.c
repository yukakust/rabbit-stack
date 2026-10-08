#include "pn.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
uint64_t original_iv_pn(uint8_t*);
int original_replay(uint64_t,uint64_t);
static unsigned checks;
#define C(x) do { checks++; if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);} }while(0)
static void put(uint8_t*p,uint32_t x){for(unsigned j=0;j<4;j++)p[j]=x>>(8*j);}
static const uint8_t ap[6]={2,3,4,5,6,7},own[6]={2,8,9,10,11,12};
static QcaHttBinding binding;
static QcaHttVersion version;
static QcaRxEvent sec(unsigned completion,unsigned index){QcaRxEvent e={0};e.completion=completion;e.pipe=1;e.endpoint=2;e.bytes=28;e.raw_bytes=36;e.raw[0]=2;e.raw[2]=28;e.raw[8]=11;e.raw[9]=6|(index==0?128:0);e.raw[10]=7;return e;}
static QpnLedger ledger(unsigned index,uint64_t initial){QpnLedger s={0};uint8_t rsc[6];for(unsigned j=0;j<6;j++)rsc[j]=initial>>(j*8);C(qpn_begin(&s,9,7,0,ap,own,&binding,&version));C(qpn_key_posted(&s,9,index,rsc,6,10,1));QcaRxEvent e=sec(11,index);C(qpn_key_sec(&s,9,&e));return s;}
static QRxInd indication(unsigned completion,unsigned tid,unsigned count){uint8_t raw[24]={18};raw[1]=tid;raw[2]=7;raw[6]=count;for(unsigned j=0;j<count;j++){put(raw+8+8*j,0x10000+2048*j);raw[12+8*j]=40;}QRxInd i={0};C(qrx_indication(3,3,56,9,completion,11,raw,8+8*count,&i)==1);return i;}
static QRxOwner owner(unsigned completion,unsigned slot){QRxOwner o={0x10000+2048*slot,2048,2,9,completion,99+slot};return o;}
static void packet(uint8_t*p,uint64_t pn,unsigned index,unsigned tid){memset(p,0,2048);unsigned qos=tid!=16,header=qos?26:24;put(p+4,0x80000000u|(index?4:0)|(qos?0:64));put(p+12,7|(1<<11)|(1<<13)|(12<<16)|(6u<<28));put(p+16,pn);put(p+20,(pn>>32)|(qos?tid<<28:0));put(p+24,40);put(p+56,3<<14);p[44]=32|(index<<6);uint8_t*f=p+300;f[0]=qos?0x88:8;f[1]=0x42;memcpy(f+4,own,6);if(index)f[4]=1;memcpy(f+10,ap,6);f[22]=12<<4;f[23]=(12<<4)>>8;if(qos)f[24]=tid;uint8_t*iv=f+header;iv[0]=pn;iv[1]=pn>>8;iv[3]=32|(index<<6);for(unsigned j=0;j<4;j++)iv[4+j]=pn>>(16+8*j);}
static int reject(QpnLedger*s,QRxInd*i,QRxOwner*o,uint8_t*p){QpnLedger before=*s;QpnView out,original;memset(&out,0xa5,sizeof out);original=out;int r=qpn_counter_owned(s,i,o,p,2048,&out);C(r!=1);C(!memcmp(&before,s,sizeof before));C(!memcmp(&out,&original,sizeof out));return r;}
int main(void){for(uint64_t n=0;n<65536;n++){uint64_t a=n*0x1234567ULL,b=(n^0x7654)*0x7654321ULL;uint8_t iv[8]={a,a>>8,0,32,a>>16,a>>24,a>>32,a>>40};C(original_iv_pn(iv)==a);C(original_replay(a,b)==(a<=b));}
 binding.endpoint=2;binding.op_version=3;binding.max_bytes=2048;version.major=3;version.minor=56;uint8_t p[2048];QpnView view;
 for(unsigned index=0;index<4;index++)for(unsigned tid=0;tid<17;tid++){uint64_t initial=0x10203040506ULL;QpnLedger s=ledger(index,initial);QRxInd i=indication(12,tid,2);QRxOwner a=owner(12,0),b=owner(12,1);packet(p,initial,index,tid);reject(&s,&i,&a,p);packet(p,initial+1,index,tid);C(qpn_counter_owned(&s,&i,&a,p,2048,&view)==1);C(view.pn==initial+1&&view.index==index&&view.tid==tid&&view.map_identity==99);packet(p,initial+2,index,tid);reject(&s,&i,&a,p);C(qpn_counter_owned(&s,&i,&b,p,2048,&view)==1);C(s.seen_count==2);i=indication(13,tid,1);a=owner(13,0);packet(p,initial+1,index,tid);reject(&s,&i,&a,p);packet(p,initial+3,index,tid);C(qpn_counter_owned(&s,&i,&a,p,2048,&view)==1);C(s.seen_count==1);QcaRxEvent e=sec(14,index);C(!qpn_key_sec(&s,9,&e));C(s.key[index].last[tid]==initial+3);C(!qpn_key_posted(&s,9,index,p,6,14,2));qpn_revoke(&s,9);reject(&s,&i,&a,p);}
 QpnLedger base=ledger(1,9);QRxInd i=indication(12,3,1);QRxOwner o=owner(12,0);packet(p,10,1,3);C(qpn_counter_owned(&base,&i,&o,p,2048,&view)==1);
 /* Every single bit mutation of the original descriptor/frame is bounded; accepted
  * metadata must still carry the exact PN/key/epoch/ownership provenance. */
 for(unsigned at=0;at<2048;at++)for(unsigned bit=0;bit<8;bit++){QpnLedger s=ledger(1,9);uint8_t raw[2048];packet(raw,10,1,3);raw[at]^=1<<bit;QpnView out={0};int r=qpn_counter_owned(&s,&i,&o,raw,2048,&out);C(r>=-1&&r<=1);if(r==1)C(out.pn==10&&out.index==1&&out.tid==3&&out.epoch==9&&out.completion==12&&out.paddr==0x10000);}
 {QpnLedger s=ledger(1,9);QRxInd bad=i;bad.epoch=10;reject(&s,&bad,&o,p);bad=i;bad.completion=11;reject(&s,&bad,&o,p);QRxOwner bo=o;bo.state=1;reject(&s,&i,&bo,p);bo=o;bo.map_identity=0;reject(&s,&i,&bo,p);bad=i;bad.raw[1]|=32;reject(&s,&bad,&o,p);bad=i;bad.raw[1]|=64;reject(&s,&bad,&o,p);bad=i;bad.raw[14]=1;reject(&s,&bad,&o,p);}
 {QpnLedger s={0};C(qpn_begin(&s,9,7,0,ap,own,&binding,&version));uint8_t r[6]={1};C(!qpn_key_posted(&s,9,1,r,5,10,1));C(qpn_key_posted(&s,9,1,r,6,10,1));QcaRxEvent e=sec(11,0);C(!qpn_key_sec(&s,9,&e));C(s.quarantined);C(!qpn_key_posted(&s,9,2,r,6,12,2));}
 printf("checks=%u owned-PN-metadata-only physical=false authentication=false\n",checks);return 0;
}
