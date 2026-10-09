#ifndef RABBIT_QCA_BOOT_IRQ_MAPPED_H
#define RABBIT_QCA_BOOT_IRQ_MAPPED_H
#include "boot_irq.h"
#include "channels_core.h"
typedef struct {
 QcaBootIrq*irq;QcaChannels*channels;uint64_t bar;
 uint16_t link_offset,link_control;
 uint32_t reads,writes,error;
} QcaMappedIrq;
/* Separate scope, not a relaxation of the legacy boot_irq API. Caller binds
 * the original exclusive IRQ owner and BAR identity to these exact14 mappings.
 * Every guard reads fresh PCI header/MEM/D0/INTx/MSI/MSI-X, mapping ownership
 * and wake/chip state. Poll separately remasks core MSI control.
 * Bus mastering must stay OFF; host IRQ remains masked.
 */
int qca_mapped_irq_guard(QcaMappedIrq*);
/* Separate active CE7 scope: exact14 exposed mappings, owned active bus, fresh
 * PCI/D0/wake identity, BME ON and masked host/device interrupts. Never usable
 * for warm/cold reset, freeing buffers or relaxing the existing OFF guards. */
int qca_mapped_irq_active_guard(QcaMappedIrq*);
/* PCI-only reset guard: no RTC/CORE accesses while cold reset asserted.
 * May observe reset-restored ASPM bits, but never permits active bus mastering.
 * Caller may use it only for the finite cold-reset register callback. */
int qca_mapped_irq_pci_guard(QcaMappedIrq*);
/* Re-mask core MSI firmware bit after CPU reset, then enable bounded boot mask.
 * This cannot restore host interrupts, enable DMA, free mappings or claim IRQs. */
int qca_mapped_irq_poll(QcaMappedIrq*);
/* Disable/clear/verify device boot IRQ; keep host/core/IRQ ownership retained. */
int qca_mapped_irq_quiesce(QcaMappedIrq*);
#endif
