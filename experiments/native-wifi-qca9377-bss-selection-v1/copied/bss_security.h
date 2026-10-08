#ifndef RABBIT_BSS_SECURITY_H
#define RABBIT_BSS_SECURITY_H
#include "beacon_rx.h"
#include "rsn_core.h"
enum {QCA_BSS_CANDIDATE=1,QCA_BSS_NOT_TARGET=0,QCA_BSS_MALFORMED=-1,QCA_BSS_UNSUPPORTED=-2,QCA_BSS_POLICY=-3};
typedef struct {
 uint64_t expected_epoch,observed_epoch;uint32_t completion,start_floor,live_frequency;
 uint16_t native_rates;uint8_t ssid_bytes,ssid[32],policy_digest[32];
 uint8_t frequency_count;uint16_t frequencies[64];
} QcaBssContext;
typedef struct {
 QcaWmiBeaconRx beacon;QcaRsnFields rsn;
 uint32_t selected_pairwise,selected_akm,group_suite,pairwise_suites[16],akm_suites[16],management_suite;
 uint16_t rates,basic_rates,selected_rates,capabilities;uint8_t offered_rates[32],rate_count,pairwise_count,akm_count,pmf_capable,pmf_required,caps_present,management_present;
 uint8_t selected_pmf,rsnx[16],rsnx_bytes;uint64_t epoch;uint32_t completion;
} QcaBssSecurity;
/* Input is an actual owned/copied MGMT payload, not a DMA pointer. Context comes
 * from verified scan/policy/native legacy-rate capabilities, never from SSID.
 * All non-CANDIDATE returns preserve output. Candidate is eligibility only:
 * PSK/CCMP offered, optional PMF tolerated but required PMF unsupported; no AP
 * authentication, association, key-install/port authorization or network ready.
 * Native rate bits use {2,4,11,22,12,18,24,36,48,72,96,108} in500kbps units.
 * Epoch/live-channel/digest equality are structural binds, not authority proof. */
int qca_bss_security(const uint8_t*,unsigned,const QcaBssContext*,QcaBssSecurity*);
#endif
