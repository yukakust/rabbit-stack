#ifndef RABBIT_STATION_JOIN_H
#define RABBIT_STATION_JOIN_H
#include "abi/rx.h"
#include "abi/persistent.h"
enum {STA_AUTH=1,STA_ASSOC=2,STA_DEAUTH=3,STA_PEER_MAP=4,STA_PEER_UNMAP=5,STA_SEC_IND=6};
typedef struct {uint32_t kind,completion,status;uint16_t aid,rates,peer_id;uint8_t vdev,cipher,unicast,peer[6];} StaEvent;
typedef struct {
 uint64_t epoch;uint32_t watermark,rx_floor,pending_floor,pending_cookie;
 uint16_t aid,peer_id;uint8_t peer[6],own_mac[6],vdev,wmi_endpoint,htt_endpoint;
 uint8_t authenticated,associated,mapped,ptk,gtk,gtk_index,core_completed,quarantined,protection;
 uint8_t pending,pending_pairwise,pending_index,attempted_pairwise,attempted_group;
} StaJoin;
/* Typed raw adapters; caller owns actual epoch, negotiated HTT3/TLV op3,
 * current scan/association channel and actual CPU RX completion identity. */
int sta_decode_htt(const QcaRxEvent*,uint8_t,StaEvent*);
int sta_decode_htt_bound(const QcaRxEvent*,const QcaHttBinding*,const QcaHttVersion*,StaEvent*);
int sta_decode_mgmt(const QcaRxEvent*,uint8_t,uint32_t,const uint8_t[6],const uint8_t[6],uint16_t,StaEvent*);
int sta_begin(StaJoin*,uint64_t,uint32_t,uint8_t,const uint8_t[6],const uint8_t[6],uint8_t,uint8_t);
int sta_observe(StaJoin*,uint64_t,const StaEvent*);
int sta_observe_owned(StaJoin*,uint64_t,const QcaRxEvent*,uint32_t,uint16_t,const QcaHttBinding*,const QcaHttVersion*);
/* Called only after sole WMI key request was actually committed. No keys,
 * secret bytes, command nonce or hardware success is invented by this API. */
int sta_key_posted(StaJoin*,uint64_t,uint8_t,uint8_t,uint32_t,uint32_t);
void sta_key_ambiguous(StaJoin*,uint64_t);
/* Actual mature set_state callback is the only caller; no AP-authorized bit. */
int sta_core_state(StaJoin*,uint64_t,unsigned);
int sta_core_protection(StaJoin*,uint64_t,const uint8_t[6],unsigned,unsigned);
int sta_local_eligibility(const StaJoin*,uint64_t);
int sta_local_eligibility_live(const StaJoin*,const QcaPersistentNative*);
#endif
