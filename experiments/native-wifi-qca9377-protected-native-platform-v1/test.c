#include "platform.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "oracle-boot.h"
_Static_assert(offsetof(EFI_BOOT_SERVICES,AllocatePool)==64,"actual EDK2 AllocatePool");
_Static_assert(offsetof(EFI_BOOT_SERVICES,FreePool)==72,"actual EDK2 FreePool");
_Static_assert(offsetof(EFI_BOOT_SERVICES,LocateProtocol)==320,"actual EDK2 LocateProtocol");
static _Alignas(16) unsigned char pool[2097152];
static unsigned allocs,frees,rng_calls,locates,infos;
static RngStatus alloc_error,free_error;static int return_bad;
static RngStatus RNG_EFIAPI alloc(uint32_t type,size_t n,void**p){assert(type==4||type==2);assert(n<=sizeof pool);allocs++;*p=return_bad?(void*)(uintptr_t)(UINTPTR_MAX-2):pool;return alloc_error;}
static RngStatus RNG_EFIAPI release(void*p){assert(p==pool);frees++;return free_error;}
static RngStatus RNG_EFIAPI info(RngProtocol*r,size_t*n,RngGuid*p){(void)r;infos++;if(!p){*n=16;return UINT64_C(0x8000000000000005);}assert(*n==16);*p=rng_ctr_guid;*n=16;return 0;}
static RngStatus RNG_EFIAPI random_sample(RngProtocol*r,RngGuid*g,size_t n,uint8_t*p){(void)r;(void)g;(void)n;(void)p;rng_calls++;assert(0&&"inventory must never invoke GetRNG");return 1;}
static RngProtocol provider={info,random_sample};
static RngStatus RNG_EFIAPI locate(RngGuid*g,void*v,void**p){assert(!v&&!memcmp(g,&rng_protocol_guid,16));locates++;*p=&provider;return 0;}
int main(void){
 RngBootApi api={locate,alloc,release};unsigned checks=0;
 _Alignas(8) uint8_t st[120]={0},bs[328]={0};uint64_t sig=UINT64_C(0x5453595320494249);uint32_t len=120;void*bp=bs;
 memcpy(st,&sig,8);memcpy(st+12,&len,4);memcpy(st+96,&bp,8);sig=UINT64_C(0x56524553544f4f42);len=328;
 memcpy(bs,&sig,8);memcpy(bs+12,&len,4);memcpy(bs+64,&api.allocate,8);memcpy(bs+72,&api.free_pool,8);memcpy(bs+320,&api.locate,8);
 RngBootApi decoded={0};assert(protected_boot_api(st,&decoded));assert(decoded.locate==locate&&decoded.allocate==alloc&&decoded.free_pool==release);checks+=2;
 for(unsigned n=0;n<328;n++){len=n;memcpy(bs+12,&len,4);RngBootApi prior=decoded;assert(!protected_boot_api(st,&decoded));assert(!memcmp(&decoded,&prior,sizeof decoded));checks++;}
 len=328;memcpy(bs+12,&len,4);assert(!protected_boot_api(st,(RngBootApi*)st));assert(!protected_boot_api(st,(RngBootApi*)bs));checks+=2;
 for(size_t size=4096;size<=2097152;size*=2){
  ProtectedArena a={0};assert(protected_arena_open(&a,&api,7,size));
  for(unsigned u=0;u<3;u++){
   void*p=0;size_t n=0;assert(protected_arena_borrow(&a,7,u,&p,&n));assert(p==pool&&n==size);
   memset(p,0xa5,n);assert(!protected_arena_borrow(&a,7,u,&p,&n));assert(!protected_arena_close(&a,7));assert(!protected_arena_return(&a,8,u));assert(!protected_arena_return(&a,7,(u+1)%3));
   assert(protected_arena_return(&a,7,u));for(size_t k=0;k<n;k++)assert(pool[k]==0);
   assert(!protected_arena_return(&a,7,u));checks+=8;
  }
  assert(protected_arena_close(&a,7));assert(protected_arena_close(&a,7));checks+=3;
 }
 for(size_t n=0;n<4096;n++){ProtectedArena a={0};unsigned old=allocs;assert(!protected_arena_open(&a,&api,7,n));assert(old==allocs);checks++;}
 ProtectedArena a={0};assert(!protected_arena_open(&a,&api,0,4096));assert(!protected_arena_open(&a,&api,7,2097168));checks+=2;
 for(unsigned k=0;k<sizeof a;k++){
  a=(ProtectedArena){0};assert(protected_arena_open(&a,&api,7,4096));unsigned old=a.users;
  assert(!protected_arena_borrow(&a,7,0,(void**)((char*)&a+k),(size_t*)&a));assert(a.users==old);assert(protected_arena_close(&a,7));checks++;
 }
 a=(ProtectedArena){0};alloc_error=1;unsigned old=frees;assert(!protected_arena_open(&a,&api,7,4096));assert(a.uncertain&&a.base==pool);assert(!protected_arena_close(&a,7)&&frees==old);alloc_error=0;checks+=3;
 a=(ProtectedArena){0};return_bad=1;assert(!protected_arena_open(&a,&api,7,4096));assert(a.uncertain);assert(!protected_arena_close(&a,7));return_bad=0;checks+=3;
 a=(ProtectedArena){0};assert(protected_arena_open(&a,&api,7,4096));free_error=1;assert(!protected_arena_close(&a,7)&&a.base==pool&&a.uncertain);free_error=0;old=frees;assert(!protected_arena_close(&a,7)&&old==frees);checks+=3;
 RngSession r={0};RngPublicDiagnostic d={0};uint8_t code[32]={1};assert(protected_rng_inventory(&r,&api,9,code,&d));assert(rng_calls==0&&locates==1&&infos==2);assert(!r.pool&&d.algorithm_count==1&&!d.owned_pool_count);assert(!memcmp(&d.algorithms[0],&rng_ctr_guid,16));checks+=4;
 printf("PASS %u platform pool/inventory checks; GetRNG calls=%u\n",checks,rng_calls);return 0;
}
