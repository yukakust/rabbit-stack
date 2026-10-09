#ifndef RABBIT_TLS_CIPHERTEXT_PUMP
#define RABBIT_TLS_CIPHERTEXT_PUMP
#include <stdint.h>
#include <stddef.h>
enum{TP_FRAGMENT=240};
typedef struct {
 void*context;size_t context_bytes;
 int(*clock)(void*,uint64_t*);
 int(*feed)(void*,uint64_t,uint32_t,const uint8_t*,size_t);
 int(*poll)(void*,uint64_t,uint64_t);
 int(*drain)(void*,uint64_t,uint8_t*,size_t);
 int(*revoke)(void*,uint64_t);
} TpOps;
typedef struct {
 TpOps ops;uint64_t epoch,last,deadline;
 uint8_t incoming[TP_FRAGMENT],previous[TP_FRAGMENT],outgoing[TP_FRAGMENT];
 uint32_t rx_next,rx_previous,tx_next,tx_current,tx_acked;
 uint32_t incoming_bytes,previous_bytes,outgoing_bytes;
 unsigned bound,busy,fault,revoke_notified,closed,error,acked_valid;
} TlsCipherPump;
/* Parent-private activation only after current identity/owner/physical full-pin
 * policy. No RNG, key, peer approval or plaintext API. Callbacks are genuine
 * typed leased-child adapters and never executed on an ATT callback stack. */
int tp_bind(TlsCipherPump*,const TpOps*,uint64_t,uint64_t,uint64_t);
/* ATT ingress only stages ciphertext. Exact retransmits are idempotent. No feed/poll/drain/revoke provider is called from these APIs. */
int tp_offer(TlsCipherPump*,uint64_t,uint32_t,const uint8_t*,size_t,uint64_t);
/* View returns byte count, zero empty, -2 insufficient destination, -1 fault. */
int tp_view(TlsCipherPump*,uint64_t,uint8_t*,size_t,uint32_t*,uint64_t);
int tp_ack(TlsCipherPump*,uint64_t,uint32_t,uint64_t);
void tp_disconnected(TlsCipherPump*);
/* Sole privileged loop, outside all HCI/ATT callbacks. */
int tp_poll(TlsCipherPump*,uint64_t,uint64_t);
int tp_close(TlsCipherPump*,uint64_t);
#endif
