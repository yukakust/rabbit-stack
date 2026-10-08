#ifndef RABBIT_QCA_FULL_READ_H
#define RABBIT_QCA_FULL_READ_H
#include "init_adapter.h"
#include "diag_ce.h"
typedef struct {
 QcaInitAdapter*adapter;QcaDiagExchange exchange;QcaDiagPipe routes[2];
 uint32_t error;uint8_t started;
} QcaFullRead;
/* Borrow the completed warm adapter's CE7 rings, retaining all14 mappings.
 * Fixed host-interest word only; no target writes/configuration/firmware. */
int qca_full_read_begin(QcaFullRead*,QcaInitAdapter*,uint32_t,uint64_t,uint64_t);
int qca_full_read_poll(QcaFullRead*,uint64_t);
/* Caller closes/cancels the adapter and polls through all-eight stop, BME off,
 * flush/unmap/free. The exchange never frees memory or clears ownership. */
#endif
