#ifndef QCA_FIRMWARE_PORT_H
#define QCA_FIRMWARE_PORT_H
#include "scene_abi.h"
#include "firmware_channel.h"
typedef struct {
 SystemTable*system;
 void *allocate,*release;
 uint8_t *memory,*workspace;
 QcaFirmwarePolicy policy;
 QcaFirmwareChunks asset;
 QcaFirmwareChannel channel;
 uint32_t phase,error;
 uint8_t memory_owned,workspace_owned,uncertain;
} QcaFirmwarePort;
/* Zero initialize. diagnostic is the native-owned QPD7 snapshot, never a
 * packet/client-supplied report. Policy is separately owner/target reviewed.
 * This gate binds known BMI type/version, not firmware compatibility itself. */
int qca_fwp_start(QcaFirmwarePort*,SystemTable*,const QcaFirmwarePolicy*,const uint8_t*,size_t);
int qca_fwp_step(QcaFirmwarePort*); /* At most one allocation, no radio/DMA. */
int qca_fwp_close(QcaFirmwarePort*); /* 1 still owned, 0 closed, -1 retained error. */
size_t qca_fwp_att(QcaFirmwarePort*,uint16_t,const uint8_t*,size_t,uint8_t*,size_t);
int qca_fwp_owned(const QcaFirmwarePort*);
#endif
