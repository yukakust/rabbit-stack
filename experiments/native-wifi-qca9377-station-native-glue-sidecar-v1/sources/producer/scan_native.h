#ifndef RABBIT_SCAN_NATIVE_PROFILE_H
#define RABBIT_SCAN_NATIVE_PROFILE_H
#include "coordinator.h"
enum {QCA_NATIVE_SCAN_RUNNING=1,QCA_NATIVE_SCAN_STOPPING,QCA_NATIVE_SCAN_QUIESCING,QCA_NATIVE_SCAN_RELEASED,QCA_NATIVE_SCAN_FAULT,QCA_NATIVE_SCAN_LIVE_DONE};
typedef struct {
 QcaPersistentNative*radio;QcaPersistentTx tx;QcaScanCoordinator scan;
 QcaRxEvent archive[16];uint64_t epoch,started,last;
 uint32_t phase,error,archive_count;uint8_t stop_requested,quiesce_requested;
} QcaNativeScan;
int qca_native_scan_begin(QcaNativeScan*,QcaPersistentNative*,uint64_t);
/*1 requests actual checked platform quiesce; NEVER establishes DMA release.*/
int qca_native_scan_poll(QcaNativeScan*,uint64_t);
/* Immutable read-only pages, <=512 bytes each.22 retained slots ×5 pages. */
unsigned qca_native_scan_export(const QcaNativeScan*,unsigned,uint8_t*,unsigned);
#endif
