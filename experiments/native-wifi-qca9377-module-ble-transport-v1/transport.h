#ifndef RABBIT_NATIVE_MODULE_BLE_TRANSPORT
#define RABBIT_NATIVE_MODULE_BLE_TRANSPORT
#include <stdint.h>
#include <stddef.h>
#define MT_MAX 65824u
enum {MT_IDLE,MT_STAGING,MT_PENDING,MT_ACCEPTED,MT_REJECTED,MT_CLOSED};
typedef int(*MtAccept)(void*,const uint8_t*,size_t);
typedef struct {
 uint8_t bytes[MT_MAX],session[8],digest[32];uint64_t epoch,started,last,progress;
 uint32_t length,received,state,error;int32_t result;unsigned borrowed;
 MtAccept accept;void*context;
} ModuleTransport;
/* Public owner-signed module bytes only: no credential or TLS secret route.
 * Outer digest/session grants no execution authority; accept must verify exact
 * owner/target/installed parent/epoch/counter/role ABI and genuine PE lifecycle.
 * A complete chunk stays PENDING until sole native loop calls mt_poll outside
 * all ATT/HCI callbacks. No bootstrap/RfFile callback is changed. */
int mt_bind(ModuleTransport*,uint64_t,MtAccept,void*);
/* B(1): 1+session8+length4+SHA25632. C(3): 1+session8. X(4): same.
 * D(2): 1+session8+offset4+bytes1..231. Exact repeated bytes are idempotent. */
int mt_control(ModuleTransport*,const uint8_t*,size_t,uint64_t epoch,uint64_t us);
int mt_data(ModuleTransport*,const uint8_t*,size_t,uint64_t epoch,uint64_t us);
int mt_poll(ModuleTransport*,uint64_t epoch,uint64_t us);
int mt_status(const ModuleTransport*,uint64_t epoch,uint8_t out[80]);
int mt_close(ModuleTransport*,uint64_t epoch);
/* New service33 handles20..26, UUID suffix34/35/36 values. Must run before
 * legacy firmware service's catch-all handle checks. Return SIZE_MAX if not
 * this service; disjoint inputs/outputs/metadata, bounded negotiated MTU247. */
size_t mt_att(ModuleTransport*,uint16_t mtu,const uint8_t*,size_t,uint8_t*,size_t,uint64_t epoch,uint64_t us);
#endif
