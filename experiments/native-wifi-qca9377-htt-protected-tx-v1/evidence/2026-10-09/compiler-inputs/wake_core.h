#ifndef RABBIT_QCA_WAKE_CORE_H
#define RABBIT_QCA_WAKE_CORE_H
#include <stdint.h>
/* Target adapter must first validate PCI identity, BAR extent, memory decode
 * and exclusive ownership. Values are TARGET facts, never world coordinates. */
typedef struct {uint32_t state,wake,chip_id,on,timeout_us;} QcaWakeTarget;
typedef int (*QcaRead32)(void*,uint32_t,uint32_t*);
typedef int (*QcaWrite32)(void*,uint32_t,uint32_t);
enum {QCA_SLEEPING,QCA_WAKE_WAIT,QCA_WAKE_READY,QCA_WAKE_FAULT};
enum {QCA_WAKE_IO=1,QCA_WAKE_TIMEOUT=2,QCA_WAKE_CHIP=3,QCA_WAKE_CLOCK=4};
typedef struct {
 QcaWakeTarget target;QcaRead32 read;QcaWrite32 write;void*context;
 uint64_t started,last_time;uint32_t chip_id;
 uint8_t phase,owned,error;
} QcaWake;
/* Cooperative: begin/poll/close each issue at most one or two MMIO operations.
 * A failed/ambiguous write retains ownership until close succeeds. */
int qca_wake_begin(QcaWake*,const QcaWakeTarget*,QcaRead32,QcaWrite32,void*,uint64_t);
int qca_wake_poll(QcaWake*,uint64_t);
int qca_wake_close(QcaWake*);
#endif
