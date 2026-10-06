#include "eapol_frame.h"
static uint16_t be16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] << 8 | p[1]);
}
int rabbit_eapol_key_frame(const uint8_t *p, size_t n,
                          struct rabbit_eapol_view *out) {
    struct rabbit_eapol_view v;
    uint64_t replay = 0;
    size_t i;
    if (!p || !out || n < 99 || n > RABBIT_EAPOL_MAX_BYTES) return -1;
    if (p[0] < 1 || p[0] > 3 || p[1] != 3) return -1;
    if ((size_t)be16(p + 2) != n - 4 || p[4] != 2) return -1;
    v.key_info = be16(p + 5);
    /* This profile excludes WPA1, SAE/SHA256 AKMs, variable MIC lengths. */
    if ((v.key_info & 7u) != 2) return -1;
    v.key_data_length = be16(p + 97);
    if ((size_t)v.key_data_length != n - 99) return -1;
    for (i = 9; i < 17; ++i) replay = (replay << 8) | p[i];
    v.version = p[0];
    v.key_length = be16(p + 7);
    v.replay_counter = replay;
    v.nonce = p + 17;
    v.mic = p + 81;
    v.key_data = p + 99;
    *out = v;
    return 0;
}
