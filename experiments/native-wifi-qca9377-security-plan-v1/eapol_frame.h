#ifndef RABBIT_EAPOL_FRAME_H
#define RABBIT_EAPOL_FRAME_H
#include <stddef.h>
#include <stdint.h>

/* A framing-only WPA2-PSK/CCMP profile. Success does NOT authenticate a frame. */
#define RABBIT_EAPOL_MAX_BYTES 4096u
struct rabbit_eapol_view {
    uint8_t version;
    uint16_t key_info, key_length, key_data_length;
    uint64_t replay_counter;
    const uint8_t *nonce, *mic, *key_data;
};
/* Input starts with 802.1X header, excludes Ethernet header and padding.
 * Returned pointers borrow input until the caller releases its RX buffer.
 * Output is untouched on failure. Neither keys nor counters are installed. */
int rabbit_eapol_key_frame(const uint8_t *frame, size_t bytes,
                          struct rabbit_eapol_view *out);
#endif
