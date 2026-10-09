#ifndef RABBIT_TRUSTED_SEED_SOURCE
#define RABBIT_TRUSTED_SEED_SOURCE
#include <stdint.h>
#include <stddef.h>
#define RNG_API __attribute__((ms_abi))
#define RNG_MAX_ATTEMPTS 256u
#define RNG_SOURCE_DEADLINE_US 2500u
typedef struct {uint32_t signature,flags;uint8_t vendor[12];} RngCpu;
typedef struct {uint64_t epoch;uint32_t cpu_signature,cpu_flags,reviewed,trusted_owner_code_only;uint8_t actual_inventory_sha256[32],parent_file_sha256[32],admitted_code_set_sha256[32];} RngApproval;
typedef struct {void*context;size_t context_bytes;int(RNG_API*clock_us)(void*,uint64_t*);} RngServices;
typedef struct {RngApproval approval;RngServices services;uint64_t last_time;uint32_t initialized,busy,revoked,attempted,source_attempts,fill_count;} TrustedSeedSource;
int RNG_API trusted_cpu_native(RngCpu*);
int RNG_API trusted_rdseed64_native(uint64_t*);
int trusted_seed_open(TrustedSeedSource*,const RngApproval*,const RngServices*);
/* Parent-private callback only for an admitted leased child; NOT an external
 * GATT/read/diagnostic API. Root composition must enforce that caller lease. */
int trusted_seed_fill(TrustedSeedSource*,uint64_t,const uint8_t[32],uint8_t*,size_t);
int trusted_seed_close(TrustedSeedSource*);
#endif
