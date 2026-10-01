#ifndef RABBIT_NATIVE_TRANSPORT_H
#define RABBIT_NATIVE_TRANSPORT_H
#include <stdint.h>
#include <stddef.h>
/* 0 waiting/duplicate, 1 rejected, 2 complete bytes, 3 staging checkpoint.
 * Neither 2 nor 3 authenticates a package or means native code was applied. */
int rabbit_rx_frame(const uint8_t frame[16]);
const uint8_t *rabbit_rx_data(void);
size_t rabbit_rx_length(void);
void rabbit_rx_reset(void);
#endif
