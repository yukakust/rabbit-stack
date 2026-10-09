#include "panel.h"
static int span(const void*p,size_t n){return p&&n&&n<=UINTPTR_MAX-(uintptr_t)p;}
static int apart(const void*a,size_t n,const void*b,size_t m){return span(a,n)&&span(b,m)&&((uintptr_t)a+n<=(uintptr_t)b||(uintptr_t)b+m<=(uintptr_t)a);}
static void zero(void*p,size_t n){volatile uint8_t*x=p;while(n--)*x++=0;}
void qr_panel_clear(PairingPanel*p){if(p)zero(p,sizeof *p);}
int qr_panel_bind(PairingPanel*p,uint64_t e,const uint8_t pin[32],uint64_t us){
 if((uintptr_t)p%_Alignof(PairingPanel)||!apart(p,sizeof *p,pin,32)||!e||!us||us>UINT64_MAX-600000000||p->ready)return -1;
 unsigned any=0;for(unsigned i=0;i<32;i++)any|=pin[i];if(!any)return -1;
 PairingPanel v={0};uint8_t tmp[QR_BUF];unsigned at=0;const char*prefix="RABBIT1:";while(*prefix)v.text[at++]=*prefix++;
 char digits[20];unsigned n=0;uint64_t q=e;do{digits[n++]=(char)('0'+q%10);q/=10;}while(q);while(n)v.text[at++]=digits[--n];v.text[at++]=':';
 const char*hex="0123456789ABCDEF";for(unsigned i=0;i<32;i++){v.spki_sha256[i]=pin[i];v.text[at++]=hex[pin[i]>>4];v.text[at++]=hex[pin[i]&15];}v.text[at]=0;
 if(at>=sizeof v.text||!qrcodegen_encodeText(v.text,tmp,v.symbol,qrcodegen_Ecc_QUARTILE,1,QR_MAX_VERSION,qrcodegen_Mask_AUTO,true)){zero(&v,sizeof v);zero(tmp,sizeof tmp);return -1;}
 v.size=(uint32_t)qrcodegen_getSize(v.symbol);v.epoch=e;v.created=us;v.expires=us+600000000;v.ready=1;*p=v;zero(tmp,sizeof tmp);zero(&v,sizeof v);return 0;
}
int qr_panel_live(const PairingPanel*p,uint64_t e,uint64_t us){return p&&(uintptr_t)p%_Alignof(PairingPanel)==0&&p->ready==1&&e==p->epoch&&us>=p->created&&us<p->expires&&p->size>=21&&p->size<=41&&p->size==(unsigned)qrcodegen_getSize(p->symbol);}
int qr_panel_paint(const PairingPanel*p,uint64_t e,uint64_t us,uint32_t*out,size_t bytes,unsigned w,unsigned h,unsigned stride,unsigned x,unsigned y,unsigned scale){
 if((uintptr_t)out%_Alignof(uint32_t)||!qr_panel_live(p,e,us)||!apart(p,sizeof *p,out,bytes)||!w||!h||w>3840||h>2160||stride<w||stride>3840||!scale||scale>16)return -1;
 size_t pixels=(size_t)(h-1)*stride+w;if(pixels>bytes/sizeof(uint32_t))return -1;
 unsigned side=(p->size+8)*scale;if(x>w||y>h||side>w-x||side>h-y)return -1;
 for(unsigned row=0;row<side;row++)for(unsigned col=0;col<side;col++){
  int qx=(int)(col/scale)-4,qy=(int)(row/scale)-4;int dark=qx>=0&&qy>=0&&qx<(int)p->size&&qy<(int)p->size&&qrcodegen_getModule(p->symbol,qx,qy);
  out[(size_t)(y+row)*stride+x+col]=dark?0:0x00ffffff;
 }
 return 0;
}
