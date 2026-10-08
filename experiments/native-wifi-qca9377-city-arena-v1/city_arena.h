#ifndef RABBIT_CITY_ARENA_H
#define RABBIT_CITY_ARENA_H
#include <stdint.h>
#include <stddef.h>
#define CITY_DEPTH_WORDS (800u*450u)
#define CITY_PICTURE_WORDS (480u*270u)
#define CITY_ARENA_BYTES ((CITY_DEPTH_WORDS+CITY_PICTURE_WORDS)*sizeof(uint32_t))
#define CITY_EFIAPI __attribute__((ms_abi))
typedef uint64_t(CITY_EFIAPI *CityAllocate)(uint32_t,size_t,void**);
typedef uint64_t(CITY_EFIAPI *CityFree)(void*);
typedef struct {void *raw;uint32_t *depth,*picture;uint32_t **depth_slot,**picture_slot;size_t bytes;uint64_t epoch;CityFree release;unsigned readers,uncertain,free_attempted;} CityArena;
int city_arena_open(CityArena*,CityAllocate,CityFree,uint64_t);
int city_arena_attach(CityArena*,uint64_t,uint32_t**,uint32_t**);
int city_arena_enter(CityArena*,uint64_t);
int city_arena_leave(CityArena*,uint64_t);
int city_arena_detach(CityArena*,uint64_t);
int city_arena_close(CityArena*,uint64_t);
#endif
