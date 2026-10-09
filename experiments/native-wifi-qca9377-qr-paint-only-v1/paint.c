#include "paint.h"
static int span(const void*p,size_t n){return p&&n&&n<=UINTPTR_MAX-(uintptr_t)p;}
static int apart(const void*a,size_t n,const void*b,size_t m){return span(a,n)&&span(b,m)&&((uintptr_t)a+n<=(uintptr_t)b||(uintptr_t)b+m<=(uintptr_t)a);}
int qp_live(const PairingPanel*p,uint64_t e,uint64_t us){
 if(!span(p,sizeof *p)||(uintptr_t)p%_Alignof(PairingPanel)||p->ready!=1||!e||e!=p->epoch||!p->created||p->created>UINT64_MAX-600000000||p->expires<=p->created||p->expires>p->created+600000000||us<p->created||us>=p->expires||p->size<21||p->size>41||(p->size-17)%4||p->symbol[0]!=p->size)return 0;
 const char*prefix="RABBIT1:";unsigned at=0;while(*prefix)if(p->text[at++]!=*prefix++)return 0;
 char digits[20];unsigned n=0;uint64_t q=e;do{digits[n++]=(char)('0'+q%10);q/=10;}while(q);while(n)if(p->text[at++]!=digits[--n])return 0;
 if(p->text[at++]!=':')return 0;
 const char*hex="0123456789ABCDEF";unsigned any=0;for(unsigned i=0;i<32;i++){any|=p->spki_sha256[i];if(p->text[at++]!=hex[p->spki_sha256[i]>>4]||p->text[at++]!=hex[p->spki_sha256[i]&15])return 0;}
 return any&&at<sizeof p->text&&!p->text[at];
}
int qp_paint(const PairingPanel*p,uint64_t e,uint64_t us,uint32_t*out,size_t bytes,unsigned w,unsigned h,unsigned stride,unsigned x,unsigned y,unsigned scale){
 if((uintptr_t)out%_Alignof(uint32_t)||!qp_live(p,e,us)||!apart(p,sizeof *p,out,bytes)||!w||!h||w>3840||h>2160||stride<w||stride>3840||!scale||scale>16)return -1;
 size_t pixels=(size_t)(h-1)*stride+w;if(pixels>bytes/sizeof(uint32_t))return -1;
 unsigned side=(p->size+8)*scale;if(x>w||y>h||side>w-x||side>h-y)return -1;
 for(unsigned row=0;row<side;row++)for(unsigned col=0;col<side;col++){
  int qx=(int)(col/scale)-4,qy=(int)(row/scale)-4,dark=0;
  if(qx>=0&&qy>=0&&qx<(int)p->size&&qy<(int)p->size){unsigned index=(unsigned)qy*p->size+(unsigned)qx;dark=(p->symbol[(index>>3)+1]>>(index&7))&1;}
  out[(size_t)(y+row)*stride+x+col]=dark?0:0x00ffffff;
 }
 return 0;
}
