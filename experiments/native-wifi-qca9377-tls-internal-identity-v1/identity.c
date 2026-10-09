#include "identity.h"
#include "mbedtls/ecp.h"
#include "mbedtls/sha256.h"
#include <string.h>
static void wipe(void*p,size_t n){volatile uint8_t*q=p;while(n--)*q++=0;}
int dell_identity_create(DellIdentity*i,int(*random)(void*,unsigned char*,size_t),void*ctx){
 if(!i||!random||i->initialized)return -1;i->initialized=1;mbedtls_pk_init(&i->key);mbedtls_x509write_cert cert;mbedtls_x509write_crt_init(&cert);mbedtls_mpi serial;mbedtls_mpi_init(&serial);uint8_t serial_bytes[16];int r=-1;
 if(mbedtls_pk_setup(&i->key,mbedtls_pk_info_from_type(MBEDTLS_PK_ECKEY))||mbedtls_ecp_gen_key(MBEDTLS_ECP_DP_SECP256R1,mbedtls_pk_ec(i->key),random,ctx)||random(ctx,serial_bytes,sizeof serial_bytes))goto done;
 serial_bytes[0]&=0x7f;serial_bytes[15]|=1;if(mbedtls_mpi_read_binary(&serial,serial_bytes,sizeof serial_bytes))goto done;
 mbedtls_x509write_crt_set_version(&cert,MBEDTLS_X509_CRT_VERSION_3);mbedtls_x509write_crt_set_md_alg(&cert,MBEDTLS_MD_SHA256);mbedtls_x509write_crt_set_subject_key(&cert,&i->key);mbedtls_x509write_crt_set_issuer_key(&cert,&i->key);
 if(mbedtls_x509write_crt_set_subject_name(&cert,"CN=rabbit.local")||mbedtls_x509write_crt_set_issuer_name(&cert,"CN=rabbit.local")||mbedtls_x509write_crt_set_serial(&cert,&serial)||mbedtls_x509write_crt_set_validity(&cert,"20200101000000","20991231235959")||mbedtls_x509write_crt_set_basic_constraints(&cert,0,-1)||mbedtls_x509write_crt_set_key_usage(&cert,MBEDTLS_X509_KU_DIGITAL_SIGNATURE))goto done;
 int n=mbedtls_pk_write_pubkey_der(&i->key,i->spki,sizeof i->spki);if(n<=0||n>(int)sizeof i->spki)goto done;memmove(i->spki,i->spki+sizeof i->spki-n,(size_t)n);i->spki_bytes=(size_t)n;wipe(i->spki+n,sizeof i->spki-(size_t)n);if(mbedtls_sha256(i->spki,i->spki_bytes,i->sha256,0))goto done;
 n=mbedtls_x509write_crt_der(&cert,i->certificate,sizeof i->certificate,random,ctx);if(n<=0||n>(int)sizeof i->certificate)goto done;memmove(i->certificate,i->certificate+sizeof i->certificate-n,(size_t)n);i->certificate_bytes=(size_t)n;wipe(i->certificate+n,sizeof i->certificate-(size_t)n);i->ready=1;r=0;
 done:wipe(serial_bytes,sizeof serial_bytes);mbedtls_mpi_free(&serial);mbedtls_x509write_crt_free(&cert);if(r)dell_identity_free(i);return r;
}
void dell_identity_free(DellIdentity*i){if(!i)return;if(i->initialized)mbedtls_pk_free(&i->key);wipe(i,sizeof(*i));}
