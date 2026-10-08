#ifndef QCA_HTT_PERSISTENT_DMA_RUNTIME_H
#define QCA_HTT_PERSISTENT_DMA_RUNTIME_H
#include "dma_buffer.h"
#include "ring.h"
#include "rx_decode.h"
enum {HTT_RUNTIME_EMPTY,HTT_RUNTIME_ALLOCATING,HTT_RUNTIME_MAPPED,HTT_RUNTIME_ACTIVE,HTT_RUNTIME_CLOSING,HTT_RUNTIME_CLOSED,HTT_RUNTIME_FAULT};
typedef struct {
 QcaUefiPort*port;QcaDmaBuffer*ce;QcaDmaStop stop;void*stop_context;
 uint64_t epoch;unsigned phase,error,allocated,cleanup;
 QcaDmaBuffer extra[33];QRingMap maps[33];QRingState ring;QRxOwner owners[2048];
 uint32_t callback_owners,rx_copy_owners,tx_owners;uint8_t service65_proven;
} QcaHttRuntime;
/* Caller supplies separately owned aligned pool, not image BSS. Only real
 * qca_dma_open populates33 extra mappings; full47 inventory is measured.
 * PCI method provenance/lifetime and trusted epoch remain caller obligations. */
int qca_htt_runtime_begin(QcaHttRuntime*,QcaUefiPort*,QcaDmaBuffer ce[14],uint64_t,QcaDmaStop,void*);
int qca_htt_runtime_allocate_one(QcaHttRuntime*);
int qca_htt_runtime_inventory(QcaHttRuntime*);
int qca_htt_runtime_bind_ring(QcaHttRuntime*,unsigned firmware_op,unsigned target_type,unsigned target_version);
/* Conservative release: actual DMA close calls stop/BME readback/Flush/Unmap/
 * FreeBuffer. Caller stop must additionally prove HTT target+callbacks stopped;
 * CE-only halt is insufficient. No ACTIVE detach or guessed release count. */
/* Actual common-buffer CPU writes + C seq-cst barrier + aligned producer index;
 * native platform coherency must be proven, no CE4 target configuration implied. */
int qca_htt_runtime_refill_one(QcaHttRuntime*,uint16_t);
int qca_htt_runtime_close_one(QcaHttRuntime*);
int qca_htt_runtime_detachable(const QcaHttRuntime*);
#endif
