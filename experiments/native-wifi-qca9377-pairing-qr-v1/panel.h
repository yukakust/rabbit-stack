#ifndef RABBIT_PUBLIC_PAIRING_QR_PANEL
#define RABBIT_PUBLIC_PAIRING_QR_PANEL
#include <stdint.h>
#include <stddef.h>
#include "reference/qrcodegen.h"
#define QR_MAX_VERSION 6
#define QR_BUF qrcodegen_BUFFER_LEN_FOR_VERSION(QR_MAX_VERSION)
typedef struct {uint8_t symbol[QR_BUF],spki_sha256[32];char text[96];uint64_t epoch,created,expires;uint32_t ready,size;} PairingPanel;
/* Pure PUBLIC renderer, never identity/entropy/pairing authority. Native caller
 * must supply full SHA256(DER-SPKI) from leased actual Dell-created identity,
 * not a host/GATT-controlled value, and clear it when that key is retired. */
int qr_panel_bind(PairingPanel*,uint64_t,const uint8_t[32],uint64_t us);
int qr_panel_live(const PairingPanel*,uint64_t,uint64_t us);
int qr_panel_paint(const PairingPanel*,uint64_t,uint64_t us,uint32_t*,size_t bytes,unsigned width,unsigned height,unsigned stride,unsigned x,unsigned y,unsigned scale);
void qr_panel_clear(PairingPanel*);
#endif
