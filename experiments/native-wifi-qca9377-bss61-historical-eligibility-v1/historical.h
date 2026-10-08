#include "bss_security.h"
typedef struct {
 uint32_t generation,quiescent,owners_released,live_frequency,observed_frequency;
 uint64_t expected_epoch,observed_epoch;
 uint32_t completion,start_floor,terminal_completion;
 uint8_t expected_policy[96],observed_policy[96],ssid_bytes,ssid[32];
} QcaHistoricalContext;
typedef struct {
 QcaBssSecurity advertisement;
 uint32_t live_frequency,observed_frequency;
 uint16_t required_basic_rates,advertised_known_rates,native_capabilities;
 uint8_t native_capabilities_proved,fresh_live_BSS_required,association_authority,port_authority;
} QcaHistoricalBss;
/* Historical advertisement eligibility only. No live radio/native rate claim. */
int qca_historical_bss(const uint8_t*,unsigned,const QcaHistoricalContext*,QcaHistoricalBss*);
/* Optional proof supplied by a validated driver, not guessed from advertisement.
 * Success remains historical and still requires fresh live BSS revalidation. */
int qca_historical_native_rates(const QcaHistoricalBss*,uint16_t caller_proved_mask,int proof_valid);
