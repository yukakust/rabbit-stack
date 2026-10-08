#ifndef RABBIT_QCA_WMI_INIT_WIRE_H
#define RABBIT_QCA_WMI_INIT_WIRE_H
#include "memory_plan.h"
#define QCA_WMI_RESOURCE_WORDS 44u
typedef struct {uint32_t id,bytes;uint64_t address;} QcaWmiHostChunk;
/* PURE serializer, not admission to hardware. Caller supplies a separately
 * approved full resource vector in the pinned wmi_tlv_resource_config order.
 * Its vdev/peer fields must match the resources used for the memory plan.
 * One unsplit mapping per request.32-bit QCA9377 addresses, no credentials.
 * Caller must prove actual mapping/retention and exclusion of control buffers.
 * Output may not alias any input. Any rejection leaves output unchanged.
 * Returns complete WMI bytes including command id, NOT the HTC header. */
unsigned qca_wmi_init_wire(uint8_t*,unsigned,const uint32_t[QCA_WMI_RESOURCE_WORDS],
 const QcaWmiServiceInfo*,const QcaWmiResources*,const QcaWmiHostChunk*,unsigned);
#endif
