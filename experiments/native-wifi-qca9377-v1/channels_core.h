#ifndef RABBIT_QCA_CHANNELS_CORE_H
#define RABBIT_QCA_CHANNELS_CORE_H
#include "ce_bus.h"
#include "ce_ring.h"
#define QCA_CHANNEL_DIRECTIONS 7u
#define QCA_CHANNEL_BUFFERS 14u
typedef struct {QcaCeBus*bus;uint8_t pipe,receive;} QcaChannelRoute;
enum {QCA_CHANNEL_IDLE,QCA_CHANNEL_ALLOCATING,QCA_CHANNEL_READY,
 QCA_CHANNEL_CONFIGURED,QCA_CHANNEL_POSTED,QCA_CHANNEL_CLOSING,
 QCA_CHANNEL_CLOSED,QCA_CHANNEL_FAULT};
typedef struct {
 QcaCeBus*bus;QcaDmaBuffer buffers[QCA_CHANNEL_BUFFERS];
 QcaCeRing rings[QCA_CHANNEL_DIRECTIONS];QcaChannelRoute routes[QCA_CHANNEL_DIRECTIONS];
 uint8_t phase,allocated,cleanup_slot;uint32_t error;
} QcaChannels;
/* Zero initialize; exclusive empty access set, all eight engines stopped and
 * zeroed, bus-master OFF. One descriptor page + one data page per direction.
 * CE0TX/1RX/2RX/3TX/4TX/7TX+RX. CE5 host disabled, CE6 target autonomous.
 * prepare_step allocates at most one page; nothing starts DMA implicitly.
 */
int qca_channels_begin(QcaChannels*,QcaCeBus*);
int qca_channels_prepare_step(QcaChannels*);
int qca_channels_configure(QcaChannels*);
/* Reuse the same retained mappings after a separately verified reset/all-eight
 * stop. Close stale software rings, configure anew, without free/map/start. */
int qca_channels_reconfigure(QcaChannels*);
/* Native proof from these exact mapped buffers/rings, not caller JSON.
 * Does not authorize target RAM writes. After bus_start, post CE1/CE2 RX
 * once. CE7 RX is reserved for each diagnostic exchange, not pre-posted.
 */
int qca_channels_prepared(QcaChannels*);
/* Retained mapping inventory only; useful while warm reset temporarily changes
 * CE registers. No hardware state or permission to enable bus mastering implied. */
int qca_channels_retained(QcaChannels*);
int qca_channels_post_receive(QcaChannels*);
/* Caller must first perform bounded all-eight bus_stop/zero/BM-off.
 * Close at most one DMA buffer per step. Failed flush/unmap/free retains
 * the current buffer and cursor; caller bounds retries and refuses unload.
 */
int qca_channels_close_step(QcaChannels*);
#endif
