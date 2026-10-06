#include "vdev_wire.h"
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
static int overlap(const void*a,unsigned na,const void*b,unsigned nb){
 uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 if(x>UINTPTR_MAX-na||y>UINTPTR_MAX-nb)return 1;
 return x<y?y-x<na:x-y<nb;
}
unsigned qca_station_create_wire(uint8_t*out,unsigned cap,unsigned id,const uint8_t mac[6]){
 if(!out||!mac||cap<28||id>=4||overlap(out,28,mac,6))return 0;
 unsigned any=0;for(unsigned j=0;j<6;j++)any|=mac[j];if(!any||(mac[0]&1))return 0;
 put(out,20481);put(out+4,20|(86u<<16));put(out+8,id);put(out+12,2);put(out+16,0);
 for(unsigned j=0;j<6;j++)out[20+j]=mac[j];out[26]=out[27]=0;return 28;
}
static unsigned simple(uint8_t*out,unsigned cap,unsigned id,uint32_t cmd,unsigned tag){
 if(!out||cap<12||id>=4||(uintptr_t)out>UINTPTR_MAX-12)return 0;
 put(out,cmd);put(out+4,4|(tag<<16));put(out+8,id);return 12;
}
unsigned qca_station_stop_wire(uint8_t*out,unsigned cap,unsigned id){return simple(out,cap,id,20486,93);}
unsigned qca_station_delete_wire(uint8_t*out,unsigned cap,unsigned id){return simple(out,cap,id,20482,87);}
