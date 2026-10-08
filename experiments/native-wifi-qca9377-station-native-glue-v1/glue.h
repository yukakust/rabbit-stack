#ifndef RABBIT_STATION_NATIVE_GLUE_H
#define RABBIT_STATION_NATIVE_GLUE_H
#include "data_path.h"
#include "copied/coordinator.h"
typedef struct {
 QcaHttDataPath*data;StaMgmtTx mgmt;StaJoin*station;
 uint64_t epoch,last;uint16_t next_id,sequence;unsigned fault;QcaRxEvent responses[2],diagnostic[8];unsigned diagnostic_count;
} QsgNative;
/* Source-bound live47 already has START/PEER_CREATE and fresh actual PEER_MAP.
 * Native start/rate/key/cipher policy authority remains outside this coupler. */
int qsg_begin(QsgNative*,QcaHttDataPath*,StaJoin*,const StaWireBss*,uint16_t selected,uint16_t listen,const uint8_t backend_source[32],uint64_t now);
/* Called by the sole persistent owned RX dispatcher. Credit producer stays sole.
 * SEC_IND/PEER events routed here before qdp_receive; never decoded as INORD. */
int qsg_receive(QsgNative*,const QcaRxEvent*,uint64_t now);
int qsg_poll(QsgNative*,uint64_t now);
void qsg_revoke(QsgNative*,unsigned);
/* Pure source-backed unprotected EAPOL bytes; no key installation/ACK authority.
 * Only pre-key EAPOL on an actually associated/mapped station is eligible. */
unsigned qsg_eapol_frame(const StaJoin*,uint64_t,const uint8_t*,unsigned,uint16_t,uint8_t*,unsigned);
#endif
