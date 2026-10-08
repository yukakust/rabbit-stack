#ifndef RABBIT_QCA_PCI_COLLECT_H
#define RABBIT_QCA_PCI_COLLECT_H
#include <stdint.h>
#define QCA_DIAGNOSTIC_SIZE 924u
/* QPD1: flags, enumeration status/count, target count, read/location status,
 * BDF, decode result, reserved, sixteen raw PCI words. Little endian. */
extern uint8_t qca_diagnostic[QCA_DIAGNOSTIC_SIZE];
#endif
