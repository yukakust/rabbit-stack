#ifndef RABBIT_QCA_WARM_CORE_H
#define RABBIT_QCA_WARM_CORE_H
#include "wake_core.h"
typedef int (*QcaWarmCheck)(void*);
typedef int (*QcaWarmPipes)(void*);
enum {QCA_WARM_IDLE,QCA_WARM_SI_ASSERT,QCA_WARM_SI_CLEAR,QCA_WARM_CPU_FIRST,
 QCA_WARM_PIPES_FIRST,QCA_WARM_ROM_FIRST,QCA_WARM_LF,QCA_WARM_CE_ASSERT,
 QCA_WARM_CE_CLEAR,QCA_WARM_CPU_SECOND,QCA_WARM_PIPES_SECOND,
 QCA_WARM_ROM_SECOND,QCA_WARM_DONE,QCA_WARM_FAULT};
enum {QCA_WARM_IO=1,QCA_WARM_TIMEOUT,QCA_WARM_CLOCK,QCA_WARM_CANCELLED,
 QCA_WARM_GUARD,QCA_WARM_ROM_ERROR};
typedef struct {
 QcaRead32 read;QcaWrite32 write;QcaWarmCheck check;QcaWarmPipes pipes;void*context;
 uint64_t started,last,operation,next;uint32_t reset_value,indicator,reads,writes;
 uint8_t phase,error,owned,ce_owned,cancelled,cpu_resets,pipe_inits;
} QcaWarm;
/* QCA9377-only finite BAR offsets from init pack. Caller verifies cold+ROM done,
 * IRQ isolation, PCI/D0/wake identity, bus master OFF, all exposed DMA retained.
 * check revalidates those invariants on EVERY normal poll. pipes cooperatively
 * prepares owned host rings without bus mastering: -1 error,0 waiting,1 done.
 * No callback may start another operation or release PCI/DMA behind this core.
 */
int qca_warm_begin(QcaWarm*,QcaRead32,QcaWrite32,QcaWarmCheck,QcaWarmPipes,void*,uint64_t);
int qca_warm_poll(QcaWarm*,uint64_t);
/* Cancellation never skips deasserting an owned CE reset after its10ms window.
 * Any error keeps exclusive ownership. Native adapter must retain module/PCI
 * until separately verified cold recovery; no implicit unload/retry is allowed.
 * A failed deassert may be retried by bounded recovery calls, never reasserted.
 */
void qca_warm_cancel(QcaWarm*);
int qca_warm_recover_ce(QcaWarm*,uint64_t);
#endif
