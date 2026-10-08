#ifndef QCA_HTT_PUBLIC_RNG_INVENTORY_JOIN_H
#define QCA_HTT_PUBLIC_RNG_INVENTORY_JOIN_H
#include "platform.h"
typedef struct {RngSession session;RngPublicDiagnostic diagnostic;uint64_t epoch;uint32_t attempted,error;uint8_t entropy_approved;} QcaHttRngInventory;
/* Public GetInfo inventory ONLY. Header/CODEhash/advertised algorithm do NOT
 * establish provider entropy provenance. This API never invokes GetRNG. */
int qca_htt_public_rng_inventory(QcaHttRngInventory*,const void*system,uint64_t,const uint8_t code_artifact_sha256[32]);
int qca_htt_public_rng_cleanup(QcaHttRngInventory*);
int qca_htt_public_rng_released(const QcaHttRngInventory*);
#endif
