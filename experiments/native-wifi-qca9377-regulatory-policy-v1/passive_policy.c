#include "passive_policy.h"
int rabbit_ge_world108_passive(const char country[2], uint32_t regdomain,
    uint32_t low_mhz, uint32_t high_mhz, uint32_t f, uint32_t width,
    struct rabbit_passive_channel *out) {
    struct rabbit_passive_channel c;
    if (!country || !out || country[0]!='G' || country[1]!='E' || regdomain!=108)
        return -1;
    if (width!=20 || low_mhz>high_mhz || f<2412 || f>2472 || (f-2412)%5)
        return -1;
    /* Full occupied 20 MHz must fit GE2402..2482 and the board rule.
     * f is now small and bounded, so +/-10 cannot overflow. */
    if (f-10<low_mhz || f+10>high_mhz) return -1;
    if (f<=2462) {
        if (f-10<2402 || f+10>2472) return -1;
        c.flags=0;
    } else {
        if (f-10<2457 || f+10>2482) return -1;
        c.flags=2; /* NO_IR, retained from board world12/13 rule */
    }
    c.frequency_mhz=f; c.centre1_mhz=f; c.centre2_mhz=0;
    c.width_mhz=20; c.passive=1; c.mode=1; /* narrow legacy11G */
    c.max_power_dbm=20; c.max_reg_power_dbm=20;
    c.antenna_gain_db=0; /* board-rule max gain parameter, not measured gain */
    *out=c; return 0;
}
