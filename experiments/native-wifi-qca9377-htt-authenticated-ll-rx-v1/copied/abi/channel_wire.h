#ifndef RABBIT_QCA_CHANNEL_WIRE_H
#define RABBIT_QCA_CHANNEL_WIRE_H
#include <stdint.h>
enum {QCA_POLICY_DISABLED=1,QCA_POLICY_NO_IR=2,QCA_POLICY_RADAR=4};
typedef struct {
 uint32_t frequency,centre1,centre2,width,flags,passive,mode;
 uint32_t max_power_dbm,max_reg_power_dbm,antenna_gain_db;
} QcaPolicyChannel;
typedef struct {
 uint8_t target[32];uint32_t regdomain,low2,high2,low5,high5;
} QcaChannelHardware;
typedef struct {
 uint32_t version,hardware_regdomain,regdomain,regdomain2,regdomain5,ctl2,ctl5;
 uint8_t target[32],reviewed_digest[32],ruleset_digest[32],location_digest[32],alpha2[2];
 uint32_t count;QcaPolicyChannel channels[64];
} QcaReviewedChannelPolicy;
/* PURE full WMI payloads, not HTC/MMIO. Caller must independently authenticate
 * and approve policy provenance and actual hardware binding before invoking.
 * Nonzero digests are structural references, NOT authority or RF admission.
 * No default country/frequencies. Narrow passive legacy20 profile, no probes,
 * IBSS/HT/VHT/DFS-country override. NO_IR and RADAR stay passive; DISABLED rejected.
 * Powers provided in whole dBm, encoded in 0.5dBm; antenna in whole dB.
 * negotiated_limit is actual WMI payload max, not an inferred radio capability.
 * Rejection changes no output. Output must not overlap policy/hardware. */
unsigned qca_scan_channels_wire(uint8_t*,unsigned,const QcaReviewedChannelPolicy*,const QcaChannelHardware*,unsigned);
unsigned qca_pdev_regdomain_wire(uint8_t*,unsigned,const QcaReviewedChannelPolicy*,const QcaChannelHardware*,unsigned);
#endif
