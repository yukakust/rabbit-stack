#ifndef RABBIT_WAN_CERTIFICATE_VERIFY
#define RABBIT_WAN_CERTIFICATE_VERIFY
#include <stdint.h>
#include <stddef.h>
/* Actual mature verification; caller still must bind approved entropy and UTC.
 * No verifier callback clears CA/name/date/signature failures. */
int wan_verify_certificate(uint64_t epoch,const unsigned char*chain[],const size_t sizes[],size_t count,const unsigned char*root,size_t root_size,const char*name,uint32_t*flags);
#endif
