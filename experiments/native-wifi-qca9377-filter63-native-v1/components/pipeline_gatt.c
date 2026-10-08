#include <stdint.h>
#include <stddef.h>
void qca_filter63_status(uint8_t[448]);
size_t qca_scan_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);
static unsigned u16(const uint8_t*p){return p[0]|((unsigned)p[1]<<8);}
static void put(uint8_t*p,unsigned v){p[0]=v;p[1]=v>>8;}
static void uuid(uint8_t*p,unsigned id){const uint8_t b[16]={0,0,0,0,0,0,0,0x80,0x49,0x46,0x54,0x49,0x42,0x42,0x41,0x52};for(unsigned i=0;i<16;i++)p[i]=b[i];p[0]=id;}
static size_t error(uint8_t*out,unsigned op,unsigned h,unsigned e){out[0]=1;out[1]=op;put(out+2,h);out[4]=e;return 5;}
size_t qca_filter63_att(uint16_t mtu,const uint8_t*p,size_t n,uint8_t*out,size_t cap){
 if(!p||!n||!out||cap<247||mtu<23||mtu>247||n>mtu)return 0;
 unsigned op=p[0],h=n>=3?u16(p+1):0;
 if(op==6&&n==23){uint8_t b[16];uuid(b,0x2e);unsigned diff=0;for(unsigned i=0;i<16;i++)diff|=b[i]^p[7+i];if(!diff){if(!h||h>u16(p+3))return error(out,op,h,1);if(u16(p+5)!=0x2800||h>29||u16(p+3)<29)return error(out,op,h,10);out[0]=7;put(out+1,29);put(out+3,31);return 5;}}
 if(h>=29&&h<=31){
  if(op==0x10||op==8||op==4){if(n!=(op==4?5u:7u))return error(out,op,h,4);if(h>u16(p+3))return error(out,op,h,1);
   if(op==0x10){if(u16(p+5)!=0x2800||h>29||u16(p+3)<29)return error(out,op,h,10);out[0]=0x11;out[1]=20;put(out+2,29);put(out+4,31);uuid(out+6,0x2e);return 22;}
   if(op==8){if(u16(p+5)!=0x2803||h>30||u16(p+3)<30)return error(out,op,h,10);out[0]=9;out[1]=21;put(out+2,30);out[4]=2;put(out+5,31);uuid(out+7,0x2f);return 23;}
   out[0]=5;put(out+2,h);if(h==31){out[1]=2;uuid(out+4,0x2f);return 20;}out[1]=1;put(out+4,h==29?0x2800:0x2803);return 6;
  }
  if(op==0x0a||op==0x0c){if(n!=(op==0x0a?3u:5u))return error(out,op,h,4);if(h!=31)return error(out,op,h,2);unsigned offset=op==0x0c?u16(p+3):0;if(offset>=448)return error(out,op,h,7);uint8_t value[448];qca_filter63_status(value);unsigned length=448-offset;if(length>mtu-1u)length=mtu-1u;out[0]=op==0x0a?0x0b:0x0d;for(unsigned i=0;i<length;i++)out[1+i]=value[offset+i];return length+1;}
  return error(out,op,h,3);
 }
 return qca_scan_att(mtu,p,n,out,cap);
}
