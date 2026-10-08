#include "auth_raw.h"
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
static QRxInd indication(unsigned completion,unsigned tid,unsigned count){uint8_t raw[24]={18};raw[1]=tid;raw[2]=7;raw[6]=count;for(unsigned j=0;j<count;j++){put(raw+8+8*j,0x10000+2048*j);raw[12+8*j]=64;}QRxInd i={0};C(qrx_indication(3,3,56,9,completion,11,raw,8+8*count,&i)==1);return i;}
static QRxOwner owner(unsigned completion,unsigned slot){QRxOwner o={0x10000+2048*slot,2048,2,9,completion,99+slot};return o;}
static void packet(uint8_t*p,uint64_t pn,unsigned index,unsigned tid){memset(p,0,2048);unsigned qos=tid!=16,header=qos?26:24;put(p+4,0x80000000u|(index?4:0)|(qos?0:64));put(p+12,7|(1<<11)|(1<<13)|(12<<16)|(6u<<28));put(p+16,pn);put(p+20,(pn>>32)|(qos?tid<<28:0));put(p+24,64);put(p+56,3<<14);p[44]=32|(index<<6);uint8_t*f=p+300;f[0]=qos?0x88:8;f[1]=0x42;memcpy(f+4,own,6);if(index)f[4]=1;memcpy(f+10,ap,6);f[22]=12<<4;f[23]=(12<<4)>>8;if(qos)f[24]=tid;uint8_t*iv=f+header;iv[0]=pn;iv[1]=pn>>8;iv[3]=32|(index<<6);for(unsigned j=0;j<4;j++)iv[4+j]=pn>>(16+8*j);}
static void llc(uint8_t*p,unsigned tid){unsigned h=tid==16?24:26;uint8_t*l=p+300+h+8;l[0]=0xaa;l[1]=0xaa;l[2]=3;l[6]=8;for(unsigned j=8;j<64-h-20;j++)l[j]=(uint8_t)(0x90+j);}
static void rejected(const QpnLedger*s,const QRxInd*i,const QRxOwner*o,const uint8_t*p,unsigned n){QpnLedger before=*s;QauthRawCandidate out,copy;memset(&out,0xa5,sizeof out);copy=out;C(!qauth_raw_candidate(s,i,o,p,n,&out));C(!memcmp(s,&before,sizeof before));C(!memcmp(&out,&copy,sizeof out));}
int main(void){binding.endpoint=2;binding.op_version=3;binding.max_bytes=2048;version.major=3;version.minor=56;
 for(unsigned index=0;index<4;index++)for(unsigned tid=0;tid<17;tid++){QpnLedger s=ledger(index,9),before=s;QRxInd i=indication(12,tid,1);QRxOwner o=owner(12,0);uint8_t p[2048];packet(p,10,index,tid);llc(p,tid);QauthRawCandidate out;C(qauth_raw_candidate(&s,&i,&o,p,2048,&out));C(!memcmp(&s,&before,sizeof s));C(out.staged.key[index].last[tid]==10);C(out.provenance.pn==10);C(!(out.frame[1]&64));C(out.frame_bytes==44);C(out.ethernet_bytes==(tid==16?26:24));C(out.ethernet[12]==8&&out.ethernet[13]==0);C(out.ethernet[14]==0x98);rejected(&out.staged,&i,&o,p,2048);
  for(unsigned bit=0;bit<32;bit++)if(((1u<<30)|(1u<<29)|(1u<<28)|(1u<<24)|(1u<<4)|(1u<<3))&(1u<<bit)){uint8_t bad[2048];memcpy(bad,p,2048);put(bad+4,(uint32_t)(p[4]|((uint32_t)p[5]<<8)|((uint32_t)p[6]<<16)|((uint32_t)p[7]<<24))|(1u<<bit));rejected(&s,&i,&o,bad,2048);}
  for(unsigned n=0;n<2048;n++)rejected(&s,&i,&o,p,n);
  for(unsigned j=0;j<8;j++){uint8_t bad[2048];memcpy(bad,p,2048);bad[300+(tid==16?24:26)+8+j]^=1;rejected(&s,&i,&o,bad,2048);}
  {uint8_t bad[2048];memcpy(bad,p,2048);put(bad+24,39);rejected(&s,&i,&o,bad,2048);}
  {QRxOwner bad=o;bad.state=1;rejected(&s,&i,&bad,p,2048);bad=o;bad.epoch=8;rejected(&s,&i,&bad,p,2048);}
 }
 printf("checks=%u source-HW-RAW-staged-PN physical=false controlled_port=false PN_original_unchanged=true\n",checks);return 0;}
