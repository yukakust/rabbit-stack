#ifndef RABBIT_TLS_BLE_ENGINE_H
#define RABBIT_TLS_BLE_ENGINE_H
#include <stdint.h>
#include <stddef.h>
#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/pk.h"
enum {TLS_BLE_QUEUE=8192,TLS_BLE_FRAGMENT=240};
typedef int(*TlsEntropy)(void*,unsigned char*,size_t);
typedef struct {
 mbedtls_ssl_context ssl;mbedtls_ssl_config config;mbedtls_x509_crt certificate;mbedtls_pk_context key;
 uint8_t inbound[TLS_BLE_QUEUE],outbound[TLS_BLE_QUEUE],expected_spki[32];
 size_t inbound_bytes,outbound_bytes;uint64_t epoch,deadline,last;uint32_t feed_sequence;
 TlsEntropy entropy;void*entropy_context;unsigned initialized,pin_verified,ready,fault,closed;int tls_error;
} TlsBleEndpoint;
/* Public test certificates are separate fixtures. Caller supplies valid owned
 * context and independently physical-confirmed full SPKI SHA256 pin in future.
 * Prototype does not create that approval or handle owner AUTH/credentials. */
int tls_ble_open(TlsBleEndpoint*,unsigned,const uint8_t*,size_t,const uint8_t*,size_t,const uint8_t[32],const char*,TlsEntropy,void*,uint64_t,uint64_t,uint64_t);
int tls_ble_feed(TlsBleEndpoint*,uint64_t,uint32_t,const uint8_t*,size_t);
size_t tls_ble_drain(TlsBleEndpoint*,uint64_t,uint8_t*,size_t);
int tls_ble_poll(TlsBleEndpoint*,uint64_t,uint64_t);
int tls_ble_write(TlsBleEndpoint*,uint64_t,const uint8_t*,size_t);
int tls_ble_read(TlsBleEndpoint*,uint64_t,uint8_t*,size_t);
void tls_ble_close(TlsBleEndpoint*);
#endif
