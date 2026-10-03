#ifndef RABBIT_QCA_BMI_TRANSPORT_H
#define RABBIT_QCA_BMI_TRANSPORT_H
#include "ce_bus.h"
#include "ce_ring.h"
enum {QCA_BMI_IDLE,QCA_BMI_WAIT,QCA_BMI_DONE,QCA_BMI_FAULT};
typedef struct {QcaCeBus*bus;uint8_t receive;} QcaBmiPipe;
typedef struct {
 QcaCeBus*bus;QcaCeRing*tx,*rx;QcaDmaBuffer*request,*response;
 uint64_t started,last;uint32_t bytes,error,version,type,info_length;
 uint8_t phase,tx_done,rx_done;
} QcaBmiExchange;
/* Ring callbacks: CE0 source / CE1 destination, checked hardware adapter. */
int qca_bmi_publish(void*,uint32_t);
int qca_bmi_ring_stop(void*);
/* Buffers and descriptor rings must be registered to this active bus.
 * Only one exchange at a time; response posted BEFORE request.
 * No firmware write/done/execute command in this first query. */
int qca_bmi_info_begin(QcaBmiExchange*,QcaCeBus*,QcaCeRing*,QcaCeRing*,QcaDmaBuffer*,QcaDmaBuffer*,uint64_t);
int qca_bmi_poll(QcaBmiExchange*,uint64_t);
#endif
