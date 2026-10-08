#ifndef QCA_GUARDED_DMA_OPEN_H
#define QCA_GUARDED_DMA_OPEN_H
#include "dma_buffer.h"
typedef int(*QcaDmaGuard)(void*,const void*,uint64_t);
int qca_dma_open_protected(QcaDmaBuffer*,QcaUefiPort*,uint32_t,QcaDmaStop,void*,QcaDmaGuard,void*);
#endif
