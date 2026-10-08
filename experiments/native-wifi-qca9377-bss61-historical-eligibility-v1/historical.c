#include "historical.h"
static int same(const uint8_t*a,const uint8_t*b,unsigned n){unsigned v=0;for(unsigned i=0;i<n;i++)v|=a[i]^b[i];return !v;}
static unsigned le16(const uint8_t*b){return b[0]|((unsigned)b[1]<<8);}
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);}
static int rate(unsigned r){static const uint8_t actual[]={2,4,11,22,12,18,24,36,48,72,96,108};for(unsigned i=0;i<12;i++)if(actual[i]==r)return i;return -1;}
int qca_historical_bss(const uint8_t*p,unsigned n,const QcaHistoricalContext*c,QcaHistoricalBss*out){
 if(!p||!c||!out||n>2040||overlap(p,n,out,sizeof(*out))||overlap(c,sizeof(*c),out,sizeof(*out)))return QCA_BSS_MALFORMED;
 unsigned digest=0;for(unsigned i=0;i<96;i++)digest|=c->expected_policy[i];
 if(c->generation!=61||c->quiescent!=1||c->owners_released!=1||c->live_frequency!=0||!c->expected_epoch||c->expected_epoch!=c->observed_epoch||c->completion<=c->start_floor||c->terminal_completion<=c->completion||!digest||!same(c->expected_policy,c->observed_policy,96)||c->observed_frequency<2412||c->observed_frequency>2472||(c->observed_frequency-2412)%5||!c->ssid_bytes||c->ssid_bytes>32)return QCA_BSS_POLICY;
 QcaWmiBeaconRx beacon={0};int parsed=qca_wmi_beacon_rx(p,n,&beacon);if(parsed!=QCA_BEACON_RX_ACCEPTED)return parsed==QCA_BEACON_RX_MALFORMED?QCA_BSS_MALFORMED:QCA_BSS_UNSUPPORTED;
 if(beacon.frequency_mhz!=c->observed_frequency)return QCA_BSS_POLICY;
 /* Derive an advertisement parsing mask from copied rate IEs only. This is NOT
  * a native rate capability mask. Frozen parser uses it solely as a grammar
  * consistency operand; native support is separately checked by the caller. */
 const uint8_t*frame=0;for(unsigned at=4;at<n;){unsigned len=le16(p+at),tag=le16(p+at+2);if(tag==17)frame=p+at+4;at+=4+len;}
 if(!frame||beacon.buf_len<36)return QCA_BSS_MALFORMED;
 uint16_t advertised=0;for(unsigned at=36;at<beacon.buf_len;){unsigned tag=frame[at],len=frame[at+1];if(tag==1||tag==50)for(unsigned i=0;i<len;i++){int bit=rate(frame[at+2+i]&127);if(bit>=0)advertised|=(uint16_t)(1u<<bit);}at+=2+len;}
 QcaBssContext grammar={0};grammar.expected_epoch=c->expected_epoch;grammar.observed_epoch=c->observed_epoch;grammar.completion=c->completion;grammar.start_floor=c->start_floor;
 /* Private compatibility translation into frozen grammar API's old field name;
  * does not assert current live frequency. Public output remains live0. */
 grammar.live_frequency=c->observed_frequency;grammar.native_rates=advertised;grammar.ssid_bytes=c->ssid_bytes;for(unsigned i=0;i<c->ssid_bytes;i++)grammar.ssid[i]=c->ssid[i];for(unsigned i=0;i<32;i++)grammar.policy_digest[i]=c->expected_policy[i];grammar.frequency_count=13;for(unsigned i=0;i<13;i++)grammar.frequencies[i]=(uint16_t)(2412+5*i);
 QcaHistoricalBss result={0};int rc=qca_bss_security(p,n,&grammar,&result.advertisement);if(rc!=QCA_BSS_CANDIDATE)return rc;
 result.advertisement.selected_rates=0; /* No native rate selection from historical grammar. */
 result.live_frequency=0;result.observed_frequency=c->observed_frequency;result.required_basic_rates=result.advertisement.basic_rates;result.advertised_known_rates=result.advertisement.rates;result.fresh_live_BSS_required=1;*out=result;return QCA_BSS_CANDIDATE;
}
int qca_historical_native_rates(const QcaHistoricalBss*b,uint16_t mask,int valid){if(!b||valid!=1||!mask||(mask&~0xfffu)||!b->fresh_live_BSS_required||b->association_authority||b->port_authority||b->live_frequency)return QCA_BSS_POLICY;return (b->required_basic_rates&~mask)?QCA_BSS_UNSUPPORTED:QCA_BSS_CANDIDATE;}
