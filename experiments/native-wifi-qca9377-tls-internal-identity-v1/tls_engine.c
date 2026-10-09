#include "tls_engine.h"
#include "mbedtls/sha256.h"
#include <string.h>
static void wipe(void*p,size_t n){volatile unsigned char*q=p;
 while(n--)*q++=0;
 }
static int span(const void*p,size_t n){return p&&n&&n<=UINTPTR_MAX-(uintptr_t)p;
 }
static int outside(const TlsBleEndpoint*s,const void*p,size_t n){return span(s,sizeof *s)&&span(p,n)&&((uintptr_t)s+sizeof *s<=(uintptr_t)p||(uintptr_t)p+n<=(uintptr_t)s);
 }
static int active(const TlsBleEndpoint*s,uint64_t epoch){return span(s,sizeof *s)&&s->initialized&&!s->closed&&!s->fault&&epoch==s->epoch;
 }
static int failure(TlsBleEndpoint*s,unsigned error){if(span(s,sizeof *s)&&!s->fault)s->fault=error?error:1;
 return -1;
 }
static int send_bio(void*context,const unsigned char*p,size_t n){
 TlsBleEndpoint*s=context;
 if(!active(s,s->epoch))return MBEDTLS_ERR_SSL_INTERNAL_ERROR;
 if(n>TLS_BLE_FRAGMENT)n=TLS_BLE_FRAGMENT;
 if(n>TLS_BLE_QUEUE-s->outbound_bytes)return MBEDTLS_ERR_SSL_WANT_WRITE;
 memcpy(s->outbound+s->outbound_bytes,p,n);
 s->outbound_bytes+=n;
 return (int)n;
}
static int recv_bio(void*context,unsigned char*p,size_t n){
 TlsBleEndpoint*s=context;
 if(!active(s,s->epoch))return MBEDTLS_ERR_SSL_INTERNAL_ERROR;
 if(!s->inbound_bytes)return MBEDTLS_ERR_SSL_WANT_READ;
 if(n>s->inbound_bytes)n=s->inbound_bytes;
 memcpy(p,s->inbound,n);
 memmove(s->inbound,s->inbound+n,s->inbound_bytes-n);
 s->inbound_bytes-=n;
 wipe(s->inbound+s->inbound_bytes,n);
 return (int)n;
}
static int verify_pin(void*context,mbedtls_x509_crt*crt,int depth,uint32_t*flags){
 TlsBleEndpoint*s=context;
 uint8_t der[128],digest[32];
 unsigned diff=0;
 if(depth!=0)return MBEDTLS_ERR_X509_CERT_VERIFY_FAILED;
 int n=mbedtls_pk_write_pubkey_der(&crt->pk,der,sizeof der);
 if(n<=0||mbedtls_sha256(der+sizeof der-(size_t)n,(size_t)n,digest,0))return MBEDTLS_ERR_X509_CERT_VERIFY_FAILED;
 for(unsigned i=0;i<32;i++)diff|=digest[i]^s->expected_spki[i];
 wipe(der,sizeof der);
 wipe(digest,sizeof digest);
 if(diff)return MBEDTLS_ERR_X509_CERT_VERIFY_FAILED;
 /* Pin replaces CA-root trust only. Retain all other mature certificate errors. */
 *flags&=~MBEDTLS_X509_BADCERT_NOT_TRUSTED;
 if(*flags)return MBEDTLS_ERR_X509_CERT_VERIFY_FAILED;
 s->pin_verified=1;
 return 0;
}
static int no_issuer_trust(void*context,const mbedtls_x509_crt*child,mbedtls_x509_crt**cas){
 (void)context;
 (void)child;
 *cas=0;
 return 0;
 /* Mature CA callback contract: no candidate issuer. Leaf trust is granted
  * solely by exact SPKI callback; VERIFY_REQUIRED remains enabled. */
}
int tls_ble_open(TlsBleEndpoint*s,unsigned server,const uint8_t*crt,size_t cn,const uint8_t*key,size_t kn,const uint8_t pin[32],const char*hostname,TlsEntropy entropy,void*ctx,uint64_t epoch,uint64_t now,uint64_t duration){
 if(!span(s,sizeof *s)||s->initialized||!cn||cn>2048||!kn||kn>512||!outside(s,crt,cn)||!outside(s,key,kn)||!outside(s,pin,32)||!entropy||!epoch||server>1||!duration||duration>60000000||now>UINT64_MAX-duration)return 0;
 unsigned any=0;
 for(unsigned i=0;i<32;i++)any|=pin[i];
 if(!any)return 0;
 if(!server){if(!outside(s,hostname,64))return 0;
 size_t n=0;
 while(n<64&&hostname[n])n++;
 if(!n||n>=64)return 0;
 }
 memset(s,0,sizeof *s);
 s->epoch=epoch;
 s->last=now;
 s->deadline=now+duration;
 s->entropy=entropy;
 s->entropy_context=ctx;
 memcpy(s->expected_spki,pin,32);
 s->initialized=1;
 mbedtls_ssl_init(&s->ssl);
 mbedtls_ssl_config_init(&s->config);
 mbedtls_x509_crt_init(&s->certificate);
 mbedtls_pk_init(&s->key);
 if(mbedtls_x509_crt_parse_der(&s->certificate,crt,cn)||mbedtls_pk_parse_key(&s->key,key,kn,0,0,entropy,ctx)||mbedtls_ssl_config_defaults(&s->config,server?MBEDTLS_SSL_IS_SERVER:MBEDTLS_SSL_IS_CLIENT,MBEDTLS_SSL_TRANSPORT_STREAM,MBEDTLS_SSL_PRESET_DEFAULT))return failure(s,2);
 mbedtls_ssl_conf_min_tls_version(&s->config,MBEDTLS_SSL_VERSION_TLS1_3);
 mbedtls_ssl_conf_max_tls_version(&s->config,MBEDTLS_SSL_VERSION_TLS1_3);
 mbedtls_ssl_conf_authmode(&s->config,MBEDTLS_SSL_VERIFY_REQUIRED);
 mbedtls_ssl_conf_verify(&s->config,verify_pin,s);
 mbedtls_ssl_conf_rng(&s->config,entropy,ctx);
 mbedtls_ssl_conf_ca_cb(&s->config,no_issuer_trust,s);
 if(mbedtls_ssl_conf_own_cert(&s->config,&s->certificate,&s->key)||mbedtls_ssl_setup(&s->ssl,&s->config))return failure(s,3);
 if(!server&&mbedtls_ssl_set_hostname(&s->ssl,hostname))return failure(s,3);
 mbedtls_ssl_set_bio(&s->ssl,s,send_bio,recv_bio,0);
 return 1;
}
int tls_ble_open_owned(TlsBleEndpoint*s,const uint8_t*crt,size_t cn,mbedtls_pk_context*key,const uint8_t pin[32],TlsEntropy entropy,void*ctx,uint64_t epoch,uint64_t now,uint64_t duration){
 if(!span(s,sizeof *s)||s->initialized||!cn||cn>2048||!outside(s,crt,cn)||!outside(s,key,sizeof(*key))||!outside(s,pin,32)||!entropy||!epoch||!duration||duration>60000000||now>UINT64_MAX-duration)return 0;
 unsigned any=0;
 for(unsigned i=0;i<32;i++)any|=pin[i];
 if(!any)return 0;
 memset(s,0,sizeof *s);
 s->epoch=epoch;
 s->last=now;
 s->deadline=now+duration;
 s->entropy=entropy;
 s->entropy_context=ctx;
 memcpy(s->expected_spki,pin,32);
 s->initialized=1;
 mbedtls_ssl_init(&s->ssl);
 mbedtls_ssl_config_init(&s->config);
 mbedtls_x509_crt_init(&s->certificate);
 mbedtls_pk_init(&s->key);
 if(mbedtls_x509_crt_parse_der(&s->certificate,crt,cn)||mbedtls_ssl_config_defaults(&s->config,MBEDTLS_SSL_IS_SERVER,MBEDTLS_SSL_TRANSPORT_STREAM,MBEDTLS_SSL_PRESET_DEFAULT))return failure(s,2);
 mbedtls_ssl_conf_min_tls_version(&s->config,MBEDTLS_SSL_VERSION_TLS1_3);
 mbedtls_ssl_conf_max_tls_version(&s->config,MBEDTLS_SSL_VERSION_TLS1_3);
 mbedtls_ssl_conf_authmode(&s->config,MBEDTLS_SSL_VERIFY_REQUIRED);
 mbedtls_ssl_conf_verify(&s->config,verify_pin,s);
 mbedtls_ssl_conf_rng(&s->config,entropy,ctx);
 mbedtls_ssl_conf_ca_cb(&s->config,no_issuer_trust,s);
 if(mbedtls_ssl_conf_own_cert(&s->config,&s->certificate,key)||mbedtls_ssl_setup(&s->ssl,&s->config))return failure(s,3);
 mbedtls_ssl_set_bio(&s->ssl,s,send_bio,recv_bio,0);
 return 1;
}
int tls_ble_feed(TlsBleEndpoint*s,uint64_t epoch,uint32_t sequence,const uint8_t*p,size_t n){
 if(!active(s,epoch)||!n||n>TLS_BLE_FRAGMENT||!outside(s,p,n)||sequence!=s->feed_sequence||sequence==UINT32_MAX||n>TLS_BLE_QUEUE-s->inbound_bytes)return failure(s,4);
 memcpy(s->inbound+s->inbound_bytes,p,n);
 s->inbound_bytes+=n;
 s->feed_sequence++;
 return 1;
}
size_t tls_ble_drain(TlsBleEndpoint*s,uint64_t epoch,uint8_t*p,size_t cap){
 if(!active(s,epoch)||!cap||!outside(s,p,cap))return 0;
 size_t n=s->outbound_bytes;
 if(n>cap)n=cap;
 if(n>TLS_BLE_FRAGMENT)n=TLS_BLE_FRAGMENT;
 memcpy(p,s->outbound,n);
 memmove(s->outbound,s->outbound+n,s->outbound_bytes-n);
 s->outbound_bytes-=n;
 wipe(s->outbound+s->outbound_bytes,n);
 return n;
}
int tls_ble_poll(TlsBleEndpoint*s,uint64_t epoch,uint64_t now){
 if(!active(s,epoch))return -1;
 if(now<s->last||(!s->ready&&now>=s->deadline))return failure(s,5);
 s->last=now;
 if(s->ready)return 1;
 int rc=mbedtls_ssl_handshake(&s->ssl);
 if(rc==MBEDTLS_ERR_SSL_WANT_READ||rc==MBEDTLS_ERR_SSL_WANT_WRITE)return 0;
 if(rc||!s->pin_verified||mbedtls_ssl_get_verify_result(&s->ssl)||mbedtls_ssl_get_version_number(&s->ssl)!=MBEDTLS_SSL_VERSION_TLS1_3){s->tls_error=rc;
 return failure(s,6);
 }s->ready=1;
 return 1;
}
int tls_ble_write(TlsBleEndpoint*s,uint64_t epoch,const uint8_t*p,size_t n){
 if(!active(s,epoch)||!s->ready||!n||n>1024||!outside(s,p,n))return -1;
 int rc=mbedtls_ssl_write(&s->ssl,p,n);
 if(rc<0&&rc!=MBEDTLS_ERR_SSL_WANT_READ&&rc!=MBEDTLS_ERR_SSL_WANT_WRITE){s->tls_error=rc;
 return failure(s,7);
 }return rc;
}
int tls_ble_read(TlsBleEndpoint*s,uint64_t epoch,uint8_t*p,size_t n){
 if(!active(s,epoch)||!s->ready||!n||n>1024||!outside(s,p,n))return -1;
 uint8_t pending[1024];
 int rc=mbedtls_ssl_read(&s->ssl,pending,n);
 if(rc>0)memcpy(p,pending,(size_t)rc);
 wipe(pending,sizeof pending);
 if(rc<=0&&rc!=MBEDTLS_ERR_SSL_WANT_READ&&rc!=MBEDTLS_ERR_SSL_WANT_WRITE){s->tls_error=rc;
 return failure(s,8);
 }return rc;
}
void tls_ble_close(TlsBleEndpoint*s){if(!s||!s->initialized||s->closed)return;
 mbedtls_ssl_free(&s->ssl);
 mbedtls_ssl_config_free(&s->config);
 mbedtls_x509_crt_free(&s->certificate);
 mbedtls_pk_free(&s->key);
 wipe(s,sizeof *s);
 s->closed=1;
 }
