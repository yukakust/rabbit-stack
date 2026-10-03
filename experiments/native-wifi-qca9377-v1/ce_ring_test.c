#include "ce_ring.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(8) uint8_t memory[256];static unsigned published,mode,stops;
static int publish(void*c,uint32_t index){(void)c;published=index;return mode==1?-1:0;}
static int stop(void*c){(void)c;stops++;return mode==2?-1:0;}
static void init(QcaCeRing*r,unsigned n,int rx){memset(r,0,sizeof(*r));mode=published=stops=0;assert(!qca_ce_init(r,memory,0x100000,n,rx,publish,stop,0));}
int main(void){
 QcaCeRing r={0};uint32_t cookie,n;
 for(unsigned entries=2;entries<=32;entries*=2){
  init(&r,entries,0);assert(!qca_ce_seed(&r,entries-1));
  for(unsigned round=0;round<1000;round++){
   unsigned before=r.write;
   for(unsigned i=0;i<entries-1;i++)assert(!qca_ce_post(&r,0x200000+i*100,100,round+i,0x3fff,0));
   assert(qca_ce_post(&r,0x300000,100,0,0,0)==1);
   assert(qca_ce_seed(&r,0)==-1);
   unsigned hw=r.write;
   for(unsigned i=0;i<entries-1;i++){assert(!qca_ce_complete(&r,hw,&cookie,&n));assert(cookie==round+i&&n==100);}
   assert(qca_ce_complete(&r,hw,&cookie,&n)==1&&r.read==r.write);(void)before;
  }
  assert(!qca_ce_close(&r)&&!r.owned);
 }
 init(&r,4,0);assert(!qca_ce_post(&r,0x10000,20,1,0,1)&&published==0);
 assert(qca_ce_complete(&r,1,&cookie,&n)==-1&&r.fault&&r.owned);assert(!qca_ce_close(&r));
 init(&r,4,0);assert(!qca_ce_post(&r,0x10000,20,1,0,1));assert(!qca_ce_post(&r,0x10100,21,2,0,0)&&published==2);
 assert(!qca_ce_complete(&r,2,&cookie,&n)&&cookie==1);assert(!qca_ce_complete(&r,2,&cookie,&n)&&cookie==2);assert(!qca_ce_close(&r));
 init(&r,4,0);mode=1;assert(qca_ce_post(&r,0x10000,20,3,0,0)==-1&&r.owned&&r.write==1&&r.fault);
 mode=2;assert(qca_ce_close(&r)==-1&&r.owned&&memory[4]==20);mode=0;assert(!qca_ce_close(&r)&&!r.owned&&!memory[4]);
 init(&r,4,1);assert(!qca_ce_post(&r,0x10000,100,4,0,0));memory[4]=50;
 assert(!qca_ce_complete(&r,1,&cookie,&n)&&cookie==4&&n==50);assert(!qca_ce_close(&r));
 for(unsigned corrupt=0;corrupt<4;corrupt++){
  init(&r,4,1);assert(!qca_ce_post(&r,0x10000,100,4,0,0));memory[4]=50;
  if(corrupt==0)memory[4]=0;
  if(corrupt==1)memory[4]=101;
  if(corrupt==2)memory[0]=1;
  if(corrupt==0){assert(qca_ce_complete(&r,1,&cookie,&n)==1&&r.owned&&!r.fault);memory[4]=50;assert(!qca_ce_complete(&r,1,&cookie,&n));}
  else assert(qca_ce_complete(&r,corrupt==3?5:1,&cookie,&n)==-1&&r.owned&&r.fault);
  assert(!qca_ce_close(&r));
 }
 init(&r,4,0);assert(qca_ce_post(&r,UINT32_MAX,2,0,0,0)==-1&&r.write==0);
 assert(qca_ce_post(&r,0x100000000ULL,1,0,0,0)==-1);assert(qca_ce_post(&r,1,65536,0,0,0)==-1);
 assert(qca_ce_post(&r,1,1,0,0x4000,0)==-1);assert(!qca_ce_close(&r));
 for(unsigned i=0;i<35;i++){r=(QcaCeRing){0};int rc=qca_ce_init(&r,memory,0x100000,i,0,publish,stop,0);if(i<2||i>32||(i&(i-1)))assert(rc==-1&&!r.owned);else assert(!rc&&!qca_ce_close(&r));}
 puts("CE ring: 5000 wrap/full cycles, gather publication, 32-bit bounds, hostile RX/index, ambiguous doorbell and failed stop retain ownership PASS; MOCK ONLY");return 0;
}
