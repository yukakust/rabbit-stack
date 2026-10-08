#ifndef RABBIT_QCA_BEACON_INFO_H
#define RABBIT_QCA_BEACON_INFO_H
#include <stdint.h>
typedef struct {
 uint8_t bssid[6],ssid[32],rsn[255];
 unsigned ssid_bytes,rsn_bytes,channel,hidden,privacy,wpa_vendor;
 uint16_t interval,capabilities;
} QcaBeaconInfo;
/* Input is one complete ordinary beacon/probe-response 802.11 frame, with
 * firmware framing and any FCS already removed by its validated RX owner.
 * Return 0 parsed, -1 rejected; rejection never changes caller output.
 * RSN stays opaque: this does NOT validate security, authenticate an AP,
 * authorize a channel, select a cipher, associate or access credentials. */
int qca_beacon_info(const uint8_t*,unsigned,QcaBeaconInfo*);
int qca_beacon_ssid_matches(const QcaBeaconInfo*,const uint8_t*,unsigned);
#endif
