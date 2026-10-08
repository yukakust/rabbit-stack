#include "bss_security.h"
static unsigned le16(const uint8_t*p){return p[0]|((unsigned)p[1]<<8);}
static uint32_t be32(const uint8_t*p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);}
static int rate(unsigned value){static const uint8_t known[]={2,4,11,22,12,18,24,36,48,72,96,108};for(unsigned j=0;j<12;j++)if(known[j]==value)return (int)j;return -1;}
static int suites(const uint8_t*p,unsigned n,unsigned*at,uint32_t*out,unsigned*count){
 if(n-*at<2)return 0;unsigned c=le16(p+*at);*at+=2;if(!c||c>16||c>(n-*at)/4)return 0;
 for(unsigned j=0;j<c;j++){out[j]=be32(p+*at);for(unsigned k=0;k<j;k++)if(out[k]==out[j])return 0;*at+=4;}*count=c;return 1;
}
static int strict_rsn(const uint8_t*p,unsigned n,QcaBssSecurity*v){
 if(n<18||le16(p)!=1)return 0;unsigned at=2,a=0,b=0;v->group_suite=be32(p+at);at+=4;
 if(!suites(p,n,&at,v->pairwise_suites,&a)||!suites(p,n,&at,v->akm_suites,&b))return 0;v->pairwise_count=(uint8_t)a;v->akm_count=(uint8_t)b;
 if(at==n)return 1;if(n-at<2)return 0;v->caps_present=1;at+=2;
 if(at==n)return 1;if(n-at<2)return 0;unsigned pmkids=le16(p+at);at+=2;if(pmkids>(n-at)/16)return 0;at+=16*pmkids;
 if(at==n)return 1;if(n-at!=4)return 0;v->management_present=1;v->management_suite=be32(p+at);return 1;
}
int qca_bss_security(const uint8_t*p,unsigned n,const QcaBssContext*c,QcaBssSecurity*out){
 if(!p||!c||!out||n>2040||overlap(p,n,out,sizeof(*out))||overlap(c,sizeof(*c),out,sizeof(*out)))return QCA_BSS_MALFORMED;
 unsigned digest=0;for(unsigned j=0;j<32;j++)digest|=c->policy_digest[j];
 if(!digest||!c->expected_epoch||c->observed_epoch!=c->expected_epoch||!c->completion||c->completion<=c->start_floor||!c->live_frequency||!c->native_rates||(c->native_rates&~0xfffu)||!c->ssid_bytes||c->ssid_bytes>32||!c->frequency_count||c->frequency_count>64)return QCA_BSS_POLICY;
 QcaBssSecurity v={0};int parsed=qca_wmi_beacon_rx(p,n,&v.beacon);
 if(parsed!=QCA_BEACON_RX_ACCEPTED)return parsed==QCA_BEACON_RX_MALFORMED?QCA_BSS_MALFORMED:QCA_BSS_UNSUPPORTED;
 unsigned selected=0;for(unsigned j=0;j<c->frequency_count;j++)selected|=c->frequencies[j]==v.beacon.frequency_mhz;
 if(!selected||v.beacon.frequency_mhz!=c->live_frequency)return QCA_BSS_POLICY;
 if(!qca_beacon_ssid_matches(&v.beacon.bss,c->ssid,c->ssid_bytes))return QCA_BSS_NOT_TARGET;
 v.capabilities=v.beacon.bss.capabilities;
 if(!v.beacon.bss.privacy||!v.beacon.bss.rsn_bytes)return QCA_BSS_UNSUPPORTED;
 /* MGMT parser already proves the40-byte metadata and owned ARRAY_BYTE span. */
 unsigned at=4;const uint8_t*frame=0;unsigned bytes=0;
 while(at<n){unsigned len=le16(p+at),tag=le16(p+at+2);if(tag==17){frame=p+at+4;bytes=v.beacon.buf_len;}at+=4+len;}
 if(!frame||bytes<36)return QCA_BSS_MALFORMED;
 unsigned supported=0,extended=0,rsnx_seen=0;
 for(at=36;at<bytes;){unsigned id=frame[at],len=frame[at+1];const uint8_t*value=frame+at+2;at+=2+len;
  if(id==1||id==50){if(!len||(id==1&&(supported++||len>8))||(id==50&&extended++)||len>32-v.rate_count)return QCA_BSS_MALFORMED;
   for(unsigned j=0;j<len;j++){unsigned raw=value[j],r=raw&127;if(!r)return QCA_BSS_MALFORMED;for(unsigned k=0;k<v.rate_count;k++)if((v.offered_rates[k]&127)==r)return QCA_BSS_MALFORMED;v.offered_rates[v.rate_count++]=(uint8_t)raw;int index=rate(r);if(index<0){if(raw&128)return QCA_BSS_UNSUPPORTED;}else{v.rates|=(uint16_t)(1u<<index);if(raw&128)v.basic_rates|=(uint16_t)(1u<<index);}}
  }else if(id==244){if(rsnx_seen++||!len||len>16)return QCA_BSS_MALFORMED;v.rsnx_bytes=(uint8_t)len;for(unsigned j=0;j<len;j++)v.rsnx[j]=value[j];}
 }
 v.selected_rates=(uint16_t)(v.rates&c->native_rates);if(supported!=1||!v.basic_rates||!v.rates||(v.basic_rates&~c->native_rates))return QCA_BSS_UNSUPPORTED;
 if(!strict_rsn(v.beacon.bss.rsn,v.beacon.bss.rsn_bytes,&v))return QCA_BSS_MALFORMED;
 uint8_t ie[257];ie[0]=48;ie[1]=(uint8_t)v.beacon.bss.rsn_bytes;for(unsigned j=0;j<v.beacon.bss.rsn_bytes;j++)ie[j+2]=v.beacon.bss.rsn[j];
 if(!qca_pinned_rsn(ie,v.beacon.bss.rsn_bytes+2,&v.rsn))return QCA_BSS_MALFORMED;
 /* Pinned hostap constants: RSN1, CCMP bit4, PSK bit1; actual raw lists retained. */
 if(v.rsn.proto!=2||!v.rsn.has_group||!v.rsn.has_pairwise||v.rsn.group!=16||!(v.rsn.pairwise&16)||!(v.rsn.akm&2))return QCA_BSS_UNSUPPORTED;
 v.pmf_required=(v.rsn.capabilities>>6)&1;v.pmf_capable=(v.rsn.capabilities>>7)&1;
 if(v.pmf_required)return QCA_BSS_UNSUPPORTED;
 v.selected_pairwise=0x000fac04;v.selected_akm=0x000fac02;v.selected_pmf=0;v.epoch=c->observed_epoch;v.completion=c->completion;*out=v;return QCA_BSS_CANDIDATE;
}
