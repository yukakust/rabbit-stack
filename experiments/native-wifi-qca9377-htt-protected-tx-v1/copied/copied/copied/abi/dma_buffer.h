#ifndef RABBIT_QCA_DMA_BUFFER_H
#define RABBIT_QCA_DMA_BUFFER_H
#include "uefi_port.h"
typedef int (*QcaDmaStop)(void*);
typedef struct {
 QcaUefiPort*port;void*host,*mapping;QcaDmaStop stop;void*context;
 uint64_t address,bytes,pages;uint32_t error;
 uint8_t allocated,mapped,valid,exposed,allocation_uncertain,closing;
} QcaDmaBuffer;
/* Zero initialize; port must retain exclusive validated PCI claim.
 * CommonBuffer mapping is checked for full length/page alignment/address32.
 * Stop callback must prove all engines using the buffer stopped. */
int qca_dma_open(QcaDmaBuffer*,QcaUefiPort*,uint32_t,QcaDmaStop,void*);
/* Mark BEFORE a CE address/doorbell or bus-master write might expose memory. */
int qca_dma_expose(QcaDmaBuffer*);
/* Stop -> actual bus-master-off readback -> Flush -> Unmap -> FreeBuffer.
 * Any failure retains remaining resources and prevents port close/unload. */
int qca_dma_close(QcaDmaBuffer*);
#endif
