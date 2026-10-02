#ifndef RABBIT_USB_PORT_H
#define RABBIT_USB_PORT_H
#include "abi.h"
#include "hci_link.h"
#define RL_EVENT_PREFIX 24u
/* Controlled diagnostic trial versus the physical 1ms baseline. Finite, not
 * proof of a hardware fix; no asynchronous reader/callback is introduced. */
#define RL_EVENT_TIMEOUT_MS 20u
typedef struct {
 Status status;uint32_t result,reported_length;
 uint8_t prefix[RL_EVENT_PREFIX],copied;
} RlEventObservation;
typedef struct {
 void *io;uint8_t events,in,out;uint8_t bound;
 uint16_t event_packet;uint8_t event_interval;
 uint8_t mask_seen,event_mask[8],le_mask[8];
 /* Passive observations from the EXISTING sole read, no new USB operation. */
 uint32_t polls,event_reads,event_timeouts,observation_sequence;
 RlEventObservation observation;
} RlUsb;
/* Nonzero poll result is fatal/unknown outcome, never a safe-to-unload claim.
 * Stable small codes for bounded Dell diagnostics, not a public module ABI. */
enum { RL_USB_ARGUMENT=1,RL_USB_EVENT_SIZE,RL_USB_EVENT_TRANSFER,
 RL_USB_BULK_SIZE,RL_USB_BULK_TRANSFER,RL_USB_COMMAND_TRANSFER,
 RL_USB_ACL_TRANSFER,RL_USB_PACKET_KIND,RL_USB_LINK_FAULT };
/* Caller is the sole event owner in the NEW supervisor, never the old loop. */
int rl_usb_bind(RlUsb *,SystemTable *);
int rl_usb_poll(RlUsb *,RlLink *);
int rl_usb_close(RlUsb *,RlLink *);
#endif
