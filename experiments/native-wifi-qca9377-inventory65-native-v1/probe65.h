#ifndef RABBIT_PUBLIC_INVENTORY65
#define RABBIT_PUBLIC_INVENTORY65
#include <stddef.h>
#include <stdint.h>
int inventory65_begin(const void*);
int inventory65_close(void);
/* Diagnostic capture is entry-only. Reads never execute CPUID/GetInfo again. */
#endif
