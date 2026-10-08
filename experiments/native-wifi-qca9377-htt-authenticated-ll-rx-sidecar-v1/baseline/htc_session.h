#ifndef RABBIT_QCA_HTC_SESSION_H
#define RABBIT_QCA_HTC_SESSION_H
#include "htc_wire.h"
enum {QCA_HTC_WAIT_READY=1,QCA_HTC_SEND_WMI,QCA_HTC_WAIT_WMI,QCA_HTC_SEND_HTT,QCA_HTC_WAIT_HTT,QCA_HTC_SEND_SETUP,QCA_HTC_RUNNING};
typedef struct {
 QcaHtcReady ready;QcaHtcConnection wmi,htt;
 unsigned phase,prepared;uint8_t sequence;
} QcaHtcSession;
int qca_htc_session_begin(QcaHtcSession*);
/* Construction is repeatable until transport confirms the same DMA transfer.
 * No phase advance before completion. Caller owns deadlines/cancel/CE cleanup. */
unsigned qca_htc_session_prepare(QcaHtcSession*,uint8_t*,unsigned);
int qca_htc_session_transmitted(QcaHtcSession*,unsigned);
/* Endpoint-zero handshake only. Invalid/unexpected input preserves state. */
int qca_htc_session_receive(QcaHtcSession*,const uint8_t*,unsigned);
#endif
