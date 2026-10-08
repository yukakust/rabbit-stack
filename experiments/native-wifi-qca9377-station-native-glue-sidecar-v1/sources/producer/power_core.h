#ifndef QCA_POWER_CORE_H
#define QCA_POWER_CORE_H
#include <stdint.h>
/* status: 1 valid PM/PCIe, 2 no PM, 3 malformed. Input is exact PCI config256. */
void qca_power_decode(const uint8_t config[256],uint8_t out[16]);
#endif
