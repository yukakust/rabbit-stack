#ifndef RABBIT_QCA_WMI_AVAILABLE_H
#define RABBIT_QCA_WMI_AVAILABLE_H
#include <stdint.h>
typedef struct {uint32_t advertised_length,words[4];} QcaWmiAvailable;
/* Pinned WMI event3/TLV559. Known QCA9377 frame has20-byte value:
 * service_map_ext_len128 then four bitmap words. Preserves opaque bitmap;
 * does not approve capabilities/resource policy or indicate SERVICE_READY.
 * Pure; rejects unknown length/extension forms; failure preserves output. */
int qca_wmi_available(const uint8_t*,unsigned,QcaWmiAvailable*);
#endif
