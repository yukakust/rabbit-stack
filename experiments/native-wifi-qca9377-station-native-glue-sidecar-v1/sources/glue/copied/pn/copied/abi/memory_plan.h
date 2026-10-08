#ifndef RABBIT_QCA_WMI_MEMORY_PLAN_H
#define RABBIT_QCA_WMI_MEMORY_PLAN_H
#include "wmi_boot_info.h"
typedef struct {uint32_t vdevs,peers,active_peers,budget_bytes;} QcaWmiResources;
typedef struct {uint32_t id,stride,units,bytes;} QcaWmiMemoryItem;
typedef struct {uint32_t count,total_bytes;QcaWmiMemoryItem item[16];} QcaWmiMemoryPlan;
/* Pure bounded plan from validated service-ready descriptions. No allocation,
 * mapping, physical addresses, firmware commands or credential access.
 * Error preserves output. Native operating profile must bind resource counts,
 * retain every actual DMA owner and validate addresses before WMI INIT. */
int qca_wmi_memory_plan(const QcaWmiServiceInfo*,const QcaWmiResources*,QcaWmiMemoryPlan*);
#endif
