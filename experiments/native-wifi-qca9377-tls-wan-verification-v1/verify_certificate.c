#include "verify_certificate.h"
#include "trusted_utc.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/sha256.h"
#include <string.h>
static const unsigned char root_hash[32]={0x69,0x72,0x9b,0x8e,0x15,0xa8,0x6e,0xfc,0x17,0x7a,0x57,0xaf,0xb7,0x17,0x1d,0xfc,0x64,0xad,0xd2,0x8c,0x2f,0xca,0x8c,0xf1,0x50,0x7e,0x34,0x45,0x3c,0xcb,0x14,0x70};
int wan_verify_certificate(uint64_t epoch,const unsigned char*chain[],const size_t sizes[],size_t count,const unsigned char*root,size_t root_size,const char*name,uint32_t*flags){
 if(!flags)return -1;*flags=UINT32_MAX;
 if(!wan_utc_current(epoch)||!chain||!sizes||!count||count>4||!root||!root_size||root_size>2048||!name)return -1;
 size_t n=0;while(n<128&&name[n]){unsigned char c=(unsigned char)name[n];if(!((c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='-'||c=='.'))return -1;n++;}if(!n||n==128)return -1;
 unsigned char digest[32];if(mbedtls_sha256(root,root_size,digest,0)||memcmp(digest,root_hash,32))return -1;
 mbedtls_x509_crt cert,anchor;mbedtls_x509_crt_init(&cert);mbedtls_x509_crt_init(&anchor);int result=-1;
 result=mbedtls_x509_crt_parse_der(&anchor,root,root_size);if(result)goto done;
 for(size_t i=0;i<count;i++){if(!chain[i]||!sizes[i]||sizes[i]>2048){result=-1;goto done;}result=mbedtls_x509_crt_parse_der(&cert,chain[i],sizes[i]);if(result)goto done;}
 result=mbedtls_x509_crt_verify_with_profile(&cert,&anchor,0,&mbedtls_x509_crt_profile_default,name,flags,0,0);
 if(!wan_utc_current(epoch)||*flags)result=-1;
 done:mbedtls_x509_crt_free(&cert);mbedtls_x509_crt_free(&anchor);return result;
}
