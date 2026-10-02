#ifndef RABBIT_USB_PORT_H
#define RABBIT_USB_PORT_H
#include "abi.h"
#include "hci_link.h"
typedef struct {void *io;uint8_t events,in,out;uint8_t bound;} RlUsb;
/* Caller is the sole event owner in the NEW supervisor, never the old loop. */
int rl_usb_bind(RlUsb *,SystemTable *);
int rl_usb_poll(RlUsb *,RlLink *);
int rl_usb_close(RlUsb *,RlLink *);
#endif
