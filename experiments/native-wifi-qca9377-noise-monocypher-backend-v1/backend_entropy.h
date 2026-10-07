#ifndef QCA_NOISE_BACKEND_ENTROPY_H
#define QCA_NOISE_BACKEND_ENTROPY_H
#include <stdint.h>
#include <stddef.h>
/* Platform-owned mandatory checked entropy: 0 success; nonzero fails closed.
 * No native implementation or test-time substitute for live cryptographic RNG. */
int qca_noise_entropy(uint8_t *destination,size_t length);
#endif
