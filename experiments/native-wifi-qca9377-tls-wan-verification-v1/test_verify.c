#define _POSIX_C_SOURCE 200809L
#include "verify_certificate.h"
#include "trusted_utc.h"
#include "tls_heap.h"
#include "mbedtls/platform.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/platform_util.h"
#include "psa/crypto.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
psa_status_t mbedtls_psa_external_get_random(mbedtls_psa_external_random_context_t*c,uint8_t*out,size_t n,size_t*written){(void)c;static unsigned fixture=7;for(size_t i=0;i<n;i++)out[i]=(uint8_t)(fixture++*17u);*written=n;return PSA_SUCCESS;}
static unsigned checks;
static unsigned char*load(const char*path,size_t*n){FILE*f=fopen(path,"rb");assert(f);assert(!fseek(f,0,SEEK_END));long size=ftell(f);assert(size>0&&size<2048);*n=(size_t)size;rewind(f);unsigned char*b=malloc(*n);assert(b&&fread(b,1,*n,f)==*n);fclose(f);return b;}
int main(int argc,char**argv){
 assert(argc==6);TlsHeap heap;unsigned char pool[131072];assert(tls_heap_bind(&heap,pool,sizeof pool));assert(!mbedtls_platform_set_calloc_free(tls_heap_calloc,tls_heap_free));assert(psa_crypto_init()==PSA_SUCCESS);
 unsigned char*bytes[5];size_t sizes[5];for(unsigned i=0;i<5;i++)bytes[i]=load(argv[i+1],&sizes[i]);const unsigned char*chain[]={bytes[0],bytes[1],bytes[2],bytes[3]};uint32_t flags;
 #define VERIFY() wan_verify_certificate(1,chain,sizes,4,bytes[4],sizes[4],"yukabox.tail1e1ad1.ts.net",&flags)
 assert(VERIFY()!=0&&flags==UINT32_MAX);checks++;
 assert(!wan_utc_bind(1,1791497149,1000));int initial=VERIFY();fprintf(stderr,"actual initial verification result=%d flags=%08x\n",initial,flags);assert(!initial&&!flags);checks++;
 assert(wan_verify_certificate(1,chain,sizes,4,bytes[4],sizes[4],"wrong.example",&flags)!=0&&(flags&MBEDTLS_X509_BADCERT_CN_MISMATCH));checks++;
 assert(wan_verify_certificate(2,chain,sizes,4,bytes[4],sizes[4],"yukabox.tail1e1ad1.ts.net",&flags)!=0&&flags==UINT32_MAX);checks++;
 assert(wan_verify_certificate(1,chain,sizes,1,bytes[4],sizes[4],"yukabox.tail1e1ad1.ts.net",&flags)!=0&&(flags&MBEDTLS_X509_BADCERT_NOT_TRUSTED));checks++;
 for(unsigned i=0;i<32;i++){bytes[4][sizes[4]-1]^=(unsigned char)(1u<<(i%8));assert(VERIFY()!=0);bytes[4][sizes[4]-1]^=(unsigned char)(1u<<(i%8));checks++;}
 for(unsigned i=0;i<64;i++){size_t p=sizes[0]-1-i;bytes[0][p]^=1u;assert(VERIFY()!=0);bytes[0][p]^=1u;checks++;}assert(!VERIFY());checks++;
 assert(!wan_utc_advance(1,601000)&&wan_utc_current(1));assert(wan_utc_advance(1,601001)==-1&&!wan_utc_current(1)&&VERIFY()!=0);checks++;
 assert(!wan_utc_bind(1,1577836800LL,0));assert(VERIFY()!=0&&(flags&MBEDTLS_X509_BADCERT_FUTURE));checks++;wan_utc_revoke();
 assert(!wan_utc_bind(1,4102444799LL,0));assert(VERIFY()!=0&&(flags&MBEDTLS_X509_BADCERT_EXPIRED));checks++;wan_utc_revoke();
 assert(!wan_utc_bind(1,1791497149,1000));assert(wan_utc_advance(1,999)==-1&&VERIFY()!=0);checks++;
 assert(!wan_utc_bind(1,1791497149,1000));assert(wan_utc_advance(2,1000)==-1&&VERIFY()!=0);checks++;
 assert(wan_utc_bind(0,1791497149,0)==-1&&wan_utc_bind(1,0,0)==-1&&wan_utc_bind(1,4102444800LL,0)==-1);checks++;
 for(time_t t=1577836800;t<4102444800LL;t+=1234567){struct tm actual,expected;assert(mbedtls_platform_gmtime_r(&t,&actual)&&gmtime_r(&t,&expected));assert(actual.tm_year==expected.tm_year&&actual.tm_mon==expected.tm_mon&&actual.tm_mday==expected.tm_mday&&actual.tm_hour==expected.tm_hour&&actual.tm_min==expected.tm_min&&actual.tm_sec==expected.tm_sec&&actual.tm_wday==expected.tm_wday&&actual.tm_yday==expected.tm_yday);checks++;}
 for(unsigned i=0;i<5;i++)free(bytes[i]);mbedtls_psa_crypto_free();assert(!heap.live&&!heap.quarantine&&tls_heap_release(&heap));
 printf("PASS %u actual mature CA/P384/SHA384/name/date/epoch and Gregorian checks; fixture entropy/time, NOT Dell\n",checks);
}
