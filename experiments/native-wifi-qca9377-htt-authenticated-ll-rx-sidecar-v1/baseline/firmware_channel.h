#ifndef QCA_FIRMWARE_CHANNEL_H
#define QCA_FIRMWARE_CHANNEL_H
#include "firmware_chunks.h"
#define QCA_FC_CONTROL 44u
#define QCA_FC_STATUS 64u
enum {QCA_FC_IDLE,QCA_FC_STAGING,QCA_FC_ACCEPTED,QCA_FC_REJECTED,QCA_FC_ABORTED};
typedef struct {
 QcaFirmwareChunks *asset;
 uint8_t *workspace;
 size_t capacity;
 uint8_t digest[32],state,error;
 uint32_t length,received;
} QcaFirmwareChannel;
int qca_fc_init(QcaFirmwareChannel*,QcaFirmwareChunks*,uint8_t*,size_t);
int qca_fc_control(QcaFirmwareChannel*,const uint8_t*,size_t);
int qca_fc_data(QcaFirmwareChannel*,const uint8_t*,size_t);
void qca_fc_status(const QcaFirmwareChannel*,uint8_t[QCA_FC_STATUS]);
int qca_fc_close(QcaFirmwareChannel*);
/* SIZE_MAX delegates to the existing native ATT handler. Handles11..17 only;
 * mtu is owned/reset by that handler. Does not claim USB, HCI or allocation. */
size_t qca_fc_att(QcaFirmwareChannel*,uint16_t,const uint8_t*,size_t,uint8_t*,size_t);
#endif
