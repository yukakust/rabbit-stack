#ifndef RABBIT_QCA_MGMT_COMPLETION_H
#define RABBIT_QCA_MGMT_COMPLETION_H
#include <stdint.h>
#define QCA_MGMT_REPORTS 32
/* Firmware status and RSSI retained as opaque u32 wire values. No native
 * dispatch, allocation or release. A completion does NOT prove host DMA done. */
typedef struct {uint32_t id,status,pdev,ppdu,rssi;} QcaMgmtReport;
typedef struct {uint32_t count;uint8_t has_ppdu,has_rssi;QcaMgmtReport report[QCA_MGMT_REPORTS];} QcaMgmtCompletion;
int qca_mgmt_completion(const uint8_t*,unsigned,unsigned,QcaMgmtCompletion*);
/* Validate whole batch against unique currently outstanding IDs before
 * returning a bit mask. Not a free operation: native caller must also prove
 * TX DMA completion, retained generation/owner and actual cleanup lifecycle. */
int qca_mgmt_completion_plan(const QcaMgmtCompletion*,const uint32_t*,unsigned,uint32_t*);
#endif
