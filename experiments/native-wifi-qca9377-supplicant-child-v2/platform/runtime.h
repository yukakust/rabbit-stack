#ifndef RABBIT_SUPPLICANT_RUNTIME_H
#define RABBIT_SUPPLICANT_RUNTIME_H
#include <stdint.h>
#include <stddef.h>
typedef void (*RsnTimerHandler)(void*,void*);
typedef struct {size_t offset,bytes,capacity;uint8_t used;} RsnAllocation;
typedef struct {uint64_t deadline,order,epoch;RsnTimerHandler handler;void*eloop;void*user;uint8_t used;} RsnTimer;
typedef struct {
 void*ctx;uint64_t epoch;uint8_t source_sha256[32];
 int(*monotonic_us)(void*,uint64_t*);int(*wall_us)(void*,uint64_t*);
 int(*random)(void*,uint8_t*,size_t);
 void(*revoked)(void*,uint64_t,unsigned);
} RsnProviders;
typedef struct {
 uint8_t*arena;size_t bytes;RsnProviders providers;
 uint64_t last_us,order;unsigned have_time,error,revoked,dispatching,terminate;
 RsnAllocation allocation[128];RsnTimer timers[64];
} RsnRuntime;
/* Caller-owned external arena/providers. Source digest is provenance only,
 * never RNG quality/physical approval. One exclusively owned runtime at a time. */
int rsn_runtime_bind(RsnRuntime*,uint8_t*,size_t,const RsnProviders*);
void rsn_runtime_revoke(RsnRuntime*,unsigned);
int rsn_runtime_poll(RsnRuntime*,uint64_t,unsigned);
int rsn_runtime_healthy(const RsnRuntime*,uint64_t);
/* Unbind only after actual mature objects deinitialized. Revocation preserves
 * arena allocations until frees; wipe-on-release needs no healthy RNG/clock. */
int rsn_runtime_unbind(RsnRuntime*);
#endif
