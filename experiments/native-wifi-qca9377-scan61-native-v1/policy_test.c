#include "scan_policy.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned u32(const uint8_t*p){return p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24);}
int main(void){
 QcaChannelHardware h={.regdomain=108,.low2=2312,.high2=2732,.low5=4920,.high5=6100};memcpy(h.target,scan_policy.target,32);
 QcaReviewedChannelPolicy p=scan_policy;uint8_t out[1808];unsigned checks=0;
 assert(qca_scan_channels_wire(out,sizeof out,&p,&h,1792)==380&&u32(out+8)==13);checks++;
 for(unsigned j=0;j<13;j++){const uint8_t*c=out+16+28*j;assert(u32(c+4)==2412+5*j&&u32(c+8)==2412+5*j&&!u32(c+12)&&u32(c+16)==129&&u32(c+20)==((40u<<8)|(40u<<16)));checks++;}
 assert(qca_pdev_regdomain_wire(out,sizeof out,&p,&h,1792)==32&&u32(out+12)==108&&u32(out+16)==108&&u32(out+20)==108);checks++;
 for(unsigned j=0;j<13;j++)for(unsigned fault=0;fault<7;fault++){
  QcaReviewedChannelPolicy bad=p;QcaPolicyChannel*c=&bad.channels[j];
  if(fault==0)c->passive=0;else if(fault==1)c->width=40;else if(fault==2)c->centre2=2412;else if(fault==3)c->flags=QCA_POLICY_DISABLED;else if(fault==4)c->mode=0;else if(fault==5)c->frequency=3500;else c->max_power_dbm=c->max_reg_power_dbm+1;
  memset(out,0xa5,sizeof out);assert(!qca_scan_channels_wire(out,sizeof out,&bad,&h,1792)&&!qca_pdev_regdomain_wire(out,sizeof out,&bad,&h,1792));for(unsigned k=0;k<sizeof out;k++)assert(out[k]==0xa5);checks+=3;
 }
 for(unsigned fault=0;fault<5;fault++){
  QcaChannelHardware bad=h;if(fault==0)bad.target[0]^=1;else if(fault==1)bad.regdomain=109;else if(fault==2)bad.low2=2500;else if(fault==3)bad.high2=2412;else bad.low5=0;
  assert(!qca_scan_channels_wire(out,sizeof out,&p,&bad,1792)&&!qca_pdev_regdomain_wire(out,sizeof out,&p,&bad,1792));checks++;
 }
 printf("EXACT GE WORLD108 PASSIVE13 NO ACTIVE/40MHz/OTHERBAND/OWNER POLICY checks=%u PASS\n",checks);return 0;
}
