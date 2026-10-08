#ifndef RABBIT_QCA_BOOT_TRANSPORT_H
#define RABBIT_QCA_BOOT_TRANSPORT_H
#include "bmi_loader.h"
#include "boot_image.h"
/* Only planner-issued commands; exclusive registered DMA/empty ring guards.
 * Timeout leaves DMA owned: caller must stop bus before freeing resources. */
int qca_boot_transport_begin(QcaBmiLoader*,QcaCeBus*,QcaCeRing*,QcaCeRing*,QcaDmaBuffer*,QcaDmaBuffer*,const QcaBootImage*,uint64_t);
int qca_boot_transport_poll(QcaBmiLoader*,uint64_t);
#endif
