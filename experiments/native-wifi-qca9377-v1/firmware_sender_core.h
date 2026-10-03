#ifndef QCA_FIRMWARE_SENDER_CORE_H
#define QCA_FIRMWARE_SENDER_CORE_H
#include <stdint.h>
#include <stddef.h>
enum {QFS_INVALID=-1,QFS_BEGIN=1,QFS_DATA,QFS_COMMIT,QFS_DONE,QFS_REJECTED,QFS_LOSS,QFS_BUSY};
typedef struct {uint32_t state,error,length,received,bitmap;uint8_t digest[32],ready,pinned,poisoned;} QfsStatus;
typedef struct {uint8_t digest[32];uint32_t length,bit,all;} QfsExpected;
typedef struct {uint32_t floor;uint8_t attempted;} QfsProgress;
int qfs_parse(QfsStatus*,const uint8_t*,size_t);
/* Pure decision. Caller durably records attempted BEFORE BEGIN/DATA/COMMIT.
 * Matching status may advance confirmed floor, never an ACK or byte count. */
int qfs_next(const QfsStatus*,const QfsExpected*,QfsProgress*);
#endif
