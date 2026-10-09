#ifndef RABBIT_TRUSTED_ENTROPY
#define RABBIT_TRUSTED_ENTROPY
#include <stdint.h>
#include <stddef.h>
#include "mbedtls/ctr_drbg.h"
#include "seed_source.h"
#define RNG_MAX_REQUEST 1024u
typedef struct {mbedtls_ctr_drbg_context drbg;RngApproval approval;TrustedSeedSource local_source;TrustedSeedSource*source;uint32_t initialized,busy,revoked,attempted,source_attempts,reseed_count,request_count;} TrustedRng;
/* Child DRBG can use its source model or a genuine parent-owned source whose
 * lease/provenance/lifetime are independently admitted by parent composition. */
int trusted_rng_open_source(TrustedRng*,const RngApproval*,TrustedSeedSource*);
int trusted_rng_open(TrustedRng*,const RngApproval*,const RngServices*);
int trusted_rng_random(TrustedRng*,uint64_t,const uint8_t[32],uint8_t*,size_t);
int trusted_rng_close(TrustedRng*);
int trusted_rng_revoke(TrustedRng*);
#endif
