#ifndef RABBIT_QCA_PCI_IDENTITY_H
#define RABBIT_QCA_PCI_IDENTITY_H
#include <stdint.h>
typedef struct {
 uint16_t subsystem_vendor,subsystem_device,command;
 uint8_t revision,bar64;
 uint64_t bar0;
} QcaPciIdentity;
/* Pure decode of a READ-ONLY PCI header snapshot; no MMIO or guessed BAR size. */
int qca_pci_identity(const uint32_t config[16],QcaPciIdentity *out);
#endif
