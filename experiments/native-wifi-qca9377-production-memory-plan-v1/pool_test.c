#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "pool_owner.h"
#include "pool_target.h"
#include "oracle-pool.h"
static unsigned checks,mode,offset,allocs,frees;static void*storage,*raw;static size_t bytes;
#define CHECK(x) do{assert(x);checks++;}while(0)
static QcaPoolOwner owner,second;static QcaPoolBoot api;
static RngStatus RNG_EFIAPI alloc(uint32_t t,size_t n,void**out){
 CHECK(t==2&&n==sizeof(QcaNoisePort)+15);allocs++;
 if(mode==1)return UINT64_C(0x8000000000000009);
 if(mode==2){*out=0;return 0;}
 if(mode==3){*out=(void*)(UINTPTR_MAX-3);return 0;}
 if(mode==4){*out=&owner;return 0;}
 storage=malloc(n+32);CHECK(storage);raw=(uint8_t*)storage+offset;bytes=n;memset(raw,0x57,n);*out=raw;
 return mode==5?UINT64_C(0x8000000000000009):0;
}
static RngStatus RNG_EFIAPI release(void*p){
 CHECK(p==raw);frees++;for(size_t j=0;j<bytes;j++)CHECK(!((uint8_t*)p)[j]);
 if(mode==6)return UINT64_C(0x8000000000000002);
 free(storage);storage=0;raw=0;return 0;
}
static void failure_case(unsigned m){
 mode=m;api=(QcaPoolBoot){alloc,release};int ok=qca_pool_acquire(&owner,&api,19);
 if(m==7||m==8){CHECK(ok);static RngSession rng;static RngReview review;static QcaNoisePort wrong;
  rng=(RngSession){.epoch=19,.pool=(void*)(uintptr_t)1,.pool_uncertain=m==8};review=(RngReview){.epoch=19};
  CHECK(qca_native_rng_bind(&rng,&review));CHECK(!qca_native_detach(&wrong));CHECK(!qca_pool_cleanup(&owner));
  CHECK(owner.raw&&owner.bound&&!owner.wiped&&!owner.free_attempted&&!frees&&owner.error==7);
  CHECK(!qca_pool_acquire(&second,&api,20));printf("PASS %u borrowed RNG owner mode%u blocks detach/wipe/free\n",checks,m);return;
 }
 if(m==6){CHECK(ok);CHECK(!qca_pool_cleanup(&owner));CHECK(owner.raw&&owner.uncertain&&owner.wiped&&!owner.bound&&owner.free_attempted&&frees==1);}
 else {CHECK(!ok);if(m==1||m==2)CHECK(!owner.raw&&!owner.uncertain);else CHECK(owner.raw&&owner.uncertain&&!owner.wiped&&!frees);}
 unsigned before=frees;CHECK(!qca_pool_cleanup(&owner)&&frees==before);
 if(owner.raw){CHECK(!qca_pool_acquire(&second,&api,20));CHECK(qca_native_live()==0);NoiseHandshakeState*h=(void*)(uintptr_t)1;CHECK(qca_nk_new(&h,NOISE_ROLE_RESPONDER)==NOISE_ERROR_INVALID_STATE&&!h);}
 /* Unknown/retained ownership is intentionally not released in this process. */
 printf("PASS %u pool failure mode%u retained/not-dereferenced\n",checks,m);
}
int main(int argc,char**argv){
 CHECK(sizeof(EFI_SYSTEM_TABLE)==120&&offsetof(EFI_SYSTEM_TABLE,BootServices)==96);CHECK(offsetof(EFI_BOOT_SERVICES,AllocatePool)==64&&offsetof(EFI_BOOT_SERVICES,FreePool)==72);
 if(argc>1){failure_case((unsigned)strtoul(argv[1],0,10));return 0;}
 api=(QcaPoolBoot){alloc,release};
 for(offset=0;offset<16;offset++){
  owner=(QcaPoolOwner){0};CHECK(qca_pool_acquire(&owner,&api,19));CHECK((uintptr_t)owner.port%16==0);
  NoiseHandshakeState*h=0;CHECK(!qca_nk_new(&h,NOISE_ROLE_RESPONDER));CHECK(!qca_pool_cleanup(&owner)&&owner.raw&&owner.bound&&!owner.wiped&&!owner.free_attempted);
  CHECK(!qca_pool_acquire(&second,&api,20));CHECK(!noise_handshakestate_free(h));h=0;
  CHECK(qca_pool_cleanup(&owner)&&!owner.raw&&!owner.port&&!owner.bound&&owner.wiped&&owner.phase==POOL_RELEASED);
  CHECK(qca_native_live()==0);CHECK(qca_pool_cleanup(&owner));
  NoiseHandshakeState*none=(void*)(uintptr_t)1;CHECK(qca_nk_new(&none,NOISE_ROLE_RESPONDER)==NOISE_ERROR_INVALID_STATE&&!none);
 }
 owner=(QcaPoolOwner){0};QcaPoolOwner old=owner;unsigned before=allocs;
 CHECK(!qca_pool_acquire(&owner,(QcaPoolBoot*)&owner,1)&&allocs==before&&!memcmp(&owner,&old,sizeof(owner)));
 CHECK(!qca_pool_acquire((QcaPoolOwner*)(UINTPTR_MAX-8),&api,1));
 _Alignas(8) uint8_t st[120]={0},bs[376]={0};uint64_t sig=UINT64_C(0x5453595320494249);uint32_t sz=120;memcpy(st,&sig,8);memcpy(st+12,&sz,4);void*p=bs;memcpy(st+96,&p,8);
 sig=UINT64_C(0x56524553544f4f42);sz=376;memcpy(bs,&sig,8);memcpy(bs+12,&sz,4);memcpy(bs+64,&api.allocate,8);memcpy(bs+72,&api.release,8);
 QcaPoolBoot result={0};CHECK(qca_pool_api_from_system(st,&result)&&result.allocate==alloc&&result.release==release);
 CHECK(!qca_pool_api_from_system(st,(QcaPoolBoot*)st));CHECK(!qca_pool_api_from_system(st,(QcaPoolBoot*)(bs+64)));CHECK(!qca_pool_api_from_system((void*)(UINTPTR_MAX-8),&result));
 for(unsigned j=0;j<8;j++){st[j]^=1;CHECK(!qca_pool_api_from_system(st,&result));st[j]^=1;}
 printf("PASS %u aligned genuine-ABI pool owner/wipe/detach/alias model\n",checks);
}
