#ifndef RABBIT_BSS_SELECTION_H
#define RABBIT_BSS_SELECTION_H
#include "abi/rx.h"
#include "abi/persistent.h"
#include "copied/bss_security.h"
enum { QCA_SELECT_ACCEPTED=1,QCA_SELECT_OTHER=0,QCA_SELECT_POLICY=-10,QCA_SELECT_WIRE=-11,QCA_SELECT_SECURITY=-12,QCA_SELECT_FULL=-13 };
enum {QCA_SELECT_WPA2_PSK=1,QCA_SELECT_CCMP_PAIR=2,QCA_SELECT_CCMP_GROUP=4,QCA_SELECT_CAPS=7};
/* Evidence hashes are provenance, not signatures. Trusted caller must derive
 * these capabilities from reviewed native implementations, never AP IEs. */
typedef struct {
 uint64_t epoch,now_us,ttl_us;uint32_t rx_floor,live_frequency;
 uint16_t native_rates;uint8_t wmi_endpoint,active,ready_mac[6];
 uint32_t native_capabilities;uint8_t capability_source[32],policy_digest[32];
 uint8_t frequency_count;uint16_t frequencies[13];
} QcaSelectionContext;
typedef struct {
 QcaRxEvent owned;QcaBssSecurity security;uint64_t observed_us;
 uint32_t snr;int64_t estimated_signal_dbm;uint8_t present;
} QcaSelectedBss;
typedef struct {
 uint64_t epoch,last_observed_us;uint32_t watermark;
 QcaSelectionContext binding;QcaSelectedBss entries[8];
} QcaBssSelection;
/* Inputs are caller-owned copies after qca_rx_take, never live DMA views.
 * All rejected calls leave table/output unchanged and caller retains raw. */
int qca_selection_begin(QcaBssSelection*,const QcaSelectionContext*);
int qca_selection_offer(QcaBssSelection*,const QcaSelectionContext*,const QcaRxEvent*,uint64_t);
int qca_selection_best(const QcaBssSelection*,const QcaSelectionContext*,QcaSelectedBss*);
/* Production bridge: inspect the existing active persistent/READY/HTC/RX
 * owners, then accept the caller's already-taken CPU copy. No qca_rx_take,
 * hardware, ownership transfer, DMA release or fabricated completion here. */
int qca_selection_offer_live(QcaBssSelection*,const QcaSelectionContext*,const QcaPersistentNative*,const QcaRxEvent*,uint64_t);
#endif
