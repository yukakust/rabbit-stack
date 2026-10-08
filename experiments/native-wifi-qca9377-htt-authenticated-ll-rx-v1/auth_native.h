#ifndef QCA_AUTH_NATIVE_CANDIDATE_H
#define QCA_AUTH_NATIVE_CANDIDATE_H
#include "glue_inputs/key_operation.h"
#include "auth_raw.h"
/* Uses the sole live data path's current OWNED pending DMA buffer. No caller
 * packet pointer, installed/authenticated boolean or PN commit is accepted.
 * Key producer dependencies are not frozen yet; this wrapper is UNADMITTED. */
int qauth_native_candidate(QsgNative*,const QsgKeyOp*ptk,const QsgKeyOp*gtk,
                          QpnLedger*,uint64_t now,QauthRawCandidate*);
/* Sole native cooperative RX dispatcher only. Caller retains a canonical-zero
 * output slot; successful bounded publication and PN commit are consecutive,
 * with no callback/poll/refill/release between them. Never opens a port. */
int qauth_native_commit(QsgNative*,const QsgKeyOp*ptk,const QsgKeyOp*gtk,
                       QpnLedger*,uint64_t now,QauthRawCandidate*empty_output);
#endif
