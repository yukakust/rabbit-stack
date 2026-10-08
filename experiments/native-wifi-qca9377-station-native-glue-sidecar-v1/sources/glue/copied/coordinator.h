#ifndef RABBIT_STATION_MGMT_COORDINATOR_H
#define RABBIT_STATION_MGMT_COORDINATOR_H
#include "wire.h"
#include "copied/station.h"
enum {STX_AUTH=1,STX_ASSOC=2,STX_WAIT=3,STX_DONE=4,STX_FAULT=5};
enum {STX_BACKEND_HTT_MGMT3=3,STX_BACKEND_WMI_MGMT=4};
typedef struct {
 StaWireBss bss;StaJoin*station;uint64_t started,last,deadline,epoch;
 uint32_t floor,cookie,tx_status,tx_completion;uint16_t msdu_id,selected,listen,sequence;
 uint8_t phase,step,prepared,posted,dma_closed,status_seen,response_seen,backend;
 uint8_t fault,peer_source[32];StaEvent response;unsigned frame_bytes;uint8_t frame[128];
} StaMgmtTx;
/* A CPU-only proposal/coordinator. Backend source contract must actually prove
 * HTT pkt_type3/ext_tid17 or service-selected WMI mgmt path. No RF admission. */
int stx_begin(StaMgmtTx*,const StaWireBss*,StaJoin*,uint64_t,uint16_t,uint16_t,unsigned,const uint8_t[32]);
unsigned stx_prepare(StaMgmtTx*,uint8_t*,unsigned,uint16_t);
/* Actual publication/ownership acknowledgements supplied by ONE real backend.
 * msdu_id must never be reused by that backend while stale completions exist. */
int stx_posted(StaMgmtTx*,uint32_t,uint16_t,uint32_t,uint64_t);
int stx_dma_closed(StaMgmtTx*,uint32_t,uint64_t);
int stx_status(StaMgmtTx*,uint64_t,uint16_t,uint32_t,uint32_t,uint64_t);
int stx_response(StaMgmtTx*,uint64_t,const QcaRxEvent*,uint32_t,uint16_t,uint64_t);
int stx_poll(StaMgmtTx*,uint64_t);
#endif
