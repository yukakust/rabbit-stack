#include "selection.h"
static int eq(const void*a,const void*b,unsigned n){const uint8_t*x=a,*y=b;for(unsigned j=0;j<n;j++)if(x[j]!=y[j])return 0;return 1;}
static int overlaps(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);}
static int nonzero(const uint8_t*p,unsigned n){unsigned x=0;for(unsigned j=0;j<n;j++)x|=p[j];return x!=0;}
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static int valid(const QcaSelectionContext*c){
 if(!c||!c->active||!c->epoch||!c->ttl_us||c->ttl_us>30000000||!c->now_us||!c->native_rates||(c->native_rates&~0xfffu)||c->native_capabilities!=QCA_SELECT_CAPS||!nonzero(c->capability_source,32)||!nonzero(c->policy_digest,32)||!nonzero(c->ready_mac,6)||(c->ready_mac[0]&1)||!c->wmi_endpoint||c->wmi_endpoint>=9||!c->frequency_count||c->frequency_count>13)return 0;
 unsigned live=0;for(unsigned j=0;j<c->frequency_count;j++){unsigned f=c->frequencies[j];if(f<2412||f>2472||(f-2412)%5)return 0;for(unsigned k=0;k<j;k++)if(c->frequencies[k]==f)return 0;live|=f==c->live_frequency;}return live!=0;
}
static int bound(const QcaBssSelection*s,const QcaSelectionContext*c){
 const QcaSelectionContext*b=&s->binding;
 return valid(c)&&s->epoch==c->epoch&&b->rx_floor==c->rx_floor&&b->ttl_us==c->ttl_us&&b->native_rates==c->native_rates&&b->wmi_endpoint==c->wmi_endpoint&&b->native_capabilities==c->native_capabilities&&eq(b->ready_mac,c->ready_mac,6)&&eq(b->capability_source,c->capability_source,32)&&eq(b->policy_digest,c->policy_digest,32)&&b->frequency_count==c->frequency_count&&eq(b->frequencies,c->frequencies,2*c->frequency_count)&&c->now_us>=s->last_observed_us;
}
int qca_selection_begin(QcaBssSelection*s,const QcaSelectionContext*c){
 if(!s||!valid(c)||overlaps(s,sizeof(*s),c,sizeof(*c))||s->epoch)return 0;
 for(unsigned j=0;j<sizeof(*s);j++)((uint8_t*)s)[j]=0;
 s->epoch=c->epoch;s->watermark=c->rx_floor;s->binding=*c;return 1;
}
int qca_selection_offer(QcaBssSelection*s,const QcaSelectionContext*c,const QcaRxEvent*e,uint64_t observed){
 if(!s||!c||!e||overlaps(s,sizeof(*s),c,sizeof(*c))||overlaps(s,sizeof(*s),e,sizeof(*e))||!bound(s,c)||!observed||observed>c->now_us||observed<s->last_observed_us||c->now_us-observed>c->ttl_us||e->completion<=s->watermark)return QCA_SELECT_POLICY;
 if(e->pipe!=2||e->endpoint!=c->wmi_endpoint||e->raw_bytes<8||e->raw_bytes>2048)return QCA_SELECT_WIRE;
 QcaHtcFrame h={0};if(!qca_htc_decode(e->raw,e->raw_bytes,&h)||h.endpoint!=e->endpoint||h.payload_bytes!=e->bytes||e->bytes<4||e->event!=word(h.payload))return QCA_SELECT_WIRE;
 if((e->event&0xffffff)!=0x7001)return QCA_SELECT_OTHER;
 QcaBssContext p={0};p.expected_epoch=p.observed_epoch=c->epoch;p.completion=e->completion;p.start_floor=c->rx_floor;p.live_frequency=c->live_frequency;p.native_rates=c->native_rates;p.ssid_bytes=10;
 static const uint8_t ssid[10]={'i','P','h','o','n','e',' ','(','9',')'};for(unsigned j=0;j<10;j++)p.ssid[j]=ssid[j];for(unsigned j=0;j<32;j++)p.policy_digest[j]=c->policy_digest[j];p.frequency_count=c->frequency_count;for(unsigned j=0;j<c->frequency_count;j++)p.frequencies[j]=c->frequencies[j];
 QcaSelectedBss v={0};int rc=qca_bss_security(h.payload,h.payload_bytes,&p,&v.security);if(rc==QCA_BSS_NOT_TARGET)return QCA_SELECT_OTHER;if(rc!=QCA_BSS_CANDIDATE)return QCA_SELECT_SECURITY;
 /* Parser already validated every TLV bound. This stage is beacon-only;
  * probe responses remain owned caller diagnostics, not hidden evidence. */
 const uint8_t*frame=0;for(unsigned at=4;at<h.payload_bytes;){unsigned len=h.payload[at]|((unsigned)h.payload[at+1]<<8),tag=h.payload[at+2]|((unsigned)h.payload[at+3]<<8);if(tag==17)frame=h.payload+at+4;at+=4+len;}if(!frame||(frame[0]&0xfc)!=0x80)return QCA_SELECT_SECURITY;
 /* Conservative WPA2 profile: mixed advertisements are retained by caller,
  * never silently downgraded to a weaker or different offered suite. */
 if(v.security.pairwise_count!=1||v.security.akm_count!=1||v.security.pairwise_suites[0]!=0x000fac04||v.security.akm_suites[0]!=0x000fac02||v.security.group_suite!=0x000fac04||v.security.rsnx_bytes||v.security.beacon.snr>INT32_MAX)return QCA_SELECT_SECURITY;
 unsigned slot=8;for(unsigned j=0;j<8;j++)if(s->entries[j].present&&eq(s->entries[j].security.beacon.bss.bssid,v.security.beacon.bss.bssid,6)){slot=j;break;}
 if(slot==8)for(unsigned j=0;j<8;j++)if(!s->entries[j].present||c->now_us-s->entries[j].observed_us>c->ttl_us){slot=j;break;}
 if(slot==8)return QCA_SELECT_FULL;
 v.owned=*e;v.observed_us=observed;v.snr=v.security.beacon.snr;v.estimated_signal_dbm=(int64_t)v.snr-95;v.present=1;s->entries[slot]=v;s->watermark=e->completion;s->last_observed_us=observed;return QCA_SELECT_ACCEPTED;
}
static int better(const QcaSelectedBss*a,const QcaSelectedBss*b){if(a->snr!=b->snr)return a->snr>b->snr;if(a->observed_us!=b->observed_us)return a->observed_us>b->observed_us;for(unsigned j=0;j<6;j++){unsigned x=a->security.beacon.bss.bssid[j],y=b->security.beacon.bss.bssid[j];if(x!=y)return x<y;}return 0;}
int qca_selection_best(const QcaBssSelection*s,const QcaSelectionContext*c,QcaSelectedBss*out){
 if(!s||!c||!out||overlaps(out,sizeof(*out),s,sizeof(*s))||overlaps(out,sizeof(*out),c,sizeof(*c))||!bound(s,c))return 0;
 const QcaSelectedBss*best=0;for(unsigned j=0;j<8;j++){const QcaSelectedBss*v=&s->entries[j];if(!v->present||c->now_us<v->observed_us||c->now_us-v->observed_us>c->ttl_us)continue;if(!best||better(v,best))best=v;}if(!best)return 0;*out=*best;return 1;
}
