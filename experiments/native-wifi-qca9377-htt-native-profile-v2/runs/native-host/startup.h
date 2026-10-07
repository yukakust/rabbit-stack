#ifndef RABBIT_QCA_WMI_NATIVE_STARTUP_H
#define RABBIT_QCA_WMI_NATIVE_STARTUP_H
#include "operating.h"
#include "init_transaction.h"
#include "resources.h"
typedef struct {
 QcaOperating*operating;QcaWmiInitTransaction transaction;QcaTlvResources resources;
 uint64_t started,last;uint32_t phase,error,tx_posted,rx_count,tx_count;
 uint32_t diagnostic[10],reject_reason,frame_bytes,prefix_bytes,frame_endpoint,payload_bytes;uint8_t prefix[128],rx1_posted,rx2_posted,cancelled;
} QcaWmiStartup;
/* Bounded real CE1/2/3 WMI INIT candidate. Only validated zero memory requests
 * supported: NEVER allocate while current bus master is active. Borrows all14
 * existing retained mappings, adapter and exact firmware pin. No RF/credentials.
 * 0 waiting,1 INIT TX actually complete + WMI READY parsed,-1 fault.
 * Every result keeps actual owners: outer probe must stop/flush/unmap/free.
 */
int qca_wmi_startup_begin(QcaWmiStartup*,QcaOperating*,uint64_t);
int qca_wmi_startup_poll(QcaWmiStartup*,uint64_t);
void qca_wmi_startup_cancel(QcaWmiStartup*);
#endif
