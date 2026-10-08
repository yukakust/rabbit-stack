#ifndef RABBIT_MODULE_ARTIFACT_H
#define RABBIT_MODULE_ARTIFACT_H
#include <stdint.h>
#include <stddef.h>
#define MOD_FILE_MAX 262144u
#define MOD_AGGREGATE_MAX 4194304u
#define MOD_CHUNK 65536u
#define MOD_HEADER 288u
#define MOD_ROLE_TLS_SERVER 1u
#define MOD_ABI 1u
typedef struct {uint8_t owner[32],target[32],parent_hash[32],digest[32];uint64_t epoch,counter,last_counter;uint32_t total,mapped,role,abi;} ModPolicy;
typedef struct {ModPolicy policy;uint8_t*memory;size_t capacity;uint32_t received,ready,poisoned,pinned;} ModArtifact;
int mod_begin(ModArtifact*,const ModPolicy*,uint8_t*,size_t);
int mod_accept(ModArtifact*,const uint8_t*,size_t);
int mod_pin(ModArtifact*);
int mod_cancel(ModArtifact*);
/* Immutable authenticated PE structural facts, no instruction sandbox. */
int mod_pe(const uint8_t*,size_t,uint32_t*,uint32_t*);
int mod_exec_address(const uint8_t*,size_t,uintptr_t,size_t,uintptr_t);
int mod_overlap(const void*,size_t,const void*,size_t);
void mod_wipe(void*,size_t);
#endif
