#ifndef RABBIT_QCA_PERSISTENT_RX_H
#define RABBIT_QCA_PERSISTENT_RX_H
#include "startup.h"
#include "lifecycle.h"
#include "version.h"
#include <stddef.h>
enum {QCA_RX_ACTIVE=1,QCA_RX_FAULT,QCA_RX_CLEARED};
typedef struct {
 uint32_t completion,event;uint16_t bytes;uint8_t endpoint,pipe;
 uint16_t raw_bytes;
 union {uint8_t raw[2048];struct {uint8_t htc_header[8],payload[2040];};};
} QcaRxEvent;
_Static_assert(offsetof(QcaRxEvent,payload)==offsetof(QcaRxEvent,raw)+8,"HTC payload byte-view offset");
_Static_assert(sizeof(((QcaRxEvent*)0)->raw)==2048&&sizeof(((QcaRxEvent*)0)->payload)==2040,"one exact owned HTC image");
typedef struct {
 QcaWmiStartup*startup;const QcaRadioLifecycle*life;uint64_t last,epoch;
 uint32_t phase,error,completed,posted_count,next_cookie,cookie[2];
 QcaHttBinding htt;uint8_t posted[2],head,count,backpressure;QcaRxEvent events[2],rejected;
} QcaPersistentRx;
/* Borrows actual startup RX1/2 descriptors + shared HTC ledger. No new DMA.
 * Caller exclusively owns startup/CE state; radio must have validated READY.
 * 1 success /0 rejected; no hardware access in begin. */
int qca_rx_begin(QcaPersistentRx*,QcaWmiStartup*,const QcaRadioLifecycle*,uint64_t);
/* At most one actual completion per pipe per call. Full FIFO causes bounded
 * backpressure: descriptors/buffers remain owned, no new posts or dropped data.
 * 1 healthy /0 caller quiesced (no hardware touch) /-1 retained fault.
 * Unknown payloads are owned copies for a later dispatcher, never ACKed.
 */
int qca_rx_poll(QcaPersistentRx*,const QcaRadioLifecycle*,uint64_t);
/* Consume FIFO head by its actual completion ID; caller receives a copy.
 * Wrong/repeated ID or short output leaves queue unchanged. */
int qca_rx_take(QcaPersistentRx*,uint32_t,QcaRxEvent*,unsigned);
/* Reset/discard only after actual all-owner release proved by lifecycle. */
int qca_rx_clear(QcaPersistentRx*,const QcaRadioLifecycle*);
#endif
