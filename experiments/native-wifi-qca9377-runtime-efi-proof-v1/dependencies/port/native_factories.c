/* Unsupported algorithms remain unavailable; fixed-suite wrapper admits NK only. */
#include <noise/protocol.h>
NoiseCipherState*noise_aesgcm_new_ref(void){return 0;}
NoiseDHState*noise_curve448_new(void){return 0;}NoiseDHState*noise_newhope_new(void){return 0;}
NoiseHashState*noise_blake2s_new(void){return 0;}NoiseHashState*noise_blake2b_new(void){return 0;}NoiseHashState*noise_sha512_new(void){return 0;}
