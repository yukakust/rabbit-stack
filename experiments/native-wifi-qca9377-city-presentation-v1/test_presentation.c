#include "presentation.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
static unsigned calls;
static void poll_network(void*context){CityPresentation*s=context;calls++;assert(s->busy);assert(!city_presentation_close(s));assert(!city_presentation_bind(s,480,270,480,1));}
static void reference(uint32_t*dst,uint32_t*surface,const uint32_t*p,unsigned w,unsigned h,unsigned stride,unsigned format,unsigned mode){
 unsigned sw=mode?800:480,sh=mode?450:270;
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){uint32_t c=p[(uint64_t)y*sh/h*sw+(uint64_t)x*sw/w];if(!format)c=((c&255)<<16)|(c&0xff00)|((c>>16)&255);dst[(size_t)y*stride+x]=c;}
 for(unsigned y=0;y<270;y++)for(unsigned x=0;x<480;x++)surface[y*480+x]=p[(uint64_t)y*sh/h*sw+(uint64_t)x*sw/w];
}
int main(void){static const unsigned sizes[][2]={{480,270},{640,360},{800,450},{1920,1080},{3840,2160}};unsigned checks=0;CityPresentation s={0};
 assert(!city_presentation_bind(&s,479,270,480,1));assert(!city_presentation_bind(&s,480,269,480,1));assert(!city_presentation_bind(&s,3841,270,3841,1));assert(!city_presentation_bind(&s,480,270,479,1));assert(!city_presentation_bind(&s,480,270,480,2));checks+=5;
 uint32_t *p=malloc(800*450*4),*a=malloc(480*270*4),*b=malloc(480*270*4);assert(p&&a&&b);for(unsigned i=0;i<800*450;i++)p[i]=(i*1234567u)&0xffffff;
 for(unsigned size=0;size<5;size++)for(unsigned format=0;format<2;format++)for(unsigned mode=0;mode<2;mode++){
  unsigned w=sizes[size][0],h=sizes[size][1],stride=w+31;size_t bytes=(size_t)h*stride*4;uint32_t*x=malloc(bytes),*y=malloc(bytes);assert(x&&y);memset(x,0xa5,bytes);memset(y,0xa5,bytes);calls=0;
  assert(city_presentation_bind(&s,w,h,stride,format));assert(!city_presentation_draw(&s,x,bytes-1,a,p,mode,poll_network,&s));assert(!city_presentation_draw(&s,x,bytes,a,a,mode,poll_network,&s));assert(!calls);checks+=2;
  reference(x,a,p,w,h,stride,format,mode);assert(city_presentation_draw(&s,y,bytes,b,p,mode,poll_network,&s));assert(!memcmp(x,y,bytes)&&!memcmp(a,b,480*270*4));assert(calls==(h+15)/16);checks+=3;
  assert(city_presentation_close(&s)&&!s.ready);free(x);free(y);
 }
 free(p);free(a);free(b);printf("PASS %u original/cached presentation/alias/service/reentry checks;20 frame cases\n",checks);return 0;
}
