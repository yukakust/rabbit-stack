#ifndef RABBIT_QCA_PERSISTENT_TX_H
#define RABBIT_QCA_PERSISTENT_TX_H
#include "persistent.h"
enum {QCA_TX_IDLE=1,QCA_TX_WAIT_CREDIT,QCA_TX_RESERVED,QCA_TX_POSTED,QCA_TX_DMA_DONE,QCA_TX_CANCELLED,QCA_TX_FAULT,QCA_TX_CLEARED};
typedef struct {
 QcaPersistentNative*radio;const QcaRadioLifecycle*life;QcaHtcCredit*credit;
 uint64_t epoch,last,deadline;uint32_t phase,error,request,serial,ticket,cookie,bytes;
 uint32_t attempted,completed;uint8_t frame[4096];
} QcaPersistentTx;
/* Zero initialize. Sole runtime CE3 publisher; shared RX credit ledger borrowed.
 * No INIT transaction reuse, station constructor or policy/serializer approval.
 * All API calls serialized with radio/RX/stop. Borrowed objects stay retained.
 */
int qca_tx_begin(QcaPersistentTx*,QcaPersistentNative*,uint64_t);
/* Input is an independently validated WMI command body, INCLUDING its4-byte
 * command header, without HTC. Minimal envelope checks are not RF permission.
 * One request only; copies immutable bytes before returning request ID.
 */
int qca_tx_submit(QcaPersistentTx*,const uint8_t*,unsigned,uint64_t,uint64_t,uint32_t*);
/* At most one transition per call.0 waiting,1 actual matching DMA completion,
 * -1 retained fault. Caller services RX separately while waiting for credits.
 * DMA completion never refunds credit or proves a firmware command ACK.
 */
int qca_tx_poll(QcaPersistentTx*,uint64_t);
/* Only WAIT/RESERVED may cancel, never committed/ambiguous publication. */
int qca_tx_cancel(QcaPersistentTx*,uint32_t,uint64_t);
/* Explicitly order next command after matching DONE/CANCELLED request ID. */
int qca_tx_retire(QcaPersistentTx*,uint32_t);
/* Discard only after SAME acquisition's actual all-owner release proof.
 * No credit refund even at reset; a new radio gets a new ledger. */
int qca_tx_clear(QcaPersistentTx*);
#endif
