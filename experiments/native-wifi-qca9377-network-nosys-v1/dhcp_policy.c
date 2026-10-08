/* New Rabbit admission adapter, unmodified lwIP upstream remains below it.
 * RFC2131 4.4.1/4.4.5: REQUESTING selects one server; REBINDING permits others.
 * RFC2132 9.3/9.6/9.7: overload, message type and server identifier encodings.
 */
#include "dhcp_policy.h"
#include "lwip/prot/dhcp.h"
#include <string.h>
struct options {unsigned type_seen,server_seen,overload_seen,type,overload;uint8_t server[4];};
static unsigned be16(const uint8_t*b){return ((unsigned)b[0]<<8)|b[1];}
static int parse(const uint8_t*b,size_t n,struct options*o,int main_options){
 size_t at=0;while(at<n){unsigned tag=b[at++];if(tag==0)continue;if(tag==255)return 0;if(at>=n)return -1;unsigned len=b[at++];if(len>n-at)return -1;
 if(tag==53){if(len!=1||o->type_seen++)return -1;o->type=b[at];}
 if(tag==54){if(len!=4||o->server_seen++)return -1;memcpy(o->server,b+at,4);}
 if(tag==52){if(!main_options||len!=1||o->overload_seen++||b[at]<1||b[at]>3)return -1;o->overload=b[at];}
 at+=len;
 }return -1; /* Missing mandatory END marker: do not reinterpret truncated TLV. */
}
int rabbit_dhcp_ingress_policy(const uint8_t*b,size_t n,unsigned state,const uint8_t selected[4],uint8_t accepted[4]){
 if(accepted)memset(accepted,0,4);
 if(!b||n<14)return -1;if(b[12]==8&&b[13]==6)return n>=42?0:-1;
 if(b[12]!=8||b[13]!=0||n<34||b[14]>>4!=4)return -1;
 const uint8_t*ip=b+14;unsigned ihl=(ip[0]&15)*4,total=be16(ip+2);if(ihl<20||ihl>60||total<ihl||total>n-14||(be16(ip+6)&0x3fff))return -1;
 if(ip[9]!=17)return 0;if(total<ihl+8)return -1;const uint8_t*u=ip+ihl;unsigned ul=be16(u+4);if(ul<8||ul!=total-ihl)return -1;
 if(be16(u)!=67||be16(u+2)!=68)return 0;
 const uint8_t*d=u+8;size_t dn=ul-8;if(dn<240||d[236]!=99||d[237]!=130||d[238]!=83||d[239]!=99)return -1;
 struct options o={0};if(parse(d+240,dn-240,&o,1))return -1;
 if((o.overload&1)&&parse(d+108,128,&o,0))return -1;
 if((o.overload&2)&&parse(d+44,64,&o,0))return -1;
 if(!o.type_seen||o.type<1||o.type>8)return -1;
 if(o.type==5){if(!o.server_seen)return -1;
  if((state==DHCP_STATE_REQUESTING||state==DHCP_STATE_RENEWING)&&(!selected||memcmp(selected,o.server,4)))return -1;
  if(accepted)memcpy(accepted,o.server,4);
 }
 return 0;
}
