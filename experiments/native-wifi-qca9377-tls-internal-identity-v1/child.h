#ifndef RABBIT_TLS_INTERNAL_IDENTITY_CHILD
#define RABBIT_TLS_INTERNAL_IDENTITY_CHILD
#include "module_abi.h"
#include "tls_engine.h"
#include "seed_source.h"
#include "qr/panel.h"
#define CHILD_OPEN 1u /* REJECTED: imported Dell private key path removed. */
#define CHILD_FEED 2u
#define CHILD_DRAIN 3u
#define CHILD_POLL 4u
#define CHILD_WRITE 5u
#define CHILD_READ 6u
#define CHILD_STATUS 7u
#define CHILD_GENERATE 0x10u
#define CHILD_PUBLIC 0x11u
#define CHILD_ACTIVATE 0x12u
#define CHILD_PUBLIC_QR 0x14u
#define CHILD_DEACTIVATE 0x13u /* clears TLS session, retains local identity */
typedef int(EFIAPI*IdentitySeedFill)(void*,uint64_t,const uint8_t[32],uint8_t*,size_t);
typedef struct {void*context;size_t context_bytes;IdentitySeedFill fill;uint8_t source_sha256[32];} IdentitySeed;
/* Parent-private reviewed request, not a plaintext GATT approval message. */
typedef struct {uint64_t epoch,now;uint8_t*pool;size_t pool_bytes;RngApproval approval;IdentitySeed source;} ChildGenerate;
typedef struct {uint64_t epoch,now,duration;const uint8_t*peer_spki;} ChildActivate;
typedef struct {uint64_t epoch;uint32_t certificate_bytes,spki_bytes;uint8_t certificate[1024],spki[128],sha256[32];char fingerprint[65];uint8_t reserved[7];} ChildPublic;
typedef struct {uint64_t epoch,now;PairingPanel panel;} ChildPublicQr;
typedef struct {uint64_t epoch,now;uint32_t sequence,reserved;uint8_t*bytes;size_t count;int result;} ChildIo;
typedef struct {uint64_t epoch;uint32_t initialized,ready,fault,heap_live,quarantine;int tls_error;} ChildStatus;
_Static_assert(sizeof(ChildPublicQr)==392,"public QR ABI");
_Static_assert(sizeof(ChildGenerate)==208,"generate ABI");
_Static_assert(sizeof(ChildPublic)==1272,"public-only identity ABI");
_Static_assert(sizeof(ChildActivate)==32,"activation ABI");
Status EFIAPI tls_child_entry(void*,SystemTable*);
#endif
