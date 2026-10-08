#ifndef RABBIT_PROTECTED_PLATFORM_H
#define RABBIT_PROTECTED_PLATFORM_H
#include "rng_port.h"
typedef struct {void *base;size_t bytes;uint64_t epoch;uint32_t users,uncertain;RngBootApi api;} ProtectedArena;
/* Genuine EDK2 x64 offsets; valid mapped firmware tables are caller-proven.
 * Header consistency is not provider/code authenticity or RNG approval. */
int protected_boot_api(const void*,RngBootApi*);
/* Callbacks and memory mappings must already be validated by the native target.
 * One bounded BootServicesData pool; no DMA, bootstrap or image cap changes. */
int protected_arena_open(ProtectedArena*,const RngBootApi*,uint64_t,size_t);
int protected_arena_borrow(ProtectedArena*,uint64_t,unsigned,void**,size_t*);
int protected_arena_return(ProtectedArena*,uint64_t,unsigned);
int protected_arena_close(ProtectedArena*,uint64_t);
/* Read-only GetInfo enumeration; NO GetRNG invocation, no random output.
 * Ownership/error must be included in the eventual native all-owner inventory. */
int protected_rng_inventory(RngSession*,const RngBootApi*,uint64_t,const uint8_t[32],RngPublicDiagnostic*);
#endif
