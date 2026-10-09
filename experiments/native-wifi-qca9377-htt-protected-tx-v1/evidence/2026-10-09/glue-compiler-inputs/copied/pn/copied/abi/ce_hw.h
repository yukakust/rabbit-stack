#ifndef RABBIT_QCA_CE_HW_H
#define RABBIT_QCA_CE_HW_H
#include "wake_core.h"
enum {QCA_CE_HW_IDLE,QCA_CE_HW_HALTING,QCA_CE_HW_STOPPED,QCA_CE_HW_CONFIGURED,QCA_CE_HW_RUNNING,QCA_CE_HW_FAULT};
typedef struct {
 QcaRead32 read;QcaWrite32 write;void*context;
 uint64_t started,last;uint32_t base,timeout,error;
 uint16_t src_entries,dst_entries,src_index,dst_index;
 uint8_t phase,owned;
} QcaCeHw;
/* Adapter first proves PCI claim/D0/awake/BAR; callbacks only access this CE. */
int qca_ce_hw_init(QcaCeHw*,unsigned,QcaRead32,QcaWrite32,void*);
int qca_ce_hw_stop_begin(QcaCeHw*,uint64_t);
int qca_ce_hw_stop_poll(QcaCeHw*,uint64_t);
/* Configure only after verified halt and zero bases/sizes. DMA remains mapped.
 * Seed software ring indices from returned src_index/dst_index before run. */
int qca_ce_hw_configure(QcaCeHw*,uint64_t,unsigned,uint64_t,unsigned,unsigned);
int qca_ce_hw_run(QcaCeHw*);
int qca_ce_hw_publish(QcaCeHw*,int,unsigned);
int qca_ce_hw_index(QcaCeHw*,int,unsigned*);
#endif
