#ifndef QCA_PERSISTENT_HTT_DATA_PATH_H
#define QCA_PERSISTENT_HTT_DATA_PATH_H
#include "dma_runtime.h"
#include "htt_native.h"
#include "wmi_boot_info.h"
#include "query_handover.h"
enum { QDP_FILLING=1,QDP_CFG_POSTED,QDP_RX_ACTIVE,QDP_QUARANTINED,QDP_QUIESCED,QDP_AGGR_POSTED };
typedef struct {
 QcaHttRuntime*runtime;QcaPersistentNative*radio;QcaHttBinding binding;
 uint64_t epoch,last,floor,tx_floor,ce_completions,transfer_deadline;uint32_t phase,error,cfg_cookie,cfg_bytes,aggr_cookie;uint8_t aggr_done;
 QcaRxEvent version_raw;uint8_t service_raw[2048];unsigned service_bytes;
 QRxRing rx;QRxInd pending;unsigned pending_index,pending_valid;
 QRxFrame output[4];uint32_t output_paddr[4];uint64_t output_completion[4];unsigned output_head,output_count;
 QRxOwner validation_owners[1023];uint8_t rejected_raw[2048];unsigned rejected_bytes;
 uint32_t tx_cookie,tx_bytes,tx_id,tx_status;uint8_t tx_posted,tx_dma_done,tx_htt_done;
 uint64_t tx_rx_completion;uint8_t tx_raw[2048];unsigned tx_raw_bytes;
} QcaHttDataPath;
/* Adopts ONLY a completed actual query, then revokes that query's publisher.
 * Does not grant association/key/controlled-port/IP authority. */
int qdp_begin(QcaHttDataPath*,QcaHttRuntime*,QcaPersistentNative*,QcaHttNative*,QcaNativeScan*owned_capture,uint64_t now);
int qdp_refill_initial(QcaHttDataPath*,uint64_t now); /* one real buffer publication */
int qdp_publish_cfg(QcaHttDataPath*,uint64_t now);
int qdp_publish_aggr(QcaHttDataPath*,uint64_t now);
int qdp_poll_dma(QcaHttDataPath*,uint64_t now);
/* Exact taken owned event; callback already applied HTC credits. This adapter
 * never updates that ledger. Backpressure0 leaves input caller-owned. */
int qdp_receive(QcaHttDataPath*,const QcaRxEvent*,uint64_t now);
int qdp_copy_one(QcaHttDataPath*,uint64_t now);
int qdp_take_frame(QcaHttDataPath*,QRxFrame*,uint64_t*completion);
/* Serialization/ownership transport only. Caller must supply independently
 * admitted station TX, local current keys and controlled-port semantics. */
int qdp_submit_raw(QcaHttDataPath*,const uint8_t*,unsigned,uint16_t id,unsigned vdev,unsigned tid,uint64_t now);
int qdp_submit_mgmt(QcaHttDataPath*,const uint8_t*,unsigned,uint16_t id,unsigned vdev,uint64_t now);
/* Without reviewed target-stop backend, stop is QUARANTINED with live map
 * owners. CE halt or a caller boolean cannot synthesize a release proof. */
void qdp_quarantine(QcaHttDataPath*,unsigned error);
#endif
