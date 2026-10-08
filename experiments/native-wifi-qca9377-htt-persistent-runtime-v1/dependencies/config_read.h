#ifndef RABBIT_QCA_CONFIG_READ_H
#define RABBIT_QCA_CONFIG_READ_H
#include "full_read.h"
typedef struct {
 QcaFullRead full;QcaDiagExchange reads[3];
 uint32_t words[11],error,mask;uint8_t phase,slot;
} QcaConfigRead;
/* Fixed state36, early_alloc4, option_flag2 four-byte reads only. */
int qca_config_read_poll(QcaConfigRead*,uint64_t);
#endif
