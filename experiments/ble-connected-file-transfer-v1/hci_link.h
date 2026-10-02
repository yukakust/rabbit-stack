#ifndef RABBIT_HCI_LINK_H
#define RABBIT_HCI_LINK_H
#include "gatt_core.h"
#define RL_ACL_MAX 251u
#define RL_TX_SLOTS 16u
enum { RL_CONFIGURING,RL_ADVERTISING,RL_CONNECTED,RL_FAULT,RL_STOPPED };
typedef struct {
 RgServer gatt;
 uint8_t rx[RL_ACL_MAX],wire[RL_ACL_MAX+4],queue[RL_TX_SLOTS][RL_ACL_MAX+4];
 uint16_t qlen[RL_TX_SLOTS],rx_used,rx_goal,handle,acl_size,credits,buffers,inflight,pending;
 uint32_t waited;
 uint8_t step,state,head,count,shared,connected,command_credits;
 uint16_t wire_used;
} RlLink;
/* ONE supervisor-owned pump calls these; never a second interrupt reader. */
void rl_init(RlLink *,RfApply);
void rl_event(RlLink *,const uint8_t *,size_t);
void rl_acl(RlLink *,const uint8_t *,size_t);
void rl_bulk(RlLink *,const uint8_t *,size_t); /* USB byte stream, arbitrary splits. */
/* kind=1: HCI command (USB control); kind=2: ACL (USB bulk OUT).
 * Adapter must fail/stop on transfer error; a consumed packet is not retried
 * blindly after ambiguous USB completion. All radio calls remain outside core. */
size_t rl_take(RlLink *,uint8_t *,size_t,uint8_t *kind);
void rl_elapsed(RlLink *,uint32_t);
void rl_stop(RlLink *);
#endif
