#define _POSIX_C_SOURCE 200809L
#include "trusted_utc.h"
#include "verify_certificate.h"
#include "tls_heap.h"
#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/platform.h"
#include "psa/crypto.h"
#include <sys/socket.h>
#include <sys/random.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
/* Linux is only this Yukabox host harness. No native/Dell provider is supplied. */
psa_status_t mbedtls_psa_external_get_random(mbedtls_psa_external_random_context_t*c,uint8_t*out,size_t n,size_t*written){(void)c;*written=0;unsigned attempts=0;while(*written<n&&attempts++<128){ssize_t r=getrandom(out+*written,n-*written,0);if(r>0)*written+=(size_t)r;else if(r<0&&errno==EINTR)continue;else break;}if(*written==n)return PSA_SUCCESS;memset(out,0,n);*written=0;return PSA_ERROR_INSUFFICIENT_ENTROPY;}
static int rng_cb(void*c,unsigned char*b,size_t n){(void)c;size_t written=0;return mbedtls_psa_external_get_random(0,b,n,&written)==PSA_SUCCESS&&written==n?0:-1;}
static int send_cb(void*c,const unsigned char*b,size_t n){ssize_t v=send(*(int*)c,b,n,MSG_NOSIGNAL);if(v>=0)return(int)v;return errno==EINTR||errno==EAGAIN?MBEDTLS_ERR_SSL_WANT_WRITE:-1;}
static int recv_cb(void*c,unsigned char*b,size_t n){ssize_t v=recv(*(int*)c,b,n,0);if(v>=0)return(int)v;return errno==EINTR||errno==EAGAIN?MBEDTLS_ERR_SSL_WANT_READ:-1;}
static uint64_t monotonic_ms(void){struct timespec t;assert(!clock_gettime(CLOCK_MONOTONIC,&t));return(uint64_t)t.tv_sec*1000+(unsigned)t.tv_nsec/1000000;}
int main(int argc,char**argv){
 assert(argc==2);FILE*f=fopen(argv[1],"rb");assert(f);unsigned char root_der[2048];size_t root_size=fread(root_der,1,sizeof root_der,f);assert(root_size&&feof(f));fclose(f);
 TlsHeap heap;static unsigned char pool[262144];assert(tls_heap_bind(&heap,pool,sizeof pool));assert(!mbedtls_platform_set_calloc_free(tls_heap_calloc,tls_heap_free));assert(psa_crypto_init()==PSA_SUCCESS);
 uint64_t start=monotonic_ms();assert(!wan_utc_bind(1,time(0),start));
 int socket_fd=socket(AF_INET,SOCK_STREAM,0);assert(socket_fd>=0);struct timeval timeout={2,0};assert(!setsockopt(socket_fd,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof timeout));assert(!setsockopt(socket_fd,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof timeout));struct sockaddr_in address={0};address.sin_family=AF_INET;address.sin_port=htons(443);assert(inet_pton(AF_INET,"100.84.137.70",&address.sin_addr)==1);assert(!connect(socket_fd,(struct sockaddr*)&address,sizeof address));
 mbedtls_ssl_context ssl;mbedtls_ssl_config config;mbedtls_x509_crt ca;mbedtls_ssl_init(&ssl);mbedtls_ssl_config_init(&config);mbedtls_x509_crt_init(&ca);assert(!mbedtls_x509_crt_parse_der(&ca,root_der,root_size));assert(!mbedtls_ssl_config_defaults(&config,MBEDTLS_SSL_IS_CLIENT,MBEDTLS_SSL_TRANSPORT_STREAM,MBEDTLS_SSL_PRESET_DEFAULT));mbedtls_ssl_conf_min_tls_version(&config,MBEDTLS_SSL_VERSION_TLS1_3);mbedtls_ssl_conf_max_tls_version(&config,MBEDTLS_SSL_VERSION_TLS1_3);mbedtls_ssl_conf_rng(&config,rng_cb,0);mbedtls_ssl_conf_authmode(&config,MBEDTLS_SSL_VERIFY_REQUIRED);mbedtls_ssl_conf_ca_chain(&config,&ca,0);int setup=mbedtls_ssl_setup(&ssl,&config);if(setup){fprintf(stderr,"actual SSL setup error=%d\n",setup);return 1;}assert(!mbedtls_ssl_set_hostname(&ssl,"yukabox.tail1e1ad1.ts.net"));mbedtls_ssl_set_bio(&ssl,&socket_fd,send_cb,recv_cb,0);
 int result;unsigned loops=0;do{assert(++loops<=64&&monotonic_ms()-start<12000);assert(!wan_utc_advance(1,monotonic_ms()));result=mbedtls_ssl_handshake(&ssl);}while(result==MBEDTLS_ERR_SSL_WANT_READ||result==MBEDTLS_ERR_SSL_WANT_WRITE);
 if(result){fprintf(stderr,"actual host TLS handshake failed %d verify=%08x\n",result,mbedtls_ssl_get_verify_result(&ssl));return 1;}assert(!mbedtls_ssl_get_verify_result(&ssl));
 const mbedtls_x509_crt*peer=mbedtls_ssl_get_peer_cert(&ssl);const unsigned char*chain[4];size_t sizes[4],count=0;while(peer){assert(count<4);chain[count]=peer->raw.p;sizes[count++]=peer->raw.len;peer=peer->next;}uint32_t flags;assert(!wan_verify_certificate(1,chain,sizes,count,root_der,root_size,"yukabox.tail1e1ad1.ts.net",&flags)&&!flags);
 /* Read-only missing route; no Funnel, command, credential or response-body log. */
 const unsigned char request[]="GET /rabbit-wifi-certificate-check HTTP/1.1\r\nHost: yukabox.tail1e1ad1.ts.net\r\nConnection: close\r\n\r\n";
 size_t offset=0;while(offset<sizeof request-1){assert(monotonic_ms()-start<12000);result=mbedtls_ssl_write(&ssl,request+offset,sizeof request-1-offset);if(result>0)offset+=(size_t)result;else assert(result==MBEDTLS_ERR_SSL_WANT_READ||result==MBEDTLS_ERR_SSL_WANT_WRITE);}
 unsigned char response[128];do{assert(monotonic_ms()-start<12000);result=mbedtls_ssl_read(&ssl,response,sizeof response);}while(result==MBEDTLS_ERR_SSL_WANT_READ||result==MBEDTLS_ERR_SSL_WANT_WRITE);assert(result>=12&&!memcmp(response,"HTTP/1.",7));unsigned code=(response[9]-'0')*100+(response[10]-'0')*10+response[11]-'0';memset(response,0,sizeof response);
 printf("PASS actual Yukabox-host MbedTLS TLS13 CA/name/time CertificateVerify/Finished; HTTP status=%u; NOT Dell/WAN-proof\n",code);
 close(socket_fd);mbedtls_ssl_free(&ssl);mbedtls_ssl_config_free(&config);mbedtls_x509_crt_free(&ca);mbedtls_psa_crypto_free();wan_utc_revoke();assert(!heap.live&&!heap.quarantine&&tls_heap_release(&heap));return 0;
}
