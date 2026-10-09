#include "transport.h"
#include "sha256.h"
static uint32_t u32(const uint8_t*p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void w32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=v>>(8*i);}
static void w64(uint8_t*p,uint64_t v){w32(p,(uint32_t)v);w32(p+4,(uint32_t)(v>>32));}
static int span(const void*p,size_t n){return p&&n&&n<=UINTPTR_MAX-(uintptr_t)p;}
static int apart(const void*a,size_t n,const void*b,size_t m){return span(a,n)&&span(b,m)&&((uintptr_t)a+n<=(uintptr_t)b||(uintptr_t)b+m<=(uintptr_t)a);}
static void copy(void*d,const void*s,size_t n){uint8_t*x=d;const uint8_t*y=s;while(n--)*x++=*y++;}
static void wipe(void*p,size_t n){volatile uint8_t*x=p;while(n--)*x++=0;}
static int equal(const void*a,const void*b,size_t n){const uint8_t*x=a,*y=b;unsigned d=0;while(n--)d|=*x++^*y++;return !d;}
static int valid(const ModuleTransport*s,uint64_t e){return s&&s->epoch&&s->epoch==e&&s->accept&&!s->borrowed&&s->state!=MT_CLOSED;}
static int reject(ModuleTransport*s,unsigned e){wipe(s->bytes,sizeof s->bytes);s->state=MT_REJECTED;s->error=e;return -1;}
static int tick(ModuleTransport*s,uint64_t us){
 if(!us||us<s->last)return reject(s,1);
 if((s->state==MT_STAGING||s->state==MT_PENDING)&&(us-s->started>=600000000||us-s->progress>=45000000))return reject(s,2);
 s->last=us;return 0;
}
int mt_bind(ModuleTransport*s,uint64_t e,MtAccept f,void*c){
 if(!span(s,sizeof *s)||!e||!f||(c&&!apart(s,sizeof *s,c,1)))return -1;
 for(size_t j=0;j<sizeof *s;j++)if(((uint8_t*)s)[j])return -1;
 s->epoch=e;s->accept=f;s->context=c;return 0;
}
int mt_control(ModuleTransport*s,const uint8_t*p,size_t n,uint64_t e,uint64_t us){
 if(!valid(s,e)||!apart(s,sizeof *s,p,n)||tick(s,us))return -1;
 if(n==45&&p[0]==1){
  uint32_t bytes=u32(p+9);unsigned nz=0;for(unsigned i=0;i<8;i++)nz|=p[1+i];
  if(!nz||bytes<289||bytes>MT_MAX)return -1;
  if(equal(s->session,p+1,8)&&s->state!=MT_IDLE){
   if(s->length!=bytes||!equal(s->digest,p+13,32))return -1;
   return s->state==MT_REJECTED?-1:0; /* Never reset a saved identical session. */
  }
  if(s->state!=MT_IDLE&&s->state!=MT_ACCEPTED&&s->state!=MT_REJECTED)return -1;
  wipe(s->bytes,sizeof s->bytes);copy(s->session,p+1,8);copy(s->digest,p+13,32);s->length=bytes;s->received=0;s->started=s->progress=us;s->state=MT_STAGING;s->error=0;s->result=0;return 0;
 }
 if(n!=9||!equal(s->session,p+1,8))return -1;
 if(p[0]==4){if(s->state==MT_PENDING)return -1;return reject(s,3);}
 if(p[0]!=3)return -1;
 if(s->state==MT_ACCEPTED||s->state==MT_PENDING)return 0;
 if(s->state!=MT_STAGING||s->received!=s->length)return -1;
 uint8_t h[32];rabbit_sha256(h,s->bytes,s->length);int ok=equal(h,s->digest,32);wipe(h,sizeof h);
 if(!ok)return reject(s,4);
 if(!equal(s->bytes,"RABMOD01",8)&&!equal(s->bytes,"RABRSN01",8))return reject(s,5);
 s->state=MT_PENDING;return 0;
}
int mt_data(ModuleTransport*s,const uint8_t*p,size_t n,uint64_t e,uint64_t us){
 if(!valid(s,e)||!apart(s,sizeof *s,p,n)||tick(s,us)||n<14||n>244||p[0]!=2||!equal(s->session,p+1,8)||s->state!=MT_STAGING)return -1;
 uint32_t off=u32(p+9);size_t bytes=n-13;
 if(off>s->received||off>s->length||bytes>s->length-off)return -1;
 if(off<s->received){if(bytes>s->received-off||!equal(s->bytes+off,p+13,bytes))return reject(s,6);return 0;}
 copy(s->bytes+off,p+13,bytes);s->received+=(uint32_t)bytes;s->progress=us;return 0;
}
int mt_poll(ModuleTransport*s,uint64_t e,uint64_t us){
 if(!valid(s,e)||tick(s,us))return -1;
 if(s->state!=MT_PENDING)return 0;
 /* Genuine owner/PE/lifetime acceptance is the callback's sole authority. */
 s->borrowed=1;int r=s->accept(s->context,s->bytes,s->length);s->borrowed=0;s->result=r;
 wipe(s->bytes,sizeof s->bytes);if(r<0)return reject(s,7);s->state=MT_ACCEPTED;return 1;
}
int mt_status(const ModuleTransport*s,uint64_t e,uint8_t out[80]){
 if(!s||s->epoch!=e||s->borrowed||!apart(s,sizeof *s,out,80))return -1;
 wipe(out,80);copy(out,"QMT00001",8);w64(out+8,s->epoch);w32(out+16,s->state);w32(out+20,s->error);w32(out+24,s->length);w32(out+28,s->received);w32(out+32,(uint32_t)s->result);copy(out+40,s->session,8);copy(out+48,s->digest,32);return 0;
}
int mt_close(ModuleTransport*s,uint64_t e){
 if(!valid(s,e))return -1;wipe(s->bytes,sizeof s->bytes);s->state=MT_CLOSED;s->accept=0;s->context=0;return 0;
}
