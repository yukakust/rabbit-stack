#ifndef RABBIT_QCA_CONFIG_SETUP_H
#define RABBIT_QCA_CONFIG_SETUP_H
#include "config_read.h"
int qca_diag_setup_bytes(const QcaConfigRead*,unsigned,uint32_t*,unsigned*,uint8_t[204]);
int qca_diag_setup_begin(QcaDiagExchange*,const QcaConfigRead*,unsigned,uint64_t);
typedef struct {
 QcaConfigRead read;QcaDiagExchange io;QcaBmiExchange bmi;QcaBmiPipe bmi_routes[2];
 uint32_t error,write_mask,readback_mask,write_attempts,cpu_before,cpu_readback,bmi_polls;
 uint8_t phase,op,cpu_attempted;
} QcaConfigSetup;
/* All fresh config reads, five write/readback pairs, CPU wake, BMI info ONLY. */
int qca_config_setup_poll(QcaConfigSetup*,uint64_t);
#endif
