#ifndef RABBIT_QCA_FILTER_BARRIER_H
#define RABBIT_QCA_FILTER_BARRIER_H
#include "htc_credit.h"
#include "wmi_boot_info.h"
enum {QCA_FILTER_READY=1,QCA_FILTER_PREPARED,QCA_FILTER_SUBMITTED,QCA_FILTER_POSTED,QCA_FILTER_ORDERED,QCA_FILTER_WAIT_ECHO,QCA_FILTER_PASSED,QCA_FILTER_FAULT,QCA_FILTER_CANCELLED};
enum {QCA_FILTER_CREATE=0,QCA_FILTER_DELETE=1,QCA_FILTER_ECHO=2};
typedef struct {
 QcaHtcCredit*credit;uint64_t epoch,last,deadline;uint32_t phase,error,step,tx_request,last_request,credit_serial,echo_arg,initial_floor,echo_floor,last_rx;
 unsigned frame_bytes,tx_count,tx_completed,echo_seen,raw_bytes;uint32_t raw_completion;uint8_t raw_pipe,raw_endpoint,mac[6];
 uint8_t frame[28],raw[2048];
} QcaFilterBarrier;
/* Raw WMI payload, no HTC. Exact copied upstream TLV layouts; fixed VDEV0 STA. */
unsigned qca_filter_wire(unsigned step,uint8_t*out,unsigned cap,const uint8_t mac[6],uint32_t echo_arg);
int qca_filter_echo_payload(const uint8_t*,unsigned,uint32_t*);
/* Zero state, actual validated READY envelope and exclusive shared WMI credit.
 * Proof of hardware/firmware/owner epoch is caller's obligation, not this codec.
 * BaseMAC is explicitly unsupported by pinned TLV ops and is NOT serialized.
 * Whole three-command diagnostic deadline3s. No allocation/register/radio access. */
int qca_filter_begin(QcaFilterBarrier*,QcaHtcCredit*,const uint8_t*ready,unsigned ready_bytes,uint64_t epoch,uint32_t rx_completed,uint32_t echo_arg,uint64_t now);
int qca_filter_prepare(QcaFilterBarrier*,uint64_t epoch,uint64_t now);
/* BODY-only preparation: qca_tx_submit is the SOLE HTC/credit/CE3 owner.
 * No API below modifies credit state. Bind returned request before polling TX. */
int qca_filter_submitted(QcaFilterBarrier*,uint64_t epoch,uint32_t request,uint64_t now);
/* Observe actual QcaPersistentTx POSTED immediately after its publish poll,
 * before another RX pump: immutable actual HTC frame and currentRX watermark.
 * Do not call this with a guessed/draft transmit frame. */
int qca_filter_post(QcaFilterBarrier*,uint64_t epoch,uint32_t request,uint32_t rx_completed,const uint8_t*actual_frame,unsigned actual_bytes,uint64_t now);
int qca_filter_tx_complete(QcaFilterBarrier*,uint64_t epoch,uint32_t request,unsigned actual_bytes,uint64_t now);
/* ONLY an already validated/taken raw event from sole combined persistent RX.
 * Ledger credits have ALREADY been applied by that owner: never apply again.
 * Return1 owned exactECHO,0 unrelated caller-owned event,-1 fault/raw retained.
 * Current pipe2/WMI endpoint, epoch, completion>publishfloor and exactarg bind.
 * Reply may precede Echo TX completion; pass requires both actual observations. */
int qca_filter_receive(QcaFilterBarrier*,uint64_t epoch,uint32_t completion,unsigned pipe,const uint8_t*raw,unsigned raw_bytes,uint64_t now);
int qca_filter_poll(QcaFilterBarrier*,uint64_t epoch,uint64_t now);
/* Only a prepared body not yet submitted may be discarded by this API.
 * Submitted/committed ambiguity faults/retains; persistentTX alone cancels its own tickets. */
int qca_filter_cancel_unposted(QcaFilterBarrier*);
void qca_filter_fault(QcaFilterBarrier*,unsigned error);
int qca_filter_passed(const QcaFilterBarrier*);
#endif
