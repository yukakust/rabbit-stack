#ifndef RABBIT_WMI_BEACON_RX_H
#define RABBIT_WMI_BEACON_RX_H
#include <stdint.h>
#include "beacon_info.h"
enum {
 QCA_BEACON_RX_ACCEPTED=1,
 QCA_BEACON_RX_OTHER_EVENT=0,
 QCA_BEACON_RX_MALFORMED=-1,
 QCA_BEACON_RX_UNSUPPORTED=-2
};
typedef struct {
 uint32_t channel,frequency_mhz,snr,rate,phy_mode,buf_len,status,rssi[4];
 unsigned platform_private;
 QcaBeaconInfo bss;
} QcaWmiBeaconRx;
/* Input starts at WMI cmd/event header AFTER validated HTC/trailer removal.
 * Output must not alias input. Pure parser copies accepted BSS/metadata;
 * never owns/releases/changes RX with that caller contract.
 * All non-ACCEPTED returns leave output untouched and caller retains input.
 * Only unextended status-OK 2.4 GHz beacon/probe-response frames are supported.
 * No policy/epoch/AP-authentication/SSID-discovery authority is granted here. */
int qca_wmi_beacon_rx(const uint8_t *,unsigned,QcaWmiBeaconRx *);
#endif
