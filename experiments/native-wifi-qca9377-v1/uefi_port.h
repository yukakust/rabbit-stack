#ifndef RABBIT_QCA_UEFI_PORT_H
#define RABBIT_QCA_UEFI_PORT_H
#include "scene_abi.h"
#include "wake_core.h"
typedef struct {uint16_t subsystem_vendor,subsystem_device;uint8_t revision;} QcaPciTarget;
typedef struct {
 SystemTable*system;void*image,*controller,*pci,*resource;
 uint64_t original_attributes,bar_extent;
 uint32_t error;
 uint16_t original_command;
 uint8_t claimed,memory_attempted,memory_ready,validated,wake_owned;
} QcaUefiPort;
/* Zero initialize. Claims PCI IO exclusively and validates fresh config/BAR.
 * Failed cleanup retains ownership; caller MUST NOT unload while claimed. */
int qca_port_open(QcaUefiPort*,SystemTable*,void*,void*,const QcaPciTarget*);
int qca_port_enable_memory(QcaUefiPort*);
int qca_port_read32(void*,uint32_t,uint32_t*);
int qca_port_write32(void*,uint32_t,uint32_t);
int qca_port_close(QcaUefiPort*,QcaWake*);
#endif
