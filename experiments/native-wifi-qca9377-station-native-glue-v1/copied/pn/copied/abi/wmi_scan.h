#ifndef RABBIT_QCA_WMI_SCAN_H
#define RABBIT_QCA_WMI_SCAN_H
#include <stdint.h>
typedef struct {const uint8_t *value;unsigned bytes,tag;} QcaWmiTlv;
typedef struct {uint32_t type,reason,frequency,request_id,scan_id,vdev;} QcaWmiScanEvent;
/* Iterator offset starts at zero, excludes the four-byte WMI command header.
 * Return 1 record, 0 end, -1 malformed. No output changes on malformed input. */
int qca_wmi_tlv(const uint8_t*,unsigned,unsigned*,QcaWmiTlv*);
int qca_wmi_scan_event(const uint8_t*,unsigned,unsigned,unsigned,QcaWmiScanEvent*);
/* Complete WMI message, not HTC frame. VDEV0, passive only, no SSID/BSSID/probe
 * IEs or credentials. Caller must first supply regulator-approved frequencies
 * and an initialized operational firmware/VDEV. This codec cannot enable radio. */
unsigned qca_wmi_passive_scan(uint8_t*,unsigned,unsigned,unsigned,const uint16_t*,unsigned);
#endif
