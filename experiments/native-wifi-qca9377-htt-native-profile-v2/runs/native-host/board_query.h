#ifndef RABBIT_QCA_BOARD_QUERY_H
#define RABBIT_QCA_BOARD_QUERY_H
#include "config_setup.h"
#include "bmi_loader.h"
typedef struct {
 QcaConfigSetup*setup;QcaBmiLoader io;const uint8_t*helper;
 uint32_t helper_bytes,offset,submitted,polls,result,error;uint8_t phase,board_id,chip_id,extended;
} QcaBoardQuery;
/* Exact immutable reviewed helper, fresh native setup/BMI, active DMA owner.
 * Poll advances at most one BMI command. phase5 means reply received;
 * usable board/chip IDs are reported separately from reply completion. */
int qca_board_begin(QcaBoardQuery*,QcaConfigSetup*,const uint8_t*,unsigned,const uint8_t[32]);
int qca_board_poll(QcaBoardQuery*,uint64_t);
#endif
