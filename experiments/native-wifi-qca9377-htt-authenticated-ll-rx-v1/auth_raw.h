#ifndef QCA_AUTH_RAW_CANDIDATE_H
#define QCA_AUTH_RAW_CANDIDATE_H
#include "pn.h"
/* Source-derived HW classification and staged PN only. The native official
 * firmware/current local controlled-port bridge is a separate required gate.
 * This API cannot grant plaintext delivery or commit the caller PN ledger. */
typedef struct {
 QpnLedger staged;
 QpnView provenance;
 unsigned frame_bytes,ethernet_bytes;
 uint8_t frame[1748],ethernet[1748];
} QauthRawCandidate;
int qauth_raw_candidate(const QpnLedger*,const QRxInd*,const QRxOwner*,
                        const uint8_t*,unsigned,QauthRawCandidate*);
#endif
