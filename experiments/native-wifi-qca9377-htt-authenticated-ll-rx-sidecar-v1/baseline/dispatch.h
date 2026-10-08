#ifndef RABBIT_QCA_STATION_DISPATCH_H
#define RABBIT_QCA_STATION_DISPATCH_H
#include "rx.h"
#include "station_scan.h"
enum {QCA_DISPATCH_EMPTY=0,QCA_DISPATCH_SCAN=1,QCA_DISPATCH_UNMATCHED=2,QCA_DISPATCH_MALFORMED=-1,QCA_DISPATCH_SEQUENCE=-2};
typedef struct {QcaStationScan *station;uint32_t last_completion,scan,request;uint8_t endpoint,vdev,head,count;QcaRxEvent owned[2];} QcaStationDispatch;
/* Takes only owned payload events from the reviewed RX pump. Pump has already
 * consumed HTC trailers exactly once. No credit ledger mutation here.
 * Borrow current pending station; fixed VDEV0 profile. Serialize all TX/dispatch.
 * Completion IDs increase strictly but may have gaps from credit-only RX. */
int qca_station_dispatch_begin(QcaStationDispatch*,QcaStationScan*,unsigned);
/* Copy into bounded owned FIFO. 1 accepted; 0 backpressure; -1 bad/replayed input.
 * On 0/-1 caller still owns event and MUST retain it; never take+drop pump data. */
int qca_station_dispatch_offer(QcaStationDispatch*,const QcaRxEvent*);
/* Scan handler consumes only fully validated matching events. Foreign/unknown
 * WMI and HTC control stay owned UNMATCHED; malformed/duplicate/early-invalid
 * head stays owned with explicit error. No fabricated CREATE ACK or acceptance.
 * Uses real pending command state, including exact TX completion ordering. */
int qca_station_dispatch_head(QcaStationDispatch*);
/* Explicit transfer of FIFO head to another owner/router (also malformed data).
 * Never a discard operation; output must be retained by the receiving owner. */
int qca_station_dispatch_take(QcaStationDispatch*,uint32_t,QcaRxEvent*,unsigned);
#endif
