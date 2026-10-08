/* PUBLIC upstream test certificate fixtures; synthetic entropy only. */
#include "tls_engine.h"
#include "tls_heap.h"
#include "mbedtls/platform.h"
#include "mbedtls/sha256.h"
#include "psa/crypto.h"
#include "test/certs.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static TlsHeap heap;static _Alignas(16) uint8_t pool[1048576];
static TlsBleEndpoint client,server;
static uint64_t fixture_state=UINT64_C(0x524142424954544c);static unsigned fail_entropy,entropy_calls;
static int fixture_rng(void*ctx,unsigned char*p,size_t n){(void)ctx;entropy_calls++;if(fail_entropy)return -1;while(n--){fixture_state^=fixture_state<<13;fixture_state^=fixture_state>>7;fixture_state^=fixture_state<<17;*p++=(uint8_t)fixture_state;}return 0;}
psa_status_t mbedtls_psa_external_get_random(mbedtls_psa_external_random_context_t*ctx,uint8_t*p,size_t n,size_t*actual){(void)ctx;*actual=0;if(fixture_rng(0,p,n))return PSA_ERROR_INSUFFICIENT_ENTROPY;*actual=n;return PSA_SUCCESS;}
static void pin(const uint8_t*p,size_t n,uint8_t hash[32]){mbedtls_x509_crt c;uint8_t der[128];mbedtls_x509_crt_init(&c);assert(!mbedtls_x509_crt_parse_der(&c,p,n));int bytes=mbedtls_pk_write_pubkey_der(&c.pk,der,sizeof der);assert(bytes>0);assert(!mbedtls_sha256(der+sizeof der-(size_t)bytes,(size_t)bytes,hash,0));mbedtls_x509_crt_free(&c);}
static void transfer(TlsBleEndpoint*a,TlsBleEndpoint*b,unsigned fragment,unsigned corrupt){uint8_t p[240];size_t n=tls_ble_drain(a,7,p,fragment);if(n){if(corrupt)p[n-1]^=1;assert(tls_ble_feed(b,7,b->feed_sequence,p,n)==1);}}
int main(void){
 size_t peak=0;unsigned cases=0,pin_checks=0;
 for(unsigned mode=0;mode<9;mode++){
  memset(&client,0,sizeof client);memset(&server,0,sizeof server);assert(tls_heap_bind(&heap,pool,sizeof pool));assert(!mbedtls_platform_set_calloc_free(tls_heap_calloc,tls_heap_free));assert(psa_crypto_init()==PSA_SUCCESS);
  uint8_t sp[32],cp[32];pin(mbedtls_test_srv_crt_ec_der,mbedtls_test_srv_crt_ec_der_len,sp);pin(mbedtls_test_cli_crt_ec_der,mbedtls_test_cli_crt_ec_der_len,cp);if(mode==1)sp[31]^=1;
  assert(tls_ble_open(&client,0,mbedtls_test_cli_crt_ec_der,mbedtls_test_cli_crt_ec_der_len,mbedtls_test_cli_key_ec_der,mbedtls_test_cli_key_ec_der_len,sp,"localhost",fixture_rng,0,7,1,50000000)==1);
  assert(tls_ble_open(&server,1,mbedtls_test_srv_crt_ec_der,mbedtls_test_srv_crt_ec_der_len,mbedtls_test_srv_key_ec_der,mbedtls_test_srv_key_ec_der_len,cp,0,fixture_rng,0,7,1,50000000)==1);
  if(mode==0){
   mbedtls_x509_crt peer;mbedtls_x509_crt_init(&peer);assert(!mbedtls_x509_crt_parse_der(&peer,mbedtls_test_srv_crt_ec_der,mbedtls_test_srv_crt_ec_der_len));
   for(unsigned bit=0;bit<256;bit++){
    client.expected_spki[bit/8]^=(uint8_t)(1u<<(bit%8));uint32_t flags=MBEDTLS_X509_BADCERT_NOT_TRUSTED;client.pin_verified=0;
    assert(client.config.MBEDTLS_PRIVATE(f_vrfy)(client.config.MBEDTLS_PRIVATE(p_vrfy),&peer,0,&flags)<0&&!client.pin_verified);
    client.expected_spki[bit/8]^=(uint8_t)(1u<<(bit%8));pin_checks++;
   }
   for(unsigned i=0;i<2;i++){
    uint32_t flags=MBEDTLS_X509_BADCERT_NOT_TRUSTED|(i?MBEDTLS_X509_BADCERT_EXPIRED:MBEDTLS_X509_BADCERT_CN_MISMATCH);client.pin_verified=0;
    assert(client.config.MBEDTLS_PRIVATE(f_vrfy)(client.config.MBEDTLS_PRIVATE(p_vrfy),&peer,0,&flags)<0&&!client.pin_verified);pin_checks++;
   }
   uint32_t flags=MBEDTLS_X509_BADCERT_NOT_TRUSTED;
   assert(client.config.MBEDTLS_PRIVATE(f_vrfy)(client.config.MBEDTLS_PRIVATE(p_vrfy),&peer,1,&flags)<0);pin_checks++;
   flags=MBEDTLS_X509_BADCERT_NOT_TRUSTED;assert(!client.config.MBEDTLS_PRIVATE(f_vrfy)(client.config.MBEDTLS_PRIVATE(p_vrfy),&peer,0,&flags)&&client.pin_verified&&!flags);pin_checks++;client.pin_verified=0;mbedtls_x509_crt_free(&peer);
   size_t used=heap.used;assert(!tls_heap_calloc(SIZE_MAX,2)&&heap.used==used);
  }
  uint8_t message[]={0x52,0x57,0x54,0x53,0,1},received[64]={0};assert(tls_ble_write(&client,7,message,sizeof message)<0);assert(!client.outbound_bytes);
  if(mode==2)fail_entropy=1;
  if(mode==3)assert(tls_ble_poll(&client,7,50000001)<0);
  if(mode==4){uint8_t x=1;assert(tls_ble_feed(&client,7,1,&x,1)<0);}
  if(mode==5){uint8_t x=1;assert(tls_ble_feed(&client,8,0,&x,1)<0);}
  int rc=0,rs=0;unsigned fragment=mode==6?1:mode==7?17:240;
  for(unsigned ticks=0;ticks<20000&&!client.fault&&!server.fault&&(!client.ready||!server.ready);ticks++){
   rc=tls_ble_poll(&client,7,2+ticks*1000);rs=tls_ble_poll(&server,7,2+ticks*1000);if(rc<0||rs<0)break;transfer(&client,&server,fragment,0);transfer(&server,&client,fragment,0);
  }
  if(mode==0||mode==6||mode==7||mode==8){
   if(!client.ready||!server.ready)printf("handshake failure mode=%u client_fault=%u server_fault=%u rc=%d rs=%d errors=%d,%d\n",mode,client.fault,server.fault,rc,rs,client.tls_error,server.tls_error);
   assert(client.ready&&server.ready&&client.pin_verified&&server.pin_verified);assert(tls_ble_write(&client,7,message,sizeof message)==sizeof message);
   for(unsigned i=0;i<1000&&!received[0]&&!server.fault;i++){transfer(&client,&server,17,mode==8&&i==0);int n=tls_ble_read(&server,7,received,sizeof received);if(n>0){assert(n==sizeof message&&!memcmp(message,received,sizeof message));break;}assert(n==MBEDTLS_ERR_SSL_WANT_READ||n==MBEDTLS_ERR_SSL_WANT_WRITE||server.fault);}
   if(mode==8){assert(server.fault&&!received[0]);assert(tls_ble_write(&server,7,message,sizeof message)<0);}else assert(received[0]);assert(tls_ble_write(&client,8,message,sizeof message)<0);
   if(mode==0){assert(tls_ble_write(&client,7,client.expected_spki,32)<0);assert(!tls_ble_drain(&client,7,(uint8_t*)&client,sizeof client));assert(tls_ble_feed(&client,7,client.feed_sequence,client.inbound,1)<0);}
  }else{assert(client.fault||server.fault);assert(!client.ready&&!server.ready);assert(tls_ble_write(&client,7,message,sizeof message)<0);}
  fail_entropy=0;if(heap.high_water>peak)peak=heap.high_water;tls_ble_close(&client);tls_ble_close(&server);mbedtls_psa_crypto_free();assert(!heap.live&&!heap.quarantine);assert(tls_heap_release(&heap));cases++;
 }
 printf("PASS %u genuine TLS13 both-endpoint synthetic cases + %u actual SPKI callback checks; heap_peak=%zu endpoint_bytes=%zu heap_metadata=%zu; no secret output\n",cases,pin_checks,peak,sizeof(TlsBleEndpoint),sizeof(TlsHeap));return 0;
}
