#ifndef RABBIT_QCA_BMI_LOADER_H
#define RABBIT_QCA_BMI_LOADER_H
#include "bmi_transport.h"
typedef struct {QcaBmiExchange wire;uint32_t request_bytes,response_bytes;} QcaBmiLoader;
/* Native-only helper path: LZ_START(0x1234/0), aligned LZ_DATA <=248,
 * EXECUTE(0x1234, GET_EEPROM_BOARD_ID). No DONE/SOC/NVRAM/OTP-write command.
 * DMA buffers/rings must belong to the current exclusive active bus. */
int qca_bmi_loader_begin(QcaBmiLoader*,QcaCeBus*,QcaCeRing*,QcaCeRing*,QcaDmaBuffer*,QcaDmaBuffer*,const uint8_t*,unsigned,uint64_t);
int qca_bmi_loader_poll(QcaBmiLoader*,uint64_t);
#endif
