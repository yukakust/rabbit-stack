#include "peer_wire.h"
static void put(uint8_t *p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
unsigned qca_sta_peer_create_wire(uint8_t *out,unsigned cap,unsigned id,const uint8_t bssid[6]){
 uintptr_t a=(uintptr_t)out,b=(uintptr_t)bssid;
 if(!out||!bssid||cap<24||id>=4||a>UINTPTR_MAX-24||b>UINTPTR_MAX-6)return 0;
 if(a<b?b-a<24:a-b<6)return 0;
 unsigned any=0;for(unsigned j=0;j<6;j++)any|=bssid[j];
 if(!any||(bssid[0]&1))return 0;
 put(out,0x6001);put(out+4,16|(97u<<16));put(out+8,id);
 for(unsigned j=0;j<6;j++)out[12+j]=bssid[j];
 out[18]=out[19]=0;put(out+20,0); /* DEFAULT peer, not BSS/TDLS. */
 return 24;
}
