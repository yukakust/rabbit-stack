#include "channel_wire.h"
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(j*8));}
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);}
static int nonzero(const uint8_t*p){unsigned n=0;for(unsigned j=0;j<32;j++)n|=p[j];return n!=0;}
static int band(uint32_t low,uint32_t high,uint32_t min,uint32_t max){return low>=min&&low<=high&&high<=max;}
static int frequency(uint32_t f){return (f>=2412&&f<=2472&&(f-2412)%5==0)||(f>=5180&&f<=5825&&f%5==0);}
static int valid(const QcaReviewedChannelPolicy*p,const QcaChannelHardware*h){
 if(!p||!h||p->version!=1||!p->count||p->count>64||!nonzero(p->reviewed_digest)||!nonzero(p->ruleset_digest)||!nonzero(p->location_digest)||!nonzero(p->target)||!nonzero(h->target)||h->regdomain>65535||p->hardware_regdomain!=h->regdomain||p->regdomain!=h->regdomain||p->regdomain2!=h->regdomain||p->regdomain5!=h->regdomain||!p->regdomain||p->regdomain>65535||!p->regdomain2||p->regdomain2>65535||!p->regdomain5||p->regdomain5>65535||p->ctl2>65535||p->ctl5>65535||!band(h->low2,h->high2,2300,2800)||!band(h->low5,h->high5,4900,6500))return 0;
 for(unsigned j=0;j<32;j++)if(p->target[j]!=h->target[j])return 0;
 unsigned country=p->alpha2[0]>='A'&&p->alpha2[0]<='Z'&&p->alpha2[1]>='A'&&p->alpha2[1]<='Z';
 if(!country&&!((p->alpha2[0]=='0'&&p->alpha2[1]=='0')||(p->alpha2[0]=='9'&&p->alpha2[1]=='9')))return 0;
 for(unsigned j=0;j<p->count;j++){
  const QcaPolicyChannel*c=&p->channels[j];
  if(!frequency(c->frequency)||c->centre1!=c->frequency||c->centre2||c->width!=20||c->flags&~7u||c->flags&QCA_POLICY_DISABLED||c->passive!=1||c->max_power_dbm>127||c->max_reg_power_dbm>127||c->max_power_dbm>c->max_reg_power_dbm||c->antenna_gain_db>255)return 0;
  if(c->frequency<3000){if(c->frequency<h->low2||c->frequency>h->high2||c->mode!=1||c->flags&QCA_POLICY_RADAR)return 0;}
  else if(c->frequency<h->low5||c->frequency>h->high5||c->mode!=0)return 0;
  for(unsigned k=0;k<j;k++)if(p->channels[k].frequency==c->frequency)return 0;
 }
 return 1;
}
static int output(uint8_t*out,unsigned cap,unsigned bytes,const QcaReviewedChannelPolicy*p,const QcaChannelHardware*h,unsigned limit){return out&&cap>=bytes&&limit>=bytes&&limit<=4088&&!overlap(out,bytes,p,sizeof(*p))&&!overlap(out,bytes,h,sizeof(*h));}
unsigned qca_scan_channels_wire(uint8_t*out,unsigned cap,const QcaReviewedChannelPolicy*p,const QcaChannelHardware*h,unsigned limit){
 if(!valid(p,h))return 0;unsigned n=16+28*p->count;if(!output(out,cap,n,p,h,limit))return 0;
 put(out,0x3003);put(out+4,4|(79u<<16));put(out+8,p->count);put(out+12,28*p->count|(18u<<16));
 for(unsigned j=0;j<p->count;j++){
  const QcaPolicyChannel*c=&p->channels[j];uint8_t*d=out+16+28*j;
  put(d,24|(80u<<16));put(d+4,c->frequency);put(d+8,c->centre1);put(d+12,0);
  put(d+16,c->mode|128u|((c->flags&QCA_POLICY_RADAR)?1024u:0));
  put(d+20,(c->max_power_dbm*2<<8)|(c->max_reg_power_dbm*2<<16));
  put(d+24,c->antenna_gain_db|(c->max_power_dbm*2<<8));
 }return n;
}
unsigned qca_pdev_regdomain_wire(uint8_t*out,unsigned cap,const QcaReviewedChannelPolicy*p,const QcaChannelHardware*h,unsigned limit){
 if(!valid(p,h)||!output(out,cap,32,p,h,limit))return 0;
 put(out,0x4001);put(out+4,24|(81u<<16));put(out+8,0);put(out+12,p->regdomain);put(out+16,p->regdomain2);put(out+20,p->regdomain5);put(out+24,p->ctl2);put(out+28,p->ctl5);return 32;
}
