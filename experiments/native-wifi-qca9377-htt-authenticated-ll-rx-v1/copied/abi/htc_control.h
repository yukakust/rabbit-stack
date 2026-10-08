#ifndef RABBIT_QCA_HTC_CONTROL_H
#define RABBIT_QCA_HTC_CONTROL_H
#include "htc_session.h"
#include "htc_credit.h"
typedef struct {
 QcaHtcSession session;
 QcaHtcCredit credit;
 unsigned posted,deferred_bytes;
 uint8_t deferred[QCA_HTC_FRAME_LIMIT];
} QcaHtcControl;
/* Pure coordinator; actual CE0 TX/CE1 RX owners, deadlines, monotonic clock
 * and stop remain caller responsibilities. Zero initialization required. */
int qca_htc_control_begin(QcaHtcControl*);
unsigned qca_htc_control_prepare(QcaHtcControl*,uint8_t*,unsigned);
/* Called before making the prepared descriptor hardware-visible. Unknown
 * submission/completion requires hardware stop, never a local rollback. */
int qca_htc_control_post(QcaHtcControl*,unsigned);
/* Called only once after validated completion of that exact CE0 descriptor. */
int qca_htc_control_complete(QcaHtcControl*,unsigned);
/* A matching endpoint-zero response may precede TX completion; validate
 * against the prospective phase and retain one copy until TX is complete.
 * Caller must consume every CE1 completion once. No arbitrary RX buffering. */
int qca_htc_control_receive(QcaHtcControl*,const uint8_t*,unsigned);
#endif
