#ifndef RABBIT_SHA256_H
#define RABBIT_SHA256_H
#include <stddef.h>
#include <stdint.h>
void rabbit_sha256(uint8_t out[32], const uint8_t *data, size_t length);
#endif
