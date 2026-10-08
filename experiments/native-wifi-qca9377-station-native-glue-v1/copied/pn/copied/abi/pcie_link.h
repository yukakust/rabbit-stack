#ifndef RABBIT_QCA_PCIE_LINK_H
#define RABBIT_QCA_PCIE_LINK_H
#include "uefi_port.h"
typedef struct {QcaUefiPort*port;uint16_t offset,original,readback;uint8_t owned,error;} QcaPcieLink;
/* Exclusive validated PCI claim; save LinkControl, clear only ASPM bits0:1.
 * Mark ownership before Write16; never write adjacent LinkStatus. */
int qca_pcie_pause(QcaPcieLink*,QcaUefiPort*);
/* Revalidate cap after cold reset; reapply ASPM-off without replacing original. */
int qca_pcie_recheck(QcaPcieLink*);
int qca_pcie_restore(QcaPcieLink*);
#endif
