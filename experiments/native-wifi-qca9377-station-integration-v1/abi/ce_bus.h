#ifndef RABBIT_QCA_CE_BUS_H
#define RABBIT_QCA_CE_BUS_H
#include "ce_hw.h"
#include "ce_uefi.h"
enum {QCA_BUS_IDLE,QCA_BUS_OFF,QCA_BUS_ACTIVE,QCA_BUS_STOPPING,QCA_BUS_FAULT};
typedef struct {QcaCeAccess*access;QcaCeHw engines[8];uint16_t command;uint8_t phase,owned;uint32_t error;} QcaCeBus;
/* Zero initialize. All eight engines must be controlled, not just BMI pipes.
 * Allocation/configuration precedes start; every DMA buffer must be registered.
 * Caller serializes operations with native unload. */
int qca_ce_bus_init(QcaCeBus*,QcaCeAccess*);
int qca_ce_bus_start(QcaCeBus*);
int qca_ce_bus_stop_begin(QcaCeBus*,uint64_t);
int qca_ce_bus_stop_poll(QcaCeBus*,uint64_t);
/* DMA close callback: checks completed stop plus fresh hardware state, no wait. */
int qca_ce_bus_released(void*);
#endif
