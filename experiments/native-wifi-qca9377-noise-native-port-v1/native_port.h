#ifndef QCA_NOISE_NATIVE_PORT_H
#define QCA_NOISE_NATIVE_PORT_H
#include <stdint.h>
#include <stddef.h>
#include <noise/protocol.h>
#include "rng_port.h"
#define QCA_NOISE_SLOTS 64
#define QCA_NOISE_SLOT_BYTES 512
/* Trusted mapped/disjoint storage; caller owns epoch and single-thread admission. */
typedef struct {
 _Alignas(16) uint8_t bytes[QCA_NOISE_SLOTS][QCA_NOISE_SLOT_BYTES];
 size_t lengths[QCA_NOISE_SLOTS];uint8_t states[QCA_NOISE_SLOTS];
 uint64_t epoch;uint32_t used,live,quarantined,allocation_calls,peak_live;
 int fail_after;RngSession *rng;const RngReview *review;
} QcaNoisePort;
int qca_native_bind(QcaNoisePort*);int qca_native_reset(QcaNoisePort*,uint64_t);
int qca_native_rng_bind(RngSession*,const RngReview*);
size_t qca_native_live(void);size_t qca_native_peak(void);unsigned qca_native_allocations(void);
void *qca_noise_new_object(size_t);void qca_noise_free(void*,size_t);
void *qca_port_malloc(size_t);void *qca_port_calloc(size_t,size_t);void qca_port_free(void*);
/* Returns only fixed suite, clears error output even for upstream dangling return. */
int qca_nk_new(NoiseHandshakeState**,int);
#endif
