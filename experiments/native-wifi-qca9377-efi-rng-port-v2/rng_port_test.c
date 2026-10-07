#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "rng_port.h"
#include "oracle-rng.h"
#include "oracle-boot.h"
static unsigned mode,calls,allocs,frees,rng_calls,checks,list_bytes=32;
static void *allocated;static size_t allocated_bytes;
static RngProtocol proto;
static RngStatus RNG_EFIAPI locate(RngGuid*g,void*r,void**out){
 assert(!r&&!memcmp(g,&rng_protocol_guid,16));calls++;
 if(mode==1)return UINT64_C(0x800000000000000e);
 *out=mode==2?NULL:mode==17?(void*)(UINTPTR_MAX-8):&proto;return mode==3?1:0;
}
static RngStatus RNG_EFIAPI allocate_pool(uint32_t type,size_t n,void**out){
 assert(type==2&&n&&n<=256&&!allocated);allocs++;
 if(mode==4)return UINT64_C(0x8000000000000009);
 allocated=malloc(n);assert(allocated);allocated_bytes=n;memset(allocated,0xa5,n);*out=allocated;
 return mode==5?UINT64_C(0x8000000000000009):0;
}
static RngStatus RNG_EFIAPI free_pool(void*p){
 assert(p==allocated);for(size_t i=0;i<allocated_bytes;i++)assert(!((uint8_t*)p)[i]);frees++;
 if(mode==6||(mode==15&&rng_calls))return UINT64_C(0x8000000000000002);
 free(p);allocated=0;return 0;
}
static RngStatus RNG_EFIAPI info(RngProtocol*p,size_t*n,RngGuid*g){
 assert(p==&proto);calls++;
 if(!g){*n=list_bytes;return mode==7?0:UINT64_C(0x8000000000000005);}
 assert(*n==list_bytes);
 if(mode==8){*n+=16;return UINT64_C(0x8000000000000005);}
 if(mode==9){*n=15;return 0;}
 for(size_t i=0;i<*n/16;i++)g[i]=i?rng_hmac_guid:rng_ctr_guid;
 if(mode==10&&*n>=32)g[1]=g[0];
 if(mode==11)for(size_t i=0;i<*n/16;i++){memset(g+i,0x55,16);g[i].a+=(uint32_t)i;}
 return mode==12?1:0;
}
static RngStatus RNG_EFIAPI get(RngProtocol*p,RngGuid*g,size_t n,uint8_t*out){
 assert(p==&proto&&g&&!memcmp(g,&rng_ctr_guid,16)&&n&&n<=256&&out==allocated);rng_calls++;
 memset(out,0x6b,n);if(mode==16)g->a^=1;return mode==13?UINT64_C(0x8000000000000007):mode==14?1:0;
}
static void reset(void){
 if(allocated){free(allocated);allocated=0;}
 calls=allocs=frees=rng_calls=0;proto.get_info=info;proto.get_rng=get;list_bytes=32;
}
int main(void){
 assert(sizeof(EFI_TABLE_HEADER)==24&&offsetof(EFI_BOOT_SERVICES,AllocatePool)==64);
 assert(offsetof(EFI_BOOT_SERVICES,FreePool)==72&&offsetof(EFI_BOOT_SERVICES,LocateProtocol)==320);
 assert(sizeof(RngGuid)==sizeof(EFI_GUID)&&sizeof(RngProtocol)==sizeof(EFI_RNG_INTERFACE));
 assert(offsetof(RngProtocol,get_info)==offsetof(EFI_RNG_INTERFACE,GetInfo));
 assert(offsetof(RngProtocol,get_rng)==offsetof(EFI_RNG_INTERFACE,GetRNG));
 EFI_GUID g=EFI_RNG_PROTOCOL_GUID;assert(!memcmp(&g,&rng_protocol_guid,16));
 g=(EFI_GUID)EFI_RNG_ALGORITHM_SP800_90_CTR_256_GUID;assert(!memcmp(&g,&rng_ctr_guid,16));
 g=(EFI_GUID)EFI_RNG_ALGORITHM_SP800_90_HMAC_256_GUID;assert(!memcmp(&g,&rng_hmac_guid,16));
 g=(EFI_GUID)EFI_RNG_ALGORITHM_SP800_90_HASH_256_GUID;assert(!memcmp(&g,&rng_hash_guid,16));
 RngBootApi boot={locate,allocate_pool,free_pool};uint8_t out[256],old[256];
 for(mode=0;mode<=17;mode++){
  reset();RngSession s={0};memset(out,0x3c,sizeof out);memcpy(old,out,sizeof old);
  int ok=rng_discover(&s,&boot,19);
  if(!mode||mode==11||mode==13||mode==14||mode==15||mode==16){assert(ok);assert(!rng_calls);
   RngReview r={.provider=&proto,.epoch=19,.algorithm=rng_ctr_guid,.provider_provenance_sha256={1}};
   int filled=rng_fill(&s,&r,out,112);
   assert(filled==(!mode));if(mode==16)assert(!memcmp(&s.selected,&rng_ctr_guid,16));if(filled){for(unsigned i=0;i<112;i++)assert(out[i]==0x6b);}else assert(!memcmp(out,old,sizeof out));
  }else assert(!ok&&!rng_calls);
  if(mode==5){assert(s.pool_uncertain&&!rng_cleanup(&s));}
  if(mode==6||mode==15){assert(s.pool&&!s.pool_uncertain);unsigned restore=mode;mode=0;assert(rng_cleanup(&s));mode=restore;}
  checks++;
 }
 mode=0;
 for(unsigned n=0;n<=257;n++){
  reset();RngSession s={0};assert(rng_discover(&s,&boot,2));memset(out,0x3c,sizeof out);memcpy(old,out,sizeof old);
  RngReview r={.provider=&proto,.epoch=2,.algorithm=rng_ctr_guid,.provider_provenance_sha256={1}};
  int ok=rng_fill(&s,&r,out,n);assert(ok==(n>=1&&n<=256));
  if(ok){for(unsigned i=0;i<n;i++)assert(out[i]==0x6b);for(unsigned i=n;i<256;i++)assert(out[i]==0x3c);}
  else assert(!memcmp(out,old,256));checks++;
 }
 for(unsigned n=0;n<=272;n++){
  reset();list_bytes=n;RngSession s={0};int ok=rng_discover(&s,&boot,2);
  /* The synthetic list duplicates HMAC from index2, so >32 is rejected. */
  assert(ok==(n==16||n==32));assert(!rng_calls);checks++;
 }
 for(unsigned k=0;k<6;k++){
  reset();RngSession s={0};assert(rng_discover(&s,&boot,2));RngReview r={.provider=&proto,.epoch=2,.algorithm=rng_ctr_guid,.provider_provenance_sha256={1}};
  if(k==0)memset(r.provider_provenance_sha256,0,32);if(k==1)r.epoch=3;if(k==2)r.provider=NULL;
  if(k==3)memset(&r.algorithm,0x55,16);if(k==4)r.algorithm=(RngGuid)EFI_RNG_ALGORITHM_RAW;
  if(k==5)proto.get_rng=0;
  memset(out,0x3c,256);memcpy(old,out,256);assert(!rng_fill(&s,&r,out,32)&&!rng_calls&&!memcmp(out,old,256));checks++;
 }
 reset();RngSession s={0};assert(!rng_discover(&s,&boot,0));checks++;
 proto.get_info=0;assert(!rng_discover(&s,&boot,2)&&!rng_calls);checks++;
 RngPublicDiagnostic pub;uint8_t code[32]={0x22};rng_diagnostic(&s,code,&pub);
 assert(pub.algorithm_count==0&&!memcmp(pub.adapter_code_sha256,code,32));checks++;
 /* No alias guard may write error state, output, or call firmware. */
 for(size_t i=0;i<sizeof(RngSession);i++){
  reset();RngSession q={0};assert(rng_discover(&q,&boot,2));RngSession prior=q;
  RngReview r={.provider=&proto,.epoch=2,.algorithm=rng_ctr_guid,.provider_provenance_sha256={1}};
  unsigned before=calls;
  assert(!rng_fill(&q,&r,(uint8_t*)&q+i,1));
  assert(!rng_calls&&calls==before&&!memcmp(&q,&prior,sizeof q));checks++;
 }
 for(size_t i=0;i<sizeof(RngReview);i++){
  reset();RngSession q={0};assert(rng_discover(&q,&boot,2));RngSession prior=q;
  RngReview r={.provider=&proto,.epoch=2,.algorithm=rng_ctr_guid,.provider_provenance_sha256={1}},oldr=r;
  unsigned before=calls;assert(!rng_fill(&q,&r,(uint8_t*)&r+i,1));
  assert(!rng_calls&&calls==before&&!memcmp(&q,&prior,sizeof q)&&!memcmp(&r,&oldr,sizeof r));checks++;
 }
 for(size_t i=0;i<sizeof(RngSession);i++){
  reset();RngSession q={0},prior=q;
  assert(!rng_discover(&q,(RngBootApi*)((uint8_t*)&q+i),2));
  assert(!calls&&!rng_calls&&!memcmp(&q,&prior,sizeof q));checks++;
  uint8_t hash[32]={0x22};rng_diagnostic(&q,hash,(RngPublicDiagnostic*)((uint8_t*)&q+i));
  assert(!memcmp(&q,&prior,sizeof q));checks++;
 }
 for(unsigned k=0;k<10;k++){
  reset();RngSession q={0};assert(rng_discover(&q,&boot,2));RngSession prior=q;
  RngReview r={.provider=&proto,.epoch=2,.algorithm=rng_ctr_guid,.provider_provenance_sha256={1}},oldr=r;
  memset(out,0x3c,256);unsigned before=calls;
  const uintptr_t bad=UINTPTR_MAX-8;int accepted=0;
  if(k==0)accepted=rng_fill(&q,&r,(uint8_t*)&q+sizeof q-1,2);
  if(k==1)accepted=rng_fill(&q,&r,(uint8_t*)&r+sizeof r-1,2);
  if(k==2)accepted=rng_fill(&q,&r,(uint8_t*)bad,32);
  if(k==3)accepted=rng_fill((RngSession*)bad,&r,out,32);
  if(k==4)accepted=rng_fill(&q,(RngReview*)bad,out,32);
  if(k==5)accepted=rng_fill(&q,(RngReview*)&q.algorithms,out,32);
  if(k==6)accepted=rng_fill(&q,&r,(uint8_t*)&proto,16);
  if(k==7)accepted=rng_discover((RngSession*)bad,&boot,2);
  if(k==8)accepted=rng_discover(&q,(RngBootApi*)bad,2);
  if(k==9)accepted=rng_cleanup((RngSession*)bad);
  assert(!accepted&&!rng_calls&&calls==before&&!memcmp(&q,&prior,sizeof q)&&!memcmp(&r,&oldr,sizeof r));
  for(unsigned i=0;i<256;i++)assert(out[i]==0x3c);checks++;
 }
 for(unsigned k=0;k<5;k++){
  reset();RngSession q={0};assert(rng_discover(&q,&boot,2));RngSession prior=q;
  RngPublicDiagnostic diag,olddiag;memset(&diag,0x33,sizeof diag);olddiag=diag;
  uint8_t hash[32]={0x22};const uintptr_t bad=UINTPTR_MAX-8;
  if(k==0)rng_diagnostic((RngSession*)bad,hash,&diag);
  if(k==1)rng_diagnostic(&q,(uint8_t*)bad,&diag);
  if(k==2)rng_diagnostic(&q,hash,(RngPublicDiagnostic*)bad);
  if(k==3)rng_diagnostic(&q,(uint8_t*)&diag,&diag);
  if(k==4)rng_diagnostic(&q,(uint8_t*)&q.algorithms,&diag);
  assert(!rng_calls&&!memcmp(&diag,&olddiag,sizeof diag)&&!memcmp(&q,&prior,sizeof q));checks++;
 }
 /* Half-open adjacent output/session storage is legal, not a false overlap. */
 {reset();struct {RngSession q;uint8_t out[32];} adjacent={0};
  assert(rng_discover(&adjacent.q,&boot,2));RngReview r={.provider=&proto,.epoch=2,.algorithm=rng_ctr_guid,.provider_provenance_sha256={1}};
  assert(rng_fill(&adjacent.q,&r,adjacent.out,32));for(unsigned i=0;i<32;i++)assert(adjacent.out[i]==0x6b);checks++;
 }
 printf("PASS %u EFI RNG bounded ABI/provider/pool/zeroize host cases; NO ENTROPY QUALITY CLAIM\n",checks);
 reset();return 0;
}
