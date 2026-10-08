#ifndef QCA_ACTUAL_OWNER47_ADAPTER_H
#define QCA_ACTUAL_OWNER47_ADAPTER_H
#include "dma_runtime.h"
#include "lifecycle47.h"
/* Basis carries independently proven live PCI/wake/link/IRQ/pin/bus/master/
 * READY/stop flags. Adapter recomputes both counts from actual retained objects,
 * never sets port.dma_users or substitutes14 while47 owners exist. */
int qca_htt_owner47_snapshot(const QcaHttRuntime*,const QcaRadioOwners*,QcaRadioOwners*);
#endif
