#include <stddef.h>
#include <stdint.h>
#include "prefix.h"
QcaPrefix*qca_prefix_view(void);void qca_prefix_status(uint8_t[240]);
static uint16_t half(const uint8_t*p){return p[0]|((unsigned)p[1]<<8);}
static void put(uint8_t*p,unsigned v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static void uuid(uint8_t*p,unsigned id){const uint8_t b[16]={0,0,0,0,0,0,0,0x80,0x49,0x46,0x54,0x49,0x42,0x42,0x41,0x52};for(unsigned i=0;i<16;i++)p[i]=b[i];p[0]=(uint8_t)id;}
static size_t error(uint8_t*r,unsigned op,unsigned h,unsigned e){r[0]=1;r[1]=(uint8_t)op;put(r+2,h);r[4]=(uint8_t)e;return 5;}
/* One minimal service29..51 UUID40, status41/value31; raw10pages UUID50..59 values33..51. */
size_t qca_prefix_att(uint16_t mtu,const uint8_t*p,size_t n,uint8_t*r,size_t cap){
 if(!p||!n||!r||cap<247||mtu<23||mtu>247||n>mtu)return 0;
 unsigned op=p[0],h=n>=3?half(p+1):0;
 if(op==2)return SIZE_MAX;
 if(op==6){if(n!=23)return SIZE_MAX;uint8_t id[16];uuid(id,0x40);unsigned mismatch=0;for(unsigned i=0;i<16;i++)mismatch|=id[i]^p[i+7];if(mismatch)return SIZE_MAX;
  if(!h||h>half(p+3))return error(r,op,h,1);
  if(half(p+5)!=0x2800||h>29||half(p+3)<29)return error(r,op,h,0x0a);
  r[0]=7;put(r+1,29);put(r+3,51);return 5;
 }
 if(h<29)return SIZE_MAX;
 if(op==0x10||op==8||op==4){
  if(n!=(op==4?5u:7u))return error(r,op,h,4);
  unsigned end=half(p+3);if(h>end)return error(r,op,h,1);
  if(op==0x10){if(half(p+5)!=0x2800)return error(r,op,h,0x10);if(h>29||end<29)return error(r,op,h,0x0a);
   r[0]=0x11;r[1]=20;put(r+2,29);put(r+4,51);uuid(r+6,0x40);return 22;
  }
  if(op==8){if(half(p+5)!=0x2803)return error(r,op,h,0x0a);unsigned decl=h<=30?30:h<=50?((h+1u)&~1u):0;if(!decl||end<decl)return error(r,op,h,0x0a);
   r[0]=9;r[1]=21;put(r+2,decl);r[4]=2;put(r+5,decl+1);uuid(r+7,decl==30?0x41:0x50+(decl-32)/2);return 23;
  }
  if(h>51)return error(r,op,h,0x0a);
  r[0]=5;put(r+2,h);if(h==29||(h>=30&&!(h&1))){r[1]=1;put(r+4,h==29?0x2800:0x2803);return 6;}
  r[1]=2;uuid(r+4,h==31?0x41:0x50+(h-33)/2);return 20;
 }
 if(op==0x0a||op==0x0c){
  if(n!=(op==0x0a?3u:5u))return error(r,op,h,4);
  unsigned off=op==0x0a?0:half(p+3);unsigned length=h==29?16:h==31?240:h>=33&&h<=51&&(h&1)?(h==51?64:512):0;
  if(!length)return error(r,op,h,h<=51?2:1);
  if(off>length)return error(r,op,h,7);
  unsigned count=length-off;if(count>mtu-1u)count=mtu-1u;r[0]=op==0x0a?0x0b:0x0d;
  if(h>=33){unsigned page=(h-33)/2;if(qca_prefix_raw(qca_prefix_view(),r+1,count,page*512+off)!=count)return error(r,op,h,7);}
  else {uint8_t v[240];if(h==29)uuid(v,0x40);else qca_prefix_status(v);for(unsigned i=0;i<count;i++)r[i+1]=v[off+i];}
  return count+1;
 }
 if(op==0x12)return error(r,op,h,h<=51?3:1);
 if(op&0x40)return 0;
 return error(r,op,h,6);
}
