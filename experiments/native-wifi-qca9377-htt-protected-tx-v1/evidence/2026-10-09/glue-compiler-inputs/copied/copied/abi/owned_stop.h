#ifndef RABBIT_OWNED_SCAN_STOP_H
#define RABBIT_OWNED_SCAN_STOP_H
#include "dispatch.h"
#include "scan_stop.h"
typedef struct {
 QcaScanStop stop;QcaStationDispatch *dispatch;
 uint64_t credit_deadline;uint32_t terminal_completion,last_processed;
 unsigned credit_wait,stop_wait;uint8_t fault;
} QcaOwnedScanStop;
/* One exclusive owner: underlying station, dispatcher, prepared STOP and shared
 * ledger. All RX payload handling goes through this wrapper. No raw HTC receive.
 * Caller monotonic milliseconds; bounded durations 1..60000. No MMIO/clock I/O. */
int qca_owned_scan_stop_begin(QcaOwnedScanStop*,QcaStationDispatch*,uint64_t,unsigned,unsigned,unsigned);
int qca_owned_scan_stop_tick(QcaOwnedScanStop*,uint64_t);
int qca_owned_scan_stop_request(QcaOwnedScanStop*,uint64_t);
int qca_owned_scan_stop_prepare(QcaOwnedScanStop*,uint64_t);
int qca_owned_scan_stop_post(QcaOwnedScanStop*,uint64_t);
int qca_owned_scan_stop_complete(QcaOwnedScanStop*,unsigned,uint64_t);
/* Calls owned dispatcher and uses only its successfully accepted matching event.
 * Unmatched stays queued; malformed/duplicate matching event faults and remains
 * owned. No credit application. Genuine natural terminal cancels only unposted
 * STOP reservation; after STOP publication both terminal and TX are required. */
int qca_owned_scan_stop_head(QcaOwnedScanStop*,uint64_t);
void qca_owned_scan_stop_fault(QcaOwnedScanStop*);
#endif
