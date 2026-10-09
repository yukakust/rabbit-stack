#ifndef RABBIT_PRIVATE_INTERNAL_IDENTITY
#define RABBIT_PRIVATE_INTERNAL_IDENTITY
#include "mbedtls/pk.h"
#include "mbedtls/x509_crt.h"
typedef struct {mbedtls_pk_context key;uint8_t certificate[1024],spki[128],sha256[32];size_t certificate_bytes,spki_bytes;unsigned initialized,ready;} DellIdentity;
int dell_identity_create(DellIdentity*,int(*)(void*,unsigned char*,size_t),void*);
void dell_identity_free(DellIdentity*);
#endif
