#include "city_core.h"
#include "city_arena.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
int original_decode(const uint8_t*,uint32_t,uint32_t,City*);
void original_render(const City*,uint32_t*,uint32_t);
uint32_t **arena_depth_holder(void);
static uint32_t *picture;
static uint64_t CITY_EFIAPI alloc_pool(uint32_t type,size_t n,void **out){assert(type==4);*out=malloc(n);return *out?0:1;}
static uint64_t CITY_EFIAPI free_pool(void *p){free(p);return 0;}
int main(int argc,char **argv){
 assert(argc==2);FILE *f=fopen(argv[1],"rb");assert(f);
 uint8_t bytes[6817];size_t n=fread(bytes,1,sizeof bytes,f);assert(!ferror(f)&&feof(f));fclose(f);
 City a={0},b={0};assert(!original_decode(bytes,n,0,&a)&&!city_decode(bytes,n,0,&b));assert(a.counter==19&&!memcmp(&a,&b,sizeof a));
 CityArena owner={0};assert(city_arena_open(&owner,alloc_pool,free_pool,64));assert(city_arena_attach(&owner,64,arena_depth_holder(),&picture));
 uint32_t *x=malloc(CITY_W*CITY_H*4),*y=malloc(CITY_W*CITY_H*4),*first=malloc(CITY_W*CITY_H*4);assert(x&&y&&first);
 static const unsigned times[]={0,1,50,250,500,999,1000,1500,1999,2000,5000,9999,10000,10001,10500,10999,11000,12000,20000,UINT32_MAX};
 unsigned changed=0;
 for(unsigned j=0;j<sizeof times/sizeof times[0];j++){
  memset(x,0xa5,CITY_W*CITY_H*4);memset(y,0x5a,CITY_W*CITY_H*4);
  original_render(&a,x,times[j]);assert(city_arena_enter(&owner,64));city_render(&b,y,times[j]);assert(city_arena_leave(&owner,64));
  assert(!memcmp(x,y,CITY_W*CITY_H*4));if(!j)memcpy(first,x,CITY_W*CITY_H*4);else changed+=memcmp(first,x,CITY_W*CITY_H*4)!=0;
  /* The legacy buffer stores exactly the same 480x270 words, without rescaling. */
  for(unsigned k=0;k<CITY_PICTURE_WORDS;k++)picture[k]=x[k];assert(!memcmp(picture,x,CITY_PICTURE_WORDS*4));
 }
 assert(changed);assert(city_arena_detach(&owner,64));assert(!*arena_depth_holder()&&!picture);assert(city_arena_close(&owner,64));
 free(x);free(y);free(first);printf("PASS 20 original/arena world19 renderer frames; animation changes %u frames; exact legacy copy\n",changed);return 0;
}
