#include "historical.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
static unsigned checks;
#define CHECK(x) do{assert(x);checks++;}while(0)
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
static const uint8_t good_rsn[]={1,0,0,15,172,4,1,0,0,15,172,4,1,0,0,15,172,2,0,0};
static void ctx(QcaHistoricalContext*c){memset(c,0,sizeof(*c));c->generation=61;c->quiescent=c->owners_released=1;c->expected_epoch=c->observed_epoch=42;c->completion=25;c->start_floor=20;c->terminal_completion=40;c->observed_frequency=2437;c->ssid_bytes=16;memcpy(c->ssid,"SILK_56E35E_Plus",16);memset(c->expected_policy,1,96);memset(c->observed_policy,1,96);}
static unsigned packet(uint8_t*p,const uint8_t*rsn,unsigned bytes,unsigned variation){memset(p,0,512);put(p,0x7001);put(p+4,40|(44u<<16));put(p+8,6);uint8_t*f=p+52;f[0]=0x80;for(unsigned j=0;j<6;j++){f[4+j]=255;f[10+j]=f[16+j]=(uint8_t)(2*j+2);}f[32]=100;f[34]=variation==9?1:0x11;unsigned pos=36;
 f[pos++]=1;f[pos++]=4;f[pos++]=0x82;f[pos++]=0x84;f[pos++]=0x8b;f[pos++]=0x96;f[pos++]=50;f[pos++]=8;static const uint8_t rates[]={12,18,24,36,48,72,96,108};memcpy(f+pos,rates,8);pos+=8;
 f[pos++]=0;f[pos++]=16;memcpy(f+pos,"SILK_56E35E_Plus",16);pos+=16;f[pos++]=3;f[pos++]=1;f[pos++]=6;
 if(bytes){f[pos++]=48;f[pos++]=bytes;memcpy(f+pos,rsn,bytes);pos+=bytes;}
 if(variation==1){f[pos++]=1;f[pos++]=1;f[pos++]=0x82;}if(variation==2){f[pos++]=50;f[pos++]=1;f[pos++]=12;}if(variation==3){f[pos++]=48;f[pos++]=bytes;memcpy(f+pos,rsn,bytes);pos+=bytes;}
 if(variation==4)f[38]=0xff;if(variation==5)f[38]=0;if(variation==6)f[38]=0x84;unsigned padded=(pos+3)&~3u;put(p+24,pos);put(p+48,padded|(17u<<16));return 52+padded;}
static void reject(uint8_t*p,unsigned n,QcaHistoricalContext*c){QcaHistoricalBss out,old;memset(&out,0xa5,sizeof(out));old=out;CHECK(qca_historical_bss(p,n,c,&out)!=QCA_BSS_CANDIDATE);CHECK(!memcmp(&out,&old,sizeof(out)));}
int main(void){QcaHistoricalContext c;ctx(&c);uint8_t p[512],rsn[255];QcaHistoricalBss out;unsigned n=packet(p,good_rsn,20,0);CHECK(qca_historical_bss(p,n,&c,&out)==1);CHECK(out.live_frequency==0&&out.observed_frequency==2437&&out.required_basic_rates==15&&out.advertised_known_rates==4095&&!out.native_capabilities_proved&&!out.native_capabilities&&!out.advertisement.selected_rates&&out.fresh_live_BSS_required&&!out.association_authority&&!out.port_authority);
 CHECK(qca_historical_native_rates(&out,4095,0)==QCA_BSS_POLICY);CHECK(qca_historical_native_rates(&out,1,1)==QCA_BSS_UNSUPPORTED);CHECK(qca_historical_native_rates(&out,4095,1)==QCA_BSS_CANDIDATE);CHECK(!out.native_capabilities_proved&&!out.association_authority&&out.fresh_live_BSS_required);
 for(unsigned mask=0;mask<4096;mask++)CHECK(qca_historical_native_rates(&out,mask,1)==(!mask?QCA_BSS_POLICY:(15&~mask)?QCA_BSS_UNSUPPORTED:QCA_BSS_CANDIDATE));
 CHECK(qca_historical_native_rates(&out,4095,2)==QCA_BSS_POLICY);CHECK(qca_historical_native_rates(&out,4096,1)==QCA_BSS_POLICY);
 for(unsigned mode=0;mode<11;mode++){ctx(&c);switch(mode){case 0:c.generation=60;break;case 1:c.quiescent=0;break;case 2:c.owners_released=0;break;case 3:c.live_frequency=2437;break;case 4:c.observed_epoch++;break;case 5:c.completion=c.start_floor;break;case 6:c.terminal_completion=c.completion;break;case 7:c.observed_frequency=2412;break;case 8:c.expected_policy[0]^=1;break;case 9:c.ssid[0]='X';break;case 10:c.observed_frequency=2484;break;}reject(p,n,&c);}ctx(&c);
 for(unsigned i=1;i<=6;i++){n=packet(p,good_rsn,20,i);reject(p,n,&c);}n=packet(p,good_rsn,0,9);reject(p,n,&c);
 memcpy(rsn,good_rsn,20);rsn[17]=8;n=packet(p,rsn,20,0);reject(p,n,&c);memcpy(rsn,good_rsn,20);rsn[5]=2;n=packet(p,rsn,20,0);reject(p,n,&c);
 for(unsigned caps=0;caps<256;caps++){memcpy(rsn,good_rsn,20);rsn[18]=caps;n=packet(p,rsn,20,0);int rc=qca_historical_bss(p,n,&c,&out);CHECK(rc==((caps&64)?QCA_BSS_UNSUPPORTED:QCA_BSS_CANDIDATE));if(rc==1)CHECK(!out.live_frequency&&!out.native_capabilities_proved&&out.fresh_live_BSS_required&&!out.association_authority);}
 n=packet(p,good_rsn,20,0);for(unsigned cut=0;cut<n;cut++)reject(p,cut,&c);
 p[n-1]=1;reject(p,n,&c); /* nonzero TLV padding */
 n=packet(p,good_rsn,20,0);for(unsigned at=0;at<n;at++)for(unsigned value=0;value<256;value+=17){uint8_t changed[512];memcpy(changed,p,n);changed[at]=value;QcaHistoricalBss old;memset(&out,0x5a,sizeof(out));old=out;int rc=qca_historical_bss(changed,n,&c,&out);if(rc==1)CHECK(!out.live_frequency&&!out.native_capabilities_proved&&out.fresh_live_BSS_required&&!out.association_authority&&out.advertisement.selected_rates==0);else CHECK(!memcmp(&out,&old,sizeof(out)));}
 printf("checks=%u SYNTHETIC-HISTORICAL61-GRAMMAR-NOT-PHYSICAL PASS\n",checks);return 0;}
