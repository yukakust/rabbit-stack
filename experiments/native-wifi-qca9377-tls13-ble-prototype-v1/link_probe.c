/* LINK-ONLY adapter: no provider bound, strong entropy absence fails closed.
 * Never launched, signed or described as native-ready. Real approved RNG
 * adaptation is intentionally unimplemented in this measurement image. */
#include "tls_engine.h"
#include "tls_heap.h"
#include "psa/crypto.h"
psa_status_t mbedtls_psa_external_get_random(mbedtls_psa_external_random_context_t*c,uint8_t*p,size_t n,size_t*written){(void)c;(void)p;(void)n;*written=0;return PSA_ERROR_INSUFFICIENT_ENTROPY;}
uint64_t __attribute__((ms_abi)) tls_link_entry(void*handle,void*system){(void)handle;(void)system;return UINT64_C(0x8000000000000003);}
