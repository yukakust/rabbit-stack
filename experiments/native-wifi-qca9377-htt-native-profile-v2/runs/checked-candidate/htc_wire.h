#ifndef RABBIT_QCA_HTC_WIRE_H
#define RABBIT_QCA_HTC_WIRE_H
#include <stdint.h>
#define QCA_HTC_ENDPOINTS 9u
#define QCA_HTC_FRAME_LIMIT 4096u
#define QCA_HTC_WMI 0x100u
#define QCA_HTC_HTT 0x300u
typedef struct {
 const uint8_t *payload;
 unsigned payload_bytes;
 uint16_t credits[QCA_HTC_ENDPOINTS];
 uint8_t endpoint;
} QcaHtcFrame;
typedef struct {
 uint16_t credits,credit_size,alt_credit_size;
 uint8_t endpoints,version,max_bundle;
} QcaHtcReady;
typedef struct {uint16_t service,max_bytes;uint8_t endpoint;} QcaHtcConnection;
/* Single unbundled PCI frame. Validate every trailer before publishing any
 * payload/credit update. Bundles and unknown records fail closed. No DMA/MMIO. */
int qca_htc_decode(const uint8_t *,unsigned,QcaHtcFrame *);
int qca_htc_ready(const QcaHtcFrame *,QcaHtcReady *);
int qca_htc_connection(const QcaHtcFrame *,unsigned,QcaHtcConnection *);
/* Full HTC wire frames, including endpoint-zero header; no bundling. */
unsigned qca_htc_connect(uint8_t *,unsigned,unsigned,unsigned,uint8_t);
unsigned qca_htc_setup(uint8_t *,unsigned,uint8_t);
unsigned qca_htc_header(uint8_t *,unsigned,unsigned,unsigned,uint8_t,int);
#endif
