#ifndef RABBIT_QCA_RESET_CORE_H
#define RABBIT_QCA_RESET_CORE_H
#include "wake_core.h"
typedef struct {uint32_t address,settle_us,deadline_us;} QcaResetTarget;
enum {QCA_RESET_IDLE,QCA_RESET_ASSERT_WAIT,QCA_RESET_CLEAR_WAIT,QCA_RESET_DONE,QCA_RESET_FAULT};
enum {QCA_RESET_IO=1,QCA_RESET_TIMEOUT=2,QCA_RESET_INVALID=3,QCA_RESET_CLOCK=4};
typedef struct {
 QcaResetTarget target;QcaRead32 read;QcaWrite32 write;void*context;
 uint64_t started,last_time,operation_time;
 uint32_t original,readback;
 uint8_t phase,owned,error,attempts,deasserted;
} QcaReset;
/* Caller must validate exclusive PCI ownership/D0/BAR/no DMA before begin.
 * Poll is cooperative. While owned, forbid accesses to this PCI device outside this machine.
 * Write errors are ambiguous: ownership persists until verified deassertion. */
int qca_reset_begin(QcaReset*,const QcaResetTarget*,QcaRead32,QcaWrite32,void*,uint64_t);
int qca_reset_poll(QcaReset*,uint64_t);
/* Explicit bounded cleanup retry; never starts another assertion. */
int qca_reset_recover(QcaReset*,uint64_t);
#endif
