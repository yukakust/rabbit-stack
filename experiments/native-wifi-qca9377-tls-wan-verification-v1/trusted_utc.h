#ifndef RABBIT_WAN_TRUSTED_UTC
#define RABBIT_WAN_TRUSTED_UTC
#include <stdint.h>
#include <time.h>
/* Caller must authenticate UTC/epoch externally; monotonic time is not UTC. */
int wan_utc_bind(uint64_t epoch,int64_t utc,uint64_t monotonic_ms);
int wan_utc_advance(uint64_t epoch,uint64_t monotonic_ms);
void wan_utc_revoke(void);
int wan_utc_current(uint64_t epoch);
#endif
