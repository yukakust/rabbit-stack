#ifndef QCA_HTT_NATIVE_H
#define QCA_HTT_NATIVE_H
#include "persistent.h"
#include "version.h"
enum {QCA_HTTN_POSTED=1,QCA_HTTN_STOPPING,QCA_HTTN_RELEASED,QCA_HTTN_FAULT,QCA_HTTN_READY};
typedef struct {
 QcaPersistentNative *radio;QcaHttBinding binding;uint64_t epoch,last,deadline;
 uint32_t phase,error,cookie,watermark,attempted,dma_completed,consumed;
 uint8_t stop_requested,version_seen,archive_count;QcaHttVersion version;
 /* NEW63: caller-owned disjoint static storage, 3 events; no DMA alias. */
 QcaRxEvent *response,*archive;uint32_t response_completion;
} QcaHttNative;
int qca_htt_native_begin(QcaHttNative*,QcaPersistentNative*,unsigned,uint64_t,QcaRxEvent*,unsigned);
/* Sole CE4 publisher; persistent radio includes sole combined CE1/2 pump.
 * 1 released successful query;0 pending; -1 retained fault. */
int qca_htt_native_poll(QcaHttNative*,uint64_t);
/* Read-only exact retained raw slot copy: response0/archive1,2/RX-head3,next4/rejected5; no write ACK. */
int qca_htt_native_export(const QcaHttNative*,unsigned,QcaRxEvent*,unsigned);
#endif
