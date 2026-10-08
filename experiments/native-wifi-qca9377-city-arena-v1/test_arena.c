#include "city_arena.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
static void *allocated;static unsigned mode,allocs,frees;static size_t allocation_bytes;
static uint64_t CITY_EFIAPI allocate(uint32_t type,size_t bytes,void **out){assert(type==4&&bytes==1958415);allocs++;allocation_bytes=bytes;if(mode==1){*out=0;return 9;}allocated=malloc(bytes+16);assert(allocated);memset(allocated,0xa5,bytes+16);*out=(uint8_t*)allocated+1;if(mode==2)return 9;return 0;}
static uint64_t CITY_EFIAPI release(void *ptr){assert(ptr==(uint8_t*)allocated+1);frees++;for(size_t i=0;i<allocation_bytes;i++)assert(((uint8_t*)ptr)[i]==0);if(mode==3)return 9;free(allocated);allocated=0;return 0;}
int main(void){unsigned checks=0;CityArena s={0};uint32_t *depth=0,*picture=0;
 assert(!city_arena_open(&s,allocate,release,0)&&!allocs);checks++;
 assert(city_arena_open(&s,allocate,release,1)&&((uintptr_t)s.depth%16)==0);checks++;
 assert(!city_arena_open(&s,allocate,release,1));checks++;
 assert(!city_arena_attach(&s,2,&depth,&picture)&&!depth&&!picture);checks++;
 assert(!city_arena_attach(&s,1,&depth,&depth));checks++;
 assert(!city_arena_attach(&s,1,(uint32_t**)&s.raw,&picture));checks++;
 assert(city_arena_attach(&s,1,&depth,&picture));checks++;
 assert(!city_arena_close(&s,1)&&!frees);checks++;
 assert(city_arena_enter(&s,1)&&!city_arena_enter(&s,1));checks++;
 depth[0]=123;depth[CITY_DEPTH_WORDS-1]=456;picture[0]=789;picture[CITY_PICTURE_WORDS-1]=999;
 assert(!city_arena_detach(&s,1)&&!city_arena_close(&s,1)&&!city_arena_leave(&s,2));checks++;
 assert(city_arena_leave(&s,1)&&city_arena_detach(&s,1)&&!depth&&!picture);checks++;
 assert(city_arena_close(&s,1)&&frees==1);checks++;
 for(mode=1;mode<=3;mode++){
  CityArena failed={0};unsigned before=frees;
  if(mode!=3){assert(!city_arena_open(&failed,allocate,release,3));if(mode==1)assert(!failed.uncertain&&city_arena_close(&failed,3));else assert(failed.uncertain&&!city_arena_close(&failed,3));assert(frees==before);if(allocated){free(allocated);allocated=0;}}
  else{assert(city_arena_open(&failed,allocate,release,3));assert(!city_arena_close(&failed,3)&&failed.uncertain&&failed.free_attempted);assert(!city_arena_close(&failed,3)&&frees==before+1);free(allocated);allocated=0;}
  checks+=3;
 }
 printf("PASS %u SYNTHETIC CITY ARENA ownership/alias/wipe/uncertainty checks\n",checks);return 0;}
