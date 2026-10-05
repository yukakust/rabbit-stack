#ifndef RABBIT_QCA_WMI_INIT_TRANSACTION_H
#define RABBIT_QCA_WMI_INIT_TRANSACTION_H
#include "init_wire.h"
#include "htc_credit.h"
#include "htc_session.h"
enum {QCA_INIT_RESERVED=1,QCA_INIT_POSTED,QCA_INIT_WAIT_READY,QCA_INIT_RUNNING,QCA_INIT_CANCELLED,QCA_INIT_FAULT};
typedef struct {
 QcaHtcCredit*credit;QcaWmiReadyInfo ready;
 uint32_t ticket,last_completion;unsigned phase,frame_bytes;
 uint8_t ready_seen,tx_complete,frame[548];
} QcaWmiInitTransaction;
/* PURE coordinator, no MMIO/mapping/signing. Exclusive borrowed credit ledger.
 * Resource vector approval and actual retained DMA mapping proof are external.
 * Begin constructs immutable INIT frame and reserves credit; no publication.
 * Rejection preserves state/ledger. All functions return1 success/0 rejection.
 */
int qca_wmi_init_begin(QcaWmiInitTransaction*,QcaHtcCredit*,const QcaHtcSession*,
 const QcaWmiServiceInfo*,const QcaWmiResources*,const uint32_t[44],const QcaWmiHostChunk*,unsigned);
/* Commit BEFORE exposing CE descriptor. Ambiguous hardware publication retains
 * committed credit and all external DMA owners; fault never refunds credit. */
int qca_wmi_init_post(QcaWmiInitTransaction*);
int qca_wmi_init_complete(QcaWmiInitTransaction*,unsigned);
/* Caller numbers actual consumed RX completions once, starting at1. Never derive
 * identity from payload bytes. Monotonic IDs reject repeated API consumption;
 * this is NOT cryptographic replay detection. Early READY waits for TX complete.
 * Current encoder ABI minor53 required. Malformed frames preserve all state.
 */
int qca_wmi_init_receive(QcaWmiInitTransaction*,const uint8_t*,unsigned,uint32_t);
int qca_wmi_init_cancel(QcaWmiInitTransaction*);
void qca_wmi_init_fault(QcaWmiInitTransaction*);
#endif
