#include "city_arena.h"
static int range(const void *p,size_t n){return p&&n<=UINTPTR_MAX-(uintptr_t)p;}
static int apart(const void *a,size_t n,const void *b,size_t m){return range(a,n)&&range(b,m)&&((uintptr_t)a+n<=(uintptr_t)b||(uintptr_t)b+m<=(uintptr_t)a);}
static void wipe(void *p,size_t n){volatile uint8_t *q=p;for(size_t i=0;i<n;i++)q[i]=0;}
int city_arena_open(CityArena *s,CityAllocate allocate,CityFree release,uint64_t epoch){
 if(!s||!allocate||!release||!epoch||s->raw||s->epoch||s->uncertain||s->free_attempted)return 0;
 s->epoch=epoch;s->release=release;s->bytes=CITY_ARENA_BYTES+15;void *raw=0;uint64_t result=allocate(4,s->bytes,&raw);s->raw=raw;
 if(result||!range(raw,s->bytes)||!apart(raw,s->bytes,s,sizeof(*s))){if(raw)s->uncertain=1;return 0;}
 uintptr_t aligned=((uintptr_t)raw+15)&~(uintptr_t)15;s->depth=(uint32_t*)aligned;s->picture=s->depth+CITY_DEPTH_WORDS;
 wipe(raw,s->bytes);return 1;
}
int city_arena_attach(CityArena *s,uint64_t epoch,uint32_t **depth,uint32_t **picture){
 if(!s||!s->raw||!s->depth||s->uncertain||epoch!=s->epoch||s->depth_slot||s->picture_slot||s->readers||!apart(depth,sizeof(*depth),picture,sizeof(*picture))||!apart(depth,sizeof(*depth),s,sizeof(*s))||!apart(picture,sizeof(*picture),s,sizeof(*s))||!apart(depth,sizeof(*depth),s->raw,s->bytes)||!apart(picture,sizeof(*picture),s->raw,s->bytes)||*depth||*picture)return 0;
 s->depth_slot=depth;s->picture_slot=picture;*depth=s->depth;*picture=s->picture;return 1;
}
static int bound(CityArena *s,uint64_t epoch){return s&&s->raw&&!s->uncertain&&epoch==s->epoch&&s->depth_slot&&s->picture_slot&&*s->depth_slot==s->depth&&*s->picture_slot==s->picture;}
int city_arena_enter(CityArena *s,uint64_t epoch){if(!bound(s,epoch)||s->readers)return 0;s->readers=1;return 1;}
int city_arena_leave(CityArena *s,uint64_t epoch){if(!bound(s,epoch)||s->readers!=1)return 0;s->readers=0;return 1;}
int city_arena_detach(CityArena *s,uint64_t epoch){
 if(!bound(s,epoch)||s->readers)return 0;
 *s->depth_slot=0;*s->picture_slot=0;s->depth_slot=s->picture_slot=0;return 1;
}
int city_arena_close(CityArena *s,uint64_t epoch){
 if(!s||epoch!=s->epoch||s->uncertain||s->free_attempted||s->readers||s->depth_slot||s->picture_slot)return 0;
 if(!s->raw)return 1;
 wipe(s->raw,s->bytes);s->free_attempted=1;if(s->release(s->raw)){s->uncertain=1;return 0;}
 s->raw=0;s->depth=s->picture=0;s->bytes=0;return 1;
}
