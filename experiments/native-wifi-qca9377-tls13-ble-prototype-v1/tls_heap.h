#ifndef RABBIT_TLS_HEAP_H
#define RABBIT_TLS_HEAP_H
#include <stddef.h>
#include <stdint.h>
typedef struct {size_t offset,bytes;unsigned live;} TlsHeapBlock;
typedef struct {uint8_t*base;size_t capacity,used,high_water;unsigned live,quarantine;TlsHeapBlock block[512];} TlsHeap;
int tls_heap_bind(TlsHeap*,uint8_t*,size_t);
int tls_heap_release(TlsHeap*);
void*tls_heap_calloc(size_t,size_t);
void tls_heap_free(void*);
#endif
