#ifndef RABBIT_QCA_BOUNDED_TRIAL_H
#define RABBIT_QCA_BOUNDED_TRIAL_H
#include <stdint.h>
enum {QCA_TRIAL_RUNNING=1,QCA_TRIAL_STOPPING,QCA_TRIAL_DONE,QCA_TRIAL_FAULT};
typedef struct {uint64_t started,last;uint32_t phase,error;uint8_t expired,stop_requested,released;} QcaBoundedTrial;
/* Pure cooperative timer in microseconds.1 requests checked qca_stop ONCE;
 * never closes resources itself. Success requires actual owner release.
 * Native radio has no station/RF operations in this bounded trial. */
int qca_trial_tick(QcaBoundedTrial*,unsigned,unsigned,uint64_t);
#endif
