#ifndef RABBIT_OWNER_AUTH_FRAME_H
#define RABBIT_OWNER_AUTH_FRAME_H
#include <stdint.h>
#include <stddef.h>
#include <noise/protocol.h>
#define OA_SIGNED 200u
#define OA_PLAIN 264u
#define OA_WIRE 304u
typedef struct {uint64_t epoch;uint8_t handshake[32],prologue[32],target[32],native[32],owner[32];} OaContext;
typedef struct {OaContext context;NoiseCipherState *send,*receive;uint8_t auth_hash[64];unsigned role,phase;} OaSession;
/* Borrowed genuine, fresh Split ciphers; trusted mapped/disjoint buffers and
 * single-owner lifetime. This does not authenticate their provenance/pinning. */
int oa_init(OaSession*,const OaContext*,unsigned,NoiseCipherState*,NoiseCipherState*);
int oa_signed_message(const OaContext*,uint8_t[OA_SIGNED]);
int oa_mac_auth(OaSession*,const uint8_t[64],uint8_t[OA_WIRE]);
int oa_dell_auth(OaSession*,const uint8_t*,size_t);
int oa_dell_ack(OaSession*,uint8_t[OA_WIRE]);
int oa_mac_ack(OaSession*,const uint8_t*,size_t);
int oa_mac_credentials_allowed(const OaSession*);
#endif
