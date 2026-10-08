#include "beacon_info.h"
static unsigned le16(const uint8_t*p){return (unsigned)p[0]|((unsigned)p[1]<<8);}
static void copy(uint8_t*d,const uint8_t*s,unsigned n){while(n--)*d++=*s++;}
static int equal(const uint8_t*a,const uint8_t*b,unsigned n){while(n--)if(*a++!=*b++)return 0;return 1;}
static int mac(const uint8_t*p){unsigned any=0;for(unsigned i=0;i<6;i++)any|=p[i];return any&&!(p[0]&1);}
int qca_beacon_info(const uint8_t*p,unsigned n,QcaBeaconInfo*out){
 if(!p||!out||n<36||n>4096)return -1;
 unsigned fc=le16(p),type=fc&0xfc;
 if((fc&0xc707)||(type!=0x80&&type!=0x50)||(le16(p+22)&15)||!mac(p+10)||!mac(p+16)||!equal(p+10,p+16,6))return -1;
 unsigned caps=le16(p+34);if(!(caps&1)||(caps&2)||!le16(p+32))return -1;
 QcaBeaconInfo t;uint8_t*z=(uint8_t*)&t;for(unsigned i=0;i<sizeof(t);i++)z[i]=0;
 copy(t.bssid,p+16,6);t.interval=(uint16_t)le16(p+32);t.capabilities=(uint16_t)caps;t.privacy=(caps>>4)&1;
 unsigned seen_ssid=0,seen_rsn=0,seen_ds=0,seen_ht=0,ds=0,ht=0;
 for(unsigned at=36;at<n;){
  if(n-at<2)return -1;
  unsigned id=p[at],bytes=p[at+1];at+=2;if(bytes>n-at)return -1;
  const uint8_t*v=p+at;
  if(id==0){
   if(seen_ssid++||bytes>32)return -1;
   t.ssid_bytes=bytes;copy(t.ssid,v,bytes);unsigned any=0;for(unsigned i=0;i<bytes;i++)any|=v[i];t.hidden=!any;
  }else if(id==3){if(seen_ds++||bytes!=1||!v[0])return -1;ds=v[0];}
  else if(id==61){if(seen_ht++||bytes!=22||!v[0])return -1;ht=v[0];}
  else if(id==48){
   if(seen_rsn++||!t.privacy||bytes<2||le16(v)!=1)return -1;
   t.rsn_bytes=bytes;copy(t.rsn,v,bytes);
  }else if(id==221&&bytes>=4&&v[0]==0&&v[1]==0x50&&v[2]==0xf2&&v[3]==1)t.wpa_vendor=1;
  at+=bytes;
 }
 if(!seen_ssid||(ds&&ht&&ds!=ht))return -1;
 t.channel=ds?ds:ht;*out=t;return 0;
}
int qca_beacon_ssid_matches(const QcaBeaconInfo*p,const uint8_t*ssid,unsigned n){
 if(!p||!ssid||!n||n>32||p->ssid_bytes>32||p->hidden||p->ssid_bytes!=n)return 0;
 return equal(p->ssid,ssid,n);
}
