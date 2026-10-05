#include "beacon_info.h"
#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "upstream-beacon.h"
static const uint8_t wanted[]="SILK_56E35E_Plus";
static unsigned groups;
static unsigned base(uint8_t*p){
 memset(p,0,4096);p[0]=0x80;p[10]=p[16]=2;p[15]=p[21]=1;p[32]=100;p[34]=0x11;
 p[36]=0;p[37]=sizeof(wanted)-1;memcpy(p+38,wanted,sizeof(wanted)-1);return 38+sizeof(wanted)-1;
}
static unsigned ie(uint8_t*p,unsigned at,unsigned id,const uint8_t*v,unsigned n){assert(at+2+n<=4096&&n<=255);p[at++]=(uint8_t)id;p[at++]=(uint8_t)n;memcpy(p+at,v,n);return at+n;}
static void bad(const uint8_t*p,unsigned n){QcaBeaconInfo b;memset(&b,0x5a,sizeof(b));QcaBeaconInfo before=b;assert(qca_beacon_info(p,n,&b)==-1&&!memcmp(&b,&before,sizeof(b)));groups++;}
int main(void){
 assert(WLAN_EID_SSID==0&&WLAN_EID_DS_PARAMS==3&&WLAN_EID_RSN==48&&WLAN_EID_HT_OPERATION==61);
 assert(IEEE80211_STYPE_BEACON==0x80&&IEEE80211_STYPE_PROBE_RESP==0x50&&WLAN_CAPABILITY_PRIVACY==16);
 assert(offsetof(struct ieee80211_mgmt,u.beacon.variable)==36&&offsetof(struct ieee80211_mgmt,u.probe_resp.variable)==36);
 assert(offsetof(struct ieee80211_mgmt,bssid)==16&&offsetof(struct ieee80211_mgmt,u.beacon.beacon_int)==32&&offsetof(struct ieee80211_mgmt,u.beacon.capab_info)==34);
 uint8_t p[4096],q[4096],rsn[255]={1,0},ht[22]={8},channel=8;unsigned n=base(p),ssid_end=n;
 n=ie(p,n,3,&channel,1);unsigned ds_at=ssid_end;
 n=ie(p,n,61,ht,22);unsigned rsn_at=n;n=ie(p,n,48,rsn,20);
 QcaBeaconInfo b;assert(!qca_beacon_info(p,n,&b)&&b.channel==8&&b.privacy&&!b.hidden&&b.interval==100&&b.rsn_bytes==20);
 assert(qca_beacon_ssid_matches(&b,wanted,sizeof(wanted)-1));assert(!qca_beacon_ssid_matches(&b,wanted,sizeof(wanted)-2));groups++;
 p[0]=0x50;assert(!qca_beacon_info(p,n,&b));p[0]=0x80;groups++;
 for(unsigned i=0;i<n;i++){QcaBeaconInfo tmp;int r=qca_beacon_info(p,i,&tmp);if(!r)assert(i==ssid_end||i==ssid_end+3||i==rsn_at);else bad(p,i);}
 memcpy(q,p,n);q[37]=33;bad(q,n);memcpy(q,p,n);q[ds_at+2]=9;bad(q,n);
 memcpy(q,p,n);q[rsn_at+2]=2;bad(q,n);memcpy(q,p,n);q[34]=1;bad(q,n);
 memcpy(q,p,n);q[10]=3;bad(q,n);memcpy(q,p,n);q[16]=4;bad(q,n);memcpy(q,p,n);q[22]=1;bad(q,n);
 for(unsigned bit=0;bit<16;bit++)if((1u<<bit)&0xc707){memcpy(q,p,n);q[bit/8]|=(uint8_t)(1u<<(bit%8));bad(q,n);}
 memcpy(q,p,n);unsigned count=ie(q,n,0,wanted,sizeof(wanted)-1);bad(q,count);
 memcpy(q,p,n);count=ie(q,n,48,rsn,20);bad(q,count);
 memcpy(q,p,n);count=ie(q,n,3,&channel,1);bad(q,count);
 memcpy(q,p,n);count=ie(q,n,61,ht,22);bad(q,count);
 for(unsigned bytes=0;bytes<=255;bytes++){
  unsigned k=base(q);k=ie(q,k,48,rsn,bytes);
  if(bytes<2)bad(q,k);else{assert(!qca_beacon_info(q,k,&b)&&b.rsn_bytes==bytes);groups++;}
 }
 for(unsigned bytes=0;bytes<=32;bytes++){
  base(q);q[37]=(uint8_t)bytes;memset(q+38,0,bytes);assert(!qca_beacon_info(q,38+bytes,&b)&&b.hidden&&!qca_beacon_ssid_matches(&b,wanted,sizeof(wanted)-1));groups++;
 }
 for(unsigned bytes=0;bytes<=255;bytes++){
  unsigned k=base(q);uint8_t unknown[255]={0};k=ie(q,k,199,unknown,bytes);assert(!qca_beacon_info(q,k,&b));groups++;
  if(bytes)bad(q,k-1);
 }
 unsigned k=base(q);q[34]=1;assert(!qca_beacon_info(q,k,&b)&&!b.privacy&&!b.rsn_bytes&&!b.channel);groups++;
 const uint8_t wpa[4]={0,0x50,0xf2,1};k=ie(q,k,221,wpa,4);assert(!qca_beacon_info(q,k,&b)&&b.wpa_vendor);groups++;
 bad(p,4097);bad(0,n);assert(qca_beacon_info(p,n,0)==-1);assert(!qca_beacon_ssid_matches(0,wanted,16));assert(!qca_beacon_ssid_matches(&b,0,16));assert(!qca_beacon_ssid_matches(&b,wanted,33));
 unsigned seed=1;
 for(unsigned round=0;round<8192;round++){
  unsigned bytes=round%4097;for(unsigned i=0;i<bytes;i++){seed=seed*1664525u+1013904223u;q[i]=(uint8_t)(seed>>24);}
  QcaBeaconInfo before;memset(&before,0xa5,sizeof(before));b=before;int r=qca_beacon_info(q,bytes,&b);if(r)assert(!memcmp(&before,&b,sizeof(b)));groups++;
 }
 printf("BOUNDED BEACON/PROBE SSID AND OPAQUE RSN %u groups PASS; NO SECURITY/ASSOCIATION CLAIM\n",groups);return 0;
}
