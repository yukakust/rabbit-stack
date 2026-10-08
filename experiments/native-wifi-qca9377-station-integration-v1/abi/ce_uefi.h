#ifndef RABBIT_QCA_CE_UEFI_H
#define RABBIT_QCA_CE_UEFI_H
#include "dma_buffer.h"
typedef struct {QcaUefiPort*port;QcaDmaBuffer*buffers[16];uint8_t count,mask;} QcaCeAccess;
/* Zero initialize; only selected engines and mapped buffers are accessible. */
int qca_ce_access_init(QcaCeAccess*,QcaUefiPort*,unsigned);
int qca_ce_access_buffer(QcaCeAccess*,QcaDmaBuffer*);
int qca_ce_access_read(void*,uint32_t,uint32_t*);
int qca_ce_access_write(void*,uint32_t,uint32_t);
#endif
