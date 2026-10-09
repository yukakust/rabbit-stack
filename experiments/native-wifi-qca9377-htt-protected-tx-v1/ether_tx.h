#ifndef QCA_EXPERIMENTAL_ETH_TX
#define QCA_EXPERIMENTAL_ETH_TX
#include "copied/key_operation.h"
enum {QETH_CONFIG_QUEUED=1,QETH_CONFIG_PUBLISHED,QETH_CONFIG_DMA_DONE,QETH_FAULT};
typedef struct {QsgNative*station;QcaPersistentTx*publisher;uint64_t epoch,last,deadline;uint32_t phase,error,request,cookie,dma_serial,pending_id;} QethPolicy;
/* Experimental bounded Ethernet2/nonQoS16 policy. Source definitions and real
 * DMA prove bytes/publication only, not established target interoperability. */
int qeth_policy_begin(QethPolicy*,QsgNative*,uint64_t);
int qeth_policy_poll(QethPolicy*,uint64_t);
/* Returns 1 only for both owned completions and HTT OK; other outcomes revoke. */
int qeth_poll_result(QethPolicy*,uint64_t);
int qeth_submit(QethPolicy*,const QsgKeyOp*ptk,const QsgKeyOp*gtk,const uint8_t*ether,unsigned bytes,uint16_t nonreused_id,uint64_t);
#endif
