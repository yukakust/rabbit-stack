#ifndef RABBIT_QCA_DIAG_CE_H
#define RABBIT_QCA_DIAG_CE_H
#include "bmi_transport.h"
enum {QCA_DIAG_IDLE,QCA_DIAG_WAIT,QCA_DIAG_DONE,QCA_DIAG_FAULT};
typedef struct {QcaCeBus*bus;uint8_t receive;} QcaDiagPipe;
typedef struct {
 QcaCeBus*bus;QcaCeRing*tx,*rx;QcaDmaBuffer*response;
 uint64_t started,last;uint32_t error,value,core,target,ce_address,bytes;
 uint32_t first_elapsed,last_elapsed,polls;
 uint16_t command,initial[2],observed[2];uint8_t phase,tx_done,rx_done,mask;
} QcaDiagExchange;
int qca_diag_publish(void*,uint32_t);
int qca_diag_stop(void*);
/* Read ONLY the fixed QCA9377/rev1 host-interest interconnect word. No target
 * writes, arbitrary addresses, pointer chasing, firmware upload or execution. */
int qca_diag_begin(QcaDiagExchange*,QcaCeBus*,QcaCeRing*,QcaCeRing*,QcaDmaBuffer*,uint32_t,uint64_t,uint64_t);
int qca_diag_poll(QcaDiagExchange*,uint64_t);
#endif
