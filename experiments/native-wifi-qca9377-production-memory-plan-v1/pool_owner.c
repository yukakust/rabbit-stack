#include "pool_owner.h"
#include "monocypher.h"
#include <string.h>
static QcaPoolOwner*holder;
static int range(const void*p,size_t n){uintptr_t a=(uintptr_t)p;return p&&n&&a<=UINTPTR_MAX-n;}
static int overlap(const void*a,size_t an,const void*b,size_t bn){return (uintptr_t)a<(uintptr_t)b+bn&&(uintptr_t)b<(uintptr_t)a+an;}
int qca_pool_cleanup(QcaPoolOwner*o){
 if(!range(o,sizeof(*o))||(uintptr_t)o%_Alignof(QcaPoolOwner))return 0;
 if(o->phase==POOL_RELEASED&&!o->raw&&!o->port)return 1;
 if(holder!=o||!o->raw||o->uncertain||o->free_attempted||!o->boot.release)return 0;
 if(o->bytes!=sizeof(QcaNoisePort)+_Alignof(QcaNoisePort)-1||!range(o->raw,o->bytes)||overlap(o->raw,o->bytes,o,sizeof(*o))){o->error=9;return 0;}
 if(o->bound){if(!qca_native_detach(o->port)){o->error=7;return 0;}o->bound=0;}
 /* Detach BEFORE metadata/pool wipe, so library never retains freed pointer. */
 crypto_wipe(o->raw,o->bytes);o->wiped=1;o->free_attempted=1;
 o->status=o->boot.release(o->raw);
 if(o->status){o->phase=POOL_FREE_RETAINED;o->uncertain=1;o->error=8;return 0;}
 o->raw=0;o->port=0;o->bytes=0;o->phase=POOL_RELEASED;holder=0;return 1;
}
int qca_pool_acquire(QcaPoolOwner*o,const QcaPoolBoot*b,uint64_t epoch){
 if(!range(o,sizeof(*o))||!range(b,sizeof(*b))||(uintptr_t)o%_Alignof(QcaPoolOwner)||(uintptr_t)b%_Alignof(QcaPoolBoot)||overlap(o,sizeof(*o),b,sizeof(*b)))return 0;
 if(holder||!epoch||o->raw||o->port||o->bound||o->uncertain||!(o->phase==POOL_EMPTY||o->phase==POOL_RELEASED)||!b->allocate||!b->release)return 0;
 o->boot=*b;o->epoch=epoch;o->bytes=sizeof(QcaNoisePort)+_Alignof(QcaNoisePort)-1;o->free_attempted=o->wiped=o->error=0;
 holder=o;void*raw=0;o->status=o->boot.allocate(2,o->bytes,&raw);o->raw=raw;
 if(o->status){o->phase=raw?POOL_UNCERTAIN:POOL_FAILED;o->uncertain=raw!=0;o->error=1;if(!raw)holder=0;return 0;}
 if(!raw){o->phase=POOL_FAILED;o->error=2;holder=0;return 0;}
 if(!range(raw,o->bytes)||overlap(raw,o->bytes,o,sizeof(*o))||overlap(raw,o->bytes,b,sizeof(*b))){o->phase=POOL_UNCERTAIN;o->uncertain=1;o->error=3;return 0;}
 uintptr_t aligned=((uintptr_t)raw+_Alignof(QcaNoisePort)-1)&~(uintptr_t)(_Alignof(QcaNoisePort)-1);
 o->port=(QcaNoisePort*)aligned;o->phase=POOL_OWNED;
 crypto_wipe(raw,o->bytes);
 if(!qca_native_reset(o->port,epoch)||!qca_native_bind(o->port)){o->error=4;return 0;}
 o->bound=1;return 1;
}
