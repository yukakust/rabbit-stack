#ifndef RABBIT_STATION_SCAN_H
#define RABBIT_STATION_SCAN_H
#include "htc_credit.h"
#include "wmi_boot_info.h"
enum {QCA_STA_READY=1,QCA_STA_CREATE_RESERVED,QCA_STA_CREATE_POSTED,QCA_STA_CREATE_ORDERED,QCA_STA_SCAN_RESERVED,QCA_STA_SCAN_POSTED,QCA_STA_SCAN_WAIT,QCA_STA_SCAN_TERMINAL,QCA_STA_CANCELLED,QCA_STA_FAULT};
enum {QCA_SCAN_NONE=0,QCA_SCAN_ACTIVE,QCA_SCAN_DONE,QCA_SCAN_FAILED};
typedef struct {
 QcaHtcCredit *credit;unsigned phase,result,frame_bytes,count,scan,request;
 uint32_t ticket,last_rx;uint8_t mac[6],sequence,started;uint16_t frequencies[64];
 uint8_t frame[388];QcaWmiScanEvent last_event;
} QcaStationScan;
/* Pure preparation only. ready is the actual validated WMI READY payload.
 * approved frequencies must come from independently reviewed country/channel
 * policy already configured on device, NOT SERVICE_READY band limits. policy
 * approval cannot be established by this codec. Exclusive credit ledger owner.
 * Fixed VDEV0. No credentials/SSID probing. Caller retains all live DMA owners. */
int qca_station_scan_begin(QcaStationScan*,QcaHtcCredit*,const uint8_t*,unsigned,const uint16_t*,unsigned,unsigned,unsigned,uint8_t);
int qca_station_scan_prepare_create(QcaStationScan*);
int qca_station_scan_prepare_scan(QcaStationScan*);
/* Commit BEFORE publishing CE3 descriptor. Failure after publication is fault,
 * not cancel. TX completion only permits ordering; it never proves acceptance
 * or refunds credit. STARTED event proves scan acceptance, not association. */
int qca_station_scan_post(QcaStationScan*);
int qca_station_scan_complete(QcaStationScan*,unsigned);
/* Consecutive IDs refer to actual consumed RX completion descriptors, not hashes
 * or firmware IDs. Decoder failures publish no state/credit. No replay security.
 * Early scan events retained until exact TX completion. */
int qca_station_scan_receive(QcaStationScan*,const uint8_t*,unsigned,uint32_t);
int qca_station_scan_cancel(QcaStationScan*);
void qca_station_scan_fault(QcaStationScan*);
#endif
