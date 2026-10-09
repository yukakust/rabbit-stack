#include "transport.h"
static uint16_t u16(const uint8_t*p){return p[0]|(uint16_t)p[1]<<8;}
static void w16(uint8_t*p,unsigned x){p[0]=x;p[1]=x>>8;}
static int apart(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return a&&b&&n&&m&&n<=UINTPTR_MAX-x&&m<=UINTPTR_MAX-y&&(x+n<=y||y+m<=x);}
static void uuid(uint8_t*p,unsigned suffix){const uint8_t b[16]={33,0,0,0,0,0,0,0x80,0x49,0x46,0x54,0x49,0x42,0x42,0x41,0x52};for(unsigned i=0;i<16;i++)p[i]=b[i];p[0]=suffix;}
static size_t error(uint8_t*r,unsigned op,unsigned h,unsigned code){r[0]=1;r[1]=op;w16(r+2,h);r[4]=code;return 5;}
size_t mt_att(ModuleTransport*s,uint16_t mtu,const uint8_t*p,size_t n,uint8_t*r,size_t cap,uint64_t e,uint64_t us){
 if(!s||mtu<23||mtu>247||!n||n>mtu||cap<247||!apart(s,sizeof *s,p,n)||!apart(s,sizeof *s,r,cap)||!apart(p,n,r,cap)||s->borrowed||s->epoch!=e||s->state==MT_CLOSED)return 0;
 unsigned op=p[0],h=n>=3?u16(p+1):0;
 if(op==2)return SIZE_MAX;
 if(op==6){
  if(n!=23)return SIZE_MAX;uint8_t wanted[16];uuid(wanted,33);unsigned d=0;for(unsigned i=0;i<16;i++)d|=wanted[i]^p[i+7];if(d)return SIZE_MAX;
  if(!h||h>u16(p+3))return error(r,op,h,1);
  if(u16(p+5)!=0x2800||h>20||u16(p+3)<20)return error(r,op,h,0x0a);
  r[0]=7;w16(r+1,20);w16(r+3,26);return 5;
 }
 if(h<20)return SIZE_MAX;
 if(h>26)return SIZE_MAX;
 if(op==0x10||op==8||op==4){
  if(n!=(op==4?5u:7u))return error(r,op,h,4);unsigned end=u16(p+3);if(h>end)return error(r,op,h,1);
  if(op==0x10){if(u16(p+5)!=0x2800||h>20||end<20)return error(r,op,h,0x0a);r[0]=0x11;r[1]=20;w16(r+2,20);w16(r+4,26);uuid(r+6,33);return 22;}
  if(op==8){if(u16(p+5)!=0x2803)return error(r,op,h,0x0a);unsigned decl=h<=21?21:h<=23?23:h<=25?25:0;if(!decl||decl>end)return error(r,op,h,0x0a);r[0]=9;r[1]=21;w16(r+2,decl);r[4]=decl==25?2:8;w16(r+5,decl+1);uuid(r+7,decl==21?34:decl==23?35:36);return 23;}
  r[0]=5;if(h==20||h==21||h==23||h==25){r[1]=1;w16(r+2,h);w16(r+4,h==20?0x2800:0x2803);return 6;}r[1]=2;w16(r+2,h);uuid(r+4,h==22?34:h==24?35:36);return 20;
 }
 if(op==0x0a||op==0x0c){
  if(n!=(op==0x0a?3u:5u))return error(r,op,h,4);unsigned off=op==0x0a?0:u16(p+3);uint8_t value[80];size_t len;
  if(h==20){uuid(value,33);len=16;}else if(h==26){if(mt_status(s,e,value))return error(r,op,h,0x80);len=80;}else return error(r,op,h,2);
  if(off>len)return error(r,op,h,7);size_t bytes=len-off;if(bytes>mtu-1u)bytes=mtu-1u;r[0]=op==0x0a?0x0b:0x0d;for(size_t i=0;i<bytes;i++)r[1+i]=value[off+i];return bytes+1;
 }
 if(op==0x12){if(n<4)return error(r,op,h,4);int rc=h==22?mt_control(s,p+3,n-3,e,us):h==24?mt_data(s,p+3,n-3,e,us):-1;if(rc)return error(r,op,h,h==22||h==24?0x80:3);r[0]=0x13;return 1;}
 if(op&0x40)return 0;return error(r,op,h,6);
}
