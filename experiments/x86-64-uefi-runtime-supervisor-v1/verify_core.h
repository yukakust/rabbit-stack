#ifndef RABBIT_UPDATE_VERIFY_H
#define RABBIT_UPDATE_VERIFY_H
#include <stdint.h>
#include <stddef.h>
#define MAX_RUNTIME_BYTES 262144u
typedef struct { uint8_t target[32],owner[32],base[32],state[32]; uint64_t counter; } UpdatePolicy;
int rabbit_update_verify(const uint8_t *data, size_t length, const UpdatePolicy *policy);
int rabbit_module_pe(const uint8_t *data, size_t length);
#endif
