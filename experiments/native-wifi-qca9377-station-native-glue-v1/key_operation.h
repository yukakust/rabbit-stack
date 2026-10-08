#ifndef RABBIT_REAL_WMI_KEY_OPERATION_H
#define RABBIT_REAL_WMI_KEY_OPERATION_H
#include "glue.h"
#include "tx.h"
#include "copied/pn/pn.h"
enum {QSK_QUEUED=1,QSK_POSTED,QSK_CONFIRMED,QSK_FAULT};
typedef struct {QsgNative*glue;QcaPersistentTx*tx;QpnLedger*pn;uint64_t epoch,last,deadline;uint32_t request,pub_floor,pub_cookie,dma_serial;uint8_t phase,index,sec_seen,dma_seen;uint8_t rsc[6];unsigned rsc_bytes;QcaRxEvent sec_raw,rejected;} QsgKeyOp;
/* Copies actual caller key into real persistent CE3 publisher. It does not
 * return a mature success until qsk_poll reports actual DMA+fresh SEC_IND.
 * One first installation per index; no deletion/rekey/port opening. */
int qsk_begin(QsgKeyOp*,QsgNative*,QcaPersistentTx*,QpnLedger*,unsigned,const uint8_t*,unsigned,const uint8_t*,unsigned,uint64_t);
int qsk_poll(QsgKeyOp*,uint64_t);
int qsk_receive(QsgKeyOp*,const QcaRxEvent*,uint64_t);
void qsk_revoke(QsgKeyOp*,unsigned);
#endif
