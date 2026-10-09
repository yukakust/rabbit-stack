#ifndef RABBIT_QCA_BOARD_SMBIOS_H
#define RABBIT_QCA_BOARD_SMBIOS_H
#include "scene_abi.h"
typedef struct {uint32_t state,error,structures,bytes;char variant[32];} QcaBoardSmbios;
/* state0 unstarted,1 absent SMBIOS,2 complete/no BDF variant,3 variant,4 fault.
 * Bounded double-NUL traversal; malformed/ambiguous data is never "absent". */
int qca_board_smbios_parse(QcaBoardSmbios*,const uint8_t*,size_t);
int qca_board_smbios_collect(QcaBoardSmbios*,SystemTable*);
#endif
