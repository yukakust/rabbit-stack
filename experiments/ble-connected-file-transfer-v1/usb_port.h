#ifndef RABBIT_USB_PORT_H
#define RABBIT_USB_PORT_H
#include "abi.h"
#include "hci_link.h"
typedef struct {void *io;uint8_t events,in,out;uint8_t bound;} RlUsb;
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
