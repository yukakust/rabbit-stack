#ifndef RABBIT_QCA_BOOT_IRQ_H
#define RABBIT_QCA_BOOT_IRQ_H
#include "uefi_port.h"
typedef struct {
 QcaUefiPort*port;uint32_t original_enable,last_enable,original_control,last_control,cause,writes;
 uint16_t original_command,command_readback,msi,msix;uint8_t owned,error;
} QcaBootIrq;
/* After reset/D0/wake, BM off: mask host INTx and verify MSI/MSI-X disabled
 * before repeated legacy boot-enable writes. No host IRQ handler installed. */
int qca_boot_irq_begin(QcaBootIrq*,QcaUefiPort*);
int qca_boot_irq_poll(QcaBootIrq*);
/* Disable -> clear pending -> flush read; restore core MSI mask and Command16.
 * Errors retain ownership and prevent PCI close/unload. */
int qca_boot_irq_close(QcaBootIrq*);
#endif
