#ifndef RABBIT_WAN_TRANSPORT_H
#define RABBIT_WAN_TRANSPORT_H
#include <stddef.h>
#include <stdint.h>
#define RABBIT_WAN_RX_CAP 4096
#define RABBIT_WAN_WANT_READ (-0x6900)
#define RABBIT_WAN_WANT_WRITE (-0x6880)
/* One owned raw TCP stream. All calls from the single NO_SYS poll owner.
 * Caller memory remains owned until close; no TLS/plaintext authentication here. */
struct rabbit_wan_context { uint32_t epoch; };
int rabbit_wan_open(uint32_t epoch,const char *hostname,uint16_t port,uint8_t *rx,size_t capacity);
int rabbit_wan_poll(uint32_t epoch);
int rabbit_wan_send(void *context,const unsigned char *bytes,size_t length);
int rabbit_wan_recv(void *context,unsigned char *bytes,size_t length);
void rabbit_wan_close(void);
#endif
