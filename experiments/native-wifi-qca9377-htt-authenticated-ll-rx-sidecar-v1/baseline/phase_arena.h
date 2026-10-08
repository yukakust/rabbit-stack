#ifndef QCA_PHASE_OWNED_CAPTURE_RUNTIME_H
#define QCA_PHASE_OWNED_CAPTURE_RUNTIME_H
#include "runtime_pool.h"
#include "scan_native.h"
#include "filter_barrier.h"
#include "htt_native.h"
#include "rng_inventory_join.h"
typedef struct {QcaHttRuntime runtime;QcaNativeScan scan;QcaFilterBarrier filter;QcaHttRngInventory rng;} QcaHttPhaseArena;
typedef struct {QcaHttPoolBoot boot;void*raw;QcaHttPhaseArena*arena;size_t bytes;uint64_t epoch;Status status;uint32_t phase,error;uint8_t uncertain,free_attempted,wiped;unsigned capture_readers;} QcaHttPhaseOwner;
int qca_htt_phase_acquire(QcaHttPhaseOwner*,const QcaHttPoolBoot*,uint64_t);
const QcaHttPhaseArena*qca_htt_phase_view(const QcaHttPhaseOwner*);
/* Only explicit retirement/unload after capture consumption. Clears exact
 * TX/query borrowed pointers/current view BEFORE wiping or FreePool. Actual
 * all-owner quiescence plus callback unregister must be proven by native caller. */
int qca_htt_phase_reader_open(QcaHttPhaseOwner*,uint64_t,const QcaHttPhaseArena**);
int qca_htt_phase_reader_close(QcaHttPhaseOwner*,uint64_t,const QcaHttPhaseArena*);
void qca_htt_phase_empty_pipeline(uint8_t out[544],uint32_t planned_generation);
unsigned qca_htt_phase_empty_raw(unsigned page,uint8_t*,unsigned);
int qca_htt_phase_detach(QcaHttPhaseOwner*,QcaHttNative*query);
int qca_htt_phase_release(QcaHttPhaseOwner*);
#endif
