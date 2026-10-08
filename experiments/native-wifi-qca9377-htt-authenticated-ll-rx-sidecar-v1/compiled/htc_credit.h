#ifndef RABBIT_QCA_HTC_CREDIT_H
#define RABBIT_QCA_HTC_CREDIT_H
#include "htc_wire.h"
typedef struct {
 uint16_t total,size,available,reserved,outstanding,max_bytes;
 uint8_t endpoint;
 uint32_t serial,ticket;
} QcaHtcCredit;
/* Zero initialized, single-threaded owner. WMI only; HTT negotiated without
 * credit flow is a separate transport. max_bytes is HTC payload length. */
int qca_htc_credit_begin(QcaHtcCredit*,const QcaHtcReady*,const QcaHtcConnection*);
/* Reserve a single frame INCLUDING its eight-byte HTC header. No DMA here.
 * Commit BEFORE exposing the descriptor; cancel only while still unposted.
 * A DMA completion/error never refunds committed credits. Unknown outcome
 * retains ownership until an actual hardware stop, outside this ledger. */
int qca_htc_credit_reserve(QcaHtcCredit*,unsigned,uint32_t*);
int qca_htc_credit_cancel(QcaHtcCredit*,uint32_t);
int qca_htc_credit_commit(QcaHtcCredit*,uint32_t);
/* Caller consumes each validated RX completion once. Firmware reports are
 * incremental, not totals. Reject excess or credits for other endpoints.
 * No state is published on any rejection. No allocations or hardware I/O. */
int qca_htc_credit_receive(QcaHtcCredit*,const QcaHtcFrame*);
#endif
