#ifndef RABBIT_SCAN_STOP_H
#define RABBIT_SCAN_STOP_H
#include "station_scan.h"
enum {QCA_STOP_MONITOR=1,QCA_STOP_REQUESTED,QCA_STOP_RESERVED,QCA_STOP_POSTED,QCA_STOP_WAIT,QCA_STOP_ENDED,QCA_STOP_FAULT};
typedef struct {QcaStationScan*scan;unsigned phase,frame_bytes,tx_complete,terminal_seen;uint32_t ticket;uint64_t last_tick,deadline,stop_deadline;uint8_t frame[32];} QcaScanStop;
/* STOP_ONE only. Exact pinned Linux union semantics: raw scan_id also appears
 * in ignored vdev_id member, prefixed ID is in scan_id. No broadcast stop. */
unsigned qca_scan_stop_wire(uint8_t*,unsigned,unsigned,unsigned);
/* Pure bounded deadline/cancel coordinator. Borrow exclusively the station
 * coordinator and its credit ledger; dispatch ALL RX through this wrapper.
 * Durations are caller monotonic milliseconds; no clock or MMIO here. */
int qca_scan_stop_begin(QcaScanStop*,QcaStationScan*,uint64_t,unsigned);
int qca_scan_stop_tick(QcaScanStop*,uint64_t);
int qca_scan_stop_request(QcaScanStop*);
int qca_scan_stop_prepare(QcaScanStop*);
int qca_scan_stop_post(QcaScanStop*,unsigned);
int qca_scan_stop_complete(QcaScanStop*,unsigned);
int qca_scan_stop_receive(QcaScanStop*,const uint8_t*,unsigned,uint32_t);
int qca_scan_stop_cancel_unposted(QcaScanStop*);
/* Timeout/publication ambiguity retains committed credits and external owners.
 * ENDED requires actual terminal scan event; after STOP posting also TX complete.
 * Does NOT prove STOP command independently acknowledged or safe DMA teardown. */
void qca_scan_stop_fault(QcaScanStop*);
#endif
