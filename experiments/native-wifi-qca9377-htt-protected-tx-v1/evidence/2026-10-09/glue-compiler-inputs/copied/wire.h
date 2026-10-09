#ifndef RABBIT_STATION_WIRE_H
#define RABBIT_STATION_WIRE_H
#include <stdint.h>
/* Pure bytes, never command/RF admission. Binding hashes are caller source
 * provenance, not an arbitrary bool granting native radio capability. */
typedef struct {
 uint64_t epoch,observed_us,ttl_us;uint32_t completion,frequency,rx_floor;uint16_t interval,dtim,native_rates,basic_rates;
 uint8_t peer[6],own[6],policy_digest[32],native_source[32];
 uint8_t ssid[32],ssid_bytes,vdev,mode,min_power,max_power,reg_power,antenna;
} StaWireBss;
unsigned sta_wmi_start(uint8_t*,unsigned,const StaWireBss*);
unsigned sta_wmi_up(uint8_t*,unsigned,const StaWireBss*,uint16_t);
unsigned sta_wmi_assoc(uint8_t*,unsigned,const StaWireBss*,uint16_t,uint16_t,uint16_t,uint16_t);
/* seq is preserved externally in pending-key/host RX PN state. Exact pinned
 * upstream generator does not encode seq in its args. Nonzero sequence bytes
 * are unsupported here until that RX-PN integration is genuinely implemented. */
unsigned sta_wmi_key(uint8_t*,unsigned,const StaWireBss*,unsigned,const uint8_t*,unsigned,const uint8_t*,unsigned);
unsigned sta_auth_frame(uint8_t*,unsigned,const StaWireBss*,uint16_t);
unsigned sta_assoc_frame(uint8_t*,unsigned,const StaWireBss*,uint16_t,uint16_t,uint16_t);
#endif
