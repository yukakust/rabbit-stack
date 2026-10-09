#ifndef QCA_REAL_HTT_WARM_STOP_H
#define QCA_REAL_HTT_WARM_STOP_H
#include "data_path.h"
enum {QSTOP_EMPTY,QSTOP_CE_WAIT,QSTOP_WARM,QSTOP_FINAL_CE,QSTOP_FENCE,QSTOP_PROVEN,QSTOP_RETAINED};
typedef struct {
 QcaHttDataPath*data;QcaInitAdapter*adapter;QcaWarm warm;
 uint64_t epoch,started,last,deadline,completion;
 uint32_t phase,error,clear_readbacks,cpu_writes,pipe_phase,recovery_calls;
} QcaHttWarmStop;
/* Sole native cooperative dispatcher: revoke external station/key callbacks
 * before this call; radio admission and registered HTT owner are revoked here.
 * Stops only the QCA9377 Wi-Fi chip. No map release, host reset or flash. */
int qstop_begin(QcaHttWarmStop*,QcaHttDataPath*,uint64_t now);
int qstop_poll(QcaHttWarmStop*,uint64_t now);
/* Fault recovery only deasserts an actually owned CE reset after its10ms wait;
 * max3 attempts, never resumes/reset-retries or grants release. */
int qstop_recover_ce(QcaHttWarmStop*,uint64_t now);
/* Native constructor's extra-DMA stop callback must call this only for the
 * exact registered runtime after this object's actual PROVEN completion. */
int qstop_release_guard(QcaHttWarmStop*);
/* Real remaining-map inventory for a new constructor/accounting adapter.
 * Does not replace observed port.dma_users with a manufactured count. */
int qstop_remaining_inventory(QcaHttWarmStop*);
int qstop_close_extra_one(QcaHttWarmStop*);
#endif
