#include "bss_security.h"
#include "utils/includes.h"
#include "utils/common.h"
#include "common/defs.h"
#include "common/wpa_common.h"
#include "common/ieee802_11_defs.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do{assert(x);checks++;}while(0)
int oracle_rsn(const uint8_t*,unsigned,QcaRsnFields*);
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
static const uint8_t good_rsn[]={1,0,0,15,172,4,1,0,0,15,172,4,1,0,0,15,172,2,0,0};
static void ctx(QcaBssContext*c){memset(c,0,sizeof(*c));c->expected_epoch=c->observed_epoch=9;c->completion=20;c->start_floor=10;c->live_frequency=2412;c->native_rates=0xfff;c->ssid_bytes=4;memcpy(c->ssid,"test",4);memset(c->policy_digest,1,32);c->frequency_count=1;c->frequencies[0]=2412;}
static unsigned packet(uint8_t*p,const uint8_t*rsn,unsigned bytes,unsigned variation){memset(p,0,512);put(p,0x7001);put(p+4,40|(44u<<16));put(p+8,1);uint8_t*f=p+52;f[0]=0x80;for(unsigned j=0;j<6;j++){f[4+j]=255;f[10+j]=f[16+j]=(uint8_t)(j+2);}f[32]=100;f[34]=variation==9?1:0x11;unsigned pos=36;
 f[pos++]=1;f[pos++]=4;f[pos++]=0x82;f[pos++]=0x84;f[pos++]=0x8b;f[pos++]=0x96;
 f[pos++]=50;f[pos++]=8;static const uint8_t rates[]={12,18,24,36,48,72,96,108};memcpy(f+pos,rates,8);pos+=8;
 f[pos++]=0;f[pos++]=4;memcpy(f+pos,"test",4);pos+=4;f[pos++]=3;f[pos++]=1;f[pos++]=1;
 if(bytes){f[pos++]=48;f[pos++]=(uint8_t)bytes;memcpy(f+pos,rsn,bytes);pos+=bytes;}
 if(variation==1){f[pos++]=1;f[pos++]=1;f[pos++]=0x82;}
 if(variation==2){f[pos++]=50;f[pos++]=1;f[pos++]=12;}
 if(variation==3){f[pos++]=48;f[pos++]=(uint8_t)bytes;memcpy(f+pos,rsn,bytes);pos+=bytes;}
 if(variation==4)f[38]=0xff; /* unsupported basic membership selector127 */
 if(variation==5)f[38]=0; /* zero bitrate malformed */
 if(variation==6)f[38]=0x84; /* duplicate rate2Mbps */
 if(variation==7){f[pos++]=221;f[pos++]=4;f[pos++]=0;f[pos++]=80;f[pos++]=242;f[pos++]=1;}
 if(variation==8){f[pos++]=244;f[pos++]=1;f[pos++]=0;}
 unsigned padded=(pos+3)&~3u;put(p+24,pos);put(p+48,padded|(17u<<16));return 52+padded;}
static void rejected(const uint8_t*p,unsigned n,QcaBssContext*c,int code){QcaBssSecurity out,old;memset(&out,0xa5,sizeof(out));old=out;int rc=qca_bss_security(p,n,c,&out);if(rc!=code)fprintf(stderr,"rejected expected=%d got=%d bytes=%u checks=%u\n",code,rc,n,checks);CHECK(rc==code);CHECK(!memcmp(&out,&old,sizeof(out)));}
int main(void){_Static_assert(WPA_PROTO_RSN==2&&WPA_CIPHER_CCMP==16&&WPA_KEY_MGMT_PSK==2&&WPA_CAPABILITY_MFPR==64&&WPA_CAPABILITY_MFPC==128,"pinned policy constants");QcaBssContext c;ctx(&c);uint8_t p[512],rsn[255],ie[257];QcaBssSecurity out;unsigned n=packet(p,good_rsn,sizeof(good_rsn),0);CHECK(qca_bss_security(p,n,&c,&out)==QCA_BSS_CANDIDATE);CHECK(out.rates==0xfff&&out.basic_rates==15&&out.selected_rates==0xfff&&out.selected_pairwise==RSN_CIPHER_SUITE_CCMP&&out.selected_akm==RSN_AUTH_KEY_MGMT_PSK_OVER_802_1X&&!out.selected_pmf&&out.beacon.bss.channel==1&&out.epoch==9);
 for(unsigned cap=0;cap<65536;cap++){memcpy(rsn,good_rsn,20);rsn[18]=cap;rsn[19]=cap>>8;n=packet(p,rsn,20,0);int rc=qca_bss_security(p,n,&c,&out);CHECK(rc==((cap&WPA_CAPABILITY_MFPR)?QCA_BSS_UNSUPPORTED:QCA_BSS_CANDIDATE));}
 for(unsigned group=0;group<16;group++)for(unsigned pair=0;pair<16;pair++)for(unsigned akm=0;akm<32;akm++){memcpy(rsn,good_rsn,20);rsn[5]=group;rsn[11]=pair;rsn[17]=akm;n=packet(p,rsn,20,0);int rc=qca_bss_security(p,n,&c,&out);if(rc==QCA_BSS_CANDIDATE)CHECK(group==4&&pair==4&&akm==2);else checks++;}
 /* True WPA2/WPA3 transition: explicit PSK+SAE, CCMP and optional PMF. */
 memcpy(rsn,good_rsn,18);rsn[12]=2;rsn[18]=0;rsn[19]=15;rsn[20]=172;rsn[21]=8;rsn[22]=128;rsn[23]=0;n=packet(p,rsn,24,8);CHECK(qca_bss_security(p,n,&c,&out)==QCA_BSS_CANDIDATE&&out.akm_count==2&&(out.rsn.akm&WPA_KEY_MGMT_SAE)&&out.pmf_capable&&!out.pmf_required);
 rsn[22]=192;n=packet(p,rsn,24,0);rejected(p,n,&c,QCA_BSS_UNSUPPORTED);
 memcpy(rsn,good_rsn,20);rsn[17]=8;n=packet(p,rsn,20,0);rejected(p,n,&c,QCA_BSS_UNSUPPORTED);rsn[17]=1;n=packet(p,rsn,20,0);rejected(p,n,&c,QCA_BSS_UNSUPPORTED);rsn[17]=2;rsn[11]=2;n=packet(p,rsn,20,0);rejected(p,n,&c,QCA_BSS_UNSUPPORTED);
 for(unsigned variant=1;variant<=6;variant++){n=packet(p,good_rsn,20,variant);rejected(p,n,&c,variant==4?QCA_BSS_UNSUPPORTED:QCA_BSS_MALFORMED);}
 n=packet(p,good_rsn,20,7);CHECK(qca_bss_security(p,n,&c,&out)==QCA_BSS_CANDIDATE&&out.beacon.bss.wpa_vendor);n=packet(p,good_rsn,0,7);rejected(p,n,&c,QCA_BSS_UNSUPPORTED);n=packet(p,good_rsn,0,9);rejected(p,n,&c,QCA_BSS_UNSUPPORTED);
 memcpy(rsn,good_rsn,18);rsn[12]=2;memcpy(rsn+18,rsn+14,4);rsn[22]=rsn[23]=0;n=packet(p,rsn,24,0);rejected(p,n,&c,QCA_BSS_MALFORMED);
 memcpy(rsn,good_rsn,20);rsn[20]=1;rsn[21]=0;n=packet(p,rsn,22,0);rejected(p,n,&c,QCA_BSS_MALFORMED);
 memcpy(rsn,good_rsn,20);rsn[20]=rsn[21]=0;rsn[22]=0;n=packet(p,rsn,23,0);rejected(p,n,&c,QCA_BSS_MALFORMED);
 n=packet(p,good_rsn,20,0);for(unsigned kind=0;kind<7;kind++){ctx(&c);switch(kind){case 0:c.observed_epoch++;break;case 1:c.completion=c.start_floor;break;case 2:c.live_frequency=2437;break;case 3:c.frequencies[0]=2437;break;case 4:memset(c.policy_digest,0,32);break;case 5:c.native_rates=0x1000;break;case 6:c.native_rates=1;break;}rejected(p,n,&c,kind==6?QCA_BSS_UNSUPPORTED:QCA_BSS_POLICY);}
 ctx(&c);c.ssid[0]='X';rejected(p,n,&c,QCA_BSS_NOT_TARGET);ctx(&c);
 for(unsigned cut=0;cut<n;cut++){QcaBssSecurity old;memset(&out,0x5a,sizeof(out));old=out;CHECK(qca_bss_security(p,cut,&c,&out)!=QCA_BSS_CANDIDATE);CHECK(!memcmp(&out,&old,sizeof(out)));}
 for(unsigned at=0;at<n;at++)for(unsigned value=0;value<256;value++){uint8_t mutated[512];memcpy(mutated,p,n);mutated[at]=value;QcaBssSecurity old;memset(&out,0x5a,sizeof(out));old=out;int rc=qca_bss_security(mutated,n,&c,&out);if(rc==QCA_BSS_CANDIDATE)CHECK(out.rsn.group==16&&(out.rsn.akm&2)&&(out.rsn.pairwise&16)&&!out.pmf_required&&!out.selected_pmf&&(out.basic_rates&~c.native_rates)==0);else CHECK(!memcmp(&out,&old,sizeof(out)));}
 ie[0]=48;ie[1]=20;memcpy(ie+2,good_rsn,20);for(unsigned at=0;at<22;at++)for(unsigned value=0;value<256;value++){uint8_t mutated[257];memcpy(mutated,ie,22);mutated[at]=value;QcaRsnFields a={0},b={0};int ours=qca_pinned_rsn(mutated,22,&a),reference=oracle_rsn(mutated,22,&b);CHECK(ours==reference);if(ours)CHECK(!memcmp(&a,&b,sizeof(a)));}
 printf("checks=%u copied-BSS/rates/RSN/PMF/policy/upstream-oracle PASS\n",checks);return 0;}
