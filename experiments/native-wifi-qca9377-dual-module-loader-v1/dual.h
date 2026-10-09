#ifndef RABBIT_DUAL_MODULE_OWNER_LEDGER
#define RABBIT_DUAL_MODULE_OWNER_LEDGER
#include "loader.h"
typedef int(*DualRevoke)(void*,uint64_t,const uint8_t[32]);
typedef struct {
 ModBudget budget;ModArtifact artifact[2];ModLoader loader[2];ModEfi efi;
 uint8_t owner[32],target[32],expected_digest[2][32],code_set[32];
 uint32_t base_mapped,initialized,busy,sealed,quarantine,closed;
 DualRevoke revoke;void*revoke_context;
} DualModules;
/* Exact current parent hash is later an owner-signed assertion, never a hash
 * of relocated memory. Root must bind actual installed parent before signing.
 * Expected child digests bind both reviewed compiler closures. Shared mapped
 * ledger and monotonic child counter are reserved BEFORE firmware entry. */
int dual_bind(DualModules*,const ModEfi*,uint64_t,uint32_t,const uint8_t[32],const uint8_t[32],const uint8_t[2][32],DualRevoke,void*);
int dual_accept(DualModules*,const uint8_t*,size_t,uint8_t*arena,size_t capacity);
/* Both actual reviewed images must be loaded before sealing. New executable
 * admission then fails; this code-set identifier is not entropy approval. */
int dual_seal(DualModules*,uint64_t,uint8_t code_set[32]);
int dual_inventory(const DualModules*);
int dual_close(DualModules*,uint64_t);
/* There is deliberately no generic untyped child dispatch. Exact TLS/RSN
 * argument/span/provider adapters still required for native integration. */
#endif
