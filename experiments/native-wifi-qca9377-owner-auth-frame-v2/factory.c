/* HOST fixture only. Fixed suite unsupported factories fail closed.
 * Device/Unix RNG is disabled; only published fixed ephemeral APIs are used. */
#include "internal.h"
#include <stdlib.h>
NoiseCipherState *noise_aesgcm_new_ref(void){return 0;}
NoiseDHState *noise_curve448_new(void){return 0;}
NoiseDHState *noise_newhope_new(void){return 0;}
NoiseHashState *noise_blake2s_new(void){return 0;}
NoiseHashState *noise_blake2b_new(void){return 0;}
NoiseHashState *noise_sha512_new(void){return 0;}
void noise_rand_bytes(void*p,size_t n){(void)p;(void)n;abort();}
int qca_noise_entropy(uint8_t*p,size_t n){(void)p;(void)n;abort();}
