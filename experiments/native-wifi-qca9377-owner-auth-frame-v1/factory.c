/* Fixed ChaChaPoly policy. Unsupported AES factory is fail closed; no fallback. */
#include "internal.h"
NoiseCipherState *noise_aesgcm_new(void){return 0;}
