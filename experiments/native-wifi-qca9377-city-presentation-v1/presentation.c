#include "presentation.h"
static int range(const void*p,size_t n){return p&&n<=UINTPTR_MAX-(uintptr_t)p;}
static int apart(const void*a,size_t n,const void*b,size_t m){return range(a,n)&&range(b,m)&&((uintptr_t)a+n<=(uintptr_t)b||(uintptr_t)b+m<=(uintptr_t)a);}
int city_presentation_bind(CityPresentation*s,unsigned w,unsigned h,unsigned stride,unsigned format){
 if(!s||s->ready||s->busy||w<480||w>3840||h<270||h>2160||stride<w||stride>16384||format>1)return 0;
 s->width=w;s->height=h;s->stride=stride;s->format=format;
 for(unsigned mode=0;mode<2;mode++){
  unsigned source_w=mode?800:480,source_h=mode?450:270;
  for(unsigned x=0;x<w;x++)s->x[mode][x]=(uint64_t)x*source_w/w;
  for(unsigned y=0;y<h;y++)s->y[mode][y]=(uint64_t)y*source_h/h;
 }
 s->ready=1;return 1;
}
int city_presentation_draw(CityPresentation*s,uint32_t*physical,size_t bytes,uint32_t*surface,const uint32_t*picture,unsigned detailed,CityService service,void*context){
 if(!s||!s->ready||s->busy||detailed>1||!surface||!picture)return 0;
 size_t physical_bytes=(size_t)s->stride*s->height*4,picture_bytes=(detailed?800u*450u:480u*270u)*4;
 if(bytes<physical_bytes||!apart(physical,physical_bytes,s,sizeof(*s))||!apart(surface,480u*270u*4,s,sizeof(*s))||!apart(picture,picture_bytes,s,sizeof(*s))||!apart(physical,physical_bytes,surface,480u*270u*4)||!apart(physical,physical_bytes,picture,picture_bytes)||!apart(surface,480u*270u*4,picture,picture_bytes))return 0;
 s->busy=1;unsigned w=detailed?800:480;
 for(unsigned y=0;y<s->height;y++){
  /* Same root callback thread, bounded service opportunity every16 rows.
   * Caller may pump only the owned network receiver, never scene/BLE callbacks. */
  if(!(y&15)&&service)service(context);
  const uint32_t*row=picture+(size_t)s->y[detailed][y]*w;uint32_t*dst=physical+(size_t)y*s->stride;
  for(unsigned x=0;x<s->width;x++){uint32_t c=row[s->x[detailed][x]];if(!s->format)c=((c&255)<<16)|(c&0xff00)|((c>>16)&255);dst[x]=c;}
 }
 for(unsigned y=0;y<270;y++)for(unsigned x=0;x<480;x++)surface[y*480+x]=picture[(size_t)s->y[detailed][y]*w+s->x[detailed][x]];
 s->busy=0;return 1;
}
int city_presentation_close(CityPresentation*s){if(!s||s->busy)return 0;volatile uint8_t*p=(volatile uint8_t*)s;for(size_t i=0;i<sizeof(*s);i++)p[i]=0;return 1;}
