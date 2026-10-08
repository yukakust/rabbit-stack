#ifndef RABBIT_OWNED_CCMP_PN_H
#define RABBIT_OWNED_CCMP_PN_H
#include "copied/rx_decode.h"
#include "copied/station.h"
enum {QPN_COUNTER_ACCEPTED=1,QPN_REJECTED=0,QPN_UNSUPPORTED=-1};
typedef struct {uint8_t attempted,confirmed;uint64_t initial,last[17];uint32_t sec_completion;} QpnKey;
typedef struct {
 uint64_t epoch,last_completion;uint16_t peer_id;uint8_t peer[6],own[6],vdev;
 QcaHttBinding htt;QcaHttVersion version;
 uint8_t pending,index,quarantined;uint32_t pending_floor,ticket;
 QpnKey key[4];unsigned seen_count;uint32_t seen[QRX_MAX];
} QpnLedger;
typedef struct {uint64_t pn,epoch,completion,map_identity;uint32_t paddr;uint16_t peer,sequence;uint8_t index,tid,multicast;unsigned attention;} QpnView;
/* CPU counter/key-provenance slice only. No key bytes, plaintext delivery,
 * firmware PN_VALIDATED input, physical admission or hardware ownership change. */
int qpn_begin(QpnLedger*,uint64_t,uint16_t,uint8_t,const uint8_t[6],const uint8_t[6],const QcaHttBinding*,const QcaHttVersion*);
int qpn_key_posted(QpnLedger*,uint64_t,unsigned,const uint8_t*,unsigned,uint32_t,uint32_t);
int qpn_key_sec(QpnLedger*,uint64_t,const QcaRxEvent*);
int qpn_counter_owned(QpnLedger*,const QRxInd*,const QRxOwner*,const uint8_t*,unsigned,QpnView*);
void qpn_revoke(QpnLedger*,uint64_t);
#endif
