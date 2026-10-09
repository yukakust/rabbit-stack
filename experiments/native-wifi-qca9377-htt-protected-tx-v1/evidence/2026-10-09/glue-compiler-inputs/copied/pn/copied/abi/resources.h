#ifndef RABBIT_QCA_TLV_RESOURCES_H
#define RABBIT_QCA_TLV_RESOURCES_H
#include "memory_plan.h"
typedef struct {uint32_t words[44];QcaWmiResources memory;} QcaTlvResources;
/* Pure Linux PCI TLV reference candidate. Needs validated SERVICE_READY with
 * exactly 128 base services in 32 u32 words. No extended service assumptions.
 * Output preserves failure; no DMA/MMIO, no native integration approval. */
int qca_tlv_resources(const QcaWmiServiceInfo*,QcaTlvResources*);
#endif
