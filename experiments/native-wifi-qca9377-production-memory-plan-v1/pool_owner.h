#ifndef QCA_ARENA_POOL_OWNER_H
#define QCA_ARENA_POOL_OWNER_H
#include "native_port.h"
typedef struct {RngStatus(RNG_EFIAPI*allocate)(uint32_t,size_t,void**);RngStatus(RNG_EFIAPI*release)(void*);} QcaPoolBoot;
typedef struct {
 QcaPoolBoot boot;void*raw;QcaNoisePort*port;size_t bytes;uint64_t epoch;
 RngStatus status;uint32_t phase,error,uncertain,bound,wiped,free_attempted;
} QcaPoolOwner;
enum {POOL_EMPTY,POOL_OWNED,POOL_FAILED,POOL_UNCERTAIN,POOL_FREE_RETAINED,POOL_RELEASED};
/* Caller proves valid mapped/disjoint zero-initialized owner/API and trusted ABI
 * callback provenance/lifetime. Numeric guards do not provide that authority. */
int qca_pool_acquire(QcaPoolOwner*,const QcaPoolBoot*,uint64_t);
int qca_pool_cleanup(QcaPoolOwner*);
#endif
