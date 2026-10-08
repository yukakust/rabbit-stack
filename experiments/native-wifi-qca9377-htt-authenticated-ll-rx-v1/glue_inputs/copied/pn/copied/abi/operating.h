#ifndef RABBIT_QCA_OPERATING_H
#define RABBIT_QCA_OPERATING_H
#include "boot_native.h"
#include "htc_control.h"
#include "wmi_boot_info.h"
#include "available.h"
typedef struct {
 QcaBootNative*boot;QcaHtcControl control;QcaWmiServiceInfo service;
 uint64_t started,last;uint32_t phase,error,tx_count,rx_count,service_bytes;
 QcaWmiAvailable available;uint32_t available_seen;
 uint8_t rx1_posted,rx2_posted,cancelled,service_valid;
 uint32_t rx_diagnostic[10];uint8_t rx_descriptor[8],rx_prefix[64];
 uint8_t service_frame[2048];
} QcaOperating;
/* Exclusive handoff AFTER actual HTC READY, without stopping the adapter or
 * dropping the exact firmware pin. No buffer may already be posted. */
int qca_operating_begin(QcaOperating*,QcaBootNative*,uint64_t);
/* Bounded diagnostic lifetime:0 waiting,1 handshake+SERVICE_READY validated,
 * -1 fault. ALL outcomes retain actual DMA/adapter/firmware ownership. Caller
 * must poll the existing all-engine stop/cleanup before release or replacement.
 * No WMI INIT, scan, credentials, association, IP or arbitrary traffic. */
int qca_operating_poll(QcaOperating*,uint64_t);
void qca_operating_cancel(QcaOperating*);
#endif
