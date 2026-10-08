#ifndef RABBIT_QCA_WMI_BOOT_INFO_H
#define RABBIT_QCA_WMI_BOOT_INFO_H
#include "wmi_scan.h"
typedef struct {uint32_t id,unit_size,unit_flags,units;} QcaWmiMemoryRequest;
typedef struct {
 uint32_t build,abi_minor,chains,regdomain,low2,high2,low5,high5;
 uint32_t service_words[128];unsigned service_count,memory_count;
 QcaWmiMemoryRequest memory[16];
} QcaWmiServiceInfo;
typedef struct {uint8_t mac[6];uint32_t abi_minor;} QcaWmiReadyInfo;
/* Read-only bounded descriptions, NOT memory allocation/regulatory approval.
 * Invalid event leaves output unchanged. Pinned TLV ABI-major/namespaces;
 * minor version is reported, as the Linux reference does not require equality. */
int qca_wmi_service_info(const uint8_t*,unsigned,QcaWmiServiceInfo*);
int qca_wmi_ready_info(const uint8_t*,unsigned,QcaWmiReadyInfo*);
#endif
