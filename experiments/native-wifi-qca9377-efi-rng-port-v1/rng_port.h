#ifndef RABBIT_EFI_RNG_PORT_H
#define RABBIT_EFI_RNG_PORT_H
#include <stdint.h>
#include <stddef.h>
#define RNG_EFIAPI __attribute__((ms_abi))
typedef uint64_t RngStatus;
typedef struct {uint32_t a;uint16_t b,c;uint8_t d[8];} RngGuid;
typedef struct RngProtocol RngProtocol;
struct RngProtocol {
 RngStatus(RNG_EFIAPI *get_info)(RngProtocol*,size_t*,RngGuid*);
 RngStatus(RNG_EFIAPI *get_rng)(RngProtocol*,RngGuid*,size_t,uint8_t*);
};
typedef struct {
 RngStatus(RNG_EFIAPI *locate)(RngGuid*,void*,void**);
 RngStatus(RNG_EFIAPI *allocate)(uint32_t,size_t,void**);
 RngStatus(RNG_EFIAPI *free_pool)(void*);
} RngBootApi;
typedef struct {
 RngProtocol *provider;uint64_t epoch;RngGuid algorithm;
 uint8_t provider_provenance_sha256[32];
} RngReview;
typedef struct {
 RngBootApi boot;RngProtocol *provider;RngProtocol bound_methods;void *pool;size_t pool_bytes;
 uint64_t epoch;RngStatus last_status;
 RngGuid algorithms[16],selected;uint32_t count,phase,error,pool_uncertain;
} RngSession;
typedef struct {
 uint32_t phase,error,algorithm_count,owned_pool_count,uncertain_pool_count;
 RngStatus status;RngGuid protocol,selected,algorithms[16];
 uint8_t adapter_code_sha256[32];
} RngPublicDiagnostic;
/* Metadata whitelist. code hash must be the caller's compiled CODE artifact,
 * never a sample/key hash. Output disjoint from session/secret buffers. */
void rng_diagnostic(const RngSession*,const uint8_t[32],RngPublicDiagnostic*);
/* Trusted caller supplies validated BootServices methods, disjoint valid buffers
 * and a fresh epoch. Review is an out-of-band trusted policy, NOT GATT authority.
 * No real firmware methods are invoked in host verification. */
int rng_discover(RngSession*,const RngBootApi*,uint64_t);
int rng_fill(RngSession*,const RngReview*,uint8_t*,size_t);
/* Frees ONLY a successfully allocated retained pool; unknown allocations remain
 * blocked. A failed free remains owned/ambiguous; do not assert release. */
int rng_cleanup(RngSession*);
extern const RngGuid rng_protocol_guid,rng_hash_guid,rng_hmac_guid,rng_ctr_guid;
#endif
