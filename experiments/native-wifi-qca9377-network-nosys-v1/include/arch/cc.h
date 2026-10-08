#ifndef RABBIT_LWIP_CC
#define RABBIT_LWIP_CC
#include <stdint.h>
#include <stddef.h>
#define BYTE_ORDER LITTLE_ENDIAN
#define LWIP_NO_INTTYPES_H 1
#define LWIP_NO_CTYPE_H 1
#define X8_F "02x"
#define U16_F "u"
#define S16_F "d"
#define X16_F "x"
#define U32_F "u"
#define S32_F "d"
#define X32_F "x"
#define SZT_F "zu"
#define LWIP_PLATFORM_DIAG(x) do {} while (0)
void rabbit_network_panic(const char*);
#define LWIP_PLATFORM_ASSERT(x) rabbit_network_panic(x)
#endif
