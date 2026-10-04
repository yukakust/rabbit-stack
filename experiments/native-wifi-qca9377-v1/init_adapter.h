#ifndef RABBIT_QCA_INIT_ADAPTER_H
#define RABBIT_QCA_INIT_ADAPTER_H
#include "boot_irq_mapped.h"
#include "warm_core.h"
#include "reset_core.h"
enum {QCA_INIT_IDLE,QCA_INIT_STOP,QCA_INIT_ALLOCATE,QCA_INIT_WARM,QCA_INIT_READY,
 QCA_INIT_RELEASE_CE,QCA_INIT_QUIESCE,QCA_INIT_RECOVERY_STOP,QCA_INIT_COLD,
 QCA_INIT_ROM_RECOVERY,QCA_INIT_CLEANUP_STOP,QCA_INIT_CLEANUP,
 QCA_INIT_CLOSED,QCA_INIT_RETAINED};
typedef struct {
 QcaCeAccess access;QcaCeBus bus;QcaChannels channels;QcaWarm warm;
 QcaMappedIrq mapped;QcaReset recovery;
 uint64_t last,rom_started,next_rom;uint32_t error,recovery_indicator;
 uint8_t phase,pipes_phase,cancelled,retries,recovery_verified,stop_started;
} QcaInitAdapter;
/* Native PCI adapter: caller already completed cold reset/wake/ROM and owns
 * masked boot IRQ and paused link, no DMA. Borrows that IRQ/PCI owner; never
 * restores interrupts, closes PCI, writes target RAM or enables bus mastering.
 * Original BAR and LinkControl offset come from the validated outer probe.
 */
int qca_init_adapter_begin(QcaInitAdapter*,QcaBootIrq*,uint64_t,unsigned,uint64_t);
/* 0 waiting,1 ready,-1 error/retained. Error does not mean safe to unload.
 * Poll continues bounded recovery/cleanup after a fault or cancellation.
 * Caller must continue polling until CLOSED or RETAINED and honor ownership.
 */
int qca_init_adapter_poll(QcaInitAdapter*,uint64_t);
void qca_init_adapter_cancel(QcaInitAdapter*);
/* Successful READY probe teardown; no cancellation error or cold recovery. */
int qca_init_adapter_close(QcaInitAdapter*);
/* CLOSED means mapped buffers released and no warm/cold operation owned.
 * Caller must still close the borrowed boot IRQ/link/wake/PCI owners. */
int qca_init_adapter_released(const QcaInitAdapter*);
#endif
