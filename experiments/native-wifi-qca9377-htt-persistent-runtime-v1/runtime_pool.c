#include "runtime_pool.h"
static void*copy(void*out,const void*in,size_t n){uint8_t*d=out;const uint8_t*s=in;for(size_t i=0;i<n;i++)d[i]=s[i];return out;}
static QcaHttPool*holder;
static int range(const void*p,size_t n){return p&&n&&(uintptr_t)p<=UINTPTR_MAX-n;}
static int overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x<y?y-x<n:x-y<m;}
static void wipe(void*p,size_t n){volatile uint8_t*b=p;while(n--)*b++=0;}
int qca_htt_pool_acquire(QcaHttPool*s,const QcaHttPoolBoot*b,uint64_t epoch){
 if(!range(s,sizeof(*s))||!range(b,sizeof(*b))||(uintptr_t)s%_Alignof(QcaHttPool)||overlap(s,sizeof(*s),b,sizeof(*b))||holder||!epoch||s->raw||s->runtime||s->uncertain||!(s->phase==HTT_POOL_EMPTY||s->phase==HTT_POOL_RELEASED)||!b->allocate||!b->release)return 0;
 s->boot=*b;s->epoch=epoch;s->bytes=sizeof(QcaHttRuntime)+_Alignof(QcaHttRuntime)-1;s->free_attempted=s->wiped=s->bound=0;holder=s;void*raw=0;s->status=s->boot.allocate(2,s->bytes,&raw);s->raw=raw;
 if(s->status){s->phase=raw?HTT_POOL_UNCERTAIN:HTT_POOL_FAILED;s->uncertain=raw!=0;s->error=1;if(!raw)holder=0;return 0;}
 if(!range(raw,s->bytes)||overlap(raw,s->bytes,s,sizeof(*s))||overlap(raw,s->bytes,b,sizeof(*b))){s->phase=raw?HTT_POOL_UNCERTAIN:HTT_POOL_FAILED;s->uncertain=raw!=0;s->error=2;if(!raw)holder=0;return 0;}
 uintptr_t aligned=((uintptr_t)raw+_Alignof(QcaHttRuntime)-1)&~(uintptr_t)(_Alignof(QcaHttRuntime)-1);s->runtime=(QcaHttRuntime*)aligned;wipe(raw,s->bytes);s->phase=HTT_POOL_OWNED;return 1;
}
int qca_htt_pool_attach(QcaHttPool*s,QcaUefiPort*p,QcaDmaBuffer ce[14],QcaDmaStop stop,void*context){if(!s||holder!=s||s->phase!=HTT_POOL_OWNED||s->bound||s->uncertain||!s->runtime)return 0;int rc=qca_htt_runtime_begin(s->runtime,p,ce,s->epoch,stop,context);if(s->runtime->phase)s->bound=1;return rc;}
int qca_htt_pool_release(QcaHttPool*s){
 if(!s)return 0;
 if(s->phase==HTT_POOL_RELEASED&&!s->raw&&!s->runtime)return 1;
 if(holder!=s||s->phase!=HTT_POOL_OWNED||s->uncertain||s->free_attempted||!range(s->raw,s->bytes)||!s->runtime||s->bytes!=sizeof(QcaHttRuntime)+_Alignof(QcaHttRuntime)-1||!s->boot.release)return 0;
 uintptr_t aligned=((uintptr_t)s->raw+_Alignof(QcaHttRuntime)-1)&~(uintptr_t)(_Alignof(QcaHttRuntime)-1);
 if((uintptr_t)s->runtime!=aligned)return 0;
 if(s->bound&&!qca_htt_runtime_detachable(s->runtime))return 0;
 s->bound=0;wipe(s->raw,s->bytes);s->wiped=1;s->free_attempted=1;s->status=s->boot.release(s->raw);
 if(s->status){s->phase=HTT_POOL_FREE_RETAINED;s->uncertain=1;s->error=3;return 0;}
 s->raw=0;s->runtime=0;s->bytes=0;s->phase=HTT_POOL_RELEASED;holder=0;return 1;
}
int qca_htt_pool_boot(const void*st,QcaHttPoolBoot*out){
 if(!range(st,120)||!range(out,sizeof(*out))||(uintptr_t)st%8||overlap(st,120,out,sizeof(*out)))return 0;
 uint64_t signature;uint32_t n;copy(&signature,st,8);copy(&n,(const uint8_t*)st+12,4);if(signature!=UINT64_C(0x5453595320494249)||n<120||n>4096)return 0;
 const void*bs;copy(&bs,(const uint8_t*)st+96,8);if(!range(bs,80)||(uintptr_t)bs%8||overlap(bs,80,out,sizeof(*out)))return 0;
 copy(&signature,bs,8);copy(&n,(const uint8_t*)bs+12,4);if(signature!=UINT64_C(0x56524553544f4f42)||n<80||n>4096)return 0;
 QcaHttPoolBoot b;copy(&b.allocate,(const uint8_t*)bs+64,8);copy(&b.release,(const uint8_t*)bs+72,8);if(!b.allocate||!b.release)return 0;*out=b;return 1;
}
