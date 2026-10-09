#ifndef RABBIT_QR_PAINT_ONLY
#define RABBIT_QR_PAINT_ONLY
#include "reference/panel.h"
/* PUBLIC bytes only. Caller obtains this from exact leased identity child and
 * clears/revokes on identity expiry or code epoch change. No host pin input. */
int qp_live(const PairingPanel*,uint64_t,uint64_t);
int qp_paint(const PairingPanel*,uint64_t,uint64_t,uint32_t*,size_t,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned);
#endif
