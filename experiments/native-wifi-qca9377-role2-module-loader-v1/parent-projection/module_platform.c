#include "module_platform.h"
static int range(const void*p,size_t n){return p&&n&&n<=UINTPTR_MAX-(uintptr_t)p;}
static int apart(const void*a,size_t na,const void*b,size_t nb){return range(a,na)&&range(b,nb)&&((uintptr_t)a+na<=(uintptr_t)b||(uintptr_t)b+nb<=(uintptr_t)a);}
static void wipe(void*p,size_t n){volatile unsigned char*q=p;while(n--)*q++=0;}
static void copy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;while(n--)*a++=*b++;}
int module_protected_boot_api(const void*st,RngBootApi*out){
 if(!apart(st,120,out,sizeof *out)||(uintptr_t)st%8||(uintptr_t)out%_Alignof(RngBootApi))return 0;
 uint64_t sig;uint32_t bytes;copy(&sig,st,8);copy(&bytes,(const uint8_t*)st+12,4);
 if(sig!=UINT64_C(0x5453595320494249)||bytes<120||bytes>4096)return 0;
 const void*bs;copy(&bs,(const uint8_t*)st+96,8);
 if(!apart(bs,328,out,sizeof *out)||(uintptr_t)bs%8)return 0;
 copy(&sig,bs,8);copy(&bytes,(const uint8_t*)bs+12,4);
 if(sig!=UINT64_C(0x56524553544f4f42)||bytes<328||bytes>4096)return 0;
 RngBootApi b;copy(&b.allocate,(const uint8_t*)bs+64,8);copy(&b.free_pool,(const uint8_t*)bs+72,8);copy(&b.locate,(const uint8_t*)bs+320,8);
 if(!b.allocate||!b.free_pool||!b.locate)return 0;*out=b;return 1;
}
int module_protected_arena_open(ProtectedArena*s,const RngBootApi*b,uint64_t epoch,size_t bytes){
 if(!apart(s,sizeof *s,b,sizeof *b)||!epoch||bytes<4096||bytes>2097152||bytes%16||s->base||s->epoch||s->users||s->uncertain||!b->allocate||!b->free_pool)return 0;
 s->api=*b;s->epoch=epoch;void*p=0;RngStatus rc=b->allocate(4,bytes,&p);
 if(rc||!range(p,bytes)||(uintptr_t)p%16||!apart(s,sizeof *s,p,bytes)||!apart(b,sizeof *b,p,bytes)){
  /* Returned bad/error pointer is retained as uncertain, never touched/freed. */
  if(p){s->base=p;s->uncertain=1;}return 0;
 }
 s->base=p;s->bytes=bytes;wipe(p,bytes);return 1;
}
int module_protected_arena_borrow(ProtectedArena*s,uint64_t epoch,unsigned user,void**out,size_t*n){
 if(!range(s,sizeof *s)||!apart(s,sizeof *s,out,sizeof *out)||!apart(s,sizeof *s,n,sizeof *n)||!apart(out,sizeof *out,n,sizeof *n)||!s->base||s->uncertain||epoch!=s->epoch||user>2||s->users)return 0;
 if(!apart(s->base,s->bytes,out,sizeof *out)||!apart(s->base,s->bytes,n,sizeof *n))return 0;
 /* Entire arena loan to ONE stage. Shared allocators are not silently composed. */
 s->users=1u<<user;*out=s->base;*n=s->bytes;return 1;
}
int module_protected_arena_return(ProtectedArena*s,uint64_t epoch,unsigned user){
 if(!range(s,sizeof *s)||!s->base||s->uncertain||epoch!=s->epoch||user>2||s->users!=(1u<<user))return 0;
 wipe(s->base,s->bytes);s->users=0;return 1;
}
int module_protected_arena_close(ProtectedArena*s,uint64_t epoch){
 if(!range(s,sizeof *s)||epoch!=s->epoch||s->users||s->uncertain)return 0;
 if(!s->base)return 1;
 wipe(s->base,s->bytes);if(s->api.free_pool(s->base)){s->uncertain=1;return 0;}
 s->base=0;s->bytes=0;return 1;
}
int module_protected_rng_inventory(RngSession*s,const RngBootApi*b,uint64_t epoch,const uint8_t code[32],RngPublicDiagnostic*out){
 if(!apart(s,sizeof *s,out,sizeof *out)||!apart(b,sizeof *b,out,sizeof *out)||!apart(code,32,out,sizeof *out)||!apart(code,32,s,sizeof *s)||!apart(code,32,b,sizeof *b))return 0;
 int rc=rng_discover(s,b,epoch);rng_diagnostic(s,code,out);return rc;
}
