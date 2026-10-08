#ifndef RABBIT_HTT_RING_H
#define RABBIT_HTT_RING_H
#include <stdint.h>
#include <stddef.h>
enum {Q_RING_SIZE=2048,Q_RING_FILL=1023,Q_RX_BYTES=2048,Q_RING_MAPS=33,Q_RING_SLABS=32,Q_RING_BUFFERS=1024,Q_RING_CFG_BYTES=40,Q_RING_REFILL_BUDGET=100};
enum {Q_RING_NEW=0,Q_RING_FILLING=1,Q_RING_CFG_TRANSFERRED=2,Q_RING_QUIESCED=3,Q_RING_CLOSED=4,Q_RING_FAULT=5};
enum {Q_BUFFER_AVAILABLE=0,Q_BUFFER_POSTED=1,Q_BUFFER_OWNED=2,Q_BUFFER_RESERVED=3};
typedef struct {uint64_t identity,epoch,paddr;uint32_t bytes;uint8_t actual_map_valid,coherent_common,allocated_masteroff;} QRingMap;
typedef struct {uint64_t epoch;uint16_t buffer,slot,producer_after;uint32_t buffer_paddr,attention_clear_offset,address_entry_offset,shadow_publish_offset;} QRingRefill;
typedef struct {uint8_t attention_cleared,buffer_visible,address_visible,device_barrier_complete,actual_index_published;} QRingPublishProof;
typedef struct {uint64_t epoch,completion;uint8_t target_halted,bme_off,callbacks_stopped,device_write_barrier;} QRingQuiesceProof;
typedef struct {
 uint64_t epoch;uint32_t phase,fill,producer;uint16_t slot_buffer[Q_RING_SIZE],buffer_slot[Q_RING_BUFFERS];uint8_t buffer_state[Q_RING_BUFFERS],map_released[Q_RING_MAPS];
 QRingMap maps[Q_RING_MAPS];QRingRefill pending;uint8_t pending_valid,cfg_serialized,cfg_posted;uint16_t released_maps;uint64_t last_indication_completion;
} QRingState;
/* Maps must be proven actual, separately from booleans. Pure structural policy
 * never allocates/syncs/publishes DMA or confirms hardware. State must start
 * zero NEW or actual fully released CLOSED. Out unchanged reject. */
int qca_ring_bind(QRingState*,const QRingMap maps[Q_RING_MAPS],uint64_t epoch,uint32_t firmware_op,uint32_t target_type,uint32_t target_version);
int qca_ring_reserve(QRingState*,uint16_t buffer,QRingRefill*);
int qca_ring_publish(QRingState*,const QRingRefill*,const QRingPublishProof*);
int qca_ring_cfg(QRingState*,uint32_t actual_shadow_index,uint8_t out[Q_RING_CFG_BYTES]);
int qca_ring_cfg_posted(QRingState*,uint64_t epoch,uint64_t actual_RX_floor);
int qca_ring_cfg_dma_complete(QRingState*,uint64_t epoch,uint64_t actual_CE4_completion);
/* Caller must first validate whole actual HTT indication, DMA acquire and
 * descriptor boundaries. No authority comes from IDs alone. */
int qca_ring_claim(QRingState*,const uint16_t*,unsigned,uint64_t epoch,uint64_t actual_indication_completion);
int qca_ring_copied(QRingState*,uint16_t buffer,uint64_t epoch,int actual_dma_acquired,int owned_copy_complete);
int qca_ring_quiesce(QRingState*,const QRingQuiesceProof*);
int qca_ring_map_released(QRingState*,uint64_t actual_map_identity,uint64_t epoch,int actual_release_success);
#endif
