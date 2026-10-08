#ifndef RABBIT_SCAN_COORDINATOR_H
#define RABBIT_SCAN_COORDINATOR_H
#include "tx.h"
#include "channel_wire.h"
#include "owned_stop.h"
#include "beacon_rx.h"
enum {QCA_SC_SETUP=1,QCA_SC_SCANNING,QCA_SC_STOPPING,QCA_SC_ENDED,QCA_SC_FAULT};
typedef struct {QcaRxEvent raw;QcaWmiBeaconRx parsed;uint64_t epoch;} QcaScanObservation;
typedef struct {
 QcaPersistentTx *tx;QcaReviewedChannelPolicy policy;QcaChannelHardware hardware;
 QcaStationScan pending;QcaStationDispatch dispatch;QcaOwnedScanStop stop;
 QcaScanObservation observation;QcaRxEvent orphan;
 uint64_t epoch,last_us;uint32_t phase,error,stage,request,frame_bytes,start_floor,live_frequency;
 uint32_t command_ms,scan_ms,credit_ms,stop_ms;uint8_t projected,stop_begun,has_observation,has_orphan,ssid_seen,ssid_bytes,ssid[32];
} QcaScanCoordinator;
/* HOST-ONLY join, not admitted for RF/native deployment. Sole publisher is tx.
 * Policy must already be independently authenticated/reviewed outside serializer.
 * Uses actual parsed v5 startup READY, not old strict36 constructor. Clock is
 * native microseconds; owned STOP receives ms with rollback checked BEFORE divide.
 * Limits: command1..10000ms; scan/credit/stop1..60000ms. No defaults. */
int qca_scan_coordinator_begin(QcaScanCoordinator*,QcaPersistentTx*,const QcaReviewedChannelPolicy*,const QcaChannelHardware*,unsigned,unsigned,const uint8_t*,unsigned,uint64_t,unsigned,unsigned,unsigned,unsigned);
int qca_scan_coordinator_poll(QcaScanCoordinator*,uint64_t);
int qca_scan_coordinator_stop(QcaScanCoordinator*,uint64_t);
/* Results retain actual payload provenance. Unmatched/orphan transfer is explicit
 * ownership; caller must retain the returned object. Never drop unknown events. */
int qca_scan_coordinator_take_unmatched(QcaScanCoordinator*,QcaRxEvent*);
int qca_scan_coordinator_take_observation(QcaScanCoordinator*,QcaScanObservation*);
#endif
