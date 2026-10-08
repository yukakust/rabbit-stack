#ifndef RABBIT_TLS_SERVER_CHILD
#define RABBIT_TLS_SERVER_CHILD
#include "module_abi.h"
#include "tls_engine.h"
#define CHILD_OPEN 1u
#define CHILD_FEED 2u
#define CHILD_DRAIN 3u
#define CHILD_POLL 4u
#define CHILD_WRITE 5u
#define CHILD_READ 6u
#define CHILD_STATUS 7u
/* Entropy provider belongs to approved parent and must outlive close. This ABI
 * does NOT authenticate provider quality/physical QR; caller admission must. */
typedef int(EFIAPI*ChildEntropy)(void*,uint8_t*,size_t);
typedef struct {uint64_t epoch,now,duration;uint8_t*pool;size_t pool_bytes;const uint8_t*certificate;size_t certificate_bytes;const uint8_t*private_key;size_t private_key_bytes;const uint8_t*peer_spki;ChildEntropy entropy;void*entropy_context;} ChildOpen;
typedef struct {uint64_t epoch,now;uint32_t sequence,reserved;uint8_t*bytes;size_t count;int result;} ChildIo;
typedef struct {uint64_t epoch;uint32_t initialized,ready,fault,heap_live,quarantine;int tls_error;} ChildStatus;
Status EFIAPI tls_child_entry(void*,SystemTable*);
#endif
