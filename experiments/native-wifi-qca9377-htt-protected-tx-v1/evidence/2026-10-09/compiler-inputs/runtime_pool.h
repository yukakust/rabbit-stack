#ifndef QCA_HTT_RUNTIME_POOL_H
#define QCA_HTT_RUNTIME_POOL_H
#include "dma_runtime.h"
typedef struct {Status(EFIAPI*allocate)(uint32_t,size_t,void**);Status(EFIAPI*release)(void*);} QcaHttPoolBoot;
typedef struct {QcaHttPoolBoot boot;void*raw;QcaHttRuntime*runtime;size_t bytes;uint64_t epoch;Status status;uint32_t phase,error;uint8_t uncertain,free_attempted,wiped,bound;} QcaHttPool;
enum {HTT_POOL_EMPTY,HTT_POOL_OWNED,HTT_POOL_FAILED,HTT_POOL_UNCERTAIN,HTT_POOL_FREE_RETAINED,HTT_POOL_RELEASED};
int qca_htt_pool_acquire(QcaHttPool*,const QcaHttPoolBoot*,uint64_t);
int qca_htt_pool_attach(QcaHttPool*,QcaUefiPort*,QcaDmaBuffer[14],QcaDmaStop,void*);
int qca_htt_pool_release(QcaHttPool*);
/* Exact EDK2 x6464/72 AllocatePool/FreePool offsets; caller proves mapped
 * platform table authenticity/lifetime. Magic checks are not that proof. */
int qca_htt_pool_boot(const void*,QcaHttPoolBoot*);
#endif
