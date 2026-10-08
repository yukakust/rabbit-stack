#ifndef QCA_SCAN_EVENT_V2_H
#define QCA_SCAN_EVENT_V2_H
#include "wmi_scan.h"
/* 0 malformed/unsupported;1 bounded known scan prefix;2 owned unknown TLVs.
 * Known tag36 accepts >=24 bytes, extra suffix remains opaque in owned packet.
 * Reason is opaque here; terminal policy belongs to dispatcher/state machine. */
int qca_scan_event_v2(const uint8_t*,unsigned,QcaWmiScanEvent*);
int qca_scan_event_v2_match(const uint8_t*,unsigned,unsigned,unsigned,QcaWmiScanEvent*);
#endif
