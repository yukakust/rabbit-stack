#include "phase_arena.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned allocations,frees,rng_calls,info_calls,locates;static RngProtocol provider;
static Status EFIAPI allocate(uint32_t type,size_t n,void**out){assert(type==2||type==4);*out=malloc(n);assert(*out);allocations++;return 0;}
static Status EFIAPI release(void*p){assert(p);free(p);frees++;return 0;}
static RngStatus RNG_EFIAPI get_info(RngProtocol*p,size_t*n,RngGuid*out){assert(p==&provider);info_calls++;if(!out){*n=16;return UINT64_C(0x8000000000000005);}assert(*n>=16);*out=rng_ctr_guid;*n=16;return 0;}
static RngStatus RNG_EFIAPI get_rng(RngProtocol*p,RngGuid*g,size_t n,uint8_t*out){(void)p;(void)g;(void)n;(void)out;rng_calls++;assert(!"GetRNG forbidden in inventory test");return 1;}
static RngStatus RNG_EFIAPI locate(RngGuid*g,void*r,void**out){assert(!r&&!memcmp(g,&rng_protocol_guid,16));locates++;*out=&provider;return 0;}
static void tables(uint8_t st[128],uint8_t bs[344]){memset(st,0,128);memset(bs,0,344);uint64_t a=UINT64_C(0x5453595320494249),b=UINT64_C(0x56524553544f4f42);uint32_t n=120,m=344;memcpy(st,&a,8);memcpy(st+12,&n,4);memcpy(st+96,&bs,8);memcpy(bs,&b,8);memcpy(bs+12,&m,4);RngBootApi api={locate,allocate,release};memcpy(bs+64,&api.allocate,8);memcpy(bs+72,&api.free_pool,8);memcpy(bs+320,&api.locate,8);}
int main(void){QcaHttPhaseOwner owner={0};QcaHttPoolBoot boot={allocate,release};assert(!qca_htt_phase_view(&owner)&&qca_htt_phase_acquire(&owner,&boot,17));QcaHttPhaseArena*a=owner.arena;a->scan.archive_count=1;a->scan.archive[0].raw[0]=0xab;
 uint8_t st[128] __attribute__((aligned(8))),bs[344] __attribute__((aligned(8)));tables(st,bs);provider.get_info=get_info;provider.get_rng=get_rng;uint8_t code[32]={1};assert(qca_htt_public_rng_inventory(&a->rng,st,17,code)&&!rng_calls&&locates==1&&info_calls==2&&a->rng.diagnostic.algorithm_count==1&&!a->rng.entropy_approved);assert(qca_htt_public_rng_cleanup(&a->rng));
 QcaPersistentNative radio={0};QcaHttNative query={0};radio.epoch=17;radio.life.phase=QCA_RADIO_ACTIVE;a->scan.radio=&radio;radio.htt_owner=&query;query.radio=&radio;query.response=&a->scan.archive[13];query.archive=&a->scan.archive[14];assert(!qca_htt_phase_detach(&owner,&query));radio.life.phase=QCA_RADIO_CLOSED;
 const QcaHttPhaseArena*view=0;assert(qca_htt_phase_reader_open(&owner,17,&view)&&view==a);assert(!qca_htt_phase_detach(&owner,&query)&&qca_htt_phase_view(&owner)==a&&a->scan.archive[0].raw[0]==0xab);assert(qca_htt_phase_reader_close(&owner,17,view)&&!qca_htt_phase_reader_close(&owner,17,view));a->rng.session.pool_uncertain=1;assert(!qca_htt_phase_detach(&owner,&query));a->rng.session.pool_uncertain=0;
 assert(qca_htt_phase_detach(&owner,&query)&&!qca_htt_phase_view(&owner)&&!radio.htt_owner&&!query.radio&&!query.response&&!query.archive&&a->scan.archive[0].raw[0]==0xab);assert(qca_htt_phase_release(&owner)&&!owner.raw&&!owner.arena&&allocations==frees&&!rng_calls);
 uint8_t empty[544];qca_htt_phase_empty_pipeline(empty,64);assert(!memcmp(empty,"QF640001",8)&&empty[244]==64&&!empty[8]&&!empty[184]);uint8_t page[512];for(unsigned i=0;i<110;i++)assert(qca_htt_phase_empty_raw(i,page,512)==(i%5==4?56u:512u));assert(!qca_htt_phase_empty_raw(110,page,512));
 printf("PHASE arena=%zu scan=%zu filter=%zu RNGinventory=%zu pool=%zu READER/LIVE/UNCERTAIN guards+detach-beforewipe/publicGetInfo2/GetRNG0 PASS synthetic only\n",sizeof(QcaHttPhaseArena),sizeof(QcaNativeScan),sizeof(QcaFilterBarrier),sizeof(QcaHttRngInventory),sizeof(QcaHttPhaseArena)+_Alignof(QcaHttPhaseArena)-1);return 0;}
