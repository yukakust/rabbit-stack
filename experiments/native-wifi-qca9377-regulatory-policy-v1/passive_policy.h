#ifndef RABBIT_PASSIVE_POLICY_H
#define RABBIT_PASSIVE_POLICY_H
#include <stdint.h>
struct rabbit_passive_channel {
    uint32_t frequency_mhz, centre1_mhz, centre2_mhz;
    uint32_t flags, passive, width_mhz, mode;
    uint32_t max_power_dbm, max_reg_power_dbm, antenna_gain_db;
};
/* Pure metadata filter, NOT an authentication or RF authorization gate.
 * Calling integration must verify the signed ruleset and provenance artifact.
 * Output remains untouched on rejection. Capability interval is only intersected
 * with the reviewed GE / unchanged WORC_WORLD108 20 MHz profile. */
int rabbit_ge_world108_passive(const char country[2], uint32_t regdomain,
    uint32_t low_mhz, uint32_t high_mhz, uint32_t frequency_mhz,
    uint32_t width_mhz, struct rabbit_passive_channel *out);
#endif
