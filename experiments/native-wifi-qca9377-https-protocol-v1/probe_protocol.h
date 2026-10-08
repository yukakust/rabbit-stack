#ifndef RABBIT_HTTPS_PROBE_PROTOCOL_H
#define RABBIT_HTTPS_PROBE_PROTOCOL_H
#include <stddef.h>
#include <stdint.h>
#define PROBE_RESPONSE_CAP 2304
struct probe_http {uint8_t bytes[PROBE_RESPONSE_CAP];char nonce[65];size_t used;uint32_t epoch;unsigned active,failed,finished;};
/* Message framing only: never proves TLS/certificate/time/RNG or actual WAN. */
int probe_request(struct probe_http*,uint32_t,const char*,const uint8_t[32],uint8_t*,size_t,size_t*);
int probe_feed(struct probe_http*,uint32_t,const uint8_t*,size_t);
int probe_finish(struct probe_http*,uint32_t);
void probe_close(struct probe_http*);
#endif
