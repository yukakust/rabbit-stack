#ifndef RABBIT_QCA_PERSISTENT_NATIVE_H
#define RABBIT_QCA_PERSISTENT_NATIVE_H
#include "startup.h"
#include "lifecycle.h"
#include "rx.h"
typedef struct {
 QcaWmiStartup *startup; QcaRadioLifecycle life; QcaPersistentRx rx;void *htt_owner;
 uint64_t epoch; uint32_t polls,error; uint8_t stop_latched;
} QcaPersistentNative;
/* Actual verified INIT/READY only. No READY fabrication or station commands.
 * Returns1 retained active,0 inactive/releasing/closed,-1 fault retained.
 * Caller retains sole ownership; no other thread may restart CE or PCI. */
int qca_persistent_begin(QcaPersistentNative*,QcaWmiStartup*,uint64_t,uint64_t);
int qca_persistent_poll(QcaPersistentNative*,uint64_t);
/* Locally authenticated stop/unload path only; does not perform cleanup.
 * Caller invokes existing checked adapter cleanup then polls this observer. */
int qca_persistent_quiesce(QcaPersistentNative*,uint64_t);
int qca_persistent_unload_safe(const QcaPersistentNative*);
#endif
